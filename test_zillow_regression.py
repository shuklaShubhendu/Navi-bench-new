"""
COMPREHENSIVE ZILLOW VERIFIER REGRESSION SUITE
================================================
Tests every encoding pattern the verifier must handle, using REAL
GT URLs from the benchmark.  Covers:

  1. Listing status — negative encoding (the bug that was just fixed)
  2. Listing status — positive encoding
  3. Listing status — mixed encoding (positive + negative)
  4. Property type  — negative encoding  (existing feature)
  5. Property type  — positive encoding
  6. Cross-format   — positive GT ↔ negative agent
  7. Rental URLs    — context flags must not pollute for-sale logic
  8. Null values     — {min:X, max:null} must not produce stale keys
  9. Range filters   — price, beds, sqft, lot, hoa
 10. Boolean filters — pool, gar, wat, view, etc.
 11. False-positive  — wrong agent URL must NOT match
 12. False-negative  — correct agent URL must match
 13. Location matching — city slug normalization
 14. Real GT URLs    — all 8 user-provided listing-status GT URLs
"""

import json, sys, os, asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from urllib.parse import quote, unquote
from navi_bench.zillow.zillow_url_match import ZillowUrlMatch


# =====================================================================
# HELPERS
# =====================================================================

def make_url(city_slug, filter_state, base="https://www.zillow.com/"):
    """Build a Zillow URL from city slug and filterState dict."""
    qs = json.dumps({"filterState": filter_state}, separators=(",", ":"))
    return f"{base}{city_slug}/?searchQueryState={quote(qs)}"


def make_url_with_region(city_slug, filter_state, region_id, region_type=6):
    """Build a Zillow URL with regionSelection (browser-style)."""
    state = {
        "pagination": {},
        "isMapVisible": True,
        "regionSelection": [{"regionId": region_id, "regionType": region_type}],
        "filterState": filter_state,
        "isListVisible": True,
    }
    qs = json.dumps(state, separators=(",", ":"))
    return f"https://www.zillow.com/{city_slug}/?searchQueryState={quote(qs)}"


passed = 0
failed = 0
errors = []


def test(name, gt_url, agent_url, expect_match=True):
    """Run a single test case."""
    global passed, failed
    verifier = ZillowUrlMatch(ground_truth_url=gt_url)
    match, details = verifier._urls_match(agent_url, gt_url)
    ok = match == expect_match
    if ok:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        reason = ""
        if details.get("mismatches"):
            reason = f" — {details['mismatches']}"
        elif match and not expect_match:
            reason = " — UNEXPECTED MATCH (false positive)"
        errors.append(f"{name}{reason}")
        print(f"  ❌ {name}{reason}")


# =====================================================================
# 1. LISTING STATUS — NEGATIVE ENCODING (Real GT URLs)
# =====================================================================
print("\n" + "=" * 75)
print("1. LISTING STATUS — NEGATIVE ENCODING (Real GT URLs)")
print("=" * 75)

# Task 32: New Construction in Phoenix — negative encoding
gt32 = "https://www.zillow.com/phoenix-az/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-112.65928120507812%2C%22east%22%3A-111.59086079492187%2C%22south%22%3A33.26390266119177%2C%22north%22%3A33.94672738516707%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A40326%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22price%22%3A%7B%22max%22%3A600000%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22usersSearchTerm%22%3A%22Phoenix%20AZ%22%7D"
# Agent uses positive encoding
agent32_pos = make_url("Phoenix,-AZ_rb", {"nc": {"value": True}, "price": {"max": 600000}})
test("Task 32 NC: positive agent matches negative GT", gt32, agent32_pos)

# Agent uses same negative encoding
agent32_neg = make_url("phoenix-az", {"fsba": {"value": False}, "fsbo": {"value": False}, "fore": {"value": False}, "auc": {"value": False}, "price": {"max": 600000}})
test("Task 32 NC: negative agent matches negative GT", gt32, agent32_neg)

