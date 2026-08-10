import os
import glob
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np

def clean_and_combine():
    print("Loading datasets...")
    dataset_dir = 'dataset'
    datasets = glob.glob(os.path.join(dataset_dir, '**', '*.xlsx'), recursive=True)
    
    language_dfs = {}
    for dataset_path in datasets:
        lang_folder = os.path.basename(os.path.dirname(os.path.dirname(dataset_path)))
        if lang_folder == 'dataset': # Fallback for flat struct
            lang_folder = os.path.basename(os.path.dirname(dataset_path))
        lang_name = lang_folder.replace('_Dataset', '').replace('_dataset', '')
        
        try:
            df = pd.read_excel(dataset_path)
            
            # Dynamic column normalization
            if 'statement' in df.columns:
                df.rename(columns={'statement': 'Claim'}, inplace=True)
            elif 'Claims' in df.columns:
                df.rename(columns={'Claims': 'Claim'}, inplace=True)
            if 'Evidence' not in df.columns and 'evidence' in df.columns:
                df.rename(columns={'evidence': 'Evidence'}, inplace=True)
            if 'label' in df.columns:
                df.rename(columns={'label': 'Label'}, inplace=True)
                
            if 'Claim' not in df.columns:
                continue
                
            df['Language'] = lang_name
            
            # Ensure label mapping (if any numerical)
            # 0=REFUTES, 1=SUPPORTS, 2=NEI
            
            if lang_name not in language_dfs:
                language_dfs[lang_name] = []
            language_dfs[lang_name].append(df)
        except Exception as e:
            print(f"Error loading {dataset_path}: {e}")
            
    # Combine and Sample
    print("Combining and Stratified Sampling...")
    all_data = []
    
    # We want ~1000 rows across 8 languages -> ~125 per language
    # But some languages might have fewer rows, so we take a proportional sample or a max per language
    rows_per_lang = 125
    
    for lang, dfs in language_dfs.items():
        lang_df = pd.concat(dfs, ignore_index=True)
        # Drop rows with NaN in critical columns
        lang_df = lang_df.dropna(subset=['Claim', 'Evidence'])
        
        # Sample
        if len(lang_df) > rows_per_lang:
            lang_df = lang_df.sample(n=rows_per_lang, random_state=42)
            
        all_data.append(lang_df)
        
    final_df = pd.concat(all_data, ignore_index=True)
    print(f"Total rows after sampling: {len(final_df)}")
    
    # Stratified Split (80/10/10) by Language
    train_df, temp_df = train_test_split(final_df, test_size=0.2, stratify=final_df['Language'], random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, stratify=temp_df['Language'], random_state=42)
    
    # Save
    out_dir = 'dataset/processed'
    os.makedirs(out_dir, exist_ok=True)
    train_df.to_csv(os.path.join(out_dir, 'train.csv'), index=False)
    val_df.to_csv(os.path.join(out_dir, 'val.csv'), index=False)
    test_df.to_csv(os.path.join(out_dir, 'test.csv'), index=False)
    
    print(f"Splits Saved: Train ({len(train_df)}), Val ({len(val_df)}), Test ({len(test_df)})")

if __name__ == "__main__":
    clean_and_combine()
