"""
RIGOROUS Zillow URL Verifier Test Suite
========================================
Tests every single ground truth URL from the CSV, validates cross-format
matching (positive vs negative property encoding), and stress-tests edge cases.

This is a CLIENT-FACING verification — zero tolerance for failures.
"""
import csv
import json
import sys
import os
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from navi_bench.zillow.zillow_url_match import ZillowUrlMatch

# ============================================================================
# HELPERS
# ============================================================================
def run_test(name, passed, details=""):
    status = "PASS" if passed else "FAIL"
    icon = "  " if passed else ">>"
    print(f"  {icon}[{status}] {name}")
    if not passed and details:
        print(f"          {details}")
    return passed


# ============================================================================
# TEST 1: PARSE EVERY CSV GROUND TRUTH URL
# ============================================================================
def test_csv_ground_truth_parsing():
    """Ensure every CSV ground truth URL can be parsed without errors and
    produces at least one filter."""
    print("\n" + "=" * 70)
    print("TEST 1: Parse Every CSV Ground Truth URL")
    print("=" * 70)

    csv_path = os.path.join(os.path.dirname(__file__), 
                            "navi_bench", "zillow", "zillow_benchmark_tasks.csv")
    
    results = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            task_id = row["task_id"]
            config = json.loads(row["task_generation_config_json"])
            gt_url = config["ground_truth_url"]
            task_desc = config["task"]
            
            try:
                verifier = ZillowUrlMatch(gt_url)
                parsed = verifier._parse_zillow_url(gt_url)
                
                has_filters = len(parsed["filters"]) > 0
                has_search_type = parsed["search_type"] in ("for_sale", "for_rent", "recently_sold")
                
                passed = has_filters and has_search_type
                detail = ""
                if not passed:
                    detail = f"filters={parsed['filters']}, search_type={parsed['search_type']}"
                
                results.append(run_test(
                    f"[{task_id}] {task_desc[:60]}...", 
                    passed, detail
                ))
            except Exception as e:
                results.append(run_test(
                    f"[{task_id}] PARSE ERROR", 
                    False, str(e)
                ))
    
    return results


# ============================================================================
# TEST 2: SELF-MATCH EVERY CSV URL
# ============================================================================
def test_csv_self_match():
    """Every ground truth URL should match itself (score 1.0)."""
    print("\n" + "=" * 70)
    print("TEST 2: Self-Match Every CSV Ground Truth URL")
    print("=" * 70)

    csv_path = os.path.join(os.path.dirname(__file__), 
                            "navi_bench", "zillow", "zillow_benchmark_tasks.csv")
    
    results = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            task_id = row["task_id"]
            config = json.loads(row["task_generation_config_json"])
            gt_url = config["ground_truth_url"]
            
            try:
                verifier = ZillowUrlMatch(gt_url)
                match, details = verifier._urls_match(gt_url, gt_url)
                
                detail = ""
                if not match:
                    mismatches = details.get("mismatches", [])
                    detail = f"Mismatches: {mismatches}"
                
                results.append(run_test(
                    f"[{task_id}] self-match", 
                    match, detail
                ))
            except Exception as e:
                results.append(run_test(
                    f"[{task_id}] SELF-MATCH ERROR", 
                    False, str(e)
                ))
    
    return results


