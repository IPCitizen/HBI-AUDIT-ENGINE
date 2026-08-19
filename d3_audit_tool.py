#!/usr/bin/env python3
"""
Dimension 3 (D3) Franchise Degradation & Electoral Asymmetry Audit Script (v1.0)
---------------------------------------------------------------------------------
Course: POLI 485 / LAW 720: Democratic Backsliding & Institutional Auditing
Description: Computes the Partisan Efficiency Gap (EG) across legislative districts
             and evaluates NVRA 90-Day Quiet Period Purge Anomalies (P_nvra).
"""

import argparse
import math
import sys
import pandas as pd

def calculate_efficiency_gap(df: pd.DataFrame) -> dict:
    """Calculates district wasted votes and state Efficiency Gap percentage."""
    tot_wasted_a = 0
    tot_wasted_b = 0
    tot_votes = 0
    records = []

    for _, row in df.iterrows():
        v_a = int(row['Party_A_Votes'])
        v_b = int(row['Party_B_Votes'])
        v_tot = v_a + v_b
        needed = math.floor(v_tot / 2) + 1

        if v_a > v_b:
            w_a = v_a - needed
            w_b = v_b
            winner = "Party A"
        else:
            w_a = v_a
            w_b = v_b - needed
            winner = "Party B"

        tot_wasted_a += w_a
        tot_wasted_b += w_b
        tot_votes += v_tot

        records.append({
            "District": row['District'],
            "Party_A_Votes": v_a,
            "Party_B_Votes": v_b,
            "Winner": winner,
            "Wasted_A": w_a,
            "Wasted_B": w_b
        })

    eg_pct = (abs(tot_wasted_a - tot_wasted_b) / tot_votes) * 100.0 if tot_votes > 0 else 0.0
    net_adv = "Party B" if (tot_wasted_a > tot_wasted_b) else "Party A"

    return {
        "Total_Votes": tot_votes,
        "Total_Wasted_A": tot_wasted_a,
        "Total_Wasted_B": tot_wasted_b,
        "EG_Percent": eg_pct,
        "Advantage": net_adv,
        "Districts": records
    }

def main():
    parser = argparse.ArgumentParser(description="Audit D3 Efficiency Gap & NVRA Purges")
    parser.add_argument("--election_data", type=str, required=True, help="CSV with columns: District, Party_A_Votes, Party_B_Votes")
    parser.add_argument("--obs_purge", type=float, default=0.08, help="Observed annual purge rate (e.g. 0.08)")
    parser.add_argument("--base_purge", type=float, default=0.05, help="Historical baseline purge rate (e.g. 0.05)")
    parser.add_argument("--quiet_period", action="store_true", help="Set flag if purges occurred within 90 days of an election")
    parser.add_argument("--output", type=str, default="d3_audit_results.csv", help="Output CSV file")
    args = parser.parse_args()

    print("=================================================================")
    print(" D3 AUDIT ENGINE: FRANCHISE DEGRADATION & ELECTORAL ASYMMETRY   ")
    print("=================================================================")

    df = pd.read_csv(args.election_data)
    eg_results = calculate_efficiency_gap(df)

    # Purge calculation
    quiet_mult = 2.0 if args.quiet_period else 1.0
    p_nvra = ((args.obs_purge - args.base_purge) / args.base_purge) * 100.0 * quiet_mult

    print("\n=================== D3 AUDIT SUMMARY ===================")
    print(f"Districts Audited:             {len(df)}")
    print(f"Total Votes Cast:              {eg_results['Total_Votes']:,}")
    print(f"Efficiency Gap (EG):           {eg_results['EG_Percent']:.2f}% (Advantage: {eg_results['Advantage']})")
    print(f"NVRA Purge Anomaly (P_nvra):   {p_nvra:.2f}% (Quiet Multiplier: {quiet_mult}x)")
    print("=========================================================\n")

    res_df = pd.DataFrame(eg_results["Districts"])
    res_df.to_csv(args.output, index=False)
    print(f"District audit details exported to: {args.output}")

if __name__ == "__main__":
    main()
