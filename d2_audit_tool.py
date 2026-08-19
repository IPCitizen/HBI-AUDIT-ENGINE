#!/usr/bin/env python3
"""
Dimension 2 (D2) Law Enforcement & Regulatory Asymmetry Audit Script (v1.0)
---------------------------------------------------------------------------------
Course: POLI 485 / LAW 720: Democratic Backsliding & Institutional Auditing
Description: Audits the Federal Register for civil service reclassification rules
             and tracks Inspector General removal notices.
"""

import argparse
import datetime
import pandas as pd
import requests

FEDERAL_REGISTER_API = "https://www.federalregister.gov/api/v1"

def audit_civil_service_actions(days_back: int) -> list:
    """Queries the Federal Register for civil service and Inspector General rules."""
    start_date = (datetime.date.today() - datetime.timedelta(days=days_back)).strftime("%Y-%m-%d")
    print(f"[1/3] Scanning Federal Register for Civil Service & OIG Rules since {start_date}...")
    
    url = f"{FEDERAL_REGISTER_API}/documents.json"
    params = {
        "conditions[term]": "excepted service OR civil service OR schedule F OR inspector general",
        "conditions[type][]": ["RULE", "PRORULE"],
        "conditions[publication_date][gte]": start_date,
        "fields[]": ["document_number", "title", "publication_date", "agency_names", "html_url", "abstract"],
        "per_page": 100
    }
    
    res = requests.get(url, params=params)
    return res.json().get("results", []) if res.status_code == 200 else []

def main():
    parser = argparse.ArgumentParser(description="Audit D2 Civil Service & Regulatory Asymmetry")
    parser.add_argument("--days", type=int, default=365, help="Days to audit")
    parser.add_argument("--output", type=str, default="d2_audit_results.csv", help="Output CSV file")
    args = parser.parse_args()

    print("=================================================================")
    print(" D2 AUDIT ENGINE: LAW ENFORCEMENT & REGULATORY ASYMMETRY        ")
    print("=================================================================")
    
    docs = audit_civil_service_actions(args.days)
    records = []
    
    for doc in docs:
        title = doc.get("title", "")
        abstract = doc.get("abstract", "") or ""
        text = f"{title} {abstract}".lower()
        
        is_reclass = any(k in text for k in ["schedule f", "excepted service", "reclassify", "exempt position"])
        is_oig = any(k in text for k in ["inspector general", "oig removal", "vacancy"])
        
        records.append({
            "Doc_Number": doc.get("document_number"),
            "Date": doc.get("publication_date"),
            "Title": title,
            "Reclassification_Flag": is_reclass,
            "OIG_Action_Flag": is_oig,
            "Yield_Status": "HIGH" if (is_reclass or is_oig) else "LOW",
            "Citation": f"Fed. Reg. Doc. {doc.get('document_number')}"
        })

    df = pd.DataFrame(records)
    df.to_csv(args.output, index=False)
    
    high_yield = df[df["Yield_Status"] == "HIGH"]
    print(f"\n[2/2] Exported {len(df)} total records to {args.output}")
    print(f"High-Yield Target Actions Flagged: {len(high_yield)}")
    print(f"Reclassification Notices:         {len(df[df['Reclassification_Flag'] == True])}")
    print(f"Inspector General Actions:        {len(df[df['OIG_Action_Flag'] == True])}\n")

if __name__ == "__main__":
    main()
