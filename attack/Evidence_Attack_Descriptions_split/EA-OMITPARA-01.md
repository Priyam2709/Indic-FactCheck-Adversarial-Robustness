# Adversarial Attack Description Document: Evidence Attacks on Automated Fact-Checking (AFC)
**Revision 2** — extracted single-attack file from Evidence_Attack_Descriptions_v2.md

This document contains one attack description from the **14 Evidence Attacks** targeting Automated Fact-Checking (AFC) systems reviewed in *"Adversarial Attacks Against Automated Fact-Checking: A Survey"* (Liu et al., 2025).

---

<a id="7-ea-omitpara-01"></a>
# 7. EA-OMITPARA-01: Omitting Paraphrase Attack

## 1. Metadata
- **Attack ID**: `EA-OMITPARA-01`
- **Attack Name**: Omitting Paraphrase Attack
- **Category**: `evidence_attack`
- **Attack Target**: `disrupted_retrieval`
- **Edit Granularity**: `sentence`
- **Strategy Type**: `lm_based`
- **Access Assumption**: Black-box retrieval, White-box verification
- **Source Paper**: Abdelnabi and Fritz (2023); Liu et al. (2025), Sec. 5.2.2, Table 4

## 2. Description
Omitting Paraphrase uses a seq2seq paraphrasing model (e.g., PEGASUS) to rewrite original evidence sentences while selectively omitting key claim-salient snippets/entities. The perturbed evidence retains high surface naturalness but hides vital facts from FC retrievers and verifiers, causing `SUP`/`REF` claims to be misclassified as `NEI`.

## 3. Preconditions / Required Inputs
- `original_evidence` (Required): Full ground truth evidence text.
- `claim_text` (Required): Claim text.
- `gold_label` (Required): Gold label (`SUP`, `REF`).
- `pegasus_paraphraser` (Required): Fine-tuned paraphrasing model.

## 4. Procedure
1. Extract claim-salient keywords/entities using token salience scoring.
2. Prompt the PEGASUS model to paraphrase `original_evidence` while constraining output to omit extracted claim-salient snippets.
3. Verify that the remaining paraphrased sentence maintains syntactic structure.
4. Replace the original evidence document with the paraphrased evidence in the corpus repository.

## 5. Output Schema (JSON)
```json
{
  "attack_id": "EA-OMITPARA-01",
  "language": "ta",
  "original_claim": "சூரியன் கிழக்கில் உதிக்கிறது.",
  "original_evidence": "சூரியன் கிழக்கில் உதித்து மேற்கில் மறைகிறது என்பது ஒரு இயற்கை உண்மை.",
  "adversarial_claim": null,
  "adversarial_evidence": "சூரியன் மாலையில் மேற்கில் மறைகிறது என்பது ஒரு இயற்கை உண்மை.",
  "gold_label": "SUP",
  "target_label": "NEI",
  "edit_granularity": "sentence",
  "technique_params": {
    "omitted_snippet": "கிழக்கில் உதித்து"
  },
  "validity_flags": {
    "fluency_checked": true,
    "label_consistent": true,
    "meaning_preserved": false
  }
}
```
*(Corrected from v1: the original_claim previously contained a stray Gurmukhi character `ਉ` inside Tamil text; replaced with Tamil உ.)*

## 6A. Implementation Notes
| Language | Script | Execution Blockers / Requirements (tooling only) |
| --- | --- | --- |
| Hindi | Devanagari | Require Hindi constrained seq2seq paraphraser. |
| Manipuri | Meitei Mayek / Bengali (script varies by corpus) | Manipuri seq2seq paraphraser for the target script. |
| Telugu | Telugu | Require Telugu seq2seq paraphraser. |
| Urdu | Perso-Arabic (RTL) | Require Urdu seq2seq paraphraser & RTL handling. |
| Punjabi | Gurmukhi | Require Punjabi seq2seq paraphraser. |
| Tamil | Tamil | Require Tamil seq2seq paraphraser. |
| Odia | Odia | Require Odia seq2seq paraphraser. |
| Malayalam | Malayalam | Require Malayalam seq2seq paraphraser. |

### Generic Mechanical Checklist
- Grapheme-cluster-aware segmentation available? No
- RTL-safe tokenization/reassembly available? Yes (for Urdu)
- Morphological analyzer / stemmer available? Optional
- Synonym / paraphrase resource or LM available for this language? Yes (CRITICAL)
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
- **Shift to NEI Rate (`→ NEI %`)**: High percentage of verdicts shifting to `NEI` (e.g., 54.4% reported for KGAT in the survey).
- **Adversarial Evidence Recall (`RecAdvEvd`)**: Low retrieval ranking score for perturbed evidence.

## 8. Example
| Field | Original | Adversarial |
| --- | --- | --- |
| Claim / Evidence | **Evidence**: Sun rises in the east and sets in the west is a natural fact. | **Adversarial Evidence**: Sun sets in the west in the evening is a natural fact. *(Rising-in-the-east snippet omitted)* |
| Label | SUP → NEI | |
| Language | English (`en`) / Tamil (`ta`) | |

## 9. Failure Modes / Skip Conditions
- Skip if the evidence text is too short to omit snippets without breaking grammar.
- Skip if a paraphrasing model for the target language is unavailable.
