"""
Generate 70 StreetEasy benchmark tasks with browser-verified URLs.
All URLs verified on live StreetEasy (Feb 2026).
"""

import csv
import json
from urllib.parse import quote

# Template for each task row
def make_row(task_id, category, idx, task_desc, gt_url, difficulty="medium"):
    config = {
        "_target_": "navi_bench.streeteasy.streeteasy_url_match.generate_task_config",
        "url": "https://streeteasy.com",
        "task": task_desc,
        "location": "New York, NY, United States",
        "timezone": "America/New_York",
        "ground_truth_url": gt_url,
    }
    # CSV-escape the JSON (double up quotes for CSV)
    config_json = json.dumps(config).replace('"', '""')
    return {
        "task_id": f"navi_bench/streeteasy/{category}/{idx}",
        "task_generation_config_json": f'"{config_json}"',
        "env": "real",
        "domain": "streeteasy",
        "l1_category": "realestate",
        "l2_category": category,
        "suggested_difficulty": difficulty,
        "suggested_hint": "null",
        "suggested_max_steps": "null",
        "suggested_split": "validation",
        "metadata_json": "null",
    }


# All 70 tasks with browser-verified URLs
tasks = []

# ============================================================
# FOR SALE BASIC (tasks 0-9)
# ============================================================
tasks.append(make_row("navi_bench/streeteasy/for_sale_basic/0", "for_sale_basic", 0,
    "Find condos for sale in Manhattan priced between $500,000 and $1,000,000 with at least 2 bedrooms.",
    "https://streeteasy.com/for-sale/manhattan/type:D1%7Cprice:500000-1000000%7Cbeds%3E=2",
    "medium"))

tasks.append(make_row("", "for_sale_basic", 1,
    "Search for co-ops for sale in Brooklyn under $700,000.",
    "https://streeteasy.com/for-sale/brooklyn/type:P1%7Cprice:-700000",
    "easy"))

tasks.append(make_row("", "for_sale_basic", 2,
    "Find all properties for sale in Queens.",
    "https://streeteasy.com/for-sale/queens",
    "easy"))

tasks.append(make_row("", "for_sale_basic", 3,
    "Search for properties for sale in the Bronx priced under $500,000.",
    "https://streeteasy.com/for-sale/bronx/price:-500000",
    "easy"))

tasks.append(make_row("", "for_sale_basic", 4,
    "Find studio apartments for sale in Manhattan.",
    "https://streeteasy.com/for-sale/manhattan/beds:0",
    "easy"))

tasks.append(make_row("", "for_sale_basic", 5,
    "Search for 3-bedroom homes for sale in Brooklyn priced between $1,000,000 and $2,000,000.",
    "https://streeteasy.com/for-sale/brooklyn/beds:3%7Cprice:1000000-2000000",
    "medium"))

tasks.append(make_row("", "for_sale_basic", 6,
    "Find properties for sale in Manhattan priced between $2,000,000 and $5,000,000 with at least 3 bedrooms and 2 or more bathrooms.",
    "https://streeteasy.com/for-sale/manhattan/price:2000000-5000000%7Cbeds%3E=3%7Cbaths%3E=2",
    "medium"))

tasks.append(make_row("", "for_sale_basic", 7,
    "Search for 1-bedroom condos for sale in Brooklyn priced between $500,000 and $1,000,000.",
    "https://streeteasy.com/for-sale/brooklyn/type:D1%7Cprice:500000-1000000%7Cbeds:1",
    "medium"))

tasks.append(make_row("", "for_sale_basic", 8,
    "Find condos for sale in Queens under $500,000 with at least 1 bedroom.",
    "https://streeteasy.com/for-sale/queens/type:D1%7Cprice:-500000%7Cbeds%3E=1",
    "medium"))

tasks.append(make_row("", "for_sale_basic", 9,
    "Search for co-ops for sale in Brooklyn priced under $500,000.",
    "https://streeteasy.com/for-sale/brooklyn/type:P1%7Cprice:-500000",
    "easy"))

# ============================================================
# FOR SALE AMENITIES (tasks 10-16)
# ============================================================
tasks.append(make_row("", "for_sale_amenities", 10,
    "Find condos for sale in Manhattan with a doorman and elevator, priced between $800,000 and $2,000,000.",
    "https://streeteasy.com/for-sale/manhattan/type:D1%7Cprice:800000-2000000%7Camenities:doorman,elevator",
    "medium"))