# Agent has NO listing status → should FAIL
agent32_none = make_url("phoenix-az", {"price": {"max": 600000}})
test("Task 32 NC: agent with no listing status must FAIL", gt32, agent32_none, expect_match=False)

# Agent has wrong listing status → should FAIL
agent32_wrong = make_url("phoenix-az", {"fore": {"value": True}, "price": {"max": 600000}})
test("Task 32 NC: agent with 'fore' instead of 'nc' must FAIL", gt32, agent32_wrong, expect_match=False)


# Task 33: Foreclosure in Detroit — negative encoding
gt33 = "https://www.zillow.com/detroit-mi/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-83.36631010253906%2C%22east%22%3A-82.83209989746094%2C%22south%22%3A42.20113380087625%2C%22north%22%3A42.504074466535435%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A17762%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A11%2C%22usersSearchTerm%22%3A%22Detroit%20MI%22%7D"
agent33 = make_url("detroit-mi", {"fore": {"value": True}})
test("Task 33 FORE: positive agent matches negative GT", gt33, agent33)
agent33_empty = "https://www.zillow.com/detroit-mi/"
test("Task 33 FORE: empty agent must FAIL (was false positive before fix)", gt33, agent33_empty, expect_match=False)

# Task 34: Auction in Las Vegas — negative encoding
gt34 = "https://www.zillow.com/las-vegas-nv/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-115.82287920507812%2C%22east%22%3A-114.75445879492187%2C%22south%22%3A35.88545000852659%2C%22north%22%3A36.546895924281515%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A18959%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22usersSearchTerm%22%3A%22Las%20Vegas%20NV%22%7D"
agent34 = make_url("las-vegas-nv", {"auc": {"value": True}})
test("Task 34 AUC: positive agent matches negative GT", gt34, agent34)
agent34_empty = "https://www.zillow.com/las-vegas-nv/"
test("Task 34 AUC: empty agent must FAIL (was false positive before fix)", gt34, agent34_empty, expect_match=False)

# Task 35: FSBO in San Antonio — negative encoding
gt35 = "https://www.zillow.com/san-antonio-tx/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-99.29006323828123%2C%22east%22%3A-97.83437476171873%2C%22south%22%3A28.89090633930402%2C%22north%22%3A29.967358877616057%7D%2C%22usersSearchTerm%22%3A%22San%20Antonio%20TX%22%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A6915%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22beds%22%3A%7B%22min%22%3A3%2C%22max%22%3Anull%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A9%7D"
agent35 = make_url("san-antonio-tx", {"fsbo": {"value": True}, "beds": {"min": 3}})
test("Task 35 FSBO: positive agent matches negative GT", gt35, agent35)
agent35_beds_only = make_url("san-antonio-tx", {"beds": {"min": 3}})
test("Task 35 FSBO: agent with only beds (no fsbo) must FAIL", gt35, agent35_beds_only, expect_match=False)

# Task 39: NC + beds + hoa in Charlotte — negative encoding
gt39 = "https://www.zillow.com/charlotte-nc/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-81.32573926562499%2C%22east%22%3A-80.33696973437499%2C%22south%22%3A34.81521166382033%2C%22north%22%3A35.60176372413327%7D%2C%22usersSearchTerm%22%3A%22Charlotte%20NC%22%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A24043%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22days%22%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22beds%22%3A%7B%22min%22%3A4%2C%22max%22%3Anull%7D%2C%22hoa%22%3A%7B%22min%22%3Anull%7D%7D%2C%22isListVisible%22%3Atrue%7D"
agent39 = make_url("charlotte-nc", {"nc": {"value": True}, "beds": {"min": 4}})
test("Task 39 NC+beds: positive agent matches negative GT", gt39, agent39)
agent39_no_nc = make_url("charlotte-nc", {"beds": {"min": 4}})
test("Task 39 NC+beds: agent without nc must FAIL", gt39, agent39_no_nc, expect_match=False)


# =====================================================================
# 2. LISTING STATUS — POSITIVE ENCODING
# =====================================================================
print("\n" + "=" * 75)
print("2. LISTING STATUS — POSITIVE ENCODING")
print("=" * 75)

