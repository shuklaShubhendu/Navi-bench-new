import csv, json
from urllib.parse import unquote

with open('navi_bench/streeteasy/streeteasy_benchmark_tasks.xlsx - streeteasy_benchmark_tasks.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

for i in [0, 5, 11, 17, 42, 48, 61, 65, 68]:
    config_csv = rows[i]['task_generation_config_json']
    if config_csv.startswith('"') and config_csv.endswith('"'):
        config_json = config_csv[1:-1].replace('""', '"')
    else:
        config_json = config_csv
    c = json.loads(config_json)
    print(f"Task {i}: {c['task'][:70]}...")
    print(f"  URL: {unquote(c['ground_truth_url'])}")
    print()
