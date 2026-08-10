# Adversarial Attack Description Document: Evidence Attacks on Automated Fact-Checking (AFC)
**Revision 2** — extracted single-attack file from Evidence_Attack_Descriptions_v2.md

This document contains one attack description from the **14 Evidence Attacks** targeting Automated Fact-Checking (AFC) systems reviewed in *"Adversarial Attacks Against Automated Fact-Checking: A Survey"* (Liu et al., 2025).

---

<a id="9-ea-claimrewrite-01"></a>
# 9. EA-CLAIMREWRITE-01: Claim-Aligned Re-Writing (Verifier Attack)

## 1. Metadata
- **Attack ID**: `EA-CLAIMREWRITE-01`
- **Attack Name**: Claim-Aligned Re-Writing (Verifier Attack)
- **Category**: `evidence_attack`
- **Attack Target**: `corrupted_verdict`
- **Edit Granularity**: `sentence`
- **Strategy Type**: `lm_based`
- **Access Assumption**: White-box verification (BERT verifier), Black-box retrieval
- **Source Paper**: Abdelnabi and Fritz (2023); Liu et al. (2025), Sec. 5.2.1, Table 4

## 2. Description
This attack masks top important tokens identified by a neural verification model (BERT) in gold evidence sentences, and uses a seq2seq model (T5) to reconstruct context-preserving fake supporting evidence. The candidate sentence that maximizes the `SUP` probability of the verifier is selected, causing `REF` claims to flip to `SUP`. The survey notes this attack is difficult to apply to `NEI` claims.

## 3. Preconditions / Required Inputs
- `original_evidence` (Required): Original refuting evidence.
- `claim_text` (Required): Original claim text.
- `gold_label` (Required): `REF` gold label.
- `access_to_verifier_scores` (Required): Token salience / gradient scores from the verifier model.
- `t5_reconstruction_model` (Required): T5 or equivalent seq2seq fill-in-the-blank model.

## 4. Procedure
1. Pass `original_evidence` and `claim_text` to the BERT verification model to compute token importance scores.
2. Mask the top-$k$ most important tokens in `original_evidence` with mask tokens.
3. Pass the masked evidence to a T5 seq2seq model to generate top-$N$ candidate reconstructions.
4. Evaluate all candidates against the BERT verifier and pick the candidate maximizing the `SUP` logit score.
5. Return the generated adversarial evidence sentence.

## 5. Output Schema (JSON)
```json
{
  "attack_id": "EA-CLAIMREWRITE-01",
  "language": "ml",
  "original_claim": "ഭൂമി പരന്നതാണ്.",
  "original_evidence": "ശാസ്ത്രീയ തെളിവുകൾ അനുസരിച്ച് ഭൂമി ഗോളാകൃതിയിലുള്ളതാണ്.",
  "adversarial_claim": null,
  "adversarial_evidence": "ശാസ്ത്രീയ തെളിവുകൾ അനുസരിച്ച് ഭൂമി പരന്ന രൂപത്തിലുള്ളതാണ്.",
  "gold_label": "REF",
  "target_label": "SUP",
  "edit_granularity": "sentence",
  "technique_params": {
    "masked_token": "ഗോളാകൃതിയിലുള്ളതാണ്",
    "t5_candidates_sampled": 10
  },
  "validity_flags": {
    "fluency_checked": true,
    "label_consistent": true,
    "meaning_preserved": false
  }
}
```

## 6A. Implementation Notes
| Language | Script | Execution Blockers / Requirements (tooling only) |
| --- | --- | --- |
| Hindi | Devanagari | Require Hindi T5 model (e.g., mT5/IndicmT5). |
| Manipuri | Meitei Mayek / Bengali (script varies by corpus) | Manipuri T5 reconstruction model for the target script. |
| Telugu | Telugu | Require Telugu T5 reconstruction model. |
| Urdu | Perso-Arabic (RTL) | Require Urdu T5 model & RTL tokenizer. |
| Punjabi | Gurmukhi | Require Punjabi T5 reconstruction model. |
| Tamil | Tamil | Require Tamil T5 reconstruction model. |
| Odia | Odia | Require Odia T5 reconstruction model. |
| Malayalam | Malayalam | Require Malayalam T5 reconstruction model. |

### Generic Mechanical Checklist
- Grapheme-cluster-aware segmentation available? No
- RTL-safe tokenization/reassembly available? Yes (for Urdu)
- Morphological analyzer / stemmer available? Optional
- Synonym / paraphrase resource or LM available for this language? Yes (T5 Span Infilling)
- Script-specific confusables/homoglyph table available? No

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
- **Verdict Shift (`REF` → `SUP`)**: High success rate in shifting verifier stance.
- **Recall of Adversarial Evidence (`RecAdvEvd`)**: High recall metric (e.g., 94.4% reported in the survey for KGAT).

## 8. Example
| Field | Original | Adversarial |
| --- | --- | --- |
| Claim / Evidence | **Claim**: The Earth is flat.<br>**Evidence**: According to scientific evidence, the Earth is spherical. | **Adversarial Evidence**: According to scientific evidence, the Earth is flat-shaped. |
| Label | REF → SUP | |
| Language | English (`en`) / Malayalam (`ml`) | |

## 9. Failure Modes / Skip Conditions
- Skip if verifier token salience scores cannot be accessed.
- Skip if a T5 masked reconstruction model is not available for the target language.
- Skip (or flag) if the claim is `NEI`, since the survey notes this attack does not transfer well to `NEI` claims.