gt_nc = make_url("Phoenix,-AZ_rb", {"nc": {"value": True}, "price": {"max": 600000}})
agent_nc = make_url("phoenix-az", {"nc": {"value": True}, "price": {"max": 600000}})
test("NC positive: both positive → match", gt_nc, agent_nc)

gt_fore = make_url("Detroit,-MI_rb", {"fore": {"value": True}})
agent_fore = make_url("detroit-mi", {"fore": {"value": True}})
test("FORE positive: both positive → match", gt_fore, agent_fore)

gt_fsbo = make_url("San-Antonio,-TX_rb", {"fsbo": {"value": True}, "beds": {"min": 3}})
agent_fsbo = make_url("san-antonio-tx", {"fsbo": {"value": True}, "beds": {"min": 3}})
test("FSBO positive: both positive → match", gt_fsbo, agent_fsbo)


# =====================================================================
# 3. LISTING STATUS — MIXED ENCODING (positive + negative)
# =====================================================================
print("\n" + "=" * 75)
print("3. LISTING STATUS — MIXED ENCODING (Real GT: Task 37)")
print("=" * 75)

gt37 = "https://www.zillow.com/tampa-fl/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-82.81820261914064%2C%22east%22%3A-82.09035838085939%2C%22south%22%3A27.721447246725198%2C%22north%22%3A28.26711776597611%7D%2C%22usersSearchTerm%22%3A%22Tampa%20FL%22%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A41176%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22pf%22%3A%7B%22value%22%3Atrue%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%7D"
# pf is positive, others are negative → pf is the primary status
agent37 = make_url("tampa-fl", {"pf": {"value": True}})
test("Task 37 PF: positive agent matches mixed GT", gt37, agent37)
agent37_wrong = make_url("tampa-fl", {"fore": {"value": True}})
test("Task 37 PF: agent with 'fore' must FAIL", gt37, agent37_wrong, expect_match=False)

# Task 38: Pending + price (positive encoding only)
gt38 = "https://www.zillow.com/columbus-oh/?searchQueryState=%7B%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22north%22%3A40.18017179877639%2C%22south%22%3A39.811423956601054%2C%22east%22%3A-82.74653761718749%2C%22west%22%3A-83.24092238281249%7D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22price%22%3A%7B%22max%22%3A400000%7D%2C%22pnd%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%2C%22listPriceActive%22%3Atrue%2C%22curatedCollection%22%3Anull%2C%22usersSearchTerm%22%3A%22Columbus%20OH%22%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A10920%2C%22regionType%22%3A6%7D%5D%2C%22mapZoom%22%3A11%2C%22pagination%22%3A%7B%7D%7D"
agent38 = make_url("columbus-oh", {"pnd": {"value": True}, "price": {"max": 400000}})
test("Task 38 PND+price: positive agent matches positive GT", gt38, agent38)
agent38_no_pnd = make_url("columbus-oh", {"price": {"max": 400000}})
test("Task 38 PND+price: agent without pnd must FAIL", gt38, agent38_no_pnd, expect_match=False)


# =====================================================================
# 4. PROPERTY TYPE — NEGATIVE ENCODING
# =====================================================================
print("\n" + "=" * 75)
print("4. PROPERTY TYPE — NEGATIVE ENCODING")
print("=" * 75)

# Task 31: Houses only in Orlando (lot filter) — negative prop encoding
gt31 = "https://www.zillow.com/orlando-fl/houses/?category=SEMANTIC&searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-82.25621353124998%2C%22east%22%3A-80.27867446874998%2C%22south%22%3A27.644221910643168%2C%22north%22%3A29.336314249584703%7D%2C%22usersSearchTerm%22%3A%22Orlando%20FL%22%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A13121%2C%22regionType%22%3A6%7D%5D%2C%22filterState%22%3A%7B%22sort%22%3A%7B%22value%22%3A%22globalrelevanceex%22%7D%2C%22lot%22%3A%7B%22min%22%3A10890%2C%22max%22%3Anull%2C%22units%22%3Anull%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22apco%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A9%7D"
# Agent uses positive property type
agent31 = make_url("orlando-fl", {"isHouse": {"value": True}, "lot": {"min": 10890}})
test("Task 31 Houses+lot: positive agent matches negative GT", gt31, agent31)

