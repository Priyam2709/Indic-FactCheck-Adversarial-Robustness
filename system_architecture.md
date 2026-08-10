# Unified Adversarial Testing Framework Architecture

To integrate both attacks (which happen dynamically) and defenses (which can be baked into training or applied at inference) into a single system, you need a **Modular Component Architecture**. 

Instead of writing a single script, you build a framework where Retrievers, Verifiers, and Attackers are treated as interchangeable "plugins".

## System Architecture Diagram

```mermaid
graph TD
    subgraph "1. Batched Context Window Architecture (Phase 5.1)"
        A[(Original Dataset 8 Languages)] -->|Extracts| B[Pandas DataFrame]
        B -->|Chunks| C[Batch Array of 50 Claims]
        
        C --> D{Multi-Agent Orchestrator}
        D -->|JSON Array Request| E[Gemini 3.5 API]
        E -->|Fault Tolerance| F{Exponential Backoff Retry}
        F -->|Fails 429| E
        F -->|Success| G[JSON Array Response]
        
        G --> H[Valid NLI Baseline Verifier \n xlm-roberta-large-xnli]
        H --> I[(Adversarial Dataset)]
    end

    subgraph "2. Pluggable Defended FC Pipeline"
        I --> J{Retriever Module}
        J -->|Baseline| K[Standard BM25 / DPR]
        J -->|Defense Plugin| L[Quin+ / AdMIRaL]
        
        K --> M{Verifier Module}
        L --> M
        
        M -->|Baseline| N[Standard RoBERTa]
        M -->|Training Defense| O[PoE / DFL Pre-trained Models]
        M -->|Inference Defense| P[CLEVER / Temporal Logic]
    end

    subgraph "3. Evaluation & Reporting"
        N --> Q[Metrics Calculator]
        O --> Q
        P --> Q
        Q --> R[[Final Applicability & Success Table]]
    end
    
    %% Styling
    classDef attacker fill:#f9d0c4,stroke:#333,stroke-width:2px;
    classDef defender fill:#d4e6f1,stroke:#333,stroke-width:2px;
    classDef eval fill:#d5f5e3,stroke:#333,stroke-width:2px;
    
    class D,E,F,G attacker;
    class J,K,L,M,N,O,P defender;
    class Q,R eval;
```

## Core Components

### 1. The Model Zoo (For Training-Time Defenses)
Defenses like **PoE** (Product of Experts) and **DFL** (Debiased Focal Loss) must be applied during training. 
* **Design:** You pre-train these models offline. Your system has a "Model Zoo" folder containing `baseline_roberta.pt`, `poe_roberta.pt`, and `dfl_roberta.pt`. 
* **Integration:** When configuring a test run, the system simply loads the requested model weights from the zoo.

### 2. The Pluggable Pipeline (For Inference-Time Defenses)
Defenses like **Quin+** (retrieval) or **CLEVER** (verification logic) run live.
* **Design:** Use an Object-Oriented approach. Define a standard `Retriever` class and `Verifier` class. 
* **Integration:** 
  ```python
  # Standard Run
  pipeline = FCPipeline(retriever=BM25(), verifier=StandardBERT())
  
  # Defended Run
  pipeline = FCPipeline(retriever=QuinPlus(), verifier=CLEVER())
  ```

### 3. The Attack Orchestrator
This manages the 53 attacks across 8 languages.
* **Design:** A single dispatcher that takes an input claim, an `attack_type`, and a `language_code`. It routes rule-based attacks to your local Python functions and generative attacks to an LLM API.
* **Integration:** It outputs a standardized JSON adversarial dataset that is completely decoupled from the fact-checking models, meaning you can generate the attacks once and test them against 10 different defense configurations without regenerating them.

## Workflow of an Integrated Experiment

1. **Configuration:** The Orchestrator automatically targets the 8 Indic language datasets (e.g. Hindi, Malayalam, Urdu) and the 53 loaded Attack Agents.
2. **Batched Attack Generation:** The Orchestrator chunks the dataset into 50-row batches. It prompts Gemini to apply the attack (e.g., `Fact Mixing`) across all 50 claims simultaneously, safely retrying via exponential backoff if the Free-Tier limit is hit.
3. **Baseline Verification:** The adversarial claims are passed to the valid NLI Baseline Verifier (`xlm-roberta-large-xnli`) to mathematically calculate the drop in Entailment vs. Contradiction.
4. **Defense Assembly (Phase 6):** Once the defense descriptions are uploaded, the system dynamically wraps the NLI Verifier with the specified defense (e.g., `CLEVER` or `DFL_Model`).
5. **Reporting:** The Orchestrator compiles the cross-matrix of every attack, against every language, with and without defenses, saving the success rates to `evaluation_report.csv` for the Gradio UI.
