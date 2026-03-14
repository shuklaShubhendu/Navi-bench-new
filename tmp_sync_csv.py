"""Sync CSV1 to match CSV2 where there are real data differences."""
import csv, json, sys, os
sys.path.insert(0, '.')

csv1_path = "navi_bench/realtor/realtor_benchmark_tasks.csv"
csv2_path = "navi_bench/realtor/realtor_benchmark_tasks2.csv"

def load_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)
    return headers, rows

def cfg_from_row(row):
    return json.loads(row["task_generation_config_json"])

def save_cfg(row, cfg):
    row["task_generation_config_json"] = json.dumps(cfg)

h1, rows1 = load_csv(csv1_path)
h2, rows2 = load_csv(csv2_path)

# Index by task_id
csv1_idx = {r["task_id"]: r for r in rows1}
csv2_idx = {r["task_id"]: r for r in rows2}

fixes = []

for tid in sorted(csv1_idx.keys()):
    if tid not in csv2_idx:
        continue
    
    cfg1 = cfg_from_row(csv1_idx[tid])
    cfg2 = cfg_from_row(csv2_idx[tid])
    
    gt1 = cfg1.get("gt_url", "")
    gt2 = cfg2.get("gt_url", "")
    task1 = cfg1.get("task", "")
    task2 = cfg2.get("task", "")
    
    changed = False
    
    # Sync GT URL to CSV2 version
    if gt1 != gt2:
        cfg1["gt_url"] = gt2
        fixes.append("GT URL [%s]: %s -> %s" % (tid, gt1, gt2))
        changed = True
    
    # Sync task text to CSV2 version
    if task1.strip() != task2.strip():
        cfg1["task"] = task2
        fixes.append("Task text [%s]: synced" % tid)
        changed = True
    
    if changed:
        save_cfg(csv1_idx[tid], cfg1)

# Write back
with open(csv1_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=h1)
    writer.writeheader()
    writer.writerows(rows1)

print("Fixes applied: %d" % len(fixes))
for fix in fixes:
    print("  %s" % fix)

# Verify both CSVs now identical
h1b, rows1b = load_csv(csv1_path)
csv1b_idx = {r["task_id"]: r for r in rows1b}

diffs = 0
for tid in csv1b_idx:
    if tid in csv2_idx:
        c1 = cfg_from_row(csv1b_idx[tid])
        c2 = cfg_from_row(csv2_idx[tid])
        if c1.get("gt_url") != c2.get("gt_url"):
            diffs += 1
            print("STILL DIFFERENT [%s]: %s vs %s" % (tid, c1["gt_url"], c2["gt_url"]))
        if c1.get("task", "").strip() != c2.get("task", "").strip():
            diffs += 1
            print("TASK TEXT STILL DIFFERENT [%s]" % tid)

if diffs == 0:
    print("\nCSV1 and CSV2 are now FULLY SYNCED on GT URLs + task text!")
else:
    print("\n%d differences remain!" % diffs)
