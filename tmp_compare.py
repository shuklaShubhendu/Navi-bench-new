"""Deep comparison: CSV1 vs CSV2."""
import csv, json, sys, os, asyncio
sys.path.insert(0, '.')
from navi_bench.realtor.realtor_url_match import RealtorUrlMatch

csv1_path = "navi_bench/realtor/realtor_benchmark_tasks.csv"
csv2_path = "navi_bench/realtor/realtor_benchmark_tasks2.csv"

def load_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    result = {}
    for row in rows:
        tid = row["task_id"]
        cfg = json.loads(row["task_generation_config_json"])
        result[tid] = {"row": row, "cfg": cfg}
    return result

csv1 = load_csv(csv1_path)
csv2 = load_csv(csv2_path)

print("=" * 80)
print("CSV1: %d rows  |  CSV2: %d rows" % (len(csv1), len(csv2)))
print("=" * 80)

# 1. Task IDs 
only_csv1 = sorted(set(csv1.keys()) - set(csv2.keys()))
only_csv2 = sorted(set(csv2.keys()) - set(csv1.keys()))
common = sorted(set(csv1.keys()) & set(csv2.keys()))

if only_csv1:
    print("\n--- ONLY IN CSV1 (%d) ---" % len(only_csv1))
    for tid in only_csv1:
        gt = csv1[tid]["cfg"].get("gt_url", "?")
        print("  %s: %s" % (tid, gt))

if only_csv2:
    print("\n--- ONLY IN CSV2 (%d) ---" % len(only_csv2))
    for tid in only_csv2:
        gt = csv2[tid]["cfg"].get("gt_url", "?")
        print("  %s: %s" % (tid, gt))

# 2. Compare GT URLs
print("\n--- GT URL COMPARISON (%d common tasks) ---" % len(common))
url_diffs = []
url_match = 0
v = RealtorUrlMatch(gt_url="https://www.realtor.com")

for tid in common:
    gt1 = csv1[tid]["cfg"].get("gt_url", "")
    gt2 = csv2[tid]["cfg"].get("gt_url", "")
    
    g1 = gt1.lower().strip().rstrip("/") if isinstance(gt1, str) else str(gt1).lower()
    g2 = gt2.lower().strip().rstrip("/") if isinstance(gt2, str) else str(gt2).lower()
    
    if g1 != g2:
        url_diffs.append((tid, gt1, gt2))
    else:
        url_match += 1

print("  Identical URLs: %d/%d" % (url_match, len(common)))
if url_diffs:
    print("  DIFFERENT URLs: %d" % len(url_diffs))
    for tid, g1, g2 in url_diffs:
        print("\n  [%s]" % tid)
        print("    CSV1: %s" % g1)
        print("    CSV2: %s" % g2)
        p1 = v._parse_realtor_url(g1 if isinstance(g1, str) else g1[0])
        p2 = v._parse_realtor_url(g2 if isinstance(g2, str) else g2[0])
        if p1["search_type"] != p2["search_type"]:
            print("    TYPE DIFF: %s vs %s" % (p1["search_type"], p2["search_type"]))
        if p1["location"] != p2["location"]:
            print("    LOC DIFF: %s vs %s" % (p1["location"], p2["location"]))
        f1_keys = set(p1["filters"].keys())
        f2_keys = set(p2["filters"].keys())
        only_f1 = f1_keys - f2_keys
        only_f2 = f2_keys - f1_keys
        if only_f1:
            parts = ["%s=%s" % (k, p1["filters"][k]) for k in only_f1]
            print("    FILTERS ONLY IN CSV1: %s" % ", ".join(parts))
        if only_f2:
            parts = ["%s=%s" % (k, p2["filters"][k]) for k in only_f2]
            print("    FILTERS ONLY IN CSV2: %s" % ", ".join(parts))
        for k in f1_keys & f2_keys:
            if p1["filters"][k] != p2["filters"][k]:
                print("    FILTER VALUE DIFF [%s]: '%s' vs '%s'" % (k, p1["filters"][k], p2["filters"][k]))

# 3. Task text diffs
print("\n--- TASK TEXT COMPARISON ---")
task_diffs = 0
for tid in common:
    t1 = csv1[tid]["cfg"].get("task", "")
    t2 = csv2[tid]["cfg"].get("task", "")
    if t1.strip() != t2.strip():
        task_diffs += 1
        if task_diffs <= 10:
            print("  [%s]" % tid)
            print("    CSV1: %s" % t1[:120])
            print("    CSV2: %s" % t2[:120])
print("  Task text diffs: %d/%d" % (task_diffs, len(common)))

# 4. Cross-match: CSV2 GT URLs self-match
print("\n--- CROSS-MATCH: CSV2 self-match ---")
async def cross():
    p, f = 0, []
    for tid in sorted(csv2.keys()):
        gt = csv2[tid]["cfg"].get("gt_url", "")
        vv = RealtorUrlMatch(gt_url=gt)
        await vv.reset()
        url = gt if isinstance(gt, str) else gt[0]
        await vv.update(url=url)
        result = await vv.compute()
        if result.score == 1.0:
            p += 1
        else:
            f.append(tid)
    return p, f

p, f = asyncio.run(cross())
print("  Self-match: %d/%d PASS" % (p, len(csv2)))
if f:
    for tid in f:
        print("  FAILED: %s" % tid)

# 5. Semantic check: does CSV1's verifier handle ALL CSV2 patterns?
print("\n--- PATTERN COVERAGE: Can verifier parse every CSV2 URL segment? ---")
all_segs = set()
for tid, data in csv2.items():
    gt = data["cfg"].get("gt_url", "")
    url = gt if isinstance(gt, str) else gt[0]
    parts = v._parse_realtor_url(url)
    for k, val in parts["filters"].items():
        all_segs.add(k)
print("  All filter keys used in CSV2: %s" % ", ".join(sorted(all_segs)))

print("\n" + "=" * 80)
print("COMPARISON COMPLETE")
print("=" * 80)