tasks.append(make_row("", "for_sale_amenities", 11,
    "Search for condos for sale in Manhattan with a gym and pool, at least 2 bedrooms, priced between $1,000,000 and $3,000,000.",
    "https://streeteasy.com/for-sale/manhattan/type:D1%7Camenities:gym,pool%7Cbeds%3E=2%7Cprice:1000000-3000000",
    "hard"))

tasks.append(make_row("", "for_sale_amenities", 12,
    "Find condos for sale in Brooklyn with a garage and at least 2 bedrooms.",
    "https://streeteasy.com/for-sale/brooklyn/type:D1%7Camenities:garage%7Cbeds%3E=2",
    "medium"))

tasks.append(make_row("", "for_sale_amenities", 13,
    "Search for co-ops for sale in Manhattan with a doorman, priced under $800,000, with at least 2 bedrooms.",
    "https://streeteasy.com/for-sale/manhattan/type:P1%7Camenities:doorman%7Cprice:-800000%7Cbeds%3E=2",
    "medium"))

tasks.append(make_row("", "for_sale_amenities", 14,
    "Find condos for sale in Manhattan with a pool, priced under $2,000,000.",
    "https://streeteasy.com/for-sale/manhattan/type:D1%7Camenities:pool%7Cprice:-2000000",
    "medium"))

tasks.append(make_row("", "for_sale_amenities", 15,
    "Search for properties for sale in Brooklyn with at least 1,000 square feet and 2 or more bedrooms.",
    "https://streeteasy.com/for-sale/brooklyn/sqft%3E=1000%7Cbeds%3E=2",
    "medium"))

tasks.append(make_row("", "for_sale_amenities", 16,
    "Find condos for sale in Manhattan with an elevator, priced between $500,000 and $1,500,000, with at least 1 bedroom.",
    "https://streeteasy.com/for-sale/manhattan/type:D1%7Camenities:elevator%7Cprice:500000-1500000%7Cbeds%3E=1",
    "medium"))

# ============================================================
# FOR SALE COMPLEX (tasks 17-22)
# ============================================================
tasks.append(make_row("", "for_sale_complex", 17,
    "Find pet-friendly condos or co-ops for sale in Manhattan with 2+ bedrooms, a doorman, and a gym, priced under $1,500,000.",
    "https://streeteasy.com/for-sale/manhattan/type:D1,P1%7Cbeds%3E=2%7Cprice:-1500000%7Cpets:allowed%7Camenities:doorman,gym",
    "hard"))

tasks.append(make_row("", "for_sale_complex", 18,
    "Search for condos or co-ops for sale in Manhattan priced between $500,000 and $1,500,000 with at least 1 bedroom and 1 bathroom.",
    "https://streeteasy.com/for-sale/manhattan/type:D1,P1%7Cprice:500000-1500000%7Cbeds%3E=1%7Cbaths%3E=1",
    "hard"))

tasks.append(make_row("", "for_sale_complex", 19,
    "Find pre-war condos for sale in Manhattan with at least 2 bedrooms, a doorman, priced between $1,000,000 and $3,000,000.",
    "https://streeteasy.com/for-sale/manhattan/type:D1%7Cprewar:1%7Cbeds%3E=2%7Cprice:1000000-3000000%7Camenities:doorman",
    "hard"))

tasks.append(make_row("", "for_sale_complex", 20,
    "Search for pre-war co-ops for sale in Manhattan with a doorman, at least 2 bedrooms, priced under $1,000,000.",
    "https://streeteasy.com/for-sale/manhattan/type:P1%7Cprewar:1%7Camenities:doorman%7Cbeds%3E=2%7Cprice:-1000000",
    "hard"))

tasks.append(make_row("", "for_sale_complex", 21,
    "Find new development condos for sale in Manhattan.",
    "https://streeteasy.com/for-sale/manhattan/type:D1%7Cnew_development:1",
    "medium"))

tasks.append(make_row("", "for_sale_complex", 22,
    "Search for condos for sale in Manhattan with 3 to 4 bedrooms.",
    "https://streeteasy.com/for-sale/manhattan/type:D1%7Cbeds:3-4",
    "medium"))

# ============================================================
# FOR SALE NEIGHBORHOOD (tasks 23-29)
# ============================================================
tasks.append(make_row("", "for_sale_neighborhood", 23,
    "Find condos for sale on the Upper West Side with 3+ bedrooms and 2+ bathrooms.",
    "https://streeteasy.com/for-sale/upper-west-side/type:D1%7Cbeds%3E=3%7Cbaths%3E=2",
    "hard"))

