import os
import json
import time
from framework.attacks.base import BaseAttack

class GenerativeAttacker(BaseAttack):
    """
    Executes an adversarial attack using a Large Language Model.
    Supports single generation and batched generation (with Strict JSON validation).
    """
    
    def __init__(self, attack_name: str, markdown_path: str, llm_client=None, target_language="hi"):
        super().__init__(attack_name, "claim_or_evidence", "variable")
        self.markdown_path = markdown_path
        self.llm_client = llm_client
        self.target_language = target_language
        self.instruction = self._load_instruction()
        self.model = None
        self._init_model()
        
    def _init_model(self):
        if self.llm_client:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.llm_client)
                self.model_name = 'gemini-3.5-flash-lite'
                print("Gemini initialized correctly using modern SDK.")
            except Exception as e:
                print(f"Failed to initialize Gemini: {e}")
        else:
            print("NO API KEY PROVIDED TO ATTACKER!")

    def _load_instruction(self):
        if os.path.exists(self.markdown_path):
            with open(self.markdown_path, 'r', encoding='utf-8') as f:
                return f.read()
        return "No instruction found."

    def build_batch_prompt(self, texts: list) -> str:
        """
        Builds a prompt that specifically instructs the LLM to process an array of claims.
        """
        input_json = json.dumps(texts, ensure_ascii=False)
        prompt = f"""You are an expert red-teamer testing a Fact-Checking system in the {self.target_language} language.
        
Below are the official specifications for the '{self.attack_name}' attack:

<ATTACK_SPECIFICATION>
{self.instruction}
</ATTACK_SPECIFICATION>

Your task is to apply this EXACT attack to each sentence in the following JSON array. 
Preserve the language ({self.target_language}) and ensure the outputs are highly fluent and natural to a native speaker.

Original Sentences (JSON Array):
{input_json}

CRITICAL REQUIREMENT: Output strictly a valid JSON array of strings containing the adversarial sentences in the exact same order. Do not output any markdown formatting, backticks, or conversational text. Just the raw JSON array `["attack 1", "attack 2"]`.
"""
        return prompt
        
    def generate_batch(self, texts: list, max_retries=5) -> list:
        """
        Calls the LLM client to perform batched generation using Gemini with Exponential Backoff.
        """
        if not hasattr(self, 'client') or not self.client:
            return [f"[Mock {self.attack_name}] {t}" for t in texts]
            
        prompt = self.build_batch_prompt(texts)
        
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                output_text = response.text.strip()
                
                # Strip potential markdown backticks if LLM hallucinates them
                if output_text.startswith("```json"):
                    output_text = output_text[7:]
                if output_text.startswith("```"):
                    output_text = output_text[3:]
                if output_text.endswith("```"):
                    output_text = output_text[:-3]
                    
                output_text = output_text.strip()
                
                # Strict JSON Parsing
                adv_claims = json.loads(output_text)
                
                # Strict Length Validation
                if len(adv_claims) != len(texts):
                    raise ValueError(f"Length mismatch: Expected {len(texts)}, got {len(adv_claims)}")
                    
                return adv_claims
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "Quota Exceeded" in error_str:
                    wait_time = (2 ** attempt) * 2  # 2s, 4s, 8s, 16s, 32s
                    print(f"[{self.attack_name}] API Rate Limit hit. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"[{self.attack_name}] Validation/JSON Error on attempt {attempt+1}: {e}")
                    # If it's a JSON hallucination, we still back off and retry
                    time.sleep(2)
                    
        # If all retries fail, return the original text to prevent crashes, but log it
        print(f"[{self.attack_name}] FAILED after {max_retries} attempts.")
        return texts

    # Keep original generate for backwards compatibility
    def generate(self, text: str) -> str:
        return self.generate_batch([text])[0]

def get_all_generative_attacks(markdown_directory, llm_client=None, lang="hi"):
    attacks = []
    for root, _, files in os.walk(markdown_directory):
        for file in files:
            if file.endswith('.md'):
                name = file.replace('.md', '')
                path = os.path.join(root, file)
                attacks.append(GenerativeAttacker(name, path, llm_client, lang))
    return attacks
