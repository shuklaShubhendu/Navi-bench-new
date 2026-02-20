import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from navi_bench.streeteasy.streeteasy_url_match import StreetEasyUrlMatch

url = "https://streeteasy.com/for-sale/manhattan/type:D1%7Cprice:1000000-3000000%7Cbeds:1-2%7Cpre_war:yes%7Camenities:doorman?sort_by=se_score"

evaluator = StreetEasyUrlMatch(url)

# Test 1: self-match
match, details = evaluator._urls_match(url, url)
print(f"1. Self-match: {match}")
if details.get("mismatches"):
    print(f"   Mismatches: {details['mismatches']}")
print()

# Test 2: vs canonical form (prewar:1 instead of pre_war:yes, same beds:1-2)
gt = "https://streeteasy.com/for-sale/manhattan/type:D1|price:1000000-3000000|beds:1-2|prewar:1|amenities:doorman"
match2, details2 = evaluator._urls_match(url, gt)
print(f"2. vs canonical (prewar:1): {match2}")
if details2.get("mismatches"):
    print(f"   Mismatches: {details2['mismatches']}")
print()

# Test 3: vs prewar:yes directly
gt3 = "https://streeteasy.com/for-sale/manhattan/type:D1|price:1000000-3000000|beds:1-2|prewar:yes|amenities:doorman"
match3, details3 = evaluator._urls_match(url, gt3)
print(f"3. vs prewar:yes: {match3}")
print()

# Test 4: beds:1-2 vs beds>=1 (should NOT match — different semantics)
gt4 = "https://streeteasy.com/for-sale/manhattan/type:D1|price:1000000-3000000|beds>=1|prewar:1|amenities:doorman"
match4, details4 = evaluator._urls_match(url, gt4)
print(f"4. beds:1-2 vs beds>=1 (should NOT match): {match4}")
if details4.get("mismatches"):
    print(f"   Mismatches: {details4['mismatches']}")
print()

# Test 5: beds:1-2 vs beds:2-3 (should NOT match)
gt5 = "https://streeteasy.com/for-sale/manhattan/type:D1|price:1000000-3000000|beds:2-3|prewar:1|amenities:doorman"
match5, details5 = evaluator._urls_match(url, gt5)
print(f"5. beds:1-2 vs beds:2-3 (should NOT match): {match5}")
if details5.get("mismatches"):
    print(f"   Mismatches: {details5['mismatches']}")
print()

# Test 6: parse to see normalized filters
parsed = evaluator._parse_streeteasy_url(url)
print(f"6. Normalized parse:")
print(f"   search_type: {parsed['search_type']}")
print(f"   location: {parsed['location']}")
for k, v in sorted(parsed["filters"].items()):
    print(f"   {k}: {v}")