tasks.append(make_row("", "for_sale_neighborhood", 24,
    "Search for condos for sale on the Upper East Side priced between $1,000,000 and $3,000,000.",
    "https://streeteasy.com/for-sale/upper-east-side/type:D1%7Cprice:1000000-3000000",
    "medium"))

tasks.append(make_row("", "for_sale_neighborhood", 25,
    "Find condos for sale in Williamsburg with at least 2 bedrooms.",
    "https://streeteasy.com/for-sale/williamsburg/type:D1%7Cbeds%3E=2",
    "medium"))

tasks.append(make_row("", "for_sale_neighborhood", 26,
    "Search for condos for sale in Chelsea priced between $1,000,000 and $2,000,000 with at least 1 bedroom.",
    "https://streeteasy.com/for-sale/chelsea/type:D1%7Cprice:1000000-2000000%7Cbeds%3E=1",
    "medium"))

tasks.append(make_row("", "for_sale_neighborhood", 27,
    "Find condos for sale in Long Island City under $800,000 with at least 1 bedroom.",
    "https://streeteasy.com/for-sale/long-island-city/type:D1%7Cbeds%3E=1%7Cprice:-800000",
    "medium"))

tasks.append(make_row("", "for_sale_neighborhood", 28,
    "Search for condos for sale in SoHo priced between $2,000,000 and $5,000,000.",
    "https://streeteasy.com/for-sale/soho/type:D1%7Cprice:2000000-5000000",
    "medium"))

tasks.append(make_row("", "for_sale_neighborhood", 29,
    "Find condos for sale in the Financial District with at least 2 bedrooms, priced under $1,500,000.",
    "https://streeteasy.com/for-sale/financial-district/type:D1%7Cbeds%3E=2%7Cprice:-1500000",
    "medium"))

# ============================================================
# FOR SALE PREWAR (tasks 30-32)
# ============================================================
tasks.append(make_row("", "for_sale_prewar", 30,
    "Search for pre-war co-ops for sale in Manhattan with at least 1 bedroom priced under $600,000.",
    "https://streeteasy.com/for-sale/manhattan/type:P1%7Cbeds%3E=1%7Cprice:-600000%7Cprewar:1",
    "medium"))

tasks.append(make_row("", "for_sale_prewar", 31,
    "Find pre-war condos for sale in Manhattan with at least 3 bedrooms, priced between $2,000,000 and $5,000,000.",
    "https://streeteasy.com/for-sale/manhattan/type:D1%7Cprewar:1%7Cbeds%3E=3%7Cprice:2000000-5000000",
    "hard"))

tasks.append(make_row("", "for_sale_prewar", 32,
    "Search for pre-war co-ops for sale in Manhattan with a doorman and elevator, priced under $1,500,000.",
    "https://streeteasy.com/for-sale/manhattan/type:P1%7Cprewar:1%7Camenities:doorman,elevator%7Cprice:-1500000",
    "hard"))

# ============================================================
# FOR RENT BASIC (tasks 33-39)
# ============================================================
tasks.append(make_row("", "for_rent_basic", 33,
    "Search for no-fee apartment rentals in Manhattan with at least 1 bedroom under $3,500 per month.",
    "https://streeteasy.com/for-rent/manhattan/no_fee:1%7Cbeds%3E=1%7Cprice:-3500",
    "medium"))

tasks.append(make_row("", "for_rent_basic", 34,
    "Find apartments for rent in Queens under $2,500 per month with at least 1 bedroom.",
    "https://streeteasy.com/for-rent/queens/price:-2500%7Cbeds%3E=1",
    "easy"))

tasks.append(make_row("", "for_rent_basic", 35,
    "Search for apartments for rent in the Bronx under $2,000 per month with at least 2 bedrooms.",
    "https://streeteasy.com/for-rent/bronx/price:-2000%7Cbeds%3E=2",
    "easy"))

tasks.append(make_row("", "for_rent_basic", 36,
    "Find no-fee apartments for rent in Manhattan with at least 2 bedrooms under $4,000 per month.",
    "https://streeteasy.com/for-rent/manhattan/no_fee:1%7Cbeds%3E=2%7Cprice:-4000",
    "medium"))