# ============================================================================
# TEST 3: NEGATIVE ENCODING <-> POSITIVE ENCODING CROSS-MATCH
# ============================================================================
def test_negative_positive_cross_match():
    """The critical bug: negative encoding (false values) must match
    positive encoding (true values) for property types."""
    print("\n" + "=" * 70)
    print("TEST 3: Negative <-> Positive Property Type Cross-Match")
    print("=" * 70)

    results = []
    
    # Test case: "Houses only" — negative encoding from CSV
    # Negative: all types except sf set to false
    neg_houses = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%7D%7D'
    # Positive: isHouse set to true
    pos_houses = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22isHouse%22%3A%7B%22value%22%3Atrue%7D%7D%7D'
    
    v = ZillowUrlMatch(neg_houses)
    parsed_neg = v._parse_zillow_url(neg_houses)
    parsed_pos = v._parse_zillow_url(pos_houses)
    
    # Both should resolve to ishouse: True
    results.append(run_test(
        "Negative encoding -> ishouse:True",
        parsed_neg["filters"].get("ishouse") == True,
        f"Got filters: {parsed_neg['filters']}"
    ))
    results.append(run_test(
        "Positive encoding -> ishouse:True",
        parsed_pos["filters"].get("ishouse") == True,
        f"Got filters: {parsed_pos['filters']}"
    ))
    
    # Cross-match: agent uses positive, GT uses negative (or vice versa)
    match1, d1 = v._urls_match(pos_houses, neg_houses)
    results.append(run_test(
        "Agent(positive) matches GT(negative) for Houses",
        match1, f"Mismatches: {d1.get('mismatches', [])}"
    ))
    
    match2, d2 = v._urls_match(neg_houses, pos_houses)
    v2 = ZillowUrlMatch(pos_houses)
    match2, d2 = v2._urls_match(neg_houses, pos_houses)
    results.append(run_test(
        "Agent(negative) matches GT(positive) for Houses",
        match2, f"Mismatches: {d2.get('mismatches', [])}"
    ))
    
    # ---- Condos only ----
    neg_condos = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22sf%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%7D%7D'
    pos_condos = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22isCondo%22%3A%7B%22value%22%3Atrue%7D%7D%7D'
    
    v3 = ZillowUrlMatch(neg_condos)
    parsed_neg_c = v3._parse_zillow_url(neg_condos)
    parsed_pos_c = v3._parse_zillow_url(pos_condos)
    
    results.append(run_test(
        "Negative encoding -> iscondo:True",
        parsed_neg_c["filters"].get("iscondo") == True,
        f"Got filters: {parsed_neg_c['filters']}"
    ))
    
    match3, d3 = v3._urls_match(pos_condos, neg_condos)
    results.append(run_test(
        "Agent(positive) matches GT(negative) for Condos",
        match3, f"Mismatches: {d3.get('mismatches', [])}"
    ))
    
    # ---- Townhomes only ----
    neg_townhomes = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22sf%22%3A%7B%22value%22%3Afalse%7D%7D%7D'
    pos_townhomes = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22isTownhouse%22%3A%7B%22value%22%3Atrue%7D%7D%7D'
    
    v4 = ZillowUrlMatch(neg_townhomes)
    match4, d4 = v4._urls_match(pos_townhomes, neg_townhomes)
    results.append(run_test(
        "Agent(positive) matches GT(negative) for Townhomes",
        match4, f"Mismatches: {d4.get('mismatches', [])}"
    ))
    
    # ---- Multi-family only ----
    neg_mf = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22sf%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%7D%7D'
    pos_mf = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22isMultiFamily%22%3A%7B%22value%22%3Atrue%7D%7D%7D'
    
    v5 = ZillowUrlMatch(neg_mf)
    match5, d5 = v5._urls_match(pos_mf, neg_mf)
    results.append(run_test(
        "Agent(positive) matches GT(negative) for Multi-Family",
        match5, f"Mismatches: {d5.get('mismatches', [])}"
    ))

    # ---- Land only ----
    neg_land = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22sf%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%7D%7D'
    pos_land = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22isLotLand%22%3A%7B%22value%22%3Atrue%7D%7D%7D'

    v6 = ZillowUrlMatch(neg_land)
    match6, d6 = v6._urls_match(pos_land, neg_land)
    results.append(run_test(
        "Agent(positive) matches GT(negative) for Land",
        match6, f"Mismatches: {d6.get('mismatches', [])}"
    ))
    
    # ---- Manufactured only ----
    neg_manu = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22sf%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%7D%7D'
    pos_manu = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22isManufactured%22%3A%7B%22value%22%3Atrue%7D%7D%7D'
    
    v7 = ZillowUrlMatch(neg_manu)
    match7, d7 = v7._urls_match(pos_manu, neg_manu)
    results.append(run_test(
        "Agent(positive) matches GT(negative) for Manufactured",
        match7, f"Mismatches: {d7.get('mismatches', [])}"
    ))
    
    # ---- Apartments only ----
    neg_apt = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22sf%22%3A%7B%22value%22%3Afalse%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%7D%7D'
    pos_apt = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22isApartment%22%3A%7B%22value%22%3Atrue%7D%7D%7D'
    
    v8 = ZillowUrlMatch(neg_apt)
    match8, d8 = v8._urls_match(pos_apt, neg_apt)
    results.append(run_test(
        "Agent(positive) matches GT(negative) for Apartments",
        match8, f"Mismatches: {d8.get('mismatches', [])}"
    ))
    
    # ---- Houses + Townhomes combo ----
    neg_ht = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%7D%7D'
    pos_ht = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22isHouse%22%3A%7B%22value%22%3Atrue%7D%2C%22isTownhouse%22%3A%7B%22value%22%3Atrue%7D%7D%7D'
    
    v9 = ZillowUrlMatch(neg_ht)
    match9, d9 = v9._urls_match(pos_ht, neg_ht)
    results.append(run_test(
        "Agent(positive) matches GT(negative) for Houses+Townhomes combo",
        match9, f"Mismatches: {d9.get('mismatches', [])}"
    ))

    # ---- Houses + Condos + Townhomes combo (CSV task 18 & 20) ----
    neg_hct = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%7D%7D'
    pos_hct = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22isHouse%22%3A%7B%22value%22%3Atrue%7D%2C%22isCondo%22%3A%7B%22value%22%3Atrue%7D%2C%22isTownhouse%22%3A%7B%22value%22%3Atrue%7D%7D%7D'
    
    v10 = ZillowUrlMatch(neg_hct)
    match10, d10 = v10._urls_match(pos_hct, neg_hct)
    results.append(run_test(
        "Agent(positive) matches GT(negative) for Houses+Condos+Townhomes",
        match10, f"Mismatches: {d10.get('mismatches', [])}"
    ))
    
    return results


