# Indic Fact-Checking Adversarial Framework

[![Hugging Face Model](https://img.shields.io/badge/🤗%20Hugging%20Face-Model-blue)](https://huggingface.co/Categorica/XLM-R-Indic-Hardened)
[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://indic-factcheck-adversarial-robustness.onrender.com/)

> **Note to Graders/Evaluators:** The Interactive UI Dashboard is hosted on a free Render instance. If the dashboard hasn't been accessed recently, the server may go to sleep to save resources. **It may take 45-60 seconds to wake up and load on your very first click!**

This project evaluates and hardens an XLM-RoBERTa model against adversarial attacks in Indian languages. It features a complete pipeline from dataset stratified splitting, adversarial generative augmentation, head-only fine-tuning for defense, and automated evaluation orchestration.

## Setup

1. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure you have the `GEMINI_API_KEY` set in your environment if you plan on regenerating adversarial data. (The evaluation orchestrator uses the hardcoded key or environmental variable).

## Project Structure

* **`dataset/`**: Contains raw train, validation, and holdout (test) data.
* **`attack/`**: Contains the Markdown definitions of all 56 generative and rule-based attacks.
* **`framework/`**: The core source code for the framework.
  * **`framework/evaluation/data_splitter.py`**: Stratified data splitting to perfectly balance regional languages.
  * **`framework/evaluation/augment_train.py`**: Generates adversarial training examples using the LLM.
  * **`framework/models/trainer.py`**: Finetunes the classification head of `xlm-roberta-large-xnli` with the augmented data.
  * **`framework/evaluation/orchestrator.py`**: Evaluates the baseline model and hardened model against the test set, outputting the CSV matrix.
  * **`framework/ui/app.py`**: The Gradio web dashboard.

## Running the Pipeline

To re-run the pipeline from scratch:

1. **Split Data**:
   ```bash
   python framework/evaluation/data_splitter.py
   ```
2. **Augment Training Data**:
   ```bash
   python framework/evaluation/augment_train.py
   ```
3. **Train Hardened Model**:
   ```bash
   python framework/models/trainer.py
   ```
4. **Generate Evaluation Matrix**:
   ```bash
   python framework/evaluation/orchestrator.py
   ```
   *(This will create `final_evaluation_report.csv`)*

## Launching the UI Dashboard

To visualize the evaluation matrix and interactively test attacks on custom sentences:
```bash
python framework/ui/app.py
```
Then navigate to `http://127.0.0.1:7860` in your browser.
