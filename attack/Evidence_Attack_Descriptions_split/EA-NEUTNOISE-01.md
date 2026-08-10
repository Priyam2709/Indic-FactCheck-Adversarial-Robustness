# Adversarial Attack Description Document: Evidence Attacks on Automated Fact-Checking (AFC)
**Revision 2** — extracted single-attack file from Evidence_Attack_Descriptions_v2.md

This document contains one attack description from the **14 Evidence Attacks** targeting Automated Fact-Checking (AFC) systems reviewed in *"Adversarial Attacks Against Automated Fact-Checking: A Survey"* (Liu et al., 2025).

---

<a id="12-ea-neutnoise-01"></a>
# 12. EA-NEUTNOISE-01: Neutral Noise Document Injection Attack

## 1. Metadata
- **Attack ID**: `EA-NEUTNOISE-01`
- **Attack Name**: Neutral Noise Document Injection Attack
- **Category**: `evidence_attack`
- **Attack Target**: `disrupted_retrieval`
- **Edit Granularity**: `article`
- **Strategy Type**: `rule_based`
- **Access Assumption**: Black-box retrieval, Black-box verification
- **Source Paper**: Samarinas et al. (2021); Liu et al. (2025), Sec. 5.2.2, Table 4

## 2. Description
Neutral Noise injects high-scoring web search documents (e.g., from Bing search) that are entailment-neutral toward target claims into the retrieval corpus. Because these documents share surface lexical overlap with claims (high BM25 score) but lack actual verification evidence, they crowd out gold evidence in dense and sparse retrievers.

## 3. Preconditions / Required Inputs
- `claim_text` (Required): Target claim text.
- `gold_label` (Required): Ground truth label.
- `search_engine_api` (Required): Bing/Google Search API access to fetch web results.
- `nli_entailment_model` (Required): NLI model to confirm document stance is `neutral`.

## 4. Procedure
1. Execute a search query using `claim_text` on the Bing/Google search engine API.
2. Fetch the top 30 search result articles.
3. Pass retrieved articles through an NLI model to filter out entailing or contradicting documents, retaining only `neutral` articles.
4. Rank neutral articles by BM25 similarity to `claim_text`.
5. Inject the top-$K$ highest-scoring neutral documents into the searchable AFC corpus index.

## 5. Output Schema (JSON)
```json
{
  "attack_id": "EA-NEUTNOISE-01",
  "language": "hi",
  "original_claim": "चांद पर पानी की खोज हुई है।",
  "original_evidence": "ISRO के चंद्रयान-1 मिशन ने 2008 में चंद्रमा की सतह पर पानी के अणुओं की खोज की थी।",
  "adversarial_claim": null,
  "adversarial_evidence": "चंद्रमा पृथ्वी का एकमात्र प्राकृतिक उपग्रह है और यह रात के समय आकाश में चमकता है।",
  "gold_label": "SUP",
  "target_label": "NEI",
  "edit_granularity": "article",
  "technique_params": {
    "retrieval_engine": "Bing-API",
    "nli_filter": "neutral-only"
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
| Hindi | Devanagari | Web search API with Hindi support & Hindi NLI model. |
| Manipuri | Meitei Mayek / Bengali (script varies by corpus) | Search API support for the target script & Manipuri NLI model. |
| Telugu | Telugu | Search API support for Telugu & Telugu NLI model. |
| Urdu | Perso-Arabic (RTL) | Search API support for Urdu & Urdu NLI model. |
| Punjabi | Gurmukhi | Search API support for Punjabi & Punjabi NLI model. |
| Tamil | Tamil | Search API support for Tamil & Tamil NLI model. |
| Odia | Odia | Search API support for Odia & Odia NLI model. |
| Malayalam | Malayalam | Search API support for Malayalam & Malayalam NLI model. |

### Generic Mechanical Checklist
- Grapheme-cluster-aware segmentation available? No
- RTL-safe tokenization/reassembly available? Yes (for Urdu)
- Morphological analyzer / stemmer available? No
- Synonym / paraphrase resource or LM available for this language? Yes (NLI Filter Model)
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
- **Document Recall Degradation**: Significant reduction in ground-truth document retrieval recall (`RecDoc`).
- **Adversarial Evidence Recall (`RecAdvEvd`)**: High proportion of injected neutral noise retrieved.

## 8. Example
| Field | Original | Adversarial |
| --- | --- | --- |
| Claim / Evidence | **Evidence**: Chandrayaan-1 discovered water molecules on the Moon in 2008. | **Adversarial Evidence**: The Moon is Earth's only natural satellite and shines brightly in the night sky. |
| Label | SUP → NEI | |
| Language | English (`en`) / Hindi (`hi`) | |

## 9. Failure Modes / Skip Conditions
- Skip if the web search API returns fewer than 5 results for the query.
- Skip if the NLI model fails to find strictly neutral documents.
