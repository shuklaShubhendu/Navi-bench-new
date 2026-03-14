"""
Address ALL reviewer concerns - verify each one is handled.
Then fix CSV1 data to match CSV2.
"""
import csv, json, sys, os, asyncio, re
sys.path.insert(0, '.')
from navi_bench.realtor.realtor_url_match import RealtorUrlMatch

print("=" * 70)
print("REVIEWER CONCERN VERIFICATION")
print("=" * 70)

v = RealtorUrlMatch(gt_url="https://www.realtor.com")

# ---- CONCERN 1: shw-nc ----
print("\n1. shw-nc parsing:")
p = v._parse_realtor_url("https://www.realtor.com/realestateandhomes-search/Phoenix_AZ/shw-nc")
nc = p["filters"].get("show-new-construction")
print("   shw-nc -> show-new-construction=%s  %s" % (nc, "PASS" if nc == "true" else "FAIL"))

# ---- CONCERN 2: hoa-500,known ----
print("\n2. hoa-500,known parsing:")
p = v._parse_realtor_url("https://www.realtor.com/realestateandhomes-search/Phoenix_AZ/hoa-500,known")
hoa = p["filters"].get("hoa")
print("   hoa-500,known -> hoa=%s  %s" % (hoa, "PASS" if hoa == "na-500" else "FAIL"))

# ---- CONCERN 3: soldwithin-N ----
print("\n3. soldwithin-N parsing:")
for months, expected_days in [("1", "30"), ("3", "90")]:
    p = v._parse_realtor_url("https://www.realtor.com/realestateandhomes-search/city/soldwithin-%s" % months)
    sw = p["filters"].get("sold-within")
    print("   soldwithin-%s -> sold-within=%s (expect %s)  %s" % (months, sw, expected_days, "PASS" if sw == expected_days else "FAIL"))

# ---- CONCERN 4: soldwithin implies show-recently-sold for matching ----
print("\n4. soldwithin implies sold (equivalence matching):")
async def test_sold_equiv():
    # GT has soldwithin-1 (no show-recently-sold), agent uses show-recently-sold + sold-within-30
    gt_url = "https://www.realtor.com/realestateandhomes-search/Miami_FL/type-condo/beds-2/price-300000-700000/soldwithin-1"
    agent_url = "https://www.realtor.com/realestateandhomes-search/Miami_FL/show-recently-sold/sold-within-30/type-condo/beds-2/price-300000-700000"
    vv = RealtorUrlMatch(gt_url=gt_url)
    await vv.reset()
    await vv.update(url=agent_url)
    result = await vv.compute()
    print("   GT(soldwithin-1) vs Agent(show-recently-sold/sold-within-30): score=%s  %s" % (result.score, "PASS" if result.score == 1.0 else "FAIL"))
    
    # GT has soldwithin-1, agent uses sold-homes path
    agent_url2 = "https://www.realtor.com/sold-homes/Miami_FL/type-condo/beds-2/price-300000-700000/sold-within-30"
    vv2 = RealtorUrlMatch(gt_url=gt_url)
    await vv2.reset()
    await vv2.update(url=agent_url2)
    result2 = await vv2.compute()
    print("   GT(soldwithin-1) vs Agent(/sold-homes/ + sold-within-30): score=%s  %s" % (result2.score, "PASS" if result2.score == 1.0 else "FAIL"))

asyncio.run(test_sold_equiv())

# ---- CONCERN 5: with_petsallowed (check if in CSV2) ----
print("\n5. with_petsallowed check:")
for csv_name in ["realtor_benchmark_tasks.csv", "realtor_benchmark_tasks2.csv"]:
    path = "navi_bench/realtor/%s" % csv_name
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if "with_petsallowed" in content:
        print("   %s: CONTAINS with_petsallowed - NEEDS FIX!" % csv_name)
    else:
        print("   %s: No with_petsallowed found - OK" % csv_name)
