import os
import glob
import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from framework.attacks.generative_llm import GenerativeAttacker
from framework.attacks.rule_based_indic import HomoglyphPerturbation, WordJumbling, RepeatPhrases
from framework.evaluation.verifier import BaselineVerifier

class AttackAgent:
    """Base Agent Class"""
    def __init__(self, name, target_mode):
        self.name = name
        self.target_mode = target_mode # 'claim', 'evidence', or 'pair'

class ClaimAttackAgent(AttackAgent):
    def __init__(self, attack_name, attacker_instance):
        super().__init__(attack_name, 'claim')
        self.attacker = attacker_instance
        
    def attack_batch(self, rows_df):
        # We assume rows_df is a pandas DataFrame chunk
        original_claims = rows_df['Claim'].astype(str).tolist()
        original_evidences = rows_df['Evidence'].astype(str).tolist() if 'Evidence' in rows_df.columns else [""] * len(rows_df)
        
        # Check if attacker supports batching natively
        if hasattr(self.attacker, 'generate_batch'):
            adv_claims = self.attacker.generate_batch(original_claims)
        else:
            # Fallback for rule-based attacks
            adv_claims = [self.attacker.generate(c) for c in original_claims]
            
        return adv_claims, original_evidences

class DualAttackAgent(AttackAgent):
    def __init__(self, attack_name, attacker_instance):
        super().__init__(attack_name, 'pair')
        self.attacker = attacker_instance
        
    def attack_batch(self, rows_df):
        original_claims = rows_df['Claim'].astype(str).tolist()
        original_evidences = rows_df['Evidence'].astype(str).tolist() if 'Evidence' in rows_df.columns else [""] * len(rows_df)
        
        if hasattr(self.attacker, 'generate_batch'):
            adv_claims = self.attacker.generate_batch(original_claims)
            adv_evidences = self.attacker.generate_batch(original_evidences)
        else:
            adv_claims = [self.attacker.generate(c) for c in original_claims]
            adv_evidences = [self.attacker.generate(e) for e in original_evidences]
            
        return adv_claims, adv_evidences

class EvidenceAttackAgent(AttackAgent):
    def __init__(self, attack_name, attacker_instance):
        super().__init__(attack_name, 'evidence')
        self.attacker = attacker_instance
        
    def attack_batch(self, rows_df):
        original_claims = rows_df['Claim'].astype(str).tolist()
        original_evidences = rows_df['Evidence'].astype(str).tolist() if 'Evidence' in rows_df.columns else [""] * len(rows_df)
        
        if hasattr(self.attacker, 'generate_batch'):
            adv_evidences = self.attacker.generate_batch(original_evidences)
        else:
            adv_evidences = [self.attacker.generate(e) for e in original_evidences]
            
        return original_claims, adv_evidences

