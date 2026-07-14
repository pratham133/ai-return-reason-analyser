# AI-Powered E-commerce Return Reason Analyser

Categorizes raw customer return reasons, finds root causes, and prioritizes
product/ops fixes — the kind of analysis a Data Analyst or Product Analyst
does to reduce return-driven revenue loss.

## Problem
Returns cost D2C/e-commerce brands 15-25% of revenue. Return reason text is
usually free-form and unstructured, so most teams never systematically
analyze *why* items come back — they just process refunds.

## Approach
This isn't a single Claude prompt — it's a small NLP pipeline:

1. **Text cleaning** — spaCy lemmatization, stopword & punctuation removal
2. **Vectorization** — TF-IDF (unigrams + bigrams) on cleaned return reasons
3. **Unsupervised clustering** — KMeans groups similar return reasons without
   any labeled data
4. **Analyst reconciliation** — raw ML clusters rarely map cleanly onto
   business categories, so cluster output is reviewed and consolidated into
   6 categories a product/ops team can act on
5. **Business layer** — each category gets a root cause, a recommended fix,
   and a priority ranking

## Results on the sample dataset (50 return reasons)

| Category | Returns | % of Total | Priority |
|---|---|---|---|
| Not as Described (Listing Mismatch) | 14 | 28% | High |
| Damaged / Incomplete on Arrival | 12 | 24% | High |
| Size / Fit Mismatch | 8 | 16% | High |
| Product Malfunction | 8 | 16% | Medium |
| Build Quality / Durability | 6 | 12% | Medium |
| Wrong Item Sent | 2 | 4% | Low-Medium |

Full breakdown with root cause + recommended fix per category:
`AI_Return_Reason_Analysis.xlsx`

## How to run it yourself

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Run the clustering pipeline (prints 8 raw clusters + top terms)
python return_analyzer.py

# 4. Run the business categorization step (prints the final summary table)
python categorize.py

# 5. (Optional) rebuild the Excel dashboard
python build_excel.py
```

You should see terminal output listing return reasons grouped into clusters,
then the final categorized summary table with counts, %, root cause, fix,
and priority per category.

## Files
- `sample_returns.csv` — sample dataset (swap in real scraped Amazon/Flipkart
  return-mention reviews to run on real data)
- `return_analyzer.py` — spaCy + TF-IDF + KMeans clustering pipeline
- `categorize.py` — reconciles clusters into business categories, computes
  root cause / fix / priority
- `AI_Return_Reason_Analysis.xlsx` — final dashboard with live formulas + chart

## Stack
Python, spaCy, scikit-learn (TF-IDF, KMeans), pandas, openpyxl

## What I'd build next
- Swap sample data for real scraped review data (Amazon/Flipkart "returned
  this item" mentions)
- Replace keyword-rule reconciliation with an LLM-assisted labeling step
  (Claude API) to auto-name clusters instead of manual rules
- Add month-over-month tracking so category volumes are trended, not
  point-in-time
