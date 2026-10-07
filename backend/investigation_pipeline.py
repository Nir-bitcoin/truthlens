"""
TruthLens — Investigation Pipeline

Yeh module saare backend engines ko orchestrate karta hai:
    - SerpApi evidence fetch
    - EEG (Expected Evidence Gap)
    - Independence analysis
    - Verdict engine
    - CEE (Counterfactual Evidence Engine)

Ek function call se pura investigation ho jayega.
"""

from typing import Any, Dict, List, Optional

# Saare engines import karo
try:
    from serpapi_evidence import (
        fetch_live_evidence,
        classify_live_evidence,
        get_serpapi_kpis,
    )
    from eeg_engine import (
        generate_expected_profile,
        match_expected_vs_found,
        get_eeg_kpis,
    )
    from independence_engine import (
        cluster_sources,
        calculate_independence,
        get_independence_kpis,
    )
    from verdict_engine import (
        calculate_verdict,
        apply_eeg_gate,
        get_verdict_badge,
        get_kpi_cards,
    )
    from cee_engine import (
        identify_decisive_evidence,
        targeted_search,
        reverify,
        run_cee_pipeline,
        get_cee_kpis,
    )
except ImportError:
    from backend.serpapi_evidence import (
        fetch_live_evidence,
        classify_live_evidence,
        get_serpapi_kpis,
    )
    from backend.eeg_engine import (
        generate_expected_profile,
        match_expected_vs_found,
        get_eeg_kpis,
    )
    from backend.independence_engine import (
        cluster_sources,
        calculate_independence,
        get_independence_kpis,
    )
    from backend.verdict_engine import (
        calculate_verdict,
        apply_eeg_gate,
        get_verdict_badge,
        get_kpi_cards,
    )
    from backend.cee_engine import (
        identify_decisive_evidence,
        targeted_search,
        reverify,
        run_cee_pipeline,
        get_cee_kpis,
    )


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_full_investigation(
    claim: str,
    document_chunks: Optional[List[Any]] = None,
    answerability: Optional[Dict[str, Any]] = None,
    enable_cee: bool = True,
) -> Dict[str, Any]:
    """
    Pura investigation pipeline ek call mein.

    Input:
        claim:            user ka claim
        document_chunks:  existing TruthLens retrieval se chunks
        answerability:    existing check_answerability() output
        enable_cee:       CEE run karna hai ya nahi (default True)

    Output:
        {
            "claim": str,
            "live_evidence": dict,
            "all_evidence": list,
            "eeg_result": dict,
            "cluster_data": dict,
            "independence": dict,
            "verdict_result": dict,
            "final_verdict": dict,
            "cee_result": dict (optional),
            "kpis": dict,
            "errors": list,
        }
    """

    result = {
        "claim": claim,
        "live_evidence": {},
        "all_evidence": [],
        "eeg_result": {},
        "cluster_data": {},
        "independence": {},
        "verdict_result": {},
        "final_verdict": {},
        "cee_result": {},
        "kpis": {},
        "errors": [],
    }

    # ------------------------------------------------------------
    # Step 1: SerpApi Live Evidence
    # ------------------------------------------------------------
    try:
        live = fetch_live_evidence(claim)
        live = classify_live_evidence(live, claim)
        result["live_evidence"] = live
    except Exception as e:
        result["errors"].append(f"SerpApi: {e}")
        live = {
            "supporting": [], "contradicting": [], "news": [],
            "fact_checks": [], "scholar": [], "neutral": [],
            "total_results": 0,
        }

    # ------------------------------------------------------------
    # Step 2: Combine all evidence
    # ------------------------------------------------------------
    all_evidence = []

    # Document evidence (agar available)
    if document_chunks:
        for c in document_chunks:
            all_evidence.append({
                "title": f"{c.get('file', 'Document')} page {c.get('page', '?')}",
                "source": c.get("file", "Document"),
                "url": "",
                "snippet": c.get("text", ""),
                "stance": "neutral",
            })

    # Live evidence
    for key in ("supporting", "contradicting", "news", "fact_checks", "scholar", "neutral"):
        for item in live.get(key, []):
            if isinstance(item, dict):
                all_evidence.append(item)

    result["all_evidence"] = all_evidence

    # ------------------------------------------------------------
    # Step 3: EEG — Expected Evidence Gap
    # ------------------------------------------------------------
    try:
        expected_profile = generate_expected_profile(claim)
        eeg_result = match_expected_vs_found(expected_profile, all_evidence)
        eeg_result["expected_profile"] = expected_profile
        result["eeg_result"] = eeg_result
    except Exception as e:
        result["errors"].append(f"EEG: {e}")
        eeg_result = {}

    # ------------------------------------------------------------
    # Step 4: Independence Analysis
    # ------------------------------------------------------------
    try:
        cluster_data = cluster_sources(all_evidence)
        independence = calculate_independence(cluster_data)
        result["cluster_data"] = cluster_data
        result["independence"] = independence
    except Exception as e:
        result["errors"].append(f"Independence: {e}")
        cluster_data = {}
        independence = {}

    # ------------------------------------------------------------
    # Step 5: Verdict Engine
    # ------------------------------------------------------------
    try:
        verdict_result = calculate_verdict(
            claim,
            all_evidence,
            answerability=answerability,
            cluster_data=cluster_data,
        )
        result["verdict_result"] = verdict_result

        # Apply EEG gate
        final_verdict = apply_eeg_gate(verdict_result, eeg_result)
        result["final_verdict"] = final_verdict
    except Exception as e:
        result["errors"].append(f"Verdict: {e}")
        final_verdict = {}

    # ------------------------------------------------------------
    # Step 6: CEE — Counterfactual (optional)
    # ------------------------------------------------------------
    if enable_cee:
        try:
            cee_result = run_cee_pipeline(
                claim,
                final_verdict,
                all_evidence,
                eeg_result,
            )
            result["cee_result"] = cee_result
        except Exception as e:
            result["errors"].append(f"CEE: {e}")

    # ------------------------------------------------------------
    # Step 7: KPIs for UI
    # ------------------------------------------------------------
    result["kpis"] = {
        "serpapi": get_serpapi_kpis(live),
        "eeg": get_eeg_kpis(eeg_result),
        "independence": get_independence_kpis(cluster_data),
        "verdict": get_kpi_cards(final_verdict),
        "cee": get_cee_kpis(result.get("cee_result", {})),
    }

    return result


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    claim = "Elon Musk acquired Twitter in 2022"

    print("=" * 60)
    print("Investigation Pipeline — Self-Test")
    print("=" * 60)
    print(f"\nClaim: {claim}\n")

    result = run_full_investigation(claim)

    # Verdict
    final = result["final_verdict"]
    print(f"Verdict:       {get_verdict_badge(final.get('verdict', 'UNKNOWN'))}")
    print(f"Confidence:    {final.get('confidence', 0)}%")
    print(f"Summary:       {final.get('summary', '')}")

    # EEG
    eeg = result["eeg_result"]
    print(f"\n[EEG]")
    print(f"  Coverage:     {eeg.get('coverage', 0)}%")
    print(f"  Gap Severity: {eeg.get('gap_severity', 'UNKNOWN')}")
    print(f"  Missing:      {len(eeg.get('missing', []))}")

    # Independence
    ind = result["independence"]
    print(f"\n[Independence]")
    print(f"  Total sources:      {ind.get('total_sources', 0)}")
    print(f"  Independent:        {ind.get('independent_clusters', 0)}")
    print(f"  Concentration:      {ind.get('concentration_level', 'UNKNOWN')}")

    # CEE
    cee = result.get("cee_result", {})
    if cee:
        print(f"\n[CEE]")
        print(f"  Old Verdict:  {cee.get('old_verdict', 'UNKNOWN')}")
        print(f"  New Verdict:  {cee.get('new_verdict', 'UNKNOWN')}")
        print(f"  Changed:      {cee.get('changed', False)}")

    # Errors
    if result["errors"]:
        print(f"\n[Errors]")
        for err in result["errors"]:
            print(f"  ⚠ {err}")