import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class BaselineVerifier:
    def __init__(self, model_name="joeddav/xlm-roberta-large-xnli", mapping=None):
        print(f"[TRACE] Loading Valid NLI Baseline Verifier: {model_name}...", flush=True)
        self.mapping = mapping if mapping else {0: "REF", 1: "NEI", 2: "SUP"}
        try:
            print("[TRACE] Initializing AutoTokenizer...", flush=True)
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
            print("[TRACE] Initializing AutoModelForSequenceClassification...", flush=True)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name, local_files_only=True)
            print("[TRACE] model.eval()...", flush=True)
            self.model.eval()
            print("[TRACE] Checking torch.cuda...", flush=True)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            print(f"[TRACE] Moving model to {self.device}...", flush=True)
            self.model.to(self.device)
            self.loaded = True
            print(f"[TRACE] Successfully loaded {model_name}.", flush=True)
        except Exception as e:
            print(f"[TRACE] Failed to load NLI model {model_name}: {e}", flush=True)
            self.loaded = False

    def verify(self, claim: str, evidence: str = "") -> str:
        """
        Takes a claim and optional evidence, and returns a verdict.
        """
        if not self.loaded:
            return "NEI"
            
        # NLI models usually take premise (evidence) and hypothesis (claim)
        premise = evidence if evidence else "This is a factual evaluation."
        hypothesis = claim
        
        inputs = self.tokenizer(premise, hypothesis, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            predicted_class_id = logits.argmax().item()
            
        return self.mapping.get(predicted_class_id, "NEI")

if __name__ == "__main__":
    verifier = BaselineVerifier()
    # Test Hindi NLI
    verdict = verifier.verify(claim="नई दिल्ली भारत की राजधानी है।", evidence="भारत की राजधानी नई दिल्ली है और यह एक बड़ा शहर है।")
    print(f"Hindi Verdict (Should be SUP): {verdict}")
    verdict = verifier.verify(claim="नई दिल्ली अमेरिका में है।", evidence="भारत की राजधानी नई दिल्ली है।")
    print(f"Hindi Verdict (Should be REF): {verdict}")
