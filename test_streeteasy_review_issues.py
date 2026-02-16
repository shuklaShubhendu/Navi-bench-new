"""
Targeted tests for each of the 13 issues flagged in the code review.
For each issue: test if the bug ACTUALLY exists in the current code.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from navi_bench.streeteasy.streeteasy_url_match import StreetEasyUrlMatch

results = []

def test(issue_num, name, gt_url, agent_url, expected_match, detail=""):
    v = StreetEasyUrlMatch(gt_url=gt_url)
    match, details = v._urls_match(agent_url, gt_url)
    passed = match == expected_match
    status = "PASS" if passed else "FAIL"
    icon = "  " if passed else ">>"
    print(f"  {icon}[{status}] Issue #{issue_num}: {name}")
    if not passed:
        print(f"          Expected match={expected_match}, got match={match}")
        print(f"          Details: {details}")
        if detail:
            print(f"          Context: {detail}")
    results.append(passed)
    return passed

def parse_test(issue_num, name, url, check_fn, detail=""):
    """Parse a URL and run a check function on the result."""
    v = StreetEasyUrlMatch(gt_url=url)
    parsed = v._parse_streeteasy_url(url)
    passed = check_fn(parsed)
    status = "PASS" if passed else "FAIL"
    icon = "  " if passed else ">>"
    print(f"  {icon}[{status}] Issue #{issue_num}: {name}")
    if not passed:
        print(f"          Parsed: {parsed}")
        if detail:
            print(f"          Context: {detail}")
    results.append(passed)
    return passed


# ============================================================================
print("=" * 70)
print("STREETEASY CODE REVIEW — ISSUE VERIFICATION")
print("=" * 70)

# ============================================================================
# ISSUE #1: Range Filter Parsing Bug
# Review says: beds>=2 becomes "2-" but _filter_values_match doesn't handle it
# ============================================================================
print("\n--- ISSUE #1: Range Filter Parsing (beds>=2 → beds:2-) ---")

# Test: beds>=2 in GT should match beds>=2 in agent (self-match)
test(1, "beds>=2 self-match",
     "https://streeteasy.com/for-sale/manhattan/beds>=2",
     "https://streeteasy.com/for-sale/manhattan/beds>=2",
     True)

# Test: beds>=2 vs beds:2 (are they treated as equivalent?)
test(1, "beds>=2 vs beds:2 (should they match?)",
     "https://streeteasy.com/for-sale/manhattan/beds>=2",
     "https://streeteasy.com/for-sale/manhattan/beds:2",
     False,  # These are DIFFERENT: "2-" (min 2+) vs "2" (exactly 2)
     ">=2 means 'at least 2' (range 2-), beds:2 means 'exactly 2'")

# Test: beds>=2 parses to what value?
parse_test(1, "beds>=2 parsed value",
     "https://streeteasy.com/for-sale/manhattan/beds>=2",
     lambda p: p["filters"].get("beds") == "2-",
     "Should be '2-' indicating min=2, no max")

# Test: beds:2 parses to what value?
parse_test(1, "beds:2 parsed value",
     "https://streeteasy.com/for-sale/manhattan/beds:2",
     lambda p: p["filters"].get("beds") == "2",
     "Should be '2' (exact)")

# Test: beds:2- vs beds>=2 (these SHOULD match — same semantics)
test(1, "beds:2- vs beds>=2 (same semantics)",
     "https://streeteasy.com/for-sale/manhattan/beds:2-",
     "https://streeteasy.com/for-sale/manhattan/beds>=2",
     True,
     "Both mean 'at least 2 beds'")


# ============================================================================
# ISSUE #2: Incomplete Multi-Value Filter Merging (subway:L|subway:1)
# Review says: pipe-delimited duplicate keys would overwrite each other
# ============================================================================
print("\n--- ISSUE #2: Multi-Value Filter Merging (subway:L|subway:1) ---")

# Test: Multiple subway lines merge correctly
parse_test(2, "subway:L|subway:1 merged",
     "https://streeteasy.com/for-rent/manhattan/subway:L|subway:1",
     lambda p: "subway" in p["filters"] and set(p["filters"]["subway"].split(",")) == {"L", "1"},
     "Should merge into comma-separated: '1,L'")

# Test: Multiple amenities merge correctly  
parse_test(2, "amenities:doorman|amenities:elevator merged",
     "https://streeteasy.com/for-sale/manhattan/amenities:doorman|amenities:elevator",
     lambda p: "amenities" in p["filters"] and set(p["filters"]["amenities"].split(",")) == {"doorman", "elevator"},
     "Should merge into comma-separated: 'doorman,elevator'")

# Test: subway:1|subway:2|subway:3 — order independent matching
test(2, "3 subway lines order independent",
     "https://streeteasy.com/for-rent/manhattan/subway:1|subway:2|subway:3",
     "https://streeteasy.com/for-rent/manhattan/subway:3|subway:1|subway:2",
     True)


# ============================================================================
# ISSUE #3: Amenities Prefix Inconsistency
# Review says: multiple amenities use separate pipe-delimited filters, not
# one filter with multiple values
# ============================================================================
print("\n--- ISSUE #3: Amenities Prefix (multiple amenities handling) ---")

# Test: Doorman + elevator combo match
test(3, "doorman + elevator combo match",
     "https://streeteasy.com/for-sale/manhattan/amenities:doorman|amenities:elevator",
     "https://streeteasy.com/for-sale/manhattan/amenities:doorman|amenities:elevator",
     True)

# Test: doorman + elevator (reversed order)
test(3, "doorman + elevator reversed order",
     "https://streeteasy.com/for-sale/manhattan/amenities:doorman|amenities:elevator",
     "https://streeteasy.com/for-sale/manhattan/amenities:elevator|amenities:doorman",
     True)

# Test: Missing one amenity should fail
test(3, "Missing elevator should fail",
     "https://streeteasy.com/for-sale/manhattan/amenities:doorman|amenities:elevator",
     "https://streeteasy.com/for-sale/manhattan/amenities:doorman",
     False,
     "GT requires both doorman AND elevator")


# ============================================================================
# ISSUE #4: Boolean Value Comparison Flaw
# Review says: returns False for identical non-boolean values
# ============================================================================
print("\n--- ISSUE #4: Boolean Value Comparison ---")

# Test: identical non-boolean values match 
test(4, "Identical non-bool 'sold' matches",
     "https://streeteasy.com/for-sale/manhattan/status:sold",
     "https://streeteasy.com/for-sale/manhattan/status:sold",
     True)

# Test: boolean true vs 1
test(4, "no_fee:1 vs no_fee:true (boolean equiv)",
     "https://streeteasy.com/for-rent/manhattan/no_fee:1",
     "https://streeteasy.com/for-rent/manhattan/no_fee:true",
     True)

# Test: boolean yes vs 1
test(4, "no_fee:1 vs no_fee:yes (boolean equiv)",
     "https://streeteasy.com/for-rent/manhattan/no_fee:1",
     "https://streeteasy.com/for-rent/manhattan/no_fee:yes",
     True)

# Test: two non-boolean strings that are different
test(4, "status:sold vs status:open (diff values)",
     "https://streeteasy.com/for-sale/manhattan/status:sold",
     "https://streeteasy.com/for-sale/manhattan/status:open",
     False)


# ============================================================================
# ISSUE #5: Neighborhood Comparison Asymmetry
# Review says: agent can have a neighborhood when GT doesn't, but not vice versa
# ============================================================================
print("\n--- ISSUE #5: Neighborhood Comparison Asymmetry ---")

# Test: GT has neighborhood, agent doesn't → should fail
test(5, "GT has neighborhood, agent doesn't → FAIL",
     "https://streeteasy.com/for-sale/manhattan/upper-west-side/beds:2",
     "https://streeteasy.com/for-sale/manhattan/beds:2",
     False)

# Test: Agent has neighborhood, GT doesn't → intentionally OK
test(5, "Agent has extra neighborhood, GT doesn't → OK (more specific)",
     "https://streeteasy.com/for-sale/manhattan/beds:2",
     "https://streeteasy.com/for-sale/manhattan/upper-west-side/beds:2",
     True,
     "Agent is more specific — intentional design: more specific ≥ required")


# ============================================================================
# ISSUE #6: Extra Filters Are Noted But Don't Fail
# Review says: overly restrictive searches pass when they shouldn't
# ============================================================================
print("\n--- ISSUE #6: Extra Filters Don't Fail ---")

# Test: Agent has extra filter beyond GT requirements → OK
test(6, "Agent has extra beds filter → OK (superset)",
     "https://streeteasy.com/for-sale/manhattan/price:500000-",
     "https://streeteasy.com/for-sale/manhattan/price:500000-|beds:2",
     True,
     "Agent added extra filter — intentional design: meet or exceed GT")

# Test: Agent is missing GT filter → FAIL
test(6, "Agent missing GT filter → FAIL",
     "https://streeteasy.com/for-sale/manhattan/price:500000-|beds:2",
     "https://streeteasy.com/for-sale/manhattan/price:500000-",
     False)


# ============================================================================
# ISSUE #7: Price Abbreviation Edge Cases
# ============================================================================
print("\n--- ISSUE #7: Price Abbreviation Edge Cases ---")

# Test: 1.5m
test(7, "1.5m matches 1500000",
     "https://streeteasy.com/for-sale/manhattan/price:1500000-",
     "https://streeteasy.com/for-sale/manhattan/price:1.5m-",
     True)

# Test: 1.5k
test(7, "1.5k matches 1500",
     "https://streeteasy.com/for-rent/manhattan/price:1500-",
     "https://streeteasy.com/for-rent/manhattan/price:1.5k-",
     True)

# Test: Invalid abbreviation fails gracefully
parse_test(7, "Invalid price 'abc' doesn't crash",
     "https://streeteasy.com/for-sale/manhattan/price:abc-",
     lambda p: "price" in p["filters"],
     "Should not crash on invalid price")


# ============================================================================
# ISSUE #9: Pipe-Delimited Same-Key Filters
# ============================================================================
print("\n--- ISSUE #9: Pipe-Delimited Same-Key Subway Filters ---")

# Test: subway:1|subway:2|subway:3 all merge
parse_test(9, "subway:1|subway:2|subway:3 → merged value",
     "https://streeteasy.com/for-rent/manhattan/subway:1|subway:2|subway:3",
     lambda p: "subway" in p["filters"] and len(p["filters"]["subway"].split(",")) == 3,
     "All 3 subway values should be merged")

# Test: subway:1|subway:2 matches subway:2|subway:1
test(9, "Subway order independence",
     "https://streeteasy.com/for-rent/manhattan/subway:1|subway:2",
     "https://streeteasy.com/for-rent/manhattan/subway:2|subway:1",
     True)


# ============================================================================
# ISSUE #10: Query Parameter Handling (IGNORED_QUERY_PARAMS actually used?)
# ============================================================================
print("\n--- ISSUE #10: Query Parameter Handling ---")

# Test: sort_by param should be ignored
test(10, "sort_by=se_score ignored",
     "https://streeteasy.com/for-sale/manhattan/beds:2",
     "https://streeteasy.com/for-sale/manhattan/beds:2?sort_by=se_score",
     True)

# Test: page param should be ignored
test(10, "page=2 ignored",
     "https://streeteasy.com/for-sale/manhattan/beds:2",
     "https://streeteasy.com/for-sale/manhattan/beds:2?page=2",
     True)

# Test: Different sort_by values still match
test(10, "Different sort values still match",
     "https://streeteasy.com/for-sale/manhattan/beds:2?sort_by=price_asc",
     "https://streeteasy.com/for-sale/manhattan/beds:2?sort_by=price_desc",
     True)


# ============================================================================
# ISSUE #11: Error Handling (GT URL validated early?)
# ============================================================================
print("\n--- ISSUE #11: Error Handling ---")

# Test: Malformed URL doesn't crash
try:
    v = StreetEasyUrlMatch(gt_url="not-a-url")
    match, details = v._urls_match("not-a-url", "not-a-url")
    print(f"  [PASS] Issue #11: Malformed URL doesn't crash (match={match})")
    results.append(True)
except Exception as e:
    print(f"  [FAIL] Issue #11: Malformed URL crashed: {e}")
    results.append(False)


# ============================================================================
# ISSUE #12: Immutable State Violation (update called multiple times)
# ============================================================================
print("\n--- ISSUE #12: State Management ---")

import asyncio

async def test_state():
    v = StreetEasyUrlMatch(gt_url="https://streeteasy.com/for-sale/manhattan/beds:2")
    
    # First update with wrong URL
    await v.update(url="https://streeteasy.com/for-sale/manhattan/beds:3")
    result1 = await v.compute()
    
    # Second update with correct URL (should now match)
    await v.update(url="https://streeteasy.com/for-sale/manhattan/beds:2")
    result2 = await v.compute()
    
    passed = result1.score == 0.0 and result2.score == 1.0
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] Issue #12: Multiple updates work (first=0, second=1)")
    if not passed:
        print(f"          First: {result1.score}, Second: {result2.score}")
    results.append(passed)
    
    # Test reset
    await v.reset()
    result3 = await v.compute()
    passed2 = result3.score == 0.0
    status2 = "PASS" if passed2 else "FAIL"
    print(f"  [{status2}] Issue #12: Reset clears state (score=0 after reset)")
    results.append(passed2)

asyncio.run(test_state())


# ============================================================================
# ISSUE #13: Type Normalization Ambiguity (unknown codes pass through)
# ============================================================================
print("\n--- ISSUE #13: Type Normalization ---")

# Test: Unknown type code passes through
parse_test(13, "Unknown type code Z9 passes through",
     "https://streeteasy.com/for-sale/manhattan/type:Z9",
     lambda p: p["filters"].get("type") == "Z9",
     "Unknown codes should pass through unchanged")

# Verify known codes work
parse_test(13, "D1 → D1 (condo)",
     "https://streeteasy.com/for-sale/manhattan/type:D1",
     lambda p: p["filters"].get("type") == "D1")

parse_test(13, "condo → D1",
     "https://streeteasy.com/for-sale/manhattan/type:condo",
     lambda p: p["filters"].get("type") == "D1")


# ============================================================================
# EXTRA: Test the critical beds>=2 vs beds:2- cross-match
# ============================================================================
print("\n--- EXTRA: Critical Cross-Format Tests ---")

# The key scenario: agent uses beds:2- (range), GT has beds>=2 (comparison)
# After parsing, both should become beds:2- → direct string match
test("X", "beds:2- (explicit range) vs beds>=2 (parsed to 2-)",
     "https://streeteasy.com/for-sale/manhattan/beds>=2",
     "https://streeteasy.com/for-sale/manhattan/beds:2-",
     True)

# Multiple amenities: GT has 3, agent has all 3 in different order
test("X", "3 amenities order-independent",
     "https://streeteasy.com/for-sale/manhattan/amenities:doorman|amenities:elevator|amenities:gym",
     "https://streeteasy.com/for-sale/manhattan/amenities:gym|amenities:doorman|amenities:elevator",
     True)

# Missing one of 3 amenities should fail
test("X", "Missing 1 of 3 amenities → FAIL",
     "https://streeteasy.com/for-sale/manhattan/amenities:doorman|amenities:elevator|amenities:gym",
     "https://streeteasy.com/for-sale/manhattan/amenities:doorman|amenities:elevator",
     False)


# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
passed = sum(results)
total = len(results)
failed = total - passed
print(f"RESULTS: {passed}/{total} tests passed ({100*passed/total:.1f}%)")
if failed > 0:
    print(f"FAILURES: {failed} tests FAILED — BUGS CONFIRMED")
else:
    print("ALL TESTS PASSED — No real bugs found")
print("=" * 70)