# Agent uses negative property type (same as GT)
agent31_neg = make_url("orlando-fl", {
    "tow": {"value": False}, "mf": {"value": False}, "con": {"value": False},
    "land": {"value": False}, "apa": {"value": False}, "apco": {"value": False},
    "manu": {"value": False}, "lot": {"min": 10890}
})
test("Task 31 Houses+lot: negative agent matches negative GT", gt31, agent31_neg)

# Agent selects condos instead → should FAIL
agent31_condo = make_url("orlando-fl", {"isCondo": {"value": True}, "lot": {"min": 10890}})
test("Task 31 Houses+lot: wrong property type (condo) must FAIL", gt31, agent31_condo, expect_match=False)


# =====================================================================
# 5. PROPERTY TYPE — POSITIVE ENCODING
# =====================================================================
print("\n" + "=" * 75)
print("5. PROPERTY TYPE — POSITIVE ENCODING")
print("=" * 75)

gt_house = make_url("Seattle,-WA_rb", {"isHouse": {"value": True}, "price": {"max": 900000}})
agent_house = make_url("seattle-wa", {"isHouse": {"value": True}, "price": {"max": 900000}})
test("House positive: both positive → match", gt_house, agent_house)

gt_condo = make_url("Chicago,-IL_rb", {"isCondo": {"value": True}, "beds": {"min": 2}})
agent_condo = make_url("chicago-il", {"isCondo": {"value": True}, "beds": {"min": 2}})
test("Condo positive: both positive → match", gt_condo, agent_condo)


# =====================================================================
# 6. CROSS-FORMAT — POSITIVE GT ↔ NEGATIVE AGENT
# =====================================================================
print("\n" + "=" * 75)
print("6. CROSS-FORMAT — POSITIVE GT ↔ NEGATIVE AGENT")
print("=" * 75)

# GT uses positive, agent uses negative → should MATCH
gt_pos_nc = make_url("Phoenix,-AZ_rb", {"nc": {"value": True}})
agent_neg_nc = make_url("phoenix-az", {
    "fsba": {"value": False}, "fsbo": {"value": False},
    "fore": {"value": False}, "auc": {"value": False}
})
test("Cross: positive GT nc ↔ negative agent → match", gt_pos_nc, agent_neg_nc)

gt_pos_house = make_url("Miami,-FL_rb", {"isHouse": {"value": True}})
agent_neg_house = make_url("miami-fl", {
    "tow": {"value": False}, "mf": {"value": False}, "con": {"value": False},
    "land": {"value": False}, "apa": {"value": False}, "apco": {"value": False},
    "manu": {"value": False}
})
test("Cross: positive GT isHouse ↔ negative agent → match", gt_pos_house, agent_neg_house)

# GT uses negative, agent uses positive → should MATCH
gt_neg_fore = make_url("Detroit,-MI_rb", {
    "auc": {"value": False}, "nc": {"value": False},
    "fsba": {"value": False}, "fsbo": {"value": False}
})
agent_pos_fore = make_url("detroit-mi", {"fore": {"value": True}})
test("Cross: negative GT fore ↔ positive agent → match", gt_neg_fore, agent_pos_fore)


# =====================================================================
# 7. RENTAL URLs — CONTEXT FLAGS SAFE
# =====================================================================
print("\n" + "=" * 75)
print("7. RENTAL URLs — CONTEXT FLAGS SAFE")
print("=" * 75)

def make_rent_url(city_slug, filter_state):
    """Build a Zillow for-rent URL."""
    qs = json.dumps({"filterState": filter_state}, separators=(",", ":"))
    return f"https://www.zillow.com/homes/for_rent/{city_slug}/?searchQueryState={quote(qs)}"

