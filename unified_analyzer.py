import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
import math
import re
from markdown_pdf import Section, MarkdownPdf

# Initialize heavy models
print("Loading multilingual sentence transformer...")
st_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("Loading multilingual sentiment model...")
sentiment_pipeline = pipeline("sentiment-analysis", model="lxyuan/distilbert-base-multilingual-cased-sentiments-student")
print("Loading multilingual NER model...")
ner_pipeline = pipeline("ner", model="Babelscape/wikineural-multilingual-ner", aggregation_strategy="simple")

def jaccard_similarity(text1, text2):
    if pd.isna(text1) or pd.isna(text2): return 0.0
    set1 = set(str(text1).lower().split())
    set2 = set(str(text2).lower().split())
    if not set1 or not set2: return 0.0
    return len(set1.intersection(set2)) / len(set1.union(set2))

def get_col(df, keywords):
    for col in df.columns:
        for kw in keywords:
            if kw.lower() in col.lower():
                return col
    return None

def is_devanagari(char): return 0x0900 <= ord(char) <= 0x097F
def is_roman(char): return (0x0041 <= ord(char) <= 0x005A) or (0x0061 <= ord(char) <= 0x007A)

def count_tokens_cmi(text):
    text = str(text)
    words = text.split()
    dev_count, rom_count, total = 0, 0, len(words)
    if total == 0: return 0, 0, 0, 0, 0
    switches = 0
    prev_lang = None
    for w in words:
        if any(is_devanagari(c) for c in w):
            dev_count += 1
            curr_lang = 'dev'
        elif any(is_roman(c) for c in w):
            rom_count += 1
            curr_lang = 'rom'
        else:
            curr_lang = prev_lang
        if prev_lang and curr_lang and prev_lang != curr_lang:
            switches += 1
        prev_lang = curr_lang
    max_lang = max(dev_count, rom_count)
    cmi = 100 * (1 - (max_lang / total)) if total > 0 else 0
    p_dev, p_rom = dev_count/total, rom_count/total
    entropy = 0
    if p_dev > 0: entropy -= p_dev * math.log2(p_dev)
    if p_rom > 0: entropy -= p_rom * math.log2(p_rom)
    return dev_count, rom_count, total, cmi, entropy, switches

def analyze_script(text):
    text = str(text)
    has_dev = any(is_devanagari(c) for c in text)
    has_rom = any(is_roman(c) for c in text)
    if has_dev and has_rom: return "Mixed"
    if has_dev: return "Native Script (Devanagari)"
    if has_rom: return "Roman/English"
    return "Unknown/Other"

