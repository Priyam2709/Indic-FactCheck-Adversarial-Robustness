import os
from huggingface_hub import HfApi, ModelCard, ModelCardData

def push_model_to_hub(model_path, repo_id, token, language="hi"):
    """
    Pushes a trained/defended fact-checking model to the Hugging Face Hub.
    """
    print(f"Uploading model from {model_path} to HuggingFace repo: {repo_id}...")
    api = HfApi(token=token)
    
    # Create the repository if it doesn't exist
    api.create_repo(repo_id=repo_id, exist_ok=True)
    
    # Upload the model directory
    api.upload_folder(
        folder_path=model_path,
        repo_id=repo_id,
        repo_type="model",
        commit_message="Initial commit: Defended Fact-Checking Model"
    )
    
    # Generate and upload a Model Card
    card_data = ModelCardData(
        language=language,
        tags=["fact-checking", "adversarial-robustness", "indic"],
        license="mit"
    )
    
    card_text = f"""
    # Defended Indic Fact-Checking Model
    
    This model has been fine-tuned and defended against adversarial attacks 
    using the Unified Adversarial Testing Framework.
    
    ## Model Details
    - **Language:** {language}
    - **Task:** Fact-Checking / Claim Verification
    - **Defenses Applied:** Product of Experts (PoE), Debiased Focal Loss (DFL)
    
    ## Intended Use
    Designed to verify claims in regional Indian languages with high robustness 
    against adversarial manipulations (e.g., character swapping, multi-hop temporal logic).
    """
    
    card = ModelCard(card_text, data=card_data)
    card.push_to_hub(repo_id, token=token)
    
    print(f"Model successfully pushed to: https://huggingface.co/{repo_id}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Push defended model to Hugging Face")
    parser.add_argument("--repo_id", type=str, required=True, help="HuggingFace Repo ID (e.g., your_username/XLM-R-Indic-Hardened)")
    args = parser.parse_args()
    
    token = os.getenv("HF_TOKEN")
    if not token:
        print("ERROR: Please set the HF_TOKEN environment variable first.")
        print("Example: $env:HF_TOKEN=\"hf_YourTokenHere\"")
        exit(1)
        
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../models/xlm-roberta-hardened_final'))
    
    if not os.path.exists(model_path):
        print(f"ERROR: Model directory not found at {model_path}")
        exit(1)
        
    push_model_to_hub(model_path, args.repo_id, token, language="Multilingual (Indic)")