# ============================================================================
# TEST 4: CSV URL CROSS-FORMAT MATCHING (AGENT USES POS, GT USES NEG)
# ============================================================================
def test_csv_cross_format_matching():
    """For each CSV task that uses negative property encoding, test that
    an agent using POSITIVE encoding would still match."""
    print("\n" + "=" * 70)
    print("TEST 4: CSV Cross-Format Matching (Positive Agent vs Negative GT)")
    print("=" * 70)
    
    csv_path = os.path.join(os.path.dirname(__file__), 
                            "navi_bench", "zillow", "zillow_benchmark_tasks.csv")
    
    # Build a map of which false abbreviations infer which positive types
    ABBREV_TO_CANONICAL = {
        "sf": "ishouse", "tow": "istownhouse", "mf": "ismultifamily",
        "con": "iscondo", "land": "islotland", "apa": "isapartment",
        "apco": "isapartment", "manu": "ismanufactured",
    }
    ALL_TYPES = {"ishouse", "istownhouse", "ismultifamily", "iscondo",
                 "islotland", "isapartment", "ismanufactured"}
    
    results = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            task_id = row["task_id"]
            config = json.loads(row["task_generation_config_json"])
            gt_url = config["ground_truth_url"]
            
            # Parse just the filterState to check if it has negative encoding
            try:
                verifier = ZillowUrlMatch(gt_url)
                from urllib.parse import urlparse, parse_qs, unquote
                parsed_url = urlparse(gt_url)
                qs = parse_qs(parsed_url.query)
                sqs_raw = qs.get("searchQueryState", ["{}"])[0]
                sqs = json.loads(unquote(sqs_raw))
                filter_state = sqs.get("filterState", {})
                
                # Find false abbreviations in this URL
                false_abbrevs = set()
                pos_types = set()
                other_filters = {}
                for k, v in filter_state.items():
                    k_lower = k.lower()
                    if isinstance(v, dict) and "value" in v:
                        if v["value"] is False and k_lower in ABBREV_TO_CANONICAL:
                            false_abbrevs.add(k_lower)
                        elif v["value"] is True and k_lower.startswith("is"):
                            pos_types.add(k_lower)
                
                # Only test tasks that use negative encoding
                if not false_abbrevs:
                    continue
                
                # Compute inferred positive types
                disabled_types = {ABBREV_TO_CANONICAL[a] for a in false_abbrevs}
                selected_types = ALL_TYPES - disabled_types
                
                if not selected_types:
                    continue
                
                # Build equivalent positive-only URL
                pos_filter = {}
                for k, v in filter_state.items():
                    k_lower = k.lower()
                    if k_lower in ABBREV_TO_CANONICAL:
                        continue  # Skip abbreviations
                    pos_filter[k] = v
                
                # Add positive property types
                for ptype in selected_types:
                    # Convert back to camelCase
                    camel = ptype  # e.g., "ishouse" -> need "isHouse"
                    for original in ["isHouse", "isTownhouse", "isMultiFamily", "isCondo",
                                     "isLotLand", "isApartment", "isManufactured"]:
                        if original.lower() == ptype:
                            camel = original
                            break
                    pos_filter[camel] = {"value": True}
                
                pos_sqs = dict(sqs)
                pos_sqs["filterState"] = pos_filter
                pos_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?searchQueryState={json.dumps(pos_sqs)}"
                
                match, details = verifier._urls_match(pos_url, gt_url)
                
                type_names = ", ".join(sorted(selected_types))
                detail = ""
                if not match:
                    detail = f"Types: {type_names}. Mismatches: {details.get('mismatches', [])}"
                
                results.append(run_test(
                    f"[{task_id}] Pos agent matches neg GT ({type_names})",
                    match, detail
                ))
                
            except Exception as e:
                results.append(run_test(
                    f"[{task_id}] CROSS-FORMAT ERROR",
                    False, f"{e}\n{traceback.format_exc()}"
                ))
    
    return results