def main():
    print("Gathering all datasets...")
    all_files = glob.glob('dataset/**/*.xlsx', recursive=True)
    
    dfs = []
    for f in all_files:
        try:
            temp_df = pd.read_excel(f)
            temp_df.columns = temp_df.columns.str.strip()
            
            label_col = get_col(temp_df, ['label', 'supported'])
            claim_col = get_col(temp_df, ['claim', 'tweet', 'text', 'post'])
            evidence_col = get_col(temp_df, ['evidence', 'proof', 'url'])
            source_col = get_col(temp_df, ['source', 'platform', 'media'])
            
            if not label_col or not claim_col:
                print(f"Skipping {f} (Missing Label or Claim col)")
                continue
            
            mapped_df = pd.DataFrame()
            mapped_df['Claim'] = temp_df[claim_col]
            mapped_df['Label'] = temp_df[label_col].astype(str).str.strip().str.title()
            mapped_df['Label'] = mapped_df['Label'].replace({
                'Support': 'Supported',
                'Refute': 'Not Supported',
                'Nei': 'Not Enough Information (NEI)',
                'Not Enough Info': 'Not Enough Information (NEI)',
                'Nan': 'Unknown'
            })
            mapped_df['Evidence'] = temp_df[evidence_col] if evidence_col else np.nan
            mapped_df['Source'] = temp_df[source_col] if source_col else "Unknown"
            
            parts = f.replace('\\', '/').split('/')
            lang = parts[1].replace('_Dataset', '') if len(parts) > 1 else "Unknown"
            mapped_df['Language'] = lang
            
            dfs.append(mapped_df)
        except Exception as e:
            print(f"Error loading {f}: {e}")
            
    if not dfs:
        return
        
    master_df = pd.concat(dfs, ignore_index=True)
    master_df = master_df.dropna(subset=['Claim'])
    master_df['Claim'] = master_df['Claim'].astype(str)
    
    out_dir = "dataset"
    img_dir = os.path.join(out_dir, "master_report_images")
    os.makedirs(img_dir, exist_ok=True)
    
    md = ["# Master Dataset Analysis Report (All Languages)\n"]
    
    # 1. Overall Stats
    md.append("## 1. Overall Dataset Statistics")
    md.append(f"- **Total Rows (Raw)**: {len(master_df)}")
    md.append(f"- **Valid Claims**: {len(master_df)}")
    md.append(f"- **Total Unique Sources**: {master_df['Source'].nunique()}")
    md.append(f"- **Total Labels**: {master_df['Label'].nunique()}")
    md.append(f"- **Total Languages Included**: {master_df['Language'].nunique()} ({', '.join(master_df['Language'].unique())})\n")
    
    # Language Distribution
    md.append("## 2. Language Distribution")
    lang_dist = master_df['Language'].value_counts()
    plt.figure(figsize=(10, 6), dpi=200)
    sns.barplot(x=lang_dist.index, y=lang_dist.values, palette='plasma')
    plt.title('Dataset Contribution by Language')
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'lang_dist.png'))
    plt.close()
    md.append(f'\n![Language Distribution](master_report_images/lang_dist.png)\n')
    
    # Label Distribution
    md.append("## 3. Label-wise Analysis")
    label_dist = master_df['Label'].value_counts()
    label_df = pd.DataFrame({'Samples': label_dist, 'Percentage (%)': (label_dist / len(master_df)) * 100})
    md.append(label_df.to_markdown() + "\n")
    plt.figure(figsize=(10, 6), dpi=200)
    sns.barplot(x=label_dist.index, y=label_dist.values, palette='viridis')
    plt.title('Global Label Distribution')
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'label_dist.png'))
    plt.close()
    md.append(f'\n![Label Distribution](master_report_images/label_dist.png)\n')

    # Source Analysis
    md.append("## 4. Source-wise Analysis (Top 10)")
    source_dist = master_df['Source'].value_counts().head(10)
    source_df = pd.DataFrame({'Samples': source_dist, 'Percentage (%)': (source_dist / len(master_df)) * 100})
    md.append(source_df.to_markdown() + "\n")

    # Source Label Heatmap
    md.append("## 5. Source × Label Analysis (Cohesion Matrix)")
    top_sources = master_df['Source'].value_counts().nlargest(10).index
    top_df = master_df[master_df['Source'].isin(top_sources)]
    heatmap_data = pd.crosstab(top_df['Source'], top_df['Label'])
    md.append(heatmap_data.to_markdown() + "\n")
    plt.figure(figsize=(14, 10), dpi=200)
    sns.heatmap(heatmap_data, annot=True, cmap='Blues', fmt='d')
    plt.title('Global Source vs Label Cohesion')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'source_label_heatmap.png'))
    plt.close()
    md.append(f'\n![Source vs Label Cohesion](master_report_images/source_label_heatmap.png)\n')

    # Text Length Analysis
    md.append("## 6. Text Length Analysis\n### Claim Length Statistics")
    master_df['Claim_Words'] = master_df['Claim'].apply(lambda x: len(x.split()))
    master_df['Claim_Chars'] = master_df['Claim'].apply(len)
    stats = master_df[['Claim_Words', 'Claim_Chars']].describe().loc[['mean', '50%', 'min', 'max', 'std']]
    stats.index = ['Mean', 'Median', 'Min', 'Max', 'Std. Dev.']
    md.append(stats.to_markdown() + "\n")
    plt.figure(figsize=(10, 6), dpi=200)
    sns.histplot(master_df['Claim_Words'], bins=30, kde=True, color='purple')
    plt.title('Claim Word Count Distribution')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'length_distribution.png'))
    plt.close()
    md.append(f'\n![Length Distribution](master_report_images/length_distribution.png)\n')

    # Code Mixing
    md.append("## 7. Code-Mixing Analysis (Token-Level)")
    total_dev, total_rom, total_words, total_cmi, total_entropy, total_switches = 0, 0, 0, 0, 0, 0
    valid_cmi_rows = 0
    for text in master_df['Claim']:
        d, r, t, cmi, ent, sw = count_tokens_cmi(text)
        total_dev += d; total_rom += r; total_words += t
        if t > 0:
            total_cmi += cmi; total_entropy += ent; total_switches += sw; valid_cmi_rows += 1
    
    if total_words > 0:
        md.append(f"* **English/Roman Tokens**: {((total_rom/total_words)*100):.1f}%")
        md.append(f"* **Native (Devanagari) Tokens**: {((total_dev/total_words)*100):.1f}%")
        md.append(f"* **Average CMI (Code-Mixing Index)**: {(total_cmi/valid_cmi_rows if valid_cmi_rows else 0):.2f}")
        md.append(f"* **Average Language Entropy**: {(total_entropy/valid_cmi_rows if valid_cmi_rows else 0):.2f}")
        md.append(f"* **Average Switch Points**: {(total_switches/valid_cmi_rows if valid_cmi_rows else 0):.2f}\n")

    # Vocabulary Richness
    md.append("## 8. Vocabulary Analysis")
    all_text = " ".join(master_df['Claim'].astype(str))
    all_tokens = all_text.split()
    unique_tokens = set(all_tokens)
    ttr = len(unique_tokens) / len(all_tokens) if all_tokens else 0
    md.append(f"- **Total Claim Tokens**: {len(all_tokens)}")
    md.append(f"- **Unique Claim Words**: {len(unique_tokens)}")
    md.append(f"- **Vocabulary Richness (Type-Token Ratio)**: {ttr:.4f}\n")

    # Annotation Quality
    md.append("## 9. Annotation Quality Analysis")
    md.append("The current dataset provides a single label per claim (`Supported`, `Not Supported`, `NEI`). Since there are no multi-annotator vote fields or annotator IDs provided, inter-annotator agreement statistics (like Cohen's Kappa or Krippendorff's Alpha) cannot be computed. It is recommended to disclose the annotation guidelines and quality-control processes used to produce these gold labels.\n")

    # Duplicate Analysis
    md.append("## 10. Duplicate Analysis")
    exact_dupes = master_df.duplicated(subset=['Claim']).sum()
    master_df['Normalized_Claim'] = master_df['Claim'].str.lower().str.replace(r'[^\w\s]', '', regex=True)
    near_dupes = master_df.duplicated(subset=['Normalized_Claim']).sum()
    empty_claims = master_df['Claim'].str.strip().eq('').sum()
    missing_labels = master_df['Label'].isna().sum()
    md.append(f"- **Exact duplicate claims (same text)**: {exact_dupes}")
    md.append(f"- **Near-duplicates (identical after case/punctuation normalization)**: {near_dupes}")
    md.append(f"- **Empty / blank claims**: {empty_claims}")
    md.append(f"- **Missing labels**: {missing_labels}\n")

    # Script Analysis
    md.append("## 11. Script Analysis (Claims)")
    master_df['Script_Type'] = master_df['Claim'].apply(analyze_script)
    script_counts = master_df['Script_Type'].value_counts()
    script_df = pd.DataFrame({'Counts': script_counts})
    md.append(script_df.to_markdown() + "\n")

    # Emojis and URLs
    md.append("## 12. Emoji, URL, Mention and Hashtag Analysis")
    emoji_count = master_df['Claim'].apply(lambda x: len(re.findall(r'[^\w\s,\.\?!\-\'\"\(\):;]', x))).sum()
    url_count = master_df['Claim'].apply(lambda x: len(re.findall(r'http[s]?://\S+', x))).sum()
    mention_count = master_df['Claim'].apply(lambda x: len(re.findall(r'@\w+', x))).sum()
    hashtag_count = master_df['Claim'].apply(lambda x: len(re.findall(r'#\w+', x))).sum()
    social_df = pd.DataFrame({
        'Feature': ['Emojis', 'URLs', 'Mentions (@)', 'Hashtags (#)'],
        'Total Count in Claims': [emoji_count, url_count, mention_count, hashtag_count]
    })
    md.append(social_df.to_markdown() + "\n")

    # Temporal Analysis
    md.append("## 13. Temporal Analysis")
    md.append("No timestamp, date, or post-time column is present in the dataset. A temporal analysis or per-year/per-month distribution cannot be computed. If the claims were sourced from specific periods or social media platforms, it is strongly recommended to retain the original post timestamps for future data releases to enable concept-drift analysis.\n")

    # Word Co-occurrence
    md.append("## 14. Lexical Cohesion Matrix (Word Co-occurrence)")
    md.append("This matrix maps the co-occurrence frequencies of the top 20 vocabulary words across all claims.")
    try:
        vectorizer_unigram = CountVectorizer(max_features=20, stop_words=None)
        X = vectorizer_unigram.fit_transform(master_df['Claim'])
        words = vectorizer_unigram.get_feature_names_out()
        Xc = (X.T * X)
        Xc.setdiag(0)
        plt.figure(figsize=(16, 12), dpi=300)
        sns.heatmap(Xc.todense(), xticklabels=words, yticklabels=words, cmap='YlGnBu', annot=True, fmt='d')
        plt.title('Lexical Cohesion: Top Word Co-occurrence')
        plt.tight_layout()
        plt.savefig(os.path.join(img_dir, 'word_cooccurrence.png'))
        plt.close()
        md.append(f'\n![Word Co-occurrence](master_report_images/word_cooccurrence.png)\n')
    except: pass

    # Semantic Cohesion
    md.append("## 15. Semantic Cohesion (Claim vs. Evidence Similarity)")
    md.append("Using multilingual embeddings (`paraphrase-multilingual-MiniLM-L12-v2`), we extracted the semantic similarity to see how tightly coupled a specific claim is to its paired evidence.")
    try:
        claims = master_df['Claim'].tolist()
        evidences = master_df['Evidence'].fillna('').astype(str).tolist()
        claim_embeddings = st_model.encode(claims, show_progress_bar=False)
        evidence_embeddings = st_model.encode(evidences, show_progress_bar=False)
        master_df['Semantic_Similarity'] = [cosine_similarity([claim_embeddings[i]], [evidence_embeddings[i]])[0][0] for i in range(len(master_df))]
        
        plt.figure(figsize=(14, 10), dpi=300)
        sns.boxplot(x='Label', y='Semantic_Similarity', data=master_df)
        plt.title('Semantic Similarity (Claim vs Evidence)')
        plt.tight_layout()
        plt.savefig(os.path.join(img_dir, 'similarity_by_label.png'))
        plt.close()
        md.append(f'\n![Semantic Cohesion](master_report_images/similarity_by_label.png)\n')
    except Exception as e: print(e)

    # Lexical Overlap
    md.append("## 16. Lexical Overlap Analysis")
    md.append("We measured the Jaccard Similarity (exact word overlap over total unique words) between each Claim and its paired Evidence. This helps identify if claims are exact quotes from the evidence or heavily paraphrased.")
    master_df['Lexical_Overlap'] = master_df.apply(lambda row: jaccard_similarity(row['Claim'], row.get('Evidence', '')), axis=1)
    plt.figure(figsize=(10, 6), dpi=200)
    sns.boxplot(x='Label', y='Lexical_Overlap', data=master_df)
    plt.title('Lexical Overlap (Jaccard) by Label')
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'lexical_overlap.png'))
    plt.close()
    md.append(f'\n![Lexical Overlap](master_report_images/lexical_overlap.png)\n')

    # N-Grams
    md.append("## 17. N-Gram Analysis (Phrases)")
    md.append("Looking at multi-word phrases (Bigrams and Trigrams) often yields more domain-specific context than single words.")
    try:
        vectorizer = CountVectorizer(ngram_range=(2, 3), max_features=20)
        X_ngrams = vectorizer.fit_transform(master_df['Claim'])
        ngram_sums = X_ngrams.sum(axis=0).A1
        ngrams_df = pd.DataFrame({'NGram': vectorizer.get_feature_names_out(), 'Frequency': ngram_sums}).sort_values(by='Frequency', ascending=False)
        plt.figure(figsize=(14, 10), dpi=300)
        sns.barplot(x='Frequency', y='NGram', data=ngrams_df, palette='viridis')
        plt.title('Top 20 Bigrams & Trigrams')
        plt.tight_layout()
        plt.savefig(os.path.join(img_dir, 'ngrams.png'))
        plt.close()
        md.append(f'\n![N-Grams](master_report_images/ngrams.png)\n')
    except: pass

    # Length Ratio
    md.append("## 18. Evidence-to-Claim Length Ratio")
    md.append("This metric measures how many words of evidence support each word of the claim. A higher ratio typically indicates detailed, comprehensive evidence.")
    master_df['Evidence_Words'] = master_df['Evidence'].apply(lambda x: len(str(x).split()) if pd.notna(x) else 0)
    master_df['Length_Ratio'] = master_df['Evidence_Words'] / master_df['Claim_Words'].replace(0, 1)
    plt.figure(figsize=(10, 6), dpi=200)
    sns.boxplot(x='Label', y='Length_Ratio', data=master_df)
    plt.title('Evidence-to-Claim Word Count Ratio by Label')
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'length_ratio.png'))
    plt.close()
    md.append(f'\n![Length Ratio](master_report_images/length_ratio.png)\n')

    # LDA
    md.append("## 19. Topic Modeling (Latent Dirichlet Allocation)")
    md.append("We used LDA clustering to discover latent thematic topics spanning the claims:")
    try:
        tf_vectorizer = CountVectorizer(max_features=1000)
        tf = tf_vectorizer.fit_transform(master_df['Claim'])
        lda = LatentDirichletAllocation(n_components=5, random_state=42)
        lda.fit(tf)
        tf_feature_names = tf_vectorizer.get_feature_names_out()
        topics_md = "| Topic | Top Keywords |\n|---|---|\n"
        for topic_idx, topic in enumerate(lda.components_):
            top_features = [tf_feature_names[i] for i in topic.argsort()[:-6:-1]]
            topics_md += f"| Topic {topic_idx+1} | {', '.join(top_features)} |\n"
        md.append(topics_md + "\n")
    except: pass

    # Sentiment
    md.append("## 20. Sentiment Analysis")
    md.append("We analyzed the emotional polarity of each claim using a multilingual DistilBERT model. The chart below visualizes whether certain label categories tend to skew positive or negative.")
    try:
        master_df['Sentiment'] = master_df['Claim'].apply(lambda x: sentiment_pipeline(x[:500])[0]['label'] if x.strip() else 'neutral')
        sentiment_crosstab = pd.crosstab(master_df['Label'], master_df['Sentiment'], normalize='index') * 100
        sentiment_crosstab.plot(kind='bar', stacked=True, figsize=(10, 6), colormap='Set2')
        plt.title('Sentiment Distribution within Labels (%)')
        plt.tight_layout()
        plt.savefig(os.path.join(img_dir, 'sentiment.png'))
        plt.close()
        md.append(f'\n![Sentiment Analysis](master_report_images/sentiment.png)\n')
    except Exception as e: print(e)
    
    # NER
    md.append("## 21. Named Entity Recognition (NER)")
    md.append("We extracted specific Organizations (ORG), Locations (LOC), and Persons (PER) cited within the claims using the WikiNeural multilingual NER model.")
    try:
        all_entities = []
        for text in master_df['Claim'].astype(str):
            if not text.strip(): continue
            ents = ner_pipeline(text[:500])
            for ent in ents:
                if ent['entity_group'] in ['ORG', 'LOC', 'PER']:
                    all_entities.append((ent['word'], ent['entity_group']))
        if all_entities:
            ent_df = pd.DataFrame(all_entities, columns=['Entity', 'Type'])
            top_entities = ent_df['Entity'].value_counts().head(15)
            plt.figure(figsize=(14, 10), dpi=300)
            sns.barplot(x=top_entities.values, y=top_entities.index, palette='magma')
            plt.title('Top 15 Named Entities (Organizations, Locations, Persons)')
            plt.tight_layout()
            plt.savefig(os.path.join(img_dir, 'ner.png'))
            plt.close()
            md.append(f'\n![Named Entities](master_report_images/ner.png)\n')
    except Exception as e: print(e)

    full_md = "\n".join(md)
    md_out_path = os.path.join(out_dir, "Master_Dataset_Analysis_Report.md")
    with open(md_out_path, 'w', encoding='utf-8') as f:
        f.write(full_md)
        
    print(f"Generating Master PDF...")
    try:
        original_cwd = os.getcwd()
        os.chdir(out_dir)
        pdf = MarkdownPdf(toc_level=2)
        pdf.add_section(Section(full_md))
        pdf.save("Master_Dataset_Analysis_Report.pdf")
        os.chdir(original_cwd)
    except Exception as e:
        print(f"Error saving PDF: {e}")

if __name__ == "__main__":
    main()