RENT_BASE = {
    "fr": {"value": True},
    "fsba": {"value": False},
    "fsbo": {"value": False},
    "nc": {"value": False},
    "cmsn": {"value": False},
    "auc": {"value": False},
    "fore": {"value": False},
}

# Rental GT and agent with all context flags
gt_rent = make_rent_url("new-york-ny", {**RENT_BASE, "beds": {"min": 1}, "mp": {"max": 3000}})
agent_rent = make_rent_url("new-york-ny", {**RENT_BASE, "beds": {"min": 1}, "mp": {"max": 3000}})
test("Rental: matching GT and agent with all context flags", gt_rent, agent_rent)

# Rental: agent without context flags but with same filters → should still match
agent_rent_simple = make_rent_url("new-york-ny", {"beds": {"min": 1}, "mp": {"max": 3000}})
test("Rental: agent without context flags (simpler) → match", gt_rent, agent_rent_simple)

# Rental GT should NOT match a for-sale agent
agent_sale = make_url("new-york-ny", {"beds": {"min": 1}, "price": {"max": 3000}})
test("Rental GT must NOT match for-sale agent", gt_rent, agent_sale, expect_match=False)

# Rental with dogs
gt_rent_dogs = make_rent_url("los-angeles-ca", {**RENT_BASE, "beds": {"min": 2}, "mp": {"max": 2500},
     "ldog": {"value": True}, "sdog": {"value": True}})
agent_rent_dogs = make_rent_url("los-angeles-ca", {"beds": {"min": 2}, "mp": {"max": 2500},
     "ldog": {"value": True}, "sdog": {"value": True}})
test("Rental dogs: matching dog filters", gt_rent_dogs, agent_rent_dogs)

# Rental missing dog filter should FAIL
agent_rent_no_dog = make_rent_url("los-angeles-ca", {"beds": {"min": 2}, "mp": {"max": 2500}})
test("Rental dogs: agent without dog filters must FAIL", gt_rent_dogs, agent_rent_no_dog, expect_match=False)


# =====================================================================
# 8. NULL VALUES IN RANGE FILTERS
# =====================================================================
print("\n" + "=" * 75)
print("8. NULL VALUES IN RANGE FILTERS")
print("=" * 75)

# beds: {min: 3, max: null} — max:null should be ignored
gt_null = make_url("san-antonio-tx", {"beds": {"min": 3, "max": None}})
agent_null = make_url("san-antonio-tx", {"beds": {"min": 3}})
test("Null max in beds: {min:3, max:null} ↔ {min:3} → match", gt_null, agent_null)

# hoa: {min: null} — min:null should produce empty (no filter)
gt_hoa_null = make_url("charlotte-nc", {"hoa": {"min": None}})
agent_hoa_none = make_url("charlotte-nc", {})
test("Null-only range: {min:null} produces no filter → match", gt_hoa_null, agent_hoa_none)

# lot: {min: 10890, max: null, units: null}
gt_lot_null = make_url("orlando-fl", {"lot": {"min": 10890, "max": None, "units": None}})
agent_lot = make_url("orlando-fl", {"lot": {"min": 10890}})
test("Lot with null max/units: match", gt_lot_null, agent_lot)


# =====================================================================
# 9. RANGE FILTERS — PRICE, BEDS, SQFT, HOA
# =====================================================================
print("\n" + "=" * 75)
print("9. RANGE FILTERS — PRICE, BEDS, SQFT, HOA")
print("=" * 75)

gt_price = make_url("Austin,-TX_rb", {"price": {"min": 200000, "max": 600000}})
agent_price = make_url("austin-tx", {"price": {"min": 200000, "max": 600000}})
test("Price range: exact match", gt_price, agent_price)

gt_price_max = make_url("Austin,-TX_rb", {"price": {"max": 600000}})
agent_price_max = make_url("austin-tx", {"price": {"max": 600000}})
test("Price max only: match", gt_price_max, agent_price_max)

