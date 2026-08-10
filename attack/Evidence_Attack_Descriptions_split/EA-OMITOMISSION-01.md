# Adversarial Attack Description Document: Evidence Attacks on Automated Fact-Checking (AFC)
**Revision 2** — extracted single-attack file from Evidence_Attack_Descriptions_v2.md

This document contains one attack description from the **14 Evidence Attacks** targeting Automated Fact-Checking (AFC) systems reviewed in *"Adversarial Attacks Against Automated Fact-Checking: A Survey"* (Liu et al., 2025).

---

<a id="13-ea-omitomission-01"></a>
# 13. EA-OMITOMISSION-01: Omission Generation Attack

## 1. Metadata
- **Attack ID**: `EA-OMITOMISSION-01`
- **Attack Name**: Omission Generation Attack
- **Category**: `evidence_attack`
- **Attack Target**: `disrupted_retrieval` / `corrupted_verdict` (survey frames it primarily as impairing evidence sufficiency prediction)
- **Edit Granularity**: `sentence`
- **Strategy Type**: `rule_based`
- **Access Assumption**: Black-box retrieval, Black-box verification
- **Source Paper**: Atanasova et al. (2022); Liu et al. (2025), Sec. 5.2.1, Table 4

## 2. Description
Omission Generation systematically deletes specific syntactic constructs (e.g., prepositional phrases, temporal modifiers, date entities, or subordinate clauses) from original gold evidence sentences. By stripping away essential qualifiers while preserving surface stance, it impairs evidence sufficiency prediction in BERT/RoBERTa/ALBERT verifiers, forcing `SUP`/`REF` claims into `NEI`.

## 3. Preconditions / Required Inputs
- `original_evidence` (Required): Complete gold evidence sentence.
- `claim_text` (Required): Target claim text.
- `gold_label` (Required): `SUP` or `REF` gold label.
- `dependency_parser` (Required): Syntactic dependency parser / POS tagger for the target language.

## 4. Procedure
1. Parse `original_evidence` using a dependency parser / POS tagger.
2. Identify optional syntactic constructs: prepositional phrases (`PP`), temporal/date modifiers (`NUM`/`DATE`), or relative clauses.
3. Delete the identified constructs from the evidence sentence.
4. Verify that the remaining text retains valid grammatical structure.
5. Pass the modified evidence to the verifier to check for a `NEI` stance shift.

## 5. Output Schema (JSON)
```json
{
  "attack_id": "EA-OMITOMISSION-01",
  "language": "hi",
  "original_claim": "अटल बिहारी वाजपेयी 1998 में भारत के प्रधानमंत्री बने।",
  "original_evidence": "अटल बिहारी वाजपेयी 1998 से 2004 तक भारत के प्रधानमंत्री रहे।",
  "adversarial_claim": null,
  "adversarial_evidence": "अटल बिहारी वाजपेयी भारत के प्रधानमंत्री रहे।",
  "gold_label": "SUP",
  "target_label": "NEI",
  "edit_granularity": "sentence",
  "technique_params": {
    "omitted_construct": "temporal_modifier",
    "deleted_tokens": ["1998 से 2004 तक"]
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
| Hindi | Devanagari | Dependency parser (e.g., Stanza/spaCy Hindi). |
| Manipuri | Meitei Mayek / Bengali (script varies by corpus) | Manipuri POS tagger / dependency parser for the target script. |
| Telugu | Telugu | Require Telugu dependency parser. |
| Urdu | Perso-Arabic (RTL) | Require Urdu dependency parser & RTL tokenizer. |
| Punjabi | Gurmukhi | Require Punjabi dependency parser. |
| Tamil | Tamil | Require Tamil dependency parser. |
| Odia | Odia | Require Odia dependency parser. |
| Malayalam | Malayalam | Require Malayalam dependency parser. |

### Generic Mechanical Checklist
- Grapheme-cluster-aware segmentation available? No
- RTL-safe tokenization/reassembly available? Yes (for Urdu)
- Morphological analyzer / stemmer available? Yes (Syntactic Dependency Parser)
- Synonym / paraphrase resource or LM available for this language? No
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
- **Macro-F1 Drop**: Maximum reduction in Macro-F1 stance prediction score.
- **NEI Conversion Rate**: High percentage shift of instances to `NEI`.

## 8. Example
| Field | Original | Adversarial |
| --- | --- | --- |
| Claim / Evidence | **Evidence**: Atal Bihari Vajpayee was Prime Minister of India from 1998 to 2004. | **Adversarial Evidence**: Atal Bihari Vajpayee was Prime Minister of India. *(Date modifier deleted)* |
| Label | SUP → NEI | |
| Language | English (`en`) / Hindi (`hi`) | |

## 9. Failure Modes / Skip Conditions
- Skip if a dependency parser is unavailable for the target language.
- Skip if the sentence lacks target syntactic constructs (e.g., no dates or prepositional phrases).