# ============================================================================
# TEST 5: RENTAL CONTEXT FLAGS (fr, fsba, fsbo) ARE PROPERLY IGNORED
# ============================================================================
def test_rental_context_flags():
    """Zillow rental URLs include context flags fr/fsba/fsbo that should be
    ignored during matching. An agent URL with these flags should match
    a GT without them, and vice versa."""
    print("\n" + "=" * 70)
    print("TEST 5: Rental Context Flags (fr/fsba/fsbo) Ignored")
    print("=" * 70)
    
    results = []
    
    # GT has rental context flags (from CSV task 60)
    gt_with_flags = 'https://www.zillow.com/homes/for_rent/?searchQueryState=%7B%22filterState%22%3A%7B%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%7D%7D'
    
    # Agent without those flags but same filters
    agent_no_flags = 'https://www.zillow.com/homes/for_rent/?searchQueryState=%7B%22filterState%22%3A%7B%22beds%22%3A%7B%22min%22%3A1%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%7D%7D'
    
    v = ZillowUrlMatch(gt_with_flags)
    match, details = v._urls_match(agent_no_flags, gt_with_flags)
    results.append(run_test(
        "Agent without rental flags matches GT with flags",
        match, f"Mismatches: {details.get('mismatches', [])}"
    ))
    
    # Vice versa
    v2 = ZillowUrlMatch(agent_no_flags)
    match2, d2 = v2._urls_match(gt_with_flags, agent_no_flags)
    results.append(run_test(
        "Agent with rental flags matches GT without flags",
        match2, f"Mismatches: {d2.get('mismatches', [])}"
    ))
    
    return results