gt_price_wrong = make_url("Austin,-TX_rb", {"price": {"max": 600000}})
agent_price_wrong = make_url("austin-tx", {"price": {"max": 500000}})
test("Price max mismatch: must FAIL", gt_price_wrong, agent_price_wrong, expect_match=False)

gt_hoa = make_url("Scottsdale,-AZ_rb", {"hoa": {"max": 0}})
agent_hoa = make_url("scottsdale-az", {"hoa": {"max": 0}})
test("HOA max 0 (no HOA): match", gt_hoa, agent_hoa)

gt_sqft = make_url("Denver,-CO_rb", {"sqft": {"min": 1500}})
agent_sqft = make_url("denver-co", {"sqft": {"min": 1500}})
test("Sqft min: match", gt_sqft, agent_sqft)


# =====================================================================
# 10. BOOLEAN FILTERS — POOL, GAR, WAT, VIEW, etc.
# =====================================================================
print("\n" + "=" * 75)
print("10. BOOLEAN FILTERS — POOL, GAR, WAT, VIEW, etc.")
print("=" * 75)

gt_pool = make_url("Miami,-FL_rb", {"pool": {"value": True}})
agent_pool = make_url("miami-fl", {"pool": {"value": True}})
test("Pool filter: match", gt_pool, agent_pool)

gt_gar = make_url("Seattle,-WA_rb", {"gar": {"value": True}})
agent_gar = make_url("seattle-wa", {"gar": {"value": True}})
test("Garage filter: match", gt_gar, agent_gar)

gt_wat = make_url("Miami,-FL_rb", {"wat": {"value": True}})
agent_wat = make_url("miami-fl", {"wat": {"value": True}})
test("Waterfront filter: match", gt_wat, agent_wat)

gt_view = make_url("SF_rb", {"view": {"value": True}})
agent_view = make_url("sf", {"view": {"value": True}})
test("View filter: match", gt_view, agent_view)

gt_single = make_url("Seattle,-WA_rb", {"isSingleStory": {"value": True}})
agent_single = make_url("seattle-wa", {"isSingleStory": {"value": True}})
test("Single story filter: match", gt_single, agent_single)

gt_lau = make_url("SF_rb", {"lau": {"value": True}})
agent_lau = make_url("sf", {"lau": {"value": True}})
test("Laundry filter: match", gt_lau, agent_lau)


# =====================================================================
# 11. FALSE POSITIVE TESTS — WRONG AGENT MUST NOT MATCH
# =====================================================================
print("\n" + "=" * 75)
print("11. FALSE POSITIVE TESTS — WRONG AGENT MUST NOT MATCH")
print("=" * 75)

gt_complex = make_url("Phoenix,-AZ_rb", {
    "isHouse": {"value": True}, "pool": {"value": True},
    "hoa": {"max": 0}, "beds": {"min": 4}, "price": {"max": 500000}
})

test("Wrong city: must FAIL",
     gt_complex, make_url("Denver,-CO_rb", {
         "isHouse": {"value": True}, "pool": {"value": True},
         "hoa": {"max": 0}, "beds": {"min": 4}, "price": {"max": 500000}
     }), expect_match=False)

test("Missing pool filter: must FAIL",
     gt_complex, make_url("Phoenix,-AZ_rb", {
         "isHouse": {"value": True},
         "hoa": {"max": 0}, "beds": {"min": 4}, "price": {"max": 500000}
     }), expect_match=False)

test("Wrong price: must FAIL",
     gt_complex, make_url("Phoenix,-AZ_rb", {
         "isHouse": {"value": True}, "pool": {"value": True},
         "hoa": {"max": 0}, "beds": {"min": 4}, "price": {"max": 700000}
     }), expect_match=False)

test("Wrong property type: must FAIL",
     gt_complex, make_url("Phoenix,-AZ_rb", {
         "isCondo": {"value": True}, "pool": {"value": True},
         "hoa": {"max": 0}, "beds": {"min": 4}, "price": {"max": 500000}
     }), expect_match=False)

test("Completely empty agent: must FAIL",
     gt_complex, "https://www.zillow.com/Phoenix,-AZ_rb/", expect_match=False)


