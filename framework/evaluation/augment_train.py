import os
import pandas as pd
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

# Import the existing agents
import sys
# Append p3 root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.attacks.generative_llm import get_all_generative_attacks, GenerativeAttacker
from framework.attacks.rule_based_indic import HomoglyphPerturbation, WordJumbling
from google import genai
from dotenv import load_dotenv

class AttackAgent:
    def __init__(self, name):
        self.name = name

class ClaimAttackAgent(AttackAgent):
    def __init__(self, attack_name, attacker_instance):
        super().__init__(attack_name)
        self.attacker = attacker_instance
        
    def attack_batch(self, rows_df):
        original_claims = rows_df['Claim'].astype(str).tolist()
        original_evidences = rows_df['Evidence'].astype(str).tolist()
        if hasattr(self.attacker, 'generate_batch'):
            adv_claims = self.attacker.generate_batch(original_claims)
        else:
            adv_claims = [self.attacker.generate(c) for c in original_claims]
        return adv_claims, original_evidences

class EvidenceAttackAgent(AttackAgent):
    def __init__(self, attack_name, attacker_instance):
        super().__init__(attack_name)
        self.attacker = attacker_instance
        
    def attack_batch(self, rows_df):
        original_claims = rows_df['Claim'].astype(str).tolist()
        original_evidences = rows_df['Evidence'].astype(str).tolist()
        if hasattr(self.attacker, 'generate_batch'):
            adv_evs = self.attacker.generate_batch(original_evidences)
        else:
            adv_evs = [self.attacker.generate(e) for e in original_evidences]
        return original_claims, adv_evs

async def main():
    # Removed hardcoded key for GitHub push protection
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return
    client = None
    try:
        client = genai.Client(api_key=gemini_api_key)
    except Exception as e:
        print("Skipping Gemini client initialization:", e)
    
    print("Loading 50 diverse training rows...")
    train_df = pd.read_csv('dataset/processed/train.csv')
    
    # Stratified sample of 50 rows
    try:
        core_df = train_df.groupby('Language', group_keys=False).apply(lambda x: x.sample(min(len(x), 7), random_state=42))
        core_df = core_df.sample(min(len(core_df), 50), random_state=42)
    except Exception:
        core_df = train_df.sample(min(len(train_df), 50), random_state=42)
        
    print(f"Sampled {len(core_df)} core rows for massive adversarial augmentation.")
    
    # Load all attacks
    attacks_dir = "attacks"
    generative_attacks = get_all_generative_attacks(attacks_dir, client, lang="Multilingual")
    
    agents = []
    for att in generative_attacks:
        if att.target_mode == 'claim':
            agents.append(ClaimAttackAgent(att.attack_name, att))
        elif att.target_mode == 'evidence':
            agents.append(EvidenceAttackAgent(att.attack_name, att))
            
    agents.append(ClaimAttackAgent("Homoglyph", HomoglyphPerturbation()))
    agents.append(ClaimAttackAgent("Jumbling", WordJumbling()))
    
    print(f"Loaded {len(agents)} total attack agents.")
    
    augmented_rows = []
    
    # We already have the original rows in the training set, so we just generate the new ones.
    batch_size = 25
    api_throttle = asyncio.Semaphore(1)
    
    async def process_batch(batch_df, agent):
        async with api_throttle:
            # Enforce 4.5s delay if it's a generative LLM agent to respect 15 RPM
            if hasattr(agent.attacker, 'client'):
                await asyncio.sleep(4.5)
            
            # Execute attack (Runs in thread to avoid blocking asyncio)
            adv_c, adv_e = await asyncio.to_thread(agent.attack_batch, batch_df)
            
            # Reconstruct df rows
            for i in range(len(batch_df)):
                row = batch_df.iloc[i].copy()
                row['Claim'] = adv_c[i]
                row['Evidence'] = adv_e[i]
                row['Augmented_By'] = agent.name
                augmented_rows.append(row)
                
    for agent in agents:
        print(f"Generating adversarial data via {agent.name}...")
        tasks = []
        for i in range(0, len(core_df), batch_size):
            batch_df = core_df.iloc[i:i+batch_size]
            tasks.append(process_batch(batch_df, agent))
            
        await asyncio.gather(*tasks)
        
    adv_df = pd.DataFrame(augmented_rows)
    print(f"Generated {len(adv_df)} adversarial examples!")
    
    # Merge with original train
    train_df['Augmented_By'] = 'Original'
    combined = pd.concat([train_df, adv_df], ignore_index=True)
    
    combined.to_csv('dataset/processed/train_adversarial.csv', index=False)
    print(f"Saved {len(combined)} total training rows to train_adversarial.csv")

if __name__ == "__main__":
    asyncio.run(main())
