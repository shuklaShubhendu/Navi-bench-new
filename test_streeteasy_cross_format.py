"""
StreetEasy Verifier — Cross-Format Matching Test Suite
======================================================

Tests every CSV ground truth URL against REALISTIC agent URLs that use the
formats StreetEasy's actual website produces (browser-verified Feb 2026).

Key format differences between CSV GT and real StreetEasy:
  1. CSV uses pipe-delimited amenities (amenities:doorman|amenities:gym)
     Real site uses comma-separated (amenities:doorman,gym)
  2. CSV uses subway:L
     Real site uses transit_lines:L
  3. CSV uses no_fee:1 as pipe filter
     Real site uses /no-fee path segment (but no_fee:1 also parseable)
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from navi_bench.streeteasy.streeteasy_url_match import StreetEasyUrlMatch


def run_test(name, gt_url, agent_url, expected_match=True):
    """Run a single test and return pass/fail."""
    evaluator = StreetEasyUrlMatch(gt_url=gt_url)
    match, details = evaluator._urls_match(agent_url, gt_url)
    status = "✅" if match == expected_match else "❌"
    passed = match == expected_match
    if not passed:
        extra = ""
        if details.get("mismatches"):
            extra = f" — {details['mismatches']}"
        print(f"  {status} {name}{extra}")
    else:
        print(f"  {status} {name}")
    return passed


def main():
    total = 0
    passed = 0

    def t(name, gt_url, agent_url, expected=True):
        nonlocal total, passed
        total += 1
        if run_test(name, gt_url, agent_url, expected):
            passed += 1

    # ================================================================
    # PART 1: Self-match — every CSV GT URL must match itself
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 1: CSV Ground Truth Self-Match (10 tasks)")
    print("=" * 70)

    csv_gts = {
        "Task 0 (condos sale)":
            "https://streeteasy.com/for-sale/manhattan/type:D1|price:500000-1000000|beds>=2",
        "Task 1 (co-ops sale)":
            "https://streeteasy.com/for-sale/brooklyn/type:P1|price:-700000",
        "Task 2 (amenities sale)":
            "https://streeteasy.com/for-sale/manhattan/type:D1|price:800000-2000000|amenities:doorman|amenities:elevator",
        "Task 3 (complex sale)":
            "https://streeteasy.com/for-sale/manhattan/type:D1,P1|beds>=2|price:-1500000|pets:allowed|amenities:doorman|amenities:gym",
        "Task 4 (rental no-fee)":
            "https://streeteasy.com/for-rent/manhattan/beds>=1|price:-3500|no_fee:1",
        "Task 5 (rental amenities)":
            "https://streeteasy.com/for-rent/brooklyn/price:2000-4000|pets:allowed|amenities:in_unit_laundry|amenities:doorman",
        "Task 6 (neighborhood)":
            "https://streeteasy.com/for-sale/manhattan/upper-west-side/type:D1|beds>=3|baths>=2",
        "Task 7 (prewar)":
            "https://streeteasy.com/for-sale/manhattan/type:P1|beds>=1|price:-600000|prewar:1",
        "Task 8 (sold status)":
            "https://streeteasy.com/for-sale/manhattan/type:D1|price:1000000-3000000|beds>=2|status:sold",
        "Task 9 (transit/subway)":
            "https://streeteasy.com/for-rent/brooklyn/beds>=2|price:-4000|no_fee:1|subway:L|amenities:gym",
    }

    for name, url in csv_gts.items():
        t(f"Self-match: {name}", url, url)

    # ================================================================
    # PART 2: Real Agent URLs vs CSV GT
    # Browser-verified formats from StreetEasy (Feb 2026)
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 2: Real Agent URLs vs CSV Ground Truth")
    print("(Agent URLs use browser-verified StreetEasy formats)")
    print("=" * 70)

    # Task 0: Agent uses exact same format → should match
    print("\n📋 Task 0: Manhattan condos $500k-$1M, 2+ beds")
    t("Agent exact match",
      csv_gts["Task 0 (condos sale)"],
      "https://streeteasy.com/for-sale/manhattan/type:D1|price:500000-1000000|beds>=2")
    t("Agent different filter order",
      csv_gts["Task 0 (condos sale)"],
      "https://streeteasy.com/for-sale/manhattan/beds>=2|price:500000-1000000|type:D1")
    t("Agent with sort param",
      csv_gts["Task 0 (condos sale)"],
      "https://streeteasy.com/for-sale/manhattan/type:D1|price:500000-1000000|beds>=2?sort_by=se_score")

    # Task 1: Simple co-op
    print("\n📋 Task 1: Brooklyn co-ops under $700k")
    t("Agent exact match",
      csv_gts["Task 1 (co-ops sale)"],
      "https://streeteasy.com/for-sale/brooklyn/type:P1|price:-700000")
    t("Agent uses 'coop' name instead of P1",
      csv_gts["Task 1 (co-ops sale)"],
      "https://streeteasy.com/for-sale/brooklyn/type:coop|price:-700000")

    # Task 2: Amenities — KEY CROSS-FORMAT TEST
    print("\n📋 Task 2: Manhattan condos with doorman+elevator")
    t("Agent pipe-delimited (same as GT)",
      csv_gts["Task 2 (amenities sale)"],
      "https://streeteasy.com/for-sale/manhattan/type:D1|price:800000-2000000|amenities:doorman|amenities:elevator")
    t("Agent COMMA-SEPARATED (real StreetEasy format)",
      csv_gts["Task 2 (amenities sale)"],
      "https://streeteasy.com/for-sale/manhattan/type:D1|price:800000-2000000|amenities:doorman,elevator")
    t("Agent comma-separated REVERSED order",
      csv_gts["Task 2 (amenities sale)"],
      "https://streeteasy.com/for-sale/manhattan/type:D1|price:800000-2000000|amenities:elevator,doorman")

    # Task 3: Complex multi-filter with amenities
    print("\n📋 Task 3: Complex - condos/co-ops, pets, doorman+gym")
    t("Agent pipe-delimited (same as GT)",
      csv_gts["Task 3 (complex sale)"],
      "https://streeteasy.com/for-sale/manhattan/type:D1,P1|beds>=2|price:-1500000|pets:allowed|amenities:doorman|amenities:gym")
    t("Agent comma-separated amenities",
      csv_gts["Task 3 (complex sale)"],
      "https://streeteasy.com/for-sale/manhattan/type:D1,P1|beds>=2|price:-1500000|pets:allowed|amenities:doorman,gym")
    t("Agent reversed type codes P1,D1",
      csv_gts["Task 3 (complex sale)"],
      "https://streeteasy.com/for-sale/manhattan/type:P1,D1|beds>=2|price:-1500000|pets:allowed|amenities:doorman|amenities:gym")
    t("Agent reversed amenity order",
      csv_gts["Task 3 (complex sale)"],
      "https://streeteasy.com/for-sale/manhattan/type:D1,P1|beds>=2|price:-1500000|pets:allowed|amenities:gym,doorman")

    # Task 4: Rental with no_fee
    print("\n📋 Task 4: Manhattan no-fee rentals, 1+ bed, <$3500")
    t("Agent exact match",
      csv_gts["Task 4 (rental no-fee)"],
      "https://streeteasy.com/for-rent/manhattan/beds>=1|price:-3500|no_fee:1")
    t("Agent uses no_fee:true",
      csv_gts["Task 4 (rental no-fee)"],
      "https://streeteasy.com/for-rent/manhattan/beds>=1|price:-3500|no_fee:true")
    t("Agent uses no-fee:1 (hyphenated)",
      csv_gts["Task 4 (rental no-fee)"],
      "https://streeteasy.com/for-rent/manhattan/beds>=1|price:-3500|no-fee:1")

    # Task 5: Rental amenities
    print("\n📋 Task 5: Brooklyn rental, pets, in-unit laundry+doorman")
    t("Agent pipe-delimited (same as GT)",
      csv_gts["Task 5 (rental amenities)"],
      "https://streeteasy.com/for-rent/brooklyn/price:2000-4000|pets:allowed|amenities:in_unit_laundry|amenities:doorman")
    t("Agent comma-separated amenities",
      csv_gts["Task 5 (rental amenities)"],
      "https://streeteasy.com/for-rent/brooklyn/price:2000-4000|pets:allowed|amenities:in_unit_laundry,doorman")
    t("Agent uses washer_dryer alias",
      csv_gts["Task 5 (rental amenities)"],
      "https://streeteasy.com/for-rent/brooklyn/price:2000-4000|pets:allowed|amenities:washer_dryer|amenities:doorman")
    t("Agent comma with washer_dryer alias",
      csv_gts["Task 5 (rental amenities)"],
      "https://streeteasy.com/for-rent/brooklyn/price:2000-4000|pets:allowed|amenities:washer_dryer,doorman")

    # Task 6: Neighborhood
    print("\n📋 Task 6: Upper West Side condos, 3+ beds, 2+ baths")
    t("Agent exact match",
      csv_gts["Task 6 (neighborhood)"],
      "https://streeteasy.com/for-sale/manhattan/upper-west-side/type:D1|beds>=3|baths>=2")
    t("Agent different filter order",
      csv_gts["Task 6 (neighborhood)"],
      "https://streeteasy.com/for-sale/manhattan/upper-west-side/baths>=2|beds>=3|type:D1")

    # Task 7: Pre-war
    print("\n📋 Task 7: Pre-war co-ops, 1+ bed, <$600k")
    t("Agent exact match",
      csv_gts["Task 7 (prewar)"],
      "https://streeteasy.com/for-sale/manhattan/type:P1|beds>=1|price:-600000|prewar:1")
    t("Agent uses prewar:true",
      csv_gts["Task 7 (prewar)"],
      "https://streeteasy.com/for-sale/manhattan/type:P1|beds>=1|price:-600000|prewar:true")
    t("Agent uses pre-war:1",
      csv_gts["Task 7 (prewar)"],
      "https://streeteasy.com/for-sale/manhattan/type:P1|beds>=1|price:-600000|pre-war:1")
    t("Agent uses price abbreviation 600k",
      csv_gts["Task 7 (prewar)"],
      "https://streeteasy.com/for-sale/manhattan/type:P1|beds>=1|price:-600k|prewar:1")

    # Task 8: Sold status
    print("\n📋 Task 8: Sold condos $1M-$3M, 2+ beds")
    t("Agent exact match",
      csv_gts["Task 8 (sold status)"],
      "https://streeteasy.com/for-sale/manhattan/type:D1|price:1000000-3000000|beds>=2|status:sold")
    t("Agent price with abbreviations",
      csv_gts["Task 8 (sold status)"],
      "https://streeteasy.com/for-sale/manhattan/type:D1|price:1m-3m|beds>=2|status:sold")

    # Task 9: Transit — KEY CROSS-FORMAT TEST
    print("\n📋 Task 9: Brooklyn rental, L train, gym, no-fee, 2+ beds")
    t("Agent with subway:L (same as GT)",
      csv_gts["Task 9 (transit/subway)"],
      "https://streeteasy.com/for-rent/brooklyn/beds>=2|price:-4000|no_fee:1|subway:L|amenities:gym")
    t("Agent with transit_lines:L (REAL StreetEasy format)",
      csv_gts["Task 9 (transit/subway)"],
      "https://streeteasy.com/for-rent/brooklyn/beds>=2|price:-4000|no_fee:1|transit_lines:L|amenities:gym")
    t("Agent with transit_lines lowercase l",
      csv_gts["Task 9 (transit/subway)"],
      "https://streeteasy.com/for-rent/brooklyn/beds>=2|price:-4000|no_fee:1|transit_lines:l|amenities:gym")

    # ================================================================
    # PART 3: Negative Tests (MUST NOT MATCH)
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 3: Negative Tests (must NOT match)")
    print("=" * 70)

    t("Wrong search type (rent vs sale)",
      csv_gts["Task 0 (condos sale)"],
      "https://streeteasy.com/for-rent/manhattan/type:D1|price:500000-1000000|beds>=2",
      expected=False)
    t("Wrong borough (brooklyn vs manhattan)",
      csv_gts["Task 0 (condos sale)"],
      "https://streeteasy.com/for-sale/brooklyn/type:D1|price:500000-1000000|beds>=2",
      expected=False)
    t("Missing required filter (no beds)",
      csv_gts["Task 0 (condos sale)"],
      "https://streeteasy.com/for-sale/manhattan/type:D1|price:500000-1000000",
      expected=False)
    t("Wrong price range",
      csv_gts["Task 0 (condos sale)"],
      "https://streeteasy.com/for-sale/manhattan/type:D1|price:500000-2000000|beds>=2",
      expected=False)
    t("Wrong property type",
      csv_gts["Task 0 (condos sale)"],
      "https://streeteasy.com/for-sale/manhattan/type:P1|price:500000-1000000|beds>=2",
      expected=False)
    t("Missing neighborhood when GT has one",
      csv_gts["Task 6 (neighborhood)"],
      "https://streeteasy.com/for-sale/manhattan/type:D1|beds>=3|baths>=2",
      expected=False)
    t("Wrong neighborhood",
      csv_gts["Task 6 (neighborhood)"],
      "https://streeteasy.com/for-sale/manhattan/east-village/type:D1|beds>=3|baths>=2",
      expected=False)
    t("Wrong subway line",
      csv_gts["Task 9 (transit/subway)"],
      "https://streeteasy.com/for-rent/brooklyn/beds>=2|price:-4000|no_fee:1|subway:A|amenities:gym",
      expected=False)
    t("Missing amenity",
      csv_gts["Task 2 (amenities sale)"],
      "https://streeteasy.com/for-sale/manhattan/type:D1|price:800000-2000000|amenities:doorman",
      expected=False)

    # ================================================================
    # PART 4: Edge Cases
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 4: Edge Cases")
    print("=" * 70)

    # URL encoding
    t("URL-encoded pipes (%7C)",
      csv_gts["Task 0 (condos sale)"],
      "https://streeteasy.com/for-sale/manhattan/type:D1%7Cprice:500000-1000000%7Cbeds%3E=2")

    # Case insensitivity
    t("Uppercase borough",
      csv_gts["Task 0 (condos sale)"],
      "https://streeteasy.com/for-sale/Manhattan/type:D1|price:500000-1000000|beds>=2")

    # www prefix
    t("www prefix",
      csv_gts["Task 0 (condos sale)"],
      "https://www.streeteasy.com/for-sale/manhattan/type:D1|price:500000-1000000|beds>=2")

    # http instead of https
    t("HTTP instead of HTTPS",
      csv_gts["Task 0 (condos sale)"],
      "http://streeteasy.com/for-sale/manhattan/type:D1|price:500000-1000000|beds>=2")

    # Extra filters in agent (should still match)
    t("Agent has extra sqft filter",
      csv_gts["Task 0 (condos sale)"],
      "https://streeteasy.com/for-sale/manhattan/type:D1|price:500000-1000000|beds>=2|sqft:750-")

    # Multiple transit lines
    t("Multiple transit lines comma-separated",
      csv_gts["Task 9 (transit/subway)"],
      "https://streeteasy.com/for-rent/brooklyn/beds>=2|price:-4000|no_fee:1|transit_lines:L|amenities:gym",
      expected=True)

    # ================================================================
    # PART 5: Amenity Alias Cross-Matching
    # ================================================================
    print("\n" + "=" * 70)
    print("PART 5: Amenity Alias Cross-Matching")
    print("=" * 70)

    t("washer_dryer → in_unit_laundry alias",
      "https://streeteasy.com/for-rent/brooklyn/amenities:in_unit_laundry",
      "https://streeteasy.com/for-rent/brooklyn/amenities:washer_dryer")

    t("fitness → gym alias",
      "https://streeteasy.com/for-rent/brooklyn/amenities:gym",
      "https://streeteasy.com/for-rent/brooklyn/amenities:fitness")

    t("laundry_in_building → laundry alias",
      "https://streeteasy.com/for-rent/brooklyn/amenities:laundry",
      "https://streeteasy.com/for-rent/brooklyn/amenities:laundry_in_building")

    t("Comma amenities with aliases",
      "https://streeteasy.com/for-rent/brooklyn/amenities:gym|amenities:doorman",
      "https://streeteasy.com/for-rent/brooklyn/amenities:fitness,doorman")

    t("Comma amenities both sides with alias",
      "https://streeteasy.com/for-rent/brooklyn/amenities:in_unit_laundry,doorman",
      "https://streeteasy.com/for-rent/brooklyn/amenities:washer_dryer,doorman")

    # ================================================================
    # RESULTS
    # ================================================================
    print("\n" + "=" * 70)
    color = "🟢" if passed == total else "🔴"
    print(f"{color} RESULTS: {passed}/{total} tests passed")
    print("=" * 70)

    if passed < total:
        print(f"\n⚠️  {total - passed} FAILURES detected!")
        return 1
    else:
        print("\n✅ All tests passed! Verifier is robust.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