# ============================================================================
# TEST 6: EDGE CASES THAT COULD BREAK THE VERIFIER
# ============================================================================
def test_edge_cases():
    """Stress test edge cases: URL encoding, whitespace, extra params,
    empty filters, weird values."""
    print("\n" + "=" * 70)
    print("TEST 6: Edge Cases & Stress Tests")
    print("=" * 70)
    
    results = []
    
    # 6a: URL with extra pagination/map params (should be stripped)
    gt = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22filterState%22%3A%7B%22price%22%3A%7B%22min%22%3A500000%7D%7D%7D'
    agent_with_extra = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%7B%22pagination%22%3A%7B%22currentPage%22%3A2%7D%2C%22mapBounds%22%3A%7B%22north%22%3A34.2%2C%22south%22%3A33.8%7D%2C%22filterState%22%3A%7B%22price%22%3A%7B%22min%22%3A500000%7D%7D%7D'
    
    v = ZillowUrlMatch(gt)
    match, details = v._urls_match(agent_with_extra, gt)
    results.append(run_test(
        "Pagination + map bounds are stripped",
        match, f"Mismatches: {details.get('mismatches', [])}"
    ))
    
    # 6b: Double URL encoding
    gt_double = 'https://www.zillow.com/homes/for_sale/?searchQueryState=%257B%2522filterState%2522%253A%257B%2522price%2522%253A%257B%2522min%2522%253A500000%257D%257D%257D'
    v2 = ZillowUrlMatch(gt)
    parsed = v2._parse_zillow_url(gt_double)
    results.append(run_test(
        "Double URL encoding handled",
        parsed["filters"].get("price_min") == 500000,
        f"Got filters: {parsed['filters']}"
    ))
    
    # 6c: Integer vs float values match
    gt_int = 'https://www.zillow.com/homes/for_sale/?searchQueryState={"filterState":{"price":{"min":500000}}}'
    agent_float = 'https://www.zillow.com/homes/for_sale/?searchQueryState={"filterState":{"price":{"min":500000.0}}}'
    
    v3 = ZillowUrlMatch(gt_int)
    match3, d3 = v3._urls_match(agent_float, gt_int)
    results.append(run_test(
        "500000 == 500000.0 (int vs float normalization)",
        match3, f"Mismatches: {d3.get('mismatches', [])}"
    ))
    
    # 6d: Case insensitivity for keys
    gt_camel = 'https://www.zillow.com/homes/for_sale/?searchQueryState={"filterState":{"hasPool":{"value":true}}}'
    agent_lower = 'https://www.zillow.com/homes/for_sale/?searchQueryState={"filterState":{"haspool":{"value":true}}}'
    
    v4 = ZillowUrlMatch(gt_camel)
    match4, d4 = v4._urls_match(agent_lower, gt_camel)
    results.append(run_test(
        "Case insensitive key matching (hasPool vs haspool)",
        match4, f"Mismatches: {d4.get('mismatches', [])}"
    ))
    
    # 6e: Empty filterState should not crash
    empty_url = 'https://www.zillow.com/homes/for_sale/?searchQueryState={"filterState":{}}'
    v5 = ZillowUrlMatch(empty_url)
    parsed_empty = v5._parse_zillow_url(empty_url)
    results.append(run_test(
        "Empty filterState handled without crash",
        parsed_empty["filters"] == {} and parsed_empty["search_type"] == "for_sale",
        f"Got: {parsed_empty}"
    ))
    
    # 6f: No searchQueryState at all
    bare_url = 'https://www.zillow.com/homes/for_sale/'
    v6 = ZillowUrlMatch(bare_url)
    parsed_bare = v6._parse_zillow_url(bare_url)
    results.append(run_test(
        "No searchQueryState handled without crash",
        parsed_bare["search_type"] == "for_sale",
        f"Got: {parsed_bare}"
    ))
    
    # 6g: Price with comma formatting (e.g. "500,000")
    price_comma = 'https://www.zillow.com/homes/for_sale/?searchQueryState={"filterState":{"price":{"min":"500,000"}}}'
    v7 = ZillowUrlMatch(price_comma)
    parsed_comma = v7._parse_zillow_url(price_comma)
    # Should either parse as 500000 or handle gracefully
    results.append(run_test(
        "Price with comma formatting (500,000)",
        parsed_comma["filters"].get("price_min") is not None,
        f"Got: price_min={parsed_comma['filters'].get('price_min')}"
    ))
    
    # 6h: HOA max:0 (meaning no HOA)
    hoa_zero = 'https://www.zillow.com/homes/for_sale/?searchQueryState={"filterState":{"hoa":{"max":0}}}'
    v8 = ZillowUrlMatch(hoa_zero)
    parsed_hoa = v8._parse_zillow_url(hoa_zero)
    results.append(run_test(
        "HOA max:0 (no HOA fee) parsed correctly",
        parsed_hoa["filters"].get("hoa_max") == 0,
        f"Got: hoa_max={parsed_hoa['filters'].get('hoa_max')}"
    ))
    
    # 6i: Sort parameter ignored in matching
    gt_no_sort = 'https://www.zillow.com/homes/for_sale/?searchQueryState={"filterState":{"price":{"min":500000}}}'
    agent_with_sort = 'https://www.zillow.com/homes/for_sale/?searchQueryState={"sortSelection":{"value":"pricea"},"filterState":{"price":{"min":500000}}}'
    
    v9 = ZillowUrlMatch(gt_no_sort)
    match9, d9 = v9._urls_match(agent_with_sort, gt_no_sort)
    results.append(run_test(
        "Sort parameter ignored in matching",
        match9, f"Mismatches: {d9.get('mismatches', [])}"
    ))

    # 6j: Negative property type encoding but GT has both neg encoding + other filters
    # This mimics real CSV task like: houses for sale with pool under $1M
    gt_complex_neg = 'https://www.zillow.com/homes/for_sale/?searchQueryState={"filterState":{"apa":{"value":false},"con":{"value":false},"land":{"value":false},"manu":{"value":false},"mf":{"value":false},"tow":{"value":false},"hasPool":{"value":true},"price":{"max":1000000}}}'
    agent_complex_pos = 'https://www.zillow.com/homes/for_sale/?searchQueryState={"filterState":{"isHouse":{"value":true},"hasPool":{"value":true},"price":{"max":1000000}}}'
    
    v10 = ZillowUrlMatch(gt_complex_neg)
    match10, d10 = v10._urls_match(agent_complex_pos, gt_complex_neg)
    results.append(run_test(
        "Complex: Houses(neg) + pool + price matches Houses(pos) + pool + price",
        match10, f"Mismatches: {d10.get('mismatches', [])}"
    ))
    
    return results


