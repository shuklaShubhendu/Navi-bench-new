"""
Deep audit stress tests for StreetEasy verifier.
Tests every potential edge case found during manual code review.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from navi_bench.streeteasy.streeteasy_url_match import StreetEasyUrlMatch

passed = 0
failed = 0

def test(name, agent_url, gt_url, expected):
    global passed, failed
    v = StreetEasyUrlMatch(gt_url=gt_url)
    match, details = v._urls_match(agent_url, gt_url)
    if match == expected:
        passed += 1
    else:
        failed += 1
        print(f"FAIL: {name}")
        print(f"  agent: {agent_url}")
        print(f"  gt:    {gt_url}")
        print(f"  expected={expected}, got={match}, details={details}")

print("=" * 70)
print("DEEP AUDIT STRESS TESTS")
print("=" * 70)

# ================================================================
# 1. beds>=2 vs beds:2- interop (>= converts to range format "2-")
# ================================================================
print("\n--- beds>=N normalization ---")
test("beds>=2 self-match",
    "https://streeteasy.com/for-sale/manhattan/beds>=2",
    "https://streeteasy.com/for-sale/manhattan/beds>=2", True)

test("beds>=2 vs beds:2 should NOT match (different semantics)",
    "https://streeteasy.com/for-sale/manhattan/beds>=2",
    "https://streeteasy.com/for-sale/manhattan/beds:2", False)

test("beds:2 exact self-match",
    "https://streeteasy.com/for-sale/manhattan/beds:2",
    "https://streeteasy.com/for-sale/manhattan/beds:2", True)

test("beds:2-3 range self-match",
    "https://streeteasy.com/for-sale/manhattan/beds:2-3",
    "https://streeteasy.com/for-sale/manhattan/beds:2-3", True)

# ================================================================
# 2. no_fee in AMENITY_ALIASES shadows no_fee as filter key
# ================================================================
print("\n--- no_fee as filter vs amenity ---")
test("no_fee:1 as filter key (standard)",
    "https://streeteasy.com/for-rent/manhattan/no_fee:1",
    "https://streeteasy.com/for-rent/manhattan/no_fee:1", True)

test("no-fee:1 alias",
    "https://streeteasy.com/for-rent/manhattan/no-fee:1",
    "https://streeteasy.com/for-rent/manhattan/no_fee:1", True)

test("no_fee:true vs no_fee:1 (boolean equiv)",
    "https://streeteasy.com/for-rent/manhattan/no_fee:true",
    "https://streeteasy.com/for-rent/manhattan/no_fee:1", True)

# no_fee as amenity (amenities:no_fee should not conflict with no_fee filter)
test("amenities:no_fee is separate from no_fee filter",
    "https://streeteasy.com/for-rent/manhattan/amenities:no_fee",
    "https://streeteasy.com/for-rent/manhattan/no_fee:1", False)

# ================================================================
# 3. transit_lines vs subway cross-matching  
# ================================================================
print("\n--- transit_lines / subway cross-matching ---")
test("transit_lines:L matches subway:L",
    "https://streeteasy.com/for-rent/brooklyn/transit_lines:L",
    "https://streeteasy.com/for-rent/brooklyn/subway:L", True)

test("subway:L matches transit_lines:L (reverse)",
    "https://streeteasy.com/for-rent/brooklyn/subway:L",
    "https://streeteasy.com/for-rent/brooklyn/transit_lines:L", True)

test("transit_lines:ACE self-match",
    "https://streeteasy.com/for-rent/manhattan/transit_lines:ACE",
    "https://streeteasy.com/for-rent/manhattan/transit_lines:ACE", True)

test("subway:l vs transit_lines:L (case insensitive)",
    "https://streeteasy.com/for-rent/brooklyn/subway:l",
    "https://streeteasy.com/for-rent/brooklyn/transit_lines:L", True)

# ================================================================
# 4. Comma-separated amenities: order + aliases
# ================================================================
print("\n--- comma amenities edge cases ---")
test("amenities:gym,doorman vs amenities:doorman,gym (order)",
    "https://streeteasy.com/for-sale/manhattan/amenities:gym,doorman",
    "https://streeteasy.com/for-sale/manhattan/amenities:doorman,gym", True)

test("amenities:washer_dryer vs amenities:in_unit_laundry (alias)",
    "https://streeteasy.com/for-rent/brooklyn/amenities:washer_dryer",
    "https://streeteasy.com/for-rent/brooklyn/amenities:in_unit_laundry", True)

test("amenities:doorman,washer_dryer vs amenities:in_unit_laundry,doorman (alias+order)",
    "https://streeteasy.com/for-rent/brooklyn/amenities:doorman,washer_dryer",
    "https://streeteasy.com/for-rent/brooklyn/amenities:in_unit_laundry,doorman", True)

# Pipe-separated amenities merged into single key
test("amenities:doorman|amenities:gym vs amenities:doorman,gym (pipe vs comma)",
    "https://streeteasy.com/for-sale/manhattan/amenities:doorman|amenities:gym",
    "https://streeteasy.com/for-sale/manhattan/amenities:doorman,gym", True)

test("amenities:gym|amenities:doorman vs amenities:doorman,gym (reversed pipe)",
    "https://streeteasy.com/for-sale/manhattan/amenities:gym|amenities:doorman",
    "https://streeteasy.com/for-sale/manhattan/amenities:doorman,gym", True)

# Triple amenities
test("triple amenities: gym,pool,doorman vs doorman,gym,pool (all orders)",
    "https://streeteasy.com/for-sale/manhattan/amenities:gym,pool,doorman",
    "https://streeteasy.com/for-sale/manhattan/amenities:doorman,gym,pool", True)

test("triple amenities pipe vs comma: amenities:gym|amenities:pool|amenities:doorman",
    "https://streeteasy.com/for-sale/manhattan/amenities:gym|amenities:pool|amenities:doorman",
    "https://streeteasy.com/for-sale/manhattan/amenities:doorman,gym,pool", True)

# ================================================================
# 5. Neighborhood cross-format
# ================================================================
print("\n--- neighborhood cross-format ---")
test("upper-west-side as location vs manhattan/upper-west-side",
    "https://streeteasy.com/for-sale/upper-west-side/type:D1",
    "https://streeteasy.com/for-sale/manhattan/upper-west-side/type:D1", True)

test("manhattan/upper-west-side vs upper-west-side (reverse)",
    "https://streeteasy.com/for-sale/manhattan/upper-west-side/type:D1",
    "https://streeteasy.com/for-sale/upper-west-side/type:D1", True)

test("brooklyn/williamsburg vs williamsburg",
    "https://streeteasy.com/for-sale/brooklyn/williamsburg/type:D1",
    "https://streeteasy.com/for-sale/williamsburg/type:D1", True)

test("wrong neighborhood must fail",
    "https://streeteasy.com/for-sale/upper-west-side/type:D1",
    "https://streeteasy.com/for-sale/east-village/type:D1", False)

test("borough vs neighborhood must fail",
    "https://streeteasy.com/for-sale/manhattan",
    "https://streeteasy.com/for-sale/upper-west-side", False)

# ================================================================
# 6. URL encoding equivalence
# ================================================================
print("\n--- URL encoding ---")
test("encoded pipes %7C vs raw |",
    "https://streeteasy.com/for-sale/manhattan/type:D1%7Cprice:500000-1000000%7Cbeds%3E=2",
    "https://streeteasy.com/for-sale/manhattan/type:D1|price:500000-1000000|beds>=2", True)

# ================================================================
# 7. Price edge cases
# ================================================================
print("\n--- price edge cases ---")
test("price:-500000 (max only)",
    "https://streeteasy.com/for-sale/bronx/price:-500000",
    "https://streeteasy.com/for-sale/bronx/price:-500000", True)

test("price:5000000- (min only, open end)",
    "https://streeteasy.com/for-sale/manhattan/price:5000000-",
    "https://streeteasy.com/for-sale/manhattan/price:5000000-", True)

test("price:500k vs price:500000",
    "https://streeteasy.com/for-sale/manhattan/price:500k-1m",
    "https://streeteasy.com/for-sale/manhattan/price:500000-1000000", True)

test("price $1,500,000 with commas",
    "https://streeteasy.com/for-sale/manhattan/price:1,500,000-2,000,000",
    "https://streeteasy.com/for-sale/manhattan/price:1500000-2000000", True)

# ================================================================
# 8. Multi-value type codes
# ================================================================
print("\n--- multi-value type codes ---")
test("type:D1,P1 vs type:P1,D1 (order independence)",
    "https://streeteasy.com/for-sale/manhattan/type:D1,P1",
    "https://streeteasy.com/for-sale/manhattan/type:P1,D1", True)

test("type:condo vs type:D1 (human-readable)",
    "https://streeteasy.com/for-sale/manhattan/type:condo",
    "https://streeteasy.com/for-sale/manhattan/type:D1", True)

test("type:condo,coop vs type:D1,P1 (human-readable combo)",
    "https://streeteasy.com/for-sale/manhattan/type:condo,coop",
    "https://streeteasy.com/for-sale/manhattan/type:D1,P1", True)

# ================================================================
# 9. Extra filters in agent (should still match)
# ================================================================
print("\n--- extra filters tolerance ---")
test("agent has extra filter, GT subset matches",
    "https://streeteasy.com/for-sale/manhattan/type:D1|beds>=2|amenities:gym",
    "https://streeteasy.com/for-sale/manhattan/type:D1|beds>=2", True)

test("GT has extra filter, agent missing = FAIL",
    "https://streeteasy.com/for-sale/manhattan/type:D1",
    "https://streeteasy.com/for-sale/manhattan/type:D1|beds>=2", False)

# ================================================================
# 10. Boolean true/1/yes matching
# ================================================================
print("\n--- boolean matching ---")
test("no_fee:yes vs no_fee:1",
    "https://streeteasy.com/for-rent/manhattan/no_fee:yes",
    "https://streeteasy.com/for-rent/manhattan/no_fee:1", True)

test("furnished:true vs furnished:1",
    "https://streeteasy.com/for-rent/manhattan/furnished:true",
    "https://streeteasy.com/for-rent/manhattan/furnished:1", True)

test("prewar:true vs prewar:1",
    "https://streeteasy.com/for-sale/manhattan/prewar:true",
    "https://streeteasy.com/for-sale/manhattan/prewar:1", True)

# ================================================================
# 11. Complex real-world scenarios
# ================================================================
print("\n--- complex real-world scenarios ---")
test("Full rental with transit + no_fee + amenities + pets",
    "https://streeteasy.com/for-rent/brooklyn/transit_lines:L|no_fee:1|beds>=2|amenities:gym,doorman|pets:allowed|price:-4000",
    "https://streeteasy.com/for-rent/brooklyn/subway:L|no_fee:1|beds>=2|amenities:doorman,gym|pets:allowed|price:-4000", True)

test("Full sale with neighborhood + prewar + type + amenities",
    "https://streeteasy.com/for-sale/upper-west-side/type:P1|prewar:1|amenities:doorman,elevator|beds>=3|price:1000000-3000000",
    "https://streeteasy.com/for-sale/manhattan/upper-west-side/type:coop|pre-war:true|amenities:elevator,doorman|beds>=3|price:1m-3m", True)

test("Sold with all cross-format differences",
    "https://streeteasy.com/for-sale/upper-east-side/status:sold|type:condo|price:2m-5m|beds>=3",
    "https://streeteasy.com/for-sale/manhattan/upper-east-side/status:sold|type:D1|price:2000000-5000000|beds>=3", True)

# ================================================================
# SUMMARY
# ================================================================
print("\n" + "=" * 70)
total = passed + failed
if failed == 0:
    print(f"ALL {total} DEEP AUDIT TESTS PASSED")
else:
    print(f"RESULT: {passed}/{total} passed, {failed} FAILED")
print("=" * 70)
