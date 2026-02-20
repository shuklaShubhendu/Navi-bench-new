"""
Rewrite all 70 StreetEasy benchmark URLs to match the REAL 
StreetEasy UI format:
  1. Filter ordering matches what the StreetEasy UI generates
  2. ?sort_by=se_score appended (StreetEasy always adds this)
  3. Special chars URL-encoded (| -> %7C, >= -> %3E=)
"""

import csv
import json
import os
from urllib.parse import unquote, urlparse

# StreetEasy's filter ordering (confirmed from UI interactions)
FILTER_ORDER = {
    "type": 1,
    "price": 2,
    "beds": 3,
    "baths": 4,
    "sqft": 5,
    "status": 6,
    "no_fee": 7,
    "furnished": 8,
    "transit_lines": 9,
    "subway": 9,
    "amenities": 10,
    "pets": 11,
    "prewar": 12,
    "new_development": 13,
}


def get_filter_key(segment):
    """Extract the filter key from 'price:500000-' or 'beds>=2'."""
    if ">=" in segment:
        return segment.split(">=")[0]
    if ":" in segment:
        return segment.split(":")[0]
    return segment


def get_filter_order(segment):
    """Get sort priority for a filter segment."""
    return FILTER_ORDER.get(get_filter_key(segment), 99)


def reorder_url(url):
    """Rewrite URL to match StreetEasy's real UI format."""
    url = unquote(url)
    
    # Remove existing query params
    base_url = url.split("?")[0]
    
    # Use urlparse to properly extract path
    parsed = urlparse(base_url if base_url.startswith("http") else "https://" + base_url)
    scheme = parsed.scheme or "https"
    host = parsed.netloc or "streeteasy.com"
    path = parsed.path.strip("/")
    
    # Split path into segments
    segments = [s for s in path.split("/") if s]
    
    # Separate path segments from filter segments
    path_parts = []
    filter_segments = []
    found_filters = False
    
    for seg in segments:
        if not found_filters:
            # Check if this segment contains filter syntax (: or >=)
            # But NOT if it's a path segment like "for-sale" or "manhattan"
            if "|" in seg or (":" in seg and seg.split(":")[0] in FILTER_ORDER) or (">=" in seg):
                found_filters = True
                # This segment may contain pipe-separated filters
                for f in seg.split("|"):
                    f = f.strip()
                    if f:
                        filter_segments.append(f)
            else:
                path_parts.append(seg)
        else:
            # Already in filter territory
            for f in seg.split("|"):
                f = f.strip()
                if f:
                    filter_segments.append(f)
    
    # Rebuild base path
    base = f"{scheme}://{host}/{'/'.join(path_parts)}"
    
    if not filter_segments:
        return base + "?sort_by=se_score"
    
    # Sort filters by StreetEasy's canonical ordering
    sorted_filters = sorted(filter_segments, key=get_filter_order)
    
    # Build filter string with URL encoding
    filter_str = "|".join(sorted_filters)
    filter_encoded = filter_str.replace(">=", "%3E=").replace("|", "%7C")
    
    return f"{base}/{filter_encoded}?sort_by=se_score"


# Read CSV
csv_path = os.path.join("navi_bench", "streeteasy",
                        "streeteasy_benchmark_tasks.xlsx - streeteasy_benchmark_tasks.csv")

rows = []
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        rows.append(row)

print(f"Read {len(rows)} tasks\n")

# Process each row
reordered_count = 0
sort_added_count = 0
unchanged_count = 0

for i, row in enumerate(rows):
    config_csv = row["task_generation_config_json"]
    
    if config_csv.startswith('"') and config_csv.endswith('"'):
        config_json = config_csv[1:-1].replace('""', '"')
    else:
        config_json = config_csv
    
    config = json.loads(config_json)
    old_url = config["ground_truth_url"]
    new_url = reorder_url(old_url)
    
    old_decoded = unquote(old_url).split("?")[0]
    new_decoded = unquote(new_url).split("?")[0]
    
    if old_decoded != new_decoded:
        reordered_count += 1
        # Show the filter order change
        old_filters = old_decoded.split("/")[-1] if any(c in old_decoded.split("/")[-1] for c in [":", ">="]) else "(none)"
        new_filters = new_decoded.split("/")[-1] if any(c in new_decoded.split("/")[-1] for c in [":", ">="]) else "(none)"
        print(f"Task {i}: REORDERED")
        print(f"  Old: {old_filters}")
        print(f"  New: {new_filters}")
        print()
    elif "sort_by" not in old_url:
        sort_added_count += 1
    else:
        unchanged_count += 1
    
    config["ground_truth_url"] = new_url
    inner_json = json.dumps(config)
    csv_value = '"' + inner_json.replace('"', '""') + '"'
    row["task_generation_config_json"] = csv_value

# Write updated CSV
with open(csv_path, "w", newline="\r\n", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\n=== SUMMARY ===")
print(f"Filter order changed: {reordered_count}")
print(f"Sort_by added only:   {sort_added_count}")
print(f"Unchanged:            {unchanged_count}")
print(f"Total:                {len(rows)}")
print(f"\nWritten to: {csv_path}")

# Verify the user's specific example (Task 5)
print("\n=== VERIFY USER'S EXAMPLE (Task 5) ===")
c5_csv = rows[5]["task_generation_config_json"]
if c5_csv.startswith('"') and c5_csv.endswith('"'):
    c5_json = c5_csv[1:-1].replace('""', '"')
else:
    c5_json = c5_csv
c5 = json.loads(c5_json)
print(f"Task:     {c5['task']}")
print(f"URL:      {c5['ground_truth_url']}")
expected = "https://streeteasy.com/for-sale/brooklyn/price:1000000-2000000%7Cbeds:3?sort_by=se_score"
print(f"Expected: {expected}")
print(f"Match:    {c5['ground_truth_url'] == expected}")