# =====================================================================
# 12. FALSE NEGATIVE TESTS — CORRECT AGENT MUST MATCH
# =====================================================================
print("\n" + "=" * 75)
print("12. FALSE NEGATIVE TESTS — CORRECT AGENT MUST MATCH")
print("=" * 75)

# Agent has EXTRA filters (should still match)
test("Agent with extra filters: still matches",
     gt_complex, make_url("Phoenix,-AZ_rb", {
         "isHouse": {"value": True}, "pool": {"value": True},
         "hoa": {"max": 0}, "beds": {"min": 4}, "price": {"max": 500000},
         "gar": {"value": True}  # Extra filter
     }))

# Agent has sort (should be ignored)
agent_with_sort = make_url("Phoenix,-AZ_rb", {
    "isHouse": {"value": True}, "pool": {"value": True},
    "hoa": {"max": 0}, "beds": {"min": 4}, "price": {"max": 500000},
    "sort": {"value": "globalrelevanceex"}
})
test("Agent with sort param: still matches (sort ignored)", gt_complex, agent_with_sort)


# =====================================================================
# 13. LOCATION MATCHING — CITY SLUG NORMALIZATION
# =====================================================================
print("\n" + "=" * 75)
print("13. LOCATION MATCHING — CITY SLUG NORMALIZATION")
print("=" * 75)

gt_loc = make_url("Phoenix,-AZ_rb", {"nc": {"value": True}})
test("Location: Phoenix,-AZ_rb ↔ phoenix-az",
     gt_loc, make_url("phoenix-az", {"nc": {"value": True}}))

gt_loc2 = make_url("san-antonio-tx", {"fore": {"value": True}})
test("Location: san-antonio-tx ↔ San-Antonio,-TX_rb",
     gt_loc2, make_url("San-Antonio,-TX_rb", {"fore": {"value": True}}))


# =====================================================================
# 14. COMBINED LISTING STATUS + PROPERTY TYPE (BOTH NEGATIVE)
# =====================================================================
print("\n" + "=" * 75)
print("14. COMBINED: LISTING STATUS + PROPERTY TYPE (BOTH NEGATIVE)")
print("=" * 75)

# GT has both property type negative encoding AND listing status negative encoding
gt_both_neg = make_url("charlotte-nc", {
    # Property type: houses only (all others false)
    "tow": {"value": False}, "mf": {"value": False}, "con": {"value": False},
    "land": {"value": False}, "apa": {"value": False}, "apco": {"value": False},
    "manu": {"value": False},
    # Listing status: NC only (all others false)
    "fsba": {"value": False}, "fsbo": {"value": False},
    "auc": {"value": False}, "fore": {"value": False},
    # Extra filters
    "beds": {"min": 4},
})
# Agent uses positive encoding for both
agent_both_pos = make_url("charlotte-nc", {
    "isHouse": {"value": True}, "nc": {"value": True}, "beds": {"min": 4}
})
test("Both negative GT ↔ both positive agent → match", gt_both_neg, agent_both_pos)

# Agent uses negative for prop type but positive for listing status
agent_mixed = make_url("charlotte-nc", {
    "tow": {"value": False}, "mf": {"value": False}, "con": {"value": False},
    "land": {"value": False}, "apa": {"value": False}, "apco": {"value": False},
    "manu": {"value": False},
    "nc": {"value": True}, "beds": {"min": 4}
})
test("Neg prop type + positive listing status → match", gt_both_neg, agent_mixed)


# =====================================================================
# SUMMARY
# =====================================================================
print("\n" + "=" * 75)
total = passed + failed
print(f"RESULTS: {passed}/{total} tests passed ({100*passed/total:.1f}%)")
if failed:
    print(f"\n❌ {failed} FAILED tests:")
    for e in errors:
        print(f"   • {e}")
else:
    print("🎉 ALL TESTS PASSED — ZERO REGRESSIONS!")
print("=" * 75)

sys.exit(0 if failed == 0 else 1)
