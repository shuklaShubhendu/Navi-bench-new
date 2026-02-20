"""
Verify all 70 StreetEasy benchmark tasks:
1. CSV can be parsed correctly
2. All GT URLs self-match in the verifier
3. Cross-format matching works
"""
import csv
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from navi_bench.streeteasy.streeteasy_url_match import StreetEasyUrlMatch


def main():
    csv_path = os.path.join("navi_bench", "streeteasy",
                            "streeteasy_benchmark_tasks.xlsx - streeteasy_benchmark_tasks.csv")
    
    # Parse CSV
    tasks = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            config_json = row["task_generation_config_json"]
            # Remove outer quotes and unescape inner quotes
            if config_json.startswith('"') and config_json.endswith('"'):
                config_json = config_json[1:-1]
            config_json = config_json.replace('""', '"')
            config = json.loads(config_json)
            tasks.append({
                "task_id": row["task_id"],
                "task": config["task"],
                "gt_url": config["ground_truth_url"],
                "category": row["l2_category"],
                "difficulty": row["suggested_difficulty"],
            })
    
    print(f"Parsed {len(tasks)} tasks from CSV\n")
    
    # ================================================================
    # TEST 1: Self-match (every GT URL matches itself)
    # ================================================================
    print("=" * 70)
    print("TEST 1: Self-Match (every GT URL matches itself)")
    print("=" * 70)
    
    passed = 0
    failed = 0
    for t in tasks:
        evaluator = StreetEasyUrlMatch(gt_url=t["gt_url"])
        match, details = evaluator._urls_match(t["gt_url"], t["gt_url"])
        if match:
            passed += 1
        else:
            failed += 1
            print(f"  ❌ Task {t['task_id']}: {details}")
    
    print(f"\n  Self-match: {passed}/{len(tasks)} passed")
    
    # ================================================================
    # TEST 2: URL-encoded equivalence
    # ================================================================
    print("\n" + "=" * 70)
    print("TEST 2: URL-encoded vs raw equivalence")
    print("=" * 70)
    
    from urllib.parse import unquote
    enc_passed = 0
    enc_failed = 0
    for t in tasks:
        raw_url = unquote(t["gt_url"])
        evaluator = StreetEasyUrlMatch(gt_url=t["gt_url"])
        match, details = evaluator._urls_match(raw_url, t["gt_url"])
        if match:
            enc_passed += 1
        else:
            enc_failed += 1
            print(f"  ❌ Task {t['task_id']}: encoded vs raw mismatch: {details}")
    
    print(f"\n  Encoded equivalence: {enc_passed}/{len(tasks)} passed")
    
    # ================================================================
    # TEST 3: Key cross-format matches
    # ================================================================
    print("\n" + "=" * 70)
    print("TEST 3: Cross-format matching (key patterns)")
    print("=" * 70)
    
    cross_tests = [
        ("transit_lines:L vs subway:L",
         "https://streeteasy.com/for-rent/brooklyn/transit_lines:L|price:-4000",
         "https://streeteasy.com/for-rent/brooklyn/subway:L|price:-4000",
         True),
        ("comma amenities: doorman,gym vs gym,doorman",
         "https://streeteasy.com/for-sale/manhattan/amenities:doorman,gym",
         "https://streeteasy.com/for-sale/manhattan/amenities:gym,doorman",
         True),
        ("neighborhood: upper-west-side vs manhattan/upper-west-side",
         "https://streeteasy.com/for-sale/upper-west-side/type:D1|beds>=3",
         "https://streeteasy.com/for-sale/manhattan/upper-west-side/type:D1|beds>=3",
         True),
        ("filter order independence",
         "https://streeteasy.com/for-sale/manhattan/beds>=2|price:500000-1000000|type:D1",
         "https://streeteasy.com/for-sale/manhattan/type:D1|price:500000-1000000|beds>=2",
         True),
        ("washer_dryer alias → in_unit_laundry",
         "https://streeteasy.com/for-rent/brooklyn/amenities:washer_dryer",
         "https://streeteasy.com/for-rent/brooklyn/amenities:in_unit_laundry",
         True),
        ("Wrong borough must fail",
         "https://streeteasy.com/for-sale/brooklyn/type:D1",
         "https://streeteasy.com/for-sale/manhattan/type:D1",
         False),
        ("Wrong search type must fail",
         "https://streeteasy.com/for-rent/manhattan/type:D1",
         "https://streeteasy.com/for-sale/manhattan/type:D1",
         False),
    ]
    
    cross_passed = 0
    for name, agent_url, gt_url, expected in cross_tests:
        evaluator = StreetEasyUrlMatch(gt_url=gt_url)
        match, details = evaluator._urls_match(agent_url, gt_url)
        if match == expected:
            cross_passed += 1
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}: expected {expected}, got {match} — {details}")
    
    print(f"\n  Cross-format: {cross_passed}/{len(cross_tests)} passed")
    
    # ================================================================
    # SUMMARY
    # ================================================================
    total = passed + enc_passed + cross_passed
    total_tests = len(tasks) + len(tasks) + len(cross_tests)
    
    print("\n" + "=" * 70)
    color = "🟢" if total == total_tests else "🔴"
    print(f"{color} OVERALL: {total}/{total_tests} tests passed")
    
    # Category breakdown
    print("\n📊 Category breakdown:")
    from collections import Counter
    cats = Counter(t["category"] for t in tasks)
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count} tasks")
    
    diffs = Counter(t["difficulty"] for t in tasks)
    print(f"\n📊 Difficulty breakdown:")
    for d, count in sorted(diffs.items()):
        print(f"  {d}: {count} tasks")
    
    print("=" * 70)
    
    return 0 if total == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())
