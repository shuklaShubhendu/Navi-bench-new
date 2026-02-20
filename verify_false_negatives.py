"""Full self-match test for all 70 tasks, plus edge case tests."""
import sys, io, csv, json
sys.stderr = io.StringIO()
from urllib.parse import unquote
from navi_bench.streeteasy.streeteasy_url_match import StreetEasyUrlMatch

with open(r'c:\Users\HP\Desktop\navi-fev\navi_bench\streeteasy\streeteasy_benchmark_tasks.xlsx - streeteasy_benchmark_tasks.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print("=" * 80)
print("FULL SELF-MATCH TEST: All 70 Tasks")
print("=" * 80)

fails = []
for i, r in enumerate(rows):
    config_raw = r.get('task_generation_config_json', '')
    config_raw = config_raw.strip('"').replace('""', '"')
    config = json.loads(config_raw)
    gt_url = config.get('ground_truth_url', '')
    if not gt_url:
        fails.append(f"Task {i}: No GT URL found")
        continue
    v = StreetEasyUrlMatch(gt_url=gt_url)
    match, details = v._urls_match(gt_url, gt_url)
    if not match:
        decoded = unquote(gt_url)
        fails.append(f"Task {i}: SELF-MATCH FAIL: {decoded} | Details: {details}")

print(f"Results: {len(rows) - len(fails)}/{len(rows)} pass")
if fails:
    print("\nFAILURES:")
    for f in fails:
        print(f"  {f}")
else:
    print("ALL 70 TASKS PASS SELF-MATCH!")

# Now test the edge cases the user was worried about
print(f"\n{'=' * 80}")
print("EDGE CASE TESTS")
print("=" * 80)

t = 0; p = 0; edge_fails = []
def T(name, gt, agent, expect=True):
    global t, p
    t += 1
    v = StreetEasyUrlMatch(gt_url=gt)
    match, details = v._urls_match(agent, gt)
    if match == expect:
        p += 1
    else:
        edge_fails.append(f"{name}: expected={expect} got={match} details={details}")

# 1. beds>=2 format equivalence
T("beds>=2 self-match",
  "https://streeteasy.com/for-sale/manhattan/beds%3E=2",
  "https://streeteasy.com/for-sale/manhattan/beds>=2")

# 2. beds:2 vs beds>=2 — should NOT match (different semantics)
T("beds:2 vs beds>=2",
  "https://streeteasy.com/for-sale/manhattan/beds%3E=2",
  "https://streeteasy.com/for-sale/manhattan/beds:2", False)

# 3. furnished:1 self-match
T("furnished:1 self-match",
  "https://streeteasy.com/for-rent/manhattan/furnished:1",
  "https://streeteasy.com/for-rent/manhattan/furnished:1")

# 4. furnished:1 vs amenities:furnished — should these match?
T("furnished:1 vs amenities:furnished",
  "https://streeteasy.com/for-rent/manhattan/furnished:1",
  "https://streeteasy.com/for-rent/manhattan/amenities:furnished", False)

# 5. new_development:1 self-match  
T("new_development:1 self-match",
  "https://streeteasy.com/for-sale/manhattan/new_development:1",
  "https://streeteasy.com/for-sale/manhattan/new_development:1")

# 6. new_developments:1 → should alias to new_development:1
T("new_developments alias",
  "https://streeteasy.com/for-sale/manhattan/new_development:1",
  "https://streeteasy.com/for-sale/manhattan/new_developments:1")

# 7. prewar:1 vs pre_war:1 equivalence
T("prewar alias",
  "https://streeteasy.com/for-sale/manhattan/prewar:1",
  "https://streeteasy.com/for-sale/manhattan/pre_war:1")

# 8. status:sold equivalence
T("status:sold self-match",
  "https://streeteasy.com/for-sale/manhattan/status:sold",
  "https://streeteasy.com/for-sale/manhattan/status:sold")

# 9. Sold page type (/sold/) vs for-sale+status:sold
T("sold type vs for-sale+status:sold",
  "https://streeteasy.com/sold/manhattan",
  "https://streeteasy.com/for-sale/manhattan/status:sold")

# 10. amenities order independence
T("amenities order",
  "https://streeteasy.com/for-rent/manhattan/amenities:doorman,elevator",
  "https://streeteasy.com/for-rent/manhattan/amenities:elevator,doorman")

# 11. Extra agent filters (should still match)
T("extra agent filters",
  "https://streeteasy.com/for-sale/manhattan/beds>=2",
  "https://streeteasy.com/for-sale/manhattan/beds>=2|type:D1")

# 12. Price abbreviation
T("price 500k",
  "https://streeteasy.com/for-sale/manhattan/price:500000-1000000",
  "https://streeteasy.com/for-sale/manhattan/price:500k-1000000")

# 13. Missing GT filter (agent doesn't have it)
T("missing filter",
  "https://streeteasy.com/for-sale/manhattan/beds>=2|type:D1",
  "https://streeteasy.com/for-sale/manhattan/beds>=2", False)

# 14. transit_lines:L → subway:L equivalence
T("transit_lines alias",
  "https://streeteasy.com/for-sale/manhattan/subway:L",
  "https://streeteasy.com/for-sale/manhattan/transit_lines:L")

print(f"\nEdge case results: {p}/{t} pass")
if edge_fails:
    print("\nFAILURES:")
    for f in edge_fails:
        print(f"  {f}")
else:
    print("ALL EDGE CASES PASS!")
