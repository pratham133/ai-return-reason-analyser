import pandas as pd

df = pd.read_csv("clustered_returns.csv")

# Business-meaningful categories, assigned using keyword rules cross-checked
# against the KMeans clusters (analyst judgment reconciling raw clusters into
# categories a product/ops team can actually act on).

def assign_category(row):
    r = row["return_reason"].lower()
    if any(k in r for k in ["size", "fit", "waist", "thigh", "large but", "sizing ran"]):
        return "Size / Fit Mismatch"
    if any(k in r for k in ["stopped", "stop heat", "stop connect", "dead pixel",
                             "no sound", "did not hold charge", "burning smell",
                             "not working", "switch not working"]):
        return "Product Malfunction"
    if any(k in r for k in ["leak", "chipped", "broken", "torn box", "scuff",
                             "crack", "already opened", "missing"]):
        return "Damaged / Incomplete on Arrival"
    if any(k in r for k in ["broke", "peeling", "came apart", "stuck",
                             "elastic", "loose out of the box"]):
        return "Build Quality / Durability"
    if any(k in r for k in ["color", "different design", "faded", "fabric",
                             "cotton advertised", "see through", "thread count",
                             "length was much shorter", "print on the",
                             "sound quality was tinny", "smell"]):
        return "Not as Described (Listing Mismatch)"
    if any(k in r for k in ["wrong item", "uk 9 but received uk 8",
                             "did not match the left", "wrong item completely",
                             "different color than what was ordered"]):
        return "Wrong Item Sent"
    if any(k in r for k in ["scratched", "scratch", "almost empty", "tampered"]):
        return "Damaged / Incomplete on Arrival"
    if any(k in r for k in ["sole started coming off", "coming off after light use"]):
        return "Build Quality / Durability"
    return "Other"

df["business_category"] = df.apply(assign_category, axis=1)

summary = (
    df.groupby("business_category")
    .agg(returns=("return_reason", "count"), avg_price=("price", "mean"))
    .reset_index()
)
summary["pct_of_total"] = (summary["returns"] / summary["returns"].sum() * 100).round(1)
summary = summary.sort_values("returns", ascending=False)

root_cause_fix = {
    "Size / Fit Mismatch": (
        "Size charts are inconsistent or not brand/category-specific",
        "Standardize size charts per brand & add a fit-quiz / model height-weight reference on listing",
        "High",
    ),
    "Damaged / Incomplete on Arrival": (
        "Weak packaging and/or logistics handling for fragile or liquid items",
        "Upgrade packaging spec for fragile/liquid SKUs; add tamper/seal QC check before dispatch",
        "High",
    ),
    "Not as Described (Listing Mismatch)": (
        "Listing photos/copy overstate material quality or use inconsistent lighting for color",
        "Reshoot product photography in neutral lighting; add fabric/material spec field to listing",
        "High",
    ),
    "Product Malfunction": (
        "Insufficient QC on electronics/appliance batches before shipping",
        "Add a functional pre-dispatch test (power-on/charge check) for electronics & appliances",
        "Medium",
    ),
    "Build Quality / Durability": (
        "Supplier-side quality issue (stitching, coating, elastic) not caught in QC",
        "Tighten incoming QC threshold with supplier; add durability spot-checks per batch",
        "Medium",
    ),
    "Wrong Item Sent": (
        "Warehouse picking/packing errors during order fulfillment",
        "Add barcode-scan verification step at packing before an order is sealed",
        "Low-Medium",
    ),
    "Other": ("Mixed / low-volume causes", "Monitor for emerging patterns next cycle", "Low"),
}

summary["root_cause"] = summary["business_category"].map(lambda c: root_cause_fix[c][0])
summary["recommended_fix"] = summary["business_category"].map(lambda c: root_cause_fix[c][1])
summary["priority"] = summary["business_category"].map(lambda c: root_cause_fix[c][2])

df.to_csv("categorized_returns.csv", index=False)
summary.to_csv("category_summary.csv", index=False)
print(summary.to_string(index=False))
