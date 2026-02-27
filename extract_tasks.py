import csv, json

csvpath = r'c:\Users\HP\Desktop\navi-fev\navi_bench\streeteasy\streeteasy_benchmark_tasks_.xlsx - streeteasy_benchmark_tasks.xlsx.csv'
with open(csvpath, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

keys = list(rows[0].keys())
with open(r'c:\Users\HP\Desktop\navi-fev\task_extract_output.txt', 'w', encoding='utf-8') as out:
    out.write(f"Total rows: {len(rows)}\n")
    out.write(f"Columns: {keys}\n\n")
    
    # Check all rows for the problematic tasks
    for i in [0, 16, 19, 21, 37, 40, 65, 67]:
        if i >= len(rows):
            out.write(f"Task {i}: OUT OF RANGE (only {len(rows)} rows)\n\n")
            continue
        r = rows[i]
        config_raw = r.get('task_generation_config_json', '')
        config_raw = config_raw.strip('"').replace('""', '"')
        try:
            config = json.loads(config_raw)
            task_desc = config.get('task', 'N/A')
            gt_url = config.get('ground_truth_url', config.get('gt_url', 'NOT FOUND'))
            l2 = r.get('l2_category', 'N/A')
            tid = r.get('task_id', 'N/A')
            out.write(f"=== ROW {i} | task_id={tid} | l2={l2} ===\n")
            out.write(f"DESCRIPTION: {task_desc}\n")
            if isinstance(gt_url, list):
                for u in gt_url:
                    out.write(f"GT_URL: {u}\n")
            else:
                out.write(f"GT_URL: {gt_url}\n")
            out.write("\n")
        except json.JSONDecodeError as e:
            out.write(f"=== ROW {i} | JSON ERROR ===\n")
            out.write(f"ERROR: {e}\n")
            out.write(f"RAW (first 300): {config_raw[:300]}\n\n")
    
    # Also check the 3 data issue rows: lines 38, 59, 68 (0-indexed: 37, 58, 67)
    out.write("\n=== DATA ISSUE ROWS ===\n")
    for line_num in [36, 57, 67]:
        if line_num >= len(rows):
            out.write(f"Line {line_num+2} (row {line_num}): OUT OF RANGE\n\n")
            continue
        r = rows[line_num]
        tid = r.get('task_id', '(empty)')
        config_raw = r.get('task_generation_config_json', '')
        config_raw_clean = config_raw.strip('"').replace('""', '"')
        out.write(f"Line {line_num+2} (row {line_num}) | task_id={tid}\n")
        try:
            config = json.loads(config_raw_clean)
            out.write(f"  JSON OK\n")
            gt = config.get('ground_truth_url', 'NOT FOUND')
            out.write(f"  GT: {gt}\n\n")
        except json.JSONDecodeError as e:
            out.write(f"  JSON ERROR: {e}\n")
            out.write(f"  RAW tail (last 100): ...{config_raw[-100:]}\n\n")

print("Done - output to task_extract_output.txt")