tasks.append(make_row("", "for_rent_basic", 37,
    "Search for furnished 1-bedroom apartments for rent in Manhattan under $4,000 per month.",
    "https://streeteasy.com/for-rent/manhattan/furnished:1%7Cbeds:1%7Cprice:-4000",
    "medium"))

tasks.append(make_row("", "for_rent_basic", 38,
    "Find studio apartments for rent in Manhattan under $2,500 per month.",
    "https://streeteasy.com/for-rent/manhattan/beds:0%7Cprice:-2500",
    "easy"))

tasks.append(make_row("", "for_rent_basic", 39,
    "Search for apartments for rent in Brooklyn priced between $2,000 and $3,500 per month with at least 2 bedrooms.",
    "https://streeteasy.com/for-rent/brooklyn/price:2000-3500%7Cbeds%3E=2",
    "medium"))

# ============================================================
# FOR RENT AMENITIES (tasks 40-47)
# ============================================================
tasks.append(make_row("", "for_rent_amenities", 40,
    "Find pet-friendly rentals in Brooklyn with in-unit laundry and a doorman, priced between $2,000 and $4,000 per month.",
    "https://streeteasy.com/for-rent/brooklyn/price:2000-4000%7Cpets:allowed%7Camenities:doorman,in_unit_laundry",
    "hard"))

tasks.append(make_row("", "for_rent_amenities", 41,
    "Search for apartments for rent in Manhattan with a doorman and elevator under $5,000 per month with at least 1 bedroom.",
    "https://streeteasy.com/for-rent/manhattan/amenities:doorman,elevator%7Cprice:-5000%7Cbeds%3E=1",
    "medium"))

tasks.append(make_row("", "for_rent_amenities", 42,
    "Find pet-friendly apartments for rent in Manhattan with a doorman, at least 1 bedroom, under $5,000 per month.",
    "https://streeteasy.com/for-rent/manhattan/pets:allowed%7Camenities:doorman%7Cbeds%3E=1%7Cprice:-5000",
    "medium"))

tasks.append(make_row("", "for_rent_amenities", 43,
    "Search for no-fee apartments for rent in Brooklyn with a gym, at least 1 bedroom, under $2,500 per month.",
    "https://streeteasy.com/for-rent/brooklyn/no_fee:1%7Camenities:gym%7Cbeds%3E=1%7Cprice:-2500",
    "hard"))

tasks.append(make_row("", "for_rent_amenities", 44,
    "Find apartments for rent in Manhattan with a pool under $6,000 per month with at least 1 bedroom.",
    "https://streeteasy.com/for-rent/manhattan/amenities:pool%7Cprice:-6000%7Cbeds%3E=1",
    "medium"))

tasks.append(make_row("", "for_rent_amenities", 45,
    "Search for pet-friendly apartments for rent in Brooklyn with in-unit laundry and a doorman, priced between $2,000 and $3,500 per month.",
    "https://streeteasy.com/for-rent/brooklyn/amenities:doorman,in_unit_laundry%7Cpets:allowed%7Cprice:2000-3500",
    "hard"))

tasks.append(make_row("", "for_rent_amenities", 46,
    "Find apartments for rent in Manhattan with a gym and doorman, at least 2 bedrooms, priced between $3,000 and $6,000 per month.",
    "https://streeteasy.com/for-rent/manhattan/amenities:doorman,gym%7Cbeds%3E=2%7Cprice:3000-6000",
    "hard"))

tasks.append(make_row("", "for_rent_amenities", 47,
    "Search for no-fee apartments for rent in Manhattan with an elevator, at least 1 bedroom, under $3,500 per month.",
    "https://streeteasy.com/for-rent/manhattan/no_fee:1%7Camenities:elevator%7Cbeds%3E=1%7Cprice:-3500",
    "medium"))

# ============================================================
# FOR RENT TRANSIT (tasks 48-54)
# ============================================================
tasks.append(make_row("", "for_rent_transit", 48,
    "Find no-fee 2+ bedroom rentals near the L train in Brooklyn under $4,000 per month with a gym.",
    "https://streeteasy.com/for-rent/brooklyn/beds%3E=2%7Cprice:-4000%7Cno_fee:1%7Ctransit_lines:L%7Camenities:gym",
    "hard"))

tasks.append(make_row("", "for_rent_transit", 49,
    "Search for apartments for rent near the 1 train in Manhattan with at least 1 bedroom under $3,000 per month.",
    "https://streeteasy.com/for-rent/manhattan/transit_lines:1%7Cbeds%3E=1%7Cprice:-3000",
    "medium"))

