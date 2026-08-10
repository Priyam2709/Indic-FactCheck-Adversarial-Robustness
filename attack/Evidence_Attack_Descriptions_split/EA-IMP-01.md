# Adversarial Attack Description Document: Evidence Attacks on Automated Fact-Checking (AFC)
**Revision 2** — extracted single-attack file from Evidence_Attack_Descriptions_v2.md

This document contains one attack description from the **14 Evidence Attacks** targeting Automated Fact-Checking (AFC) systems reviewed in *"Adversarial Attacks Against Automated Fact-Checking: A Survey"* (Liu et al., 2025).

---

<a id="3-ea-imp-01"></a>
# 3. EA-IMP-01: Imperceptible Character-Level Verification Attack

## 1. Metadata
- **Attack ID**: `EA-IMP-01`
- **Attack Name**: Imperceptible Character-Level Verification Attack
- **Category**: `evidence_attack`
- **Attack Target**: `corrupted_verdict`
- **Edit Granularity**: `character`
- **Strategy Type**: `rule_based`
- **Access Assumption**: Black-box verification (iterative, query-based optimization against classifier output — no gradient access required)
- **Source Paper**: Boucher et al. (2022); Liu et al. (2025), Sec. 5.2.2, Table 4

## 2. Description
This attack modifies characters inside the evidence text by replacing standard Unicode characters with visually identical homoglyphs, zero-width space characters, or deletion control characters (e.g., `U+200B`, `U+0008`). These edits disrupt subword tokenization in neural verifiers (e.g., BERT/RoBERTa) to force incorrect veracity predictions while remaining visually imperceptible to human readers.

## 3. Preconditions / Required Inputs
- `original_evidence` (Required): Target evidence text to perturb.
- `claim_text` (Required): Associated claim text.
- `gold_label` (Required): Gold label (`SUP`, `REF`, `NEI`).
- `access_to_verifier_scores` (Required): Black-box query access to model output probabilities, used to evaluate and guide candidate perturbations.
- `homoglyph_map` (Required): Dictionary of Unicode confusables for the target script.

## 4. Procedure
1. Parse `original_evidence` into grapheme clusters.
2. Identify candidate character positions corresponding to key named entities or salient verbs.
3. Query `homoglyph_map` or insert zero-width non-joiner (`U+200C`) / control characters into selected grapheme clusters.
4. Query the verifier model's output probability for `gold_label` on each candidate perturbation (evolutionary/black-box search, no gradients needed).
5. Iteratively select the perturbation that minimizes the probability of `gold_label` under a character edit budget $\epsilon \le 5$.
6. Output the perturbed adversarial evidence text.

## 5. Output Schema (JSON)
```json
{
  "attack_id": "EA-IMP-01",
  "language": "hi",
  "original_claim": "महात्मा गांधी का जन्म 1869 में हुआ था।",
  "original_evidence": "महात्मा गांधी का जन्म 2 अक्टूबर 1869 को पोरबंदर में हुआ था।",
  "adversarial_claim": null,
  "adversarial_evidence": "म​हात्मा गां​धी का जन्म 2 अक्​टूबर 1869 को पोर​बंदर में हुआ था।",
  "gold_label": "SUP",
  "target_label": "REF",
  "edit_granularity": "character",
  "technique_params": {
    "control_char_inserted": "U+200B",
    "edit_budget_epsilon": 5
  },
  "validity_flags": {
    "fluency_checked": true,
    "label_consistent": true,
    "meaning_preserved": true
  }
}
```

## 6A. Implementation Notes
| Language | Script | Execution Blockers / Requirements (tooling only) |
| --- | --- | --- |
| Hindi | Devanagari | Grapheme cluster segmentation (`regex` / `unicodedata`), Devanagari homoglyph confusable table. |
| Manipuri | Meitei Mayek / Bengali (script varies by corpus) | Unicode confusable mapping & grapheme parser for whichever script the corpus uses. |
| Telugu | Telugu | Telugu grapheme segmentation & confusable mapping. |
| Urdu | Perso-Arabic (RTL) | RTL character joiner aware parser (ZWJ/ZWNJ preservation). |
| Punjabi | Gurmukhi | Gurmukhi grapheme parser & confusable table. |
| Tamil | Tamil | Tamil composite character aware parser. |
| Odia | Odia | Odia grapheme parser & confusable table. |
| Malayalam | Malayalam | Malayalam chillu & conjunct aware grapheme parser. |

### Generic Mechanical Checklist
- Grapheme-cluster-aware segmentation available? Yes (CRITICAL)
- RTL-safe tokenization/reassembly available? Yes (for Urdu)
- Morphological analyzer / stemmer available? No
- Synonym / paraphrase resource or LM available for this language? No
- Script-specific confusables/homoglyph table available? Yes (CRITICAL)

## 6B. Empirical Outcome
```json
{
  "language": "",
  "attack_executed": true,
  "execution_notes": "",
  "verdict_flipped": null,
  "retrieval_disrupted": null,
  "fluency_score": null,
  "human_detectability": null,
  "attack_success_rate": null,
  "notes": ""
}
```

## 7. Success / Validity Criteria
- **Human Detectability**: Zero visual difference when rendered in standard browser/UI fonts.
- **Verdict Flipped Rate**: High rate of verifier misclassification (e.g., `SUP` → `REF` or `NEI`).
- **Low Edit Distance**: Normalized character edit distance ≤ 0.05.

## 8. Example
| Field | Original | Adversarial |
| --- | --- | --- |
| Claim / Evidence | **Evidence**: Mahatma Gandhi was born on 2 October 1869. | **Adversarial Evidence**: Mаhatma Gаndhi was born on 2 Oсtober 1869. *(Cyrillic 'а' and 'с' substituted for Latin 'a' and 'c')* |
| Label | SUP → REF | |
| Language | English (`en`) / Hindi (`hi`) | |

## 9. Failure Modes / Skip Conditions
- Skip if a text normalization / Unicode strip sanitization pipeline is active upstream of the verifier.
- Skip if `homoglyph_map` is empty for the target Indic script.
