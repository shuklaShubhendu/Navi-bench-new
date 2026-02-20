import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from navi_bench.streeteasy.streeteasy_url_match import StreetEasyUrlMatch

url = "https://streeteasy.com/for-sale/manhattan/type:D1%7Cnew_developments:new%20development?sort_by=se_score"

evaluator = StreetEasyUrlMatch(url)

# Test 1: self-match
match, details = evaluator._urls_match(url, url)
print(f"1. Self-match: {match}")
if details.get("mismatches"):
    print(f"   Mismatches: {details['mismatches']}")
print()

# Test 2: vs new_development:1 (our canonical form)
gt = "https://streeteasy.com/for-sale/manhattan/type:D1|new_development:1"
match2, details2 = evaluator._urls_match(url, gt)
print(f"2. new_developments:new development vs new_development:1: {match2}")
if details2.get("mismatches"):
    print(f"   Mismatches: {details2['mismatches']}")
print()

# Test 3: vs new_development:yes
gt3 = "https://streeteasy.com/for-sale/manhattan/type:D1|new_development:yes"
match3, details3 = evaluator._urls_match(url, gt3)
print(f"3. new_developments:new development vs new_development:yes: {match3}")
if details3.get("mismatches"):
    print(f"   Mismatches: {details3['mismatches']}")
print()

# Test 4: parse to see what it normalizes to
parsed = evaluator._parse_streeteasy_url(url)
print(f"4. Normalized parse:")
print(f"   search_type: {parsed['search_type']}")
print(f"   location: {parsed['location']}")
for k, v in sorted(parsed["filters"].items()):
    print(f"   {k}: {v}")