# ============================================================================
# TEST 7: SPECIFIC CSV TASKS THAT USE NEGATIVE ENCODING
# ============================================================================
def test_specific_csv_negative_tasks():
    """Directly test the CSV tasks that Nikhil flagged (tasks 10-21, 48-59)
    which use negative encoding for property types."""
    print("\n" + "=" * 70)
    print("TEST 7: Specific CSV Tasks Using Negative Encoding (10-21, 48-59)")
    print("=" * 70)
    
    csv_path = os.path.join(os.path.dirname(__file__), 
                            "navi_bench", "zillow", "zillow_benchmark_tasks.csv")
    
    ABBREV_TO_CANONICAL = {
        "sf": "ishouse", "tow": "istownhouse", "mf": "ismultifamily",
        "con": "iscondo", "land": "islotland", "apa": "isapartment",
        "apco": "isapartment", "manu": "ismanufactured",
    }
    ALL_TYPES = {"ishouse", "istownhouse", "ismultifamily", "iscondo",
                 "islotland", "isapartment", "ismanufactured"}
    
    results = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            task_id = row["task_id"]
            config = json.loads(row["task_generation_config_json"])
            gt_url = config["ground_truth_url"]
            task_desc = config["task"]
            
            # Test only property type tasks
            if "property_type" not in task_id and "complex" not in task_id:
                continue
            
            verifier = ZillowUrlMatch(gt_url)
            parsed = verifier._parse_zillow_url(gt_url)
            
            # Check what property types were inferred
            inferred_types = {k: v for k, v in parsed["filters"].items() 
                            if k in ALL_TYPES and v == True}
            
            has_any_type = len(inferred_types) > 0
            
            detail = ""
            if not has_any_type:
                detail = f"NO property types inferred! Filters: {parsed['filters']}"
            else:
                detail = f"Inferred: {inferred_types}"
            
            results.append(run_test(
                f"[{task_id}] types={list(inferred_types.keys())} | {task_desc[:50]}",
                has_any_type, detail
            ))
    
    return results