class MultiAgentOrchestrator:
    def __init__(self, dataset_dir, gemini_api_key):
        self.dataset_dir = dataset_dir
        self.gemini_api_key = gemini_api_key
        self.verifier = BaselineVerifier()
        
        # Load Hardened Model (0=REF, 1=SUP, 2=NEI mapping from trainer)
        try:
            hardened_path = os.path.join(os.path.dirname(__file__), '../models/xlm-roberta-hardened_final')
            hardened_mapping = {0: "REF", 1: "SUP", 2: "NEI"}
            self.hardened_verifier = BaselineVerifier(model_name=hardened_path, mapping=hardened_mapping)
        except Exception as e:
            print(f"[WARN] Hardened model not found. Skipping side-by-side evaluation. Error: {e}")
            
        self.agents = []
        self._load_agents()
        
    def _load_agents(self):
        print("Initializing Agents from Markdown metadata...", flush=True)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        attack_files = glob.glob(os.path.join(base_dir, 'attack', '**', '*.md'), recursive=True)
        
        for f in attack_files:
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()
                name = os.path.basename(f).replace('.md', '')
                try:
                    attacker = GenerativeAttacker(name, f, self.gemini_api_key)
                    
                    if 'pair_attack' in content:
                        self.agents.append(DualAttackAgent(name, attacker))
                    elif 'evidence_attack' in content:
                        self.agents.append(EvidenceAttackAgent(name, attacker))
                    elif 'claim_attack' in content:
                        self.agents.append(ClaimAttackAgent(name, attacker))
                except Exception as e:
                    print(f"Error loading {name}: {e}", flush=True)
                    
        # Add rule based ones manually to ClaimAttackAgent
        self.agents.append(ClaimAttackAgent("Homoglyph", HomoglyphPerturbation()))
        self.agents.append(ClaimAttackAgent("Jumbling", WordJumbling()))
        
        print(f"Loaded {len(self.agents)} Attack Agents.", flush=True)

    def _evaluate_batch_sync(self, batch_df, agent):
        """Runs the entire batched evaluation synchronously for thread executor"""
        # 1. Baseline prediction (No Attack)
        orig_claims = batch_df['Claim'].astype(str).tolist()
        orig_evs = batch_df['Evidence'].astype(str).tolist() if 'Evidence' in batch_df.columns else [""] * len(batch_df)
        
        baseline_verdicts = [self.verifier.verify(c, e) for c, e in zip(orig_claims, orig_evs)]
        
        # 2. Agent Attack (Batched JSON call with Self-Healing)
        adv_claims, adv_evs = agent.attack_batch(batch_df)
        
        # 3. Adversarial Prediction
        adv_verdicts = [self.verifier.verify(c, e) for c, e in zip(adv_claims, adv_evs)]
        
        # Calculate Success
        successes = sum(1 for b, a in zip(baseline_verdicts, adv_verdicts) if b != a)
        
        with open('debug_claims.txt', 'a', encoding='utf-8') as f:
            f.write(f"--- DEBUG {agent.name} ---\n")
            for i in range(len(orig_claims)):
                f.write(f"Orig: {orig_claims[i]} -> {baseline_verdicts[i]}\n")
                f.write(f"Adv : {adv_claims[i]} -> {adv_verdicts[i]}\n")
            f.write("-----------------------\n")
        
        return successes, len(batch_df)

    async def run_matrix(self):
        print("Starting Final Test Orchestrator on Holdout Set...", flush=True)
        
        try:
            df = pd.read_csv('dataset/processed/test.csv')
            df = df.sample(min(len(df), 20), random_state=42)
            print(f"Loaded strictly the holdout test set: {len(df)} rows across {df['Language'].nunique()} languages.")
        except Exception as e:
            print(f"Test dataset not found. Run data_splitter.py first! {e}")
            return
            
        results = []
        api_throttle = asyncio.Semaphore(1)
        
        for agent in self.agents:
            print(f"  Testing {agent.name} (Global Batch)...", flush=True)
            async with api_throttle:
                # 4.5s delay for Generative Attacks
                if hasattr(agent, 'attacker') and hasattr(agent.attacker, 'client') and agent.attacker.client is not None:
                    await asyncio.sleep(4.5)
                
                # Global Attack Batch
                adv_claims, adv_evs = await asyncio.to_thread(agent.attack_batch, df)
                orig_claims = df['Claim'].astype(str).tolist()
                orig_evs = df['Evidence'].astype(str).tolist() if 'Evidence' in df.columns else [""] * len(df)
                
                # 1. Baseline Evaluation
                b_orig_v = [self.verifier.verify(c, e) for c, e in zip(orig_claims, orig_evs)]
                b_adv_v = [self.verifier.verify(c, e) for c, e in zip(adv_claims, adv_evs)]
                b_successes = [1 if b != a else 0 for b, a in zip(b_orig_v, b_adv_v)]
                
                # 2. Hardened Evaluation (if available)
                if hasattr(self, 'hardened_verifier'):
                    h_orig_v = [self.hardened_verifier.verify(c, e) for c, e in zip(orig_claims, orig_evs)]
                    h_adv_v = [self.hardened_verifier.verify(c, e) for c, e in zip(adv_claims, adv_evs)]
                    h_successes = [1 if b != a else 0 for b, a in zip(h_orig_v, h_adv_v)]
                else:
                    h_successes = [0] * len(df)
            
            # Now tally per language
            df['b_success'] = b_successes
            df['h_success'] = h_successes
            for lang, lang_df in df.groupby('Language'):
                total_eval = len(lang_df)
                lang_b_success = lang_df['b_success'].sum()
                lang_h_success = lang_df['h_success'].sum()
                
                b_asr = (lang_b_success / total_eval) * 100 if total_eval > 0 else 0
                h_asr = (lang_h_success / total_eval) * 100 if total_eval > 0 else 0
                mitigation = b_asr - h_asr
                
                results.append({
                    "Language": lang,
                    "Attack Name": agent.name,
                    "Is Applicable": "Yes",
                    "Defense Applied": "None (Baseline)",
                    "Attack Success Rate": f"{b_asr:.2f}%",
                    "Defense Mitigation": "N/A"
                })
                results.append({
                    "Language": lang,
                    "Attack Name": agent.name,
                    "Is Applicable": "Yes",
                    "Defense Applied": "Head-Only Finetuning",
                    "Attack Success Rate": f"{h_asr:.2f}%",
                    "Defense Mitigation": f"{-mitigation:.2f}%"
                })
                
        # Save completely at the end to a fresh file
        pd.DataFrame(results).to_csv('final_evaluation_report.csv', index=False)
        print("Saved completely to final_evaluation_report.csv", flush=True)
        return pd.DataFrame(results)

if __name__ == "__main__":
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        sys.exit(1)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    dataset_dir = os.path.join(base_dir, 'dataset')
    
    orchestrator = MultiAgentOrchestrator(dataset_dir, api_key)
    asyncio.run(orchestrator.run_matrix())
