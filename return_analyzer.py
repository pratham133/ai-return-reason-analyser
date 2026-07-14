"""
AI Return Reason Analyser
--------------------------
Pipeline:
  1. Load raw return reason text data (product, category, price, return_reason)
  2. Clean & lemmatize text with spaCy
  3. Vectorize with TF-IDF
  4. Cluster with KMeans (unsupervised categorization of return reasons)
  5. Surface top terms per cluster + representative examples
     -> These get labeled with a category / root cause / fix in a
        separate analysis step (analyst judgment, not hardcoded).

Author: Pratham Pasi
"""

import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np

nlp = spacy.load("en_core_web_sm")


def clean_text(text: str) -> str:
    """Lemmatize, lowercase, strip stopwords & punctuation."""
    doc = nlp(text.lower())
    tokens = [
        tok.lemma_ for tok in doc
        if not tok.is_stop and not tok.is_punct and not tok.is_space
    ]
    return " ".join(tokens)


def run_pipeline(csv_path: str, n_clusters: int = 8, random_state: int = 42):
    df = pd.read_csv(csv_path)
    df["clean_reason"] = df["return_reason"].apply(clean_text)

    vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
    X = vectorizer.fit_transform(df["clean_reason"])

    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    df["cluster"] = km.fit_predict(X)

    # top terms per cluster (for labeling)
    terms = np.array(vectorizer.get_feature_names_out())
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]

    cluster_summary = {}
    for i in range(n_clusters):
        top_terms = terms[order_centroids[i, :8]]
        examples = df[df["cluster"] == i]["return_reason"].head(3).tolist()
        cluster_summary[i] = {
            "size": int((df["cluster"] == i).sum()),
            "top_terms": list(top_terms),
            "examples": examples,
        }

    return df, cluster_summary


if __name__ == "__main__":
    df, summary = run_pipeline("sample_returns.csv", n_clusters=8)
    df.to_csv("clustered_returns.csv", index=False)

    for cid, info in sorted(summary.items(), key=lambda x: -x[1]["size"]):
        print(f"\n=== Cluster {cid} | size={info['size']} ===")
        print("Top terms:", ", ".join(info["top_terms"]))
        for ex in info["examples"]:
            print("  -", ex)