tasks.append(make_row("", "for_rent_transit", 50,
    "Find apartments for rent near the A train in Brooklyn under $3,000 per month.",
    "https://streeteasy.com/for-rent/brooklyn/transit_lines:A%7Cprice:-3000",
    "medium"))

tasks.append(make_row("", "for_rent_transit", 51,
    "Search for no-fee apartments for rent near the 7 train in Manhattan under $3,500 per month.",
    "https://streeteasy.com/for-rent/manhattan/transit_lines:7%7Cno_fee:1%7Cprice:-3500",
    "medium"))

tasks.append(make_row("", "for_rent_transit", 52,
    "Find no-fee apartments for rent near the G train in Brooklyn with at least 1 bedroom under $2,500 per month.",
    "https://streeteasy.com/for-rent/brooklyn/transit_lines:G%7Cno_fee:1%7Cbeds%3E=1%7Cprice:-2500",
    "hard"))

tasks.append(make_row("", "for_rent_transit", 53,
    "Search for apartments for rent near the ACE trains in Manhattan with at least 1 bedroom under $3,000 per month.",
    "https://streeteasy.com/for-rent/manhattan/transit_lines:ACE%7Cbeds%3E=1%7Cprice:-3000",
    "medium"))

tasks.append(make_row("", "for_rent_transit", 54,
    "Find pet-friendly apartments for rent near the L train in Brooklyn with in-unit laundry, at least 1 bedroom, under $3,500 per month.",
    "https://streeteasy.com/for-rent/brooklyn/transit_lines:L%7Cpets:allowed%7Camenities:in_unit_laundry%7Cbeds%3E=1%7Cprice:-3500",
    "hard"))

# ============================================================
# FOR RENT NEIGHBORHOOD (tasks 55-59)
# ============================================================
tasks.append(make_row("", "for_rent_neighborhood", 55,
    "Find apartments for rent on the Upper West Side with at least 2 bedrooms under $4,000 per month.",
    "https://streeteasy.com/for-rent/upper-west-side/beds%3E=2%7Cprice:-4000",
    "medium"))

tasks.append(make_row("", "for_rent_neighborhood", 56,
    "Search for apartments for rent in the East Village with at least 1 bedroom under $3,500 per month.",
    "https://streeteasy.com/for-rent/east-village/price:-3500%7Cbeds%3E=1",
    "medium"))

tasks.append(make_row("", "for_rent_neighborhood", 57,
    "Find pet-friendly apartments for rent in Park Slope with at least 2 bedrooms under $4,000 per month.",
    "https://streeteasy.com/for-rent/park-slope/beds%3E=2%7Cprice:-4000%7Cpets:allowed",
    "hard"))

tasks.append(make_row("", "for_rent_neighborhood", 58,
    "Search for studio apartments for rent in Midtown under $3,500 per month.",
    "https://streeteasy.com/for-rent/midtown/price:-3500%7Cbeds:0",
    "medium"))

tasks.append(make_row("", "for_rent_neighborhood", 59,
    "Find apartments for rent in Williamsburg under $3,000 per month with at least 1 bedroom.",
    "https://streeteasy.com/for-rent/williamsburg/price:-3000%7Cbeds%3E=1",
    "medium"))

# ============================================================
# SOLD / PAST SALES (tasks 60-65)
# ============================================================
tasks.append(make_row("", "sold", 60,
    "Find recently sold condos in Manhattan that sold for between $1,000,000 and $3,000,000 with 2+ bedrooms.",
    "https://streeteasy.com/for-sale/manhattan/type:D1%7Cprice:1000000-3000000%7Cbeds%3E=2%7Cstatus:sold",
    "medium"))

tasks.append(make_row("", "sold", 61,
    "Search for sold condos in Manhattan priced between $2,000,000 and $5,000,000 with at least 3 bedrooms.",
    "https://streeteasy.com/for-sale/manhattan/status:sold%7Ctype:D1%7Cprice:2000000-5000000%7Cbeds%3E=3",
    "hard"))

tasks.append(make_row("", "sold", 62,
    "Find sold co-ops in Brooklyn under $500,000.",
    "https://streeteasy.com/for-sale/brooklyn/type:P1%7Cprice:-500000%7Cstatus:sold",
    "medium"))

