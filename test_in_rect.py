"""Test that in_rect map filter is correctly ignored."""
import sys; sys.stderr = open('NUL', 'w')
from navi_bench.streeteasy.streeteasy_url_match import StreetEasyUrlMatch

gt = "https://streeteasy.com/for-rent/manhattan/price:-3500|beds:1"
agent_with_rect = "https://streeteasy.com/for-rent/manhattan/price:-3500%7Cbeds:1%7Cin_rect:40.761,40.797,-73.99,-73.921?sort_by=se_score"
agent_no_rect = "https://streeteasy.com/for-rent/manhattan/price:-3500|beds:1?sort_by=se_score"

v = StreetEasyUrlMatch(gt_url=gt)

# Test 1: Parse the URL with in_rect to see what filters we get
parsed = v._parse_streeteasy_url(agent_with_rect)
print("Parsed agent_with_rect:")
print(f"  search_type: {parsed['search_type']}")
print(f"  location: {parsed['location']}")
print(f"  filters: {parsed['filters']}")

# Test 2: Parse GT
parsed_gt = v._parse_streeteasy_url(gt)
print(f"\nParsed GT:")
print(f"  filters: {parsed_gt['filters']}")

# Test 3: Match without in_rect
m1, d1 = v._urls_match(agent_no_rect, gt)
print(f"\nWithout in_rect: match={m1} details={d1}")

# Test 4: Match WITH in_rect (should be same result)
m2, d2 = v._urls_match(agent_with_rect, gt)
print(f"With in_rect:    match={m2} details={d2}")

# Test 5: Both sides have in_rect
both_rect = "https://streeteasy.com/for-rent/manhattan/price:-3500|beds:1|in_rect:40.761,40.797,-73.99,-73.921"
m3, d3 = v._urls_match(both_rect, both_rect)
print(f"Both have rect:  match={m3}")
