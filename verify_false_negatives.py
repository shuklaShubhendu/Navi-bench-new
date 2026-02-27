"""Verify all fixes: self-match + agent simulation for affected tasks."""
import sys, io, csv, json
sys.stderr = io.StringIO()
from urllib.parse import unquote
sys.path.insert(0, r'c:\Users\HP\Desktop\navi-fev')
from navi_bench.streeteasy.streeteasy_url_match import StreetEasyUrlMatch

csvpath = r'c:\Users\HP\Desktop\navi-fev\navi_bench\streeteasy\streeteasy_benchmark_tasks_.xlsx - streeteasy_benchmark_tasks.xlsx.csv'
with open(csvpath, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

out = []
out.append("=" * 80)
out.append("SECTION 1: FULL SELF-MATCH TEST (All 70 Tasks)")
out.append("=" * 80)

fails = []
for i, r in enumerate(rows):
    config_raw = r.get('task_generation_config_json', '')
    config_raw = config_raw.strip('"').replace('""', '"')
    try:
        config = json.loads(config_raw)
    except json.JSONDecodeError as e:
        fails.append(f"Row {i}: JSON parse error: {e}")
        continue
    gt_url = config.get('ground_truth_url', '')
    if not gt_url:
        fails.append(f"Row {i}: No GT URL")
        continue
    v = StreetEasyUrlMatch(gt_url=gt_url)
    match, details = v._urls_match(gt_url, gt_url)
    if not match:
        decoded = unquote(gt_url)
        fails.append(f"Row {i}: SELF-MATCH FAIL: {decoded} | Details: {details}")

out.append(f"Results: {len(rows) - len(fails)}/{len(rows)} pass")
if fails:
    out.append("\nFAILURES:")
    for f in fails:
        out.append(f"  {f}")
else:
    out.append("ALL 70 TASKS PASS SELF-MATCH!")

# Section 2: Verify the fixed tasks specifically
out.append("")
out.append("=" * 80)
out.append("SECTION 2: FIXED TASKS - Agent Simulation Tests")
out.append("=" * 80)

# Extract GT URLs for the fixed tasks
fixed_gts = {}
for i in [16, 21, 37, 67]:
    config_raw = rows[i].get('task_generation_config_json', '')
    config_raw = config_raw.strip('"').replace('""', '"')
    config = json.loads(config_raw)
    fixed_gts[i] = config.get('ground_truth_url', '')
    out.append(f"\nTask {i} GT (decoded): {unquote(fixed_gts[i])}")

# Test with realistic agent URLs
agent_tests = {
    21: ("Agent: new_development:1", 
         "https://streeteasy.com/for-sale/manhattan/type:D1|new_development:1"),
    37: ("Agent: furnished:1 separate filter", 
         "https://streeteasy.com/for-rent/manhattan/price:-4000|beds:1|furnished:1"),
    67: ("Agent: furnished:1 + amenities:doorman,elevator", 
         "https://streeteasy.com/for-rent/manhattan/price:-5000|beds>=1|furnished:1|amenities:doorman,elevator"),
}

out.append("\n--- Agent vs GT Tests ---")
all_pass = True
for task_id, (desc, agent_url) in agent_tests.items():
    gt_url = fixed_gts[task_id]
    v = StreetEasyUrlMatch(gt_url=gt_url)
    match, details = v._urls_match(agent_url, gt_url)
    status = "PASS" if match else "FAIL"
    if not match:
        all_pass = False
    out.append(f"\nTask {task_id} [{status}]: {desc}")
    out.append(f"  Agent: {agent_url}")
    out.append(f"  GT:    {unquote(gt_url)}")
    if not match:
        out.append(f"  DETAILS: {details}")

out.append(f"\n{'=' * 80}")
out.append(f"FINAL: {'ALL PASS' if (not fails and all_pass) else 'SOME FAILURES'}")
out.append("=" * 80)

with open(r'c:\Users\HP\Desktop\navi-fev\verify_output.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('\n'.join(out))
