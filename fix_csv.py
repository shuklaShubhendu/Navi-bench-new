"""Fix the StreetEasy benchmark CSV GT URLs for tasks 21, 37, 67, and 16 typo."""
import csv, json, copy

csvpath = r'c:\Users\HP\Desktop\navi-fev\navi_bench\streeteasy\streeteasy_benchmark_tasks_.xlsx - streeteasy_benchmark_tasks.xlsx.csv'

with open(csvpath, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fieldnames = reader.fieldnames

print(f"Loaded {len(rows)} rows")
print(f"Columns: {fieldnames}")

fixes_applied = []

for i, r in enumerate(rows):
    config_raw = r.get('task_generation_config_json', '')
    # The CSV wraps JSON in quotes and doubles internal quotes
    inner = config_raw.strip('"').replace('""', '"')
    try:
        config = json.loads(inner)
    except json.JSONDecodeError:
        print(f"  Row {i}: JSON parse error, skipping")
        continue
    
    gt_url = config.get('ground_truth_url', '')
    original_gt = gt_url
    changed = False
    
    # === Task 21: Fix new_developments:new%20development → new_development:1 ===
    if i == 21:
        if 'new_developments:new%20development' in gt_url or 'new_developments:new development' in gt_url:
            gt_url = gt_url.replace('new_developments:new%20development', 'new_development:1')
            gt_url = gt_url.replace('new_developments:new development', 'new_development:1')
            changed = True
            fixes_applied.append(f"Task 21: new_developments:new%20development → new_development:1")
    
    # === Task 37: Fix amenities:furnished → furnished:1 ===
    if i == 37:
        if 'amenities:furnished' in gt_url:
            # Replace amenities:furnished with furnished:1
            gt_url = gt_url.replace('%7Camenities:furnished', '%7Cfurnished:1')
            gt_url = gt_url.replace('amenities:furnished%7C', 'furnished:1%7C')
            gt_url = gt_url.replace('amenities:furnished', 'furnished:1')
            changed = True
            fixes_applied.append(f"Task 37: amenities:furnished → furnished:1")
    
    # === Task 67: Extract furnished from amenities compound ===
    if i == 67:
        # amenities:doorman,furnished,elevator → amenities:doorman,elevator|furnished:1
        if 'amenities:doorman,furnished,elevator' in gt_url:
            gt_url = gt_url.replace('amenities:doorman,furnished,elevator', 
                                     'amenities:doorman,elevator%7Cfurnished:1')
            changed = True
            fixes_applied.append(f"Task 67: amenities:doorman,furnished,elevator → amenities:doorman,elevator|furnished:1")
    
    # === Task 16: Fix sort_by typo (listed_descc → listed_desc) ===
    if i == 16:
        if 'listed_descc' in gt_url:
            gt_url = gt_url.replace('listed_descc', 'listed_desc')
            changed = True
            fixes_applied.append(f"Task 16: sort_by=listed_descc → sort_by=listed_desc (typo fix)")
    
    if changed:
        config['ground_truth_url'] = gt_url
        # Re-serialize: JSON with doubled quotes wrapped in outer quotes
        new_json = json.dumps(config, ensure_ascii=False)
        # CSV format: wrap in quotes and double any internal quotes
        new_csv_value = '"' + new_json.replace('"', '""') + '"'
        r['task_generation_config_json'] = new_csv_value
        print(f"  Row {i}: FIXED")
        print(f"    OLD: {original_gt}")
        print(f"    NEW: {gt_url}")

# Write fixed CSV
with open(csvpath, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\nTotal fixes applied: {len(fixes_applied)}")
for fix in fixes_applied:
    print(f"  ✓ {fix}")
print(f"\nCSV saved to: {csvpath}")
