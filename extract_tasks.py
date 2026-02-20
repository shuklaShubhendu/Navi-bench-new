import csv, json

with open(r'c:\Users\HP\Desktop\navi-fev\navi_bench\streeteasy\streeteasy_benchmark_tasks.xlsx - streeteasy_benchmark_tasks.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

out = []
for i in [0, 16, 19, 21, 37, 40, 65, 67]:
    r = rows[i]
    config_raw = r.get('task_generation_config_json', '')
    config_raw = config_raw.strip('"').replace('""', '"')
    config = json.loads(config_raw)
    task_desc = config.get('task', 'N/A')
    gt_url = config.get('ground_truth_url', 'NOT FOUND')
    l2 = r.get('l2_category', 'N/A')
    out.append(f"=== TASK {i} ({l2}) ===")
    out.append(f"DESCRIPTION: {task_desc}")
    out.append(f"GT_URL: {gt_url}")
    out.append("")

with open(r'c:\Users\HP\Desktop\navi-fev\task_extract_output.txt', 'w') as f:
    f.write('\n'.join(out))
print("Done")