# ============================================================================
# TEST 8: LOCATION MATCHING ROBUSTNESS
# ============================================================================
def test_location_matching():
    """Test location matching with various formats."""
    print("\n" + "=" * 70)
    print("TEST 8: Location Matching Robustness")
    print("=" * 70)
    
    results = []
    
    # Los Angeles CA vs Los Angeles, CA
    gt = 'https://www.zillow.com/homes/for_sale/Los-Angeles,-CA_rb/?searchQueryState={"usersSearchTerm":"Los Angeles CA","filterState":{"price":{"min":500000}}}'
    agent = 'https://www.zillow.com/homes/for_sale/Los-Angeles,-CA_rb/?searchQueryState={"usersSearchTerm":"los angeles, ca","filterState":{"price":{"min":500000}}}'
    
    v = ZillowUrlMatch(gt)
    match, d = v._urls_match(agent, gt)
    results.append(run_test(
        "Los Angeles CA vs los angeles, ca",
        match, f"Mismatches: {d.get('mismatches', [])}"
    ))
    
    # Different location = should fail
    gt2 = 'https://www.zillow.com/homes/for_sale/Los-Angeles,-CA_rb/?searchQueryState={"usersSearchTerm":"Los Angeles CA","filterState":{"price":{"min":500000}}}'
    agent2 = 'https://www.zillow.com/homes/for_sale/San-Francisco,-CA_rb/?searchQueryState={"usersSearchTerm":"San Francisco CA","filterState":{"price":{"min":500000}}}'
    
    v2 = ZillowUrlMatch(gt2)
    match2, d2 = v2._urls_match(agent2, gt2)
    results.append(run_test(
        "Los Angeles vs San Francisco should NOT match",
        not match2, f"Unexpectedly matched!"
    ))
    
    return results


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("RIGOROUS ZILLOW VERIFIER TEST SUITE")
    print("Zero tolerance for failures — client delivery verification")
    print("=" * 70)
    
    all_results = []
    
    try:
        all_results += test_csv_ground_truth_parsing()
        all_results += test_csv_self_match()
        all_results += test_negative_positive_cross_match()
        all_results += test_csv_cross_format_matching()
        all_results += test_rental_context_flags()
        all_results += test_edge_cases()
        all_results += test_specific_csv_negative_tasks()
        all_results += test_location_matching()
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        traceback.print_exc()
    
    # Final summary
    print("\n" + "=" * 70)
    passed = sum(all_results)
    total = len(all_results)
    failed = total - passed
    pct = 100 * passed / total if total > 0 else 0
    
    print(f"FINAL RESULTS: {passed}/{total} tests passed ({pct:.1f}%)")
    if failed > 0:
        print(f"FAILURES: {failed} tests FAILED")
    else:
        print("ALL TESTS PASSED — READY FOR CLIENT")
    print("=" * 70)