tasks.append(make_row("", "sold", 63,
    "Search for sold condos on the Upper East Side priced between $1,000,000 and $3,000,000.",
    "https://streeteasy.com/for-sale/upper-east-side/type:D1%7Cprice:1000000-3000000%7Cstatus:sold",
    "medium"))

tasks.append(make_row("", "sold", 64,
    "Find sold properties in Manhattan with at least 4 bedrooms that sold for over $5,000,000.",
    "https://streeteasy.com/for-sale/manhattan/beds%3E=4%7Cprice:5000000-%7Cstatus:sold",
    "hard"))

tasks.append(make_row("", "sold", 65,
    "Search for sold condos in Manhattan with 2+ bedrooms, a doorman, priced between $1,000,000 and $2,000,000.",
    "https://streeteasy.com/for-sale/manhattan/type:D1%7Cbeds%3E=2%7Camenities:doorman%7Cprice:1000000-2000000%7Cstatus:sold",
    "hard"))

# ============================================================
# FOR RENT COMPLEX (tasks 66-69)
# ============================================================
tasks.append(make_row("", "for_rent_complex", 66,
    "Find no-fee, pet-friendly apartments for rent in Manhattan with a doorman, at least 2 bedrooms, under $5,000 per month.",
    "https://streeteasy.com/for-rent/manhattan/no_fee:1%7Cpets:allowed%7Camenities:doorman%7Cbeds%3E=2%7Cprice:-5000",
    "hard"))

tasks.append(make_row("", "for_rent_complex", 67,
    "Search for furnished apartments for rent in Manhattan with a doorman and elevator, at least 1 bedroom, under $5,000 per month.",
    "https://streeteasy.com/for-rent/manhattan/furnished:1%7Camenities:doorman,elevator%7Cbeds%3E=1%7Cprice:-5000",
    "hard"))

tasks.append(make_row("", "for_rent_complex", 68,
    "Find no-fee apartments for rent near the L train in Brooklyn with a gym and doorman, at least 1 bedroom, under $3,000 per month.",
    "https://streeteasy.com/for-rent/brooklyn/no_fee:1%7Ctransit_lines:L%7Camenities:doorman,gym%7Cbeds%3E=1%7Cprice:-3000",
    "hard"))

tasks.append(make_row("", "for_rent_complex", 69,
    "Search for pet-friendly no-fee apartments for rent on the Upper West Side with at least 2 bedrooms under $4,500 per month.",
    "https://streeteasy.com/for-rent/upper-west-side/no_fee:1%7Cpets:allowed%7Cbeds%3E=2%7Cprice:-4500",
    "hard"))


# ============================================================
# Write CSV
# ============================================================
header = [
    "task_id", "task_generation_config_json", "env", "domain",
    "l1_category", "l2_category", "suggested_difficulty",
    "suggested_hint", "suggested_max_steps", "suggested_split", "metadata_json"
]

output_path = r"navi_bench\streeteasy\streeteasy_benchmark_tasks.xlsx - streeteasy_benchmark_tasks.csv"

with open(output_path, "w", newline="\r\n", encoding="utf-8") as f:
    # Write header
    f.write(",".join(header) + "\r\n")
    
    for i, task in enumerate(tasks):
        # Fix task_id
        category = task["task_generation_config_json"].split('"l2_category"')[0]  # Not needed
        
        # Extract the config JSON properly
        config_str = task["task_generation_config_json"]
        
        # Build the row manually to match the exact CSV format
        config = json.loads(config_str.strip('"').replace('""', '"'))
        gt_url = config["ground_truth_url"]
        task_desc = config["task"]
        l2 = task["l2_category"]
        difficulty = task["suggested_difficulty"]
        
        task_id = f"navi_bench/streeteasy/{l2}/{i}"
        
        # Build config JSON in the exact format of the XLSX
        inner_json = json.dumps({
            "_target_": "navi_bench.streeteasy.streeteasy_url_match.generate_task_config",
            "url": "https://streeteasy.com",
            "task": task_desc,
            "location": "New York, NY, United States",
            "timezone": "America/New_York",
            "ground_truth_url": gt_url
        })
        
        # CSV-escape: wrap in quotes, double internal quotes
        csv_json = '"' + inner_json.replace('"', '""') + '"'
        
        row = f"{task_id},{csv_json},real,streeteasy,realestate,{l2},{difficulty},null,null,validation,null"
        f.write(row + "\r\n")

print(f"Generated {len(tasks)} tasks to {output_path}")