# Also check verifier handles it
p = v._parse_realtor_url("https://www.realtor.com/apartments/SF_CA/with_petsallowed")
print("   Verifier parses with_petsallowed: filters=%s" % p["filters"])

# ---- CONCERN 6: type-apartments stripping ----
print("\n6. type-apartments stripping in rental comparison:")
async def test_type_apt():
    # GT has type-apartments, agent doesn't
    gt = "https://www.realtor.com/apartments/SF_CA/type-apartments/beds-2/price-na-3000"
    agent = "https://www.realtor.com/apartments/SF_CA/beds-2/price-na-3000"
    vv = RealtorUrlMatch(gt_url=gt)
    await vv.reset()
    await vv.update(url=agent)
    result = await vv.compute()
    print("   GT(type-apartments) vs Agent(no type): score=%s  %s" % (result.score, "PASS" if result.score == 1.0 else "FAIL"))
    
    # Reverse
    vv2 = RealtorUrlMatch(gt_url=agent)
    await vv2.reset()
    await vv2.update(url=gt)
    result2 = await vv2.compute()
    print("   GT(no type) vs Agent(type-apartments): score=%s  %s" % (result2.score, "PASS" if result2.score == 1.0 else "FAIL"))

asyncio.run(test_type_apt())

# ---- CONCERN 7: type-townhome,condo ----
print("\n7. type-townhome,condo vs type-condo/type-townhome:")
async def test_comma_type():
    gt = "https://www.realtor.com/realestateandhomes-search/SF_CA/type-townhome,condo"
    agent = "https://www.realtor.com/realestateandhomes-search/SF_CA/type-condo/type-townhome"
    vv = RealtorUrlMatch(gt_url=gt)
    await vv.reset()
    await vv.update(url=agent)
    result = await vv.compute()
    print("   GT(type-townhome,condo) vs Agent(type-condo/type-townhome): score=%s  %s" % (result.score, "PASS" if result.score == 1.0 else "FAIL"))

asyncio.run(test_comma_type())

# ---- CONCERN 8: age single-value ----
print("\n8. age single-value normalization:")
async def test_age():
    gt = "https://www.realtor.com/realestateandhomes-search/Denver_CO/age-10"
    agent = "https://www.realtor.com/realestateandhomes-search/Denver_CO/age-0-10"
    vv = RealtorUrlMatch(gt_url=gt)
    await vv.reset()
    await vv.update(url=agent)
    result = await vv.compute()
    print("   GT(age-10) vs Agent(age-0-10): score=%s  %s" % (result.score, "PASS" if result.score == 1.0 else "FAIL"))

asyncio.run(test_age())

# ---- CONCERN 9: Garbage row in CSV2 ----
print("\n9. Garbage row check:")
for csv_name in ["realtor_benchmark_tasks.csv", "realtor_benchmark_tasks2.csv"]:
    path = "navi_bench/realtor/%s" % csv_name
    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    empty_ids = [i for i, r in enumerate(rows) if not r.get("task_id", "").strip()]
    print("   %s: %d rows, empty task_ids at indices: %s" % (csv_name, len(rows), empty_ids if empty_ids else "none"))

# ---- FULL SELF-MATCH both CSVs ----
print("\n10. Full self-match:")
for csv_name in ["realtor_benchmark_tasks.csv", "realtor_benchmark_tasks2.csv"]:
    path = "navi_bench/realtor/%s" % csv_name
    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    async def run():
        p, f = 0, []
        for row in rows:
            cfg = json.loads(row["task_generation_config_json"])
            gt = cfg["gt_url"]
            vv = RealtorUrlMatch(gt_url=gt)
            await vv.reset()
            url = gt if isinstance(gt, str) else gt[0]
            await vv.update(url=url)
            result = await vv.compute()
            if result.score == 1.0: p += 1
            else: f.append(row["task_id"])
        return p, f
    p, f = asyncio.run(run())
    status = "ALL PASS" if not f else "FAIL: " + ", ".join(f)
    print("   %s: %d/%d (%s)" % (csv_name, p, len(rows), status))

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)
