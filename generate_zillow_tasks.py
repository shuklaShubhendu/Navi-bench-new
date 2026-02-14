"""Generate 70 Zillow benchmark tasks in CSV format matching navi-bench schema."""
import csv
import json
import os
from urllib.parse import quote

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "navi_bench", "zillow", "zillow_benchmark_tasks.csv")

TARGET = "navi_bench.zillow.zillow_url_match.generate_task_config"
BASE_URL = "https://www.zillow.com/homes/for_sale/"
RENT_URL = "https://www.zillow.com/homes/for_rent/"
SOLD_URL = "https://www.zillow.com/homes/recently_sold/"

# Schema columns
FIELDS = [
    "task_id", "task_generation_config_json", "env", "domain",
    "l1_category", "l2_category", "suggested_difficulty",
    "suggested_hint", "suggested_max_steps", "suggested_split", "metadata_json"
]

# ---------------------------------------------------------------------------
# Zillow property type negative encoding
#
# Zillow uses abbreviated keys and NEGATIVE encoding for property types.
# To select "Condos only", it sets ALL OTHER types to false:
#   sf:false, tow:false, mf:false, land:false, apa:false, manu:false
#   (con is absent → condos are shown)
#
# Abbreviation mapping:
#   sf   = Houses (single family)
#   tow  = Townhomes
#   mf   = Multi-family
#   con  = Condos
#   land = Lots/Land
#   apa  = Apartments
#   manu = Manufactured
# ---------------------------------------------------------------------------
ALL_TYPE_ABBREVS = {"sf", "tow", "mf", "con", "land", "apa", "manu"}

CANONICAL_TO_ABBREV = {
    "isHouse": "sf",
    "isTownhouse": "tow",
    "isMultiFamily": "mf",
    "isCondo": "con",
    "isLotLand": "land",
    "isApartment": "apa",
    "isManufactured": "manu",
}


def property_type_filters(*selected_canonical_keys):
    """
    Convert positive property type keys to Zillow's negative encoding.

    Example:
        property_type_filters("isHouse")
        → {"tow":{"value":false},"mf":{"value":false},"con":{"value":false},
           "land":{"value":false},"apa":{"value":false},"manu":{"value":false}}

        property_type_filters("isHouse", "isCondo")
        → {"tow":{"value":false},"mf":{"value":false},
           "land":{"value":false},"apa":{"value":false},"manu":{"value":false}}
    """
    selected_abbrevs = set()
    for key in selected_canonical_keys:
        abbrev = CANONICAL_TO_ABBREV.get(key)
        if abbrev:
            selected_abbrevs.add(abbrev)

    # Set all NON-selected types to false
    filters = {}
    for abbrev in sorted(ALL_TYPE_ABBREVS - selected_abbrevs):
        filters[abbrev] = {"value": False}
    return filters


def make_gt_url(base, location_slug, filter_state_dict):
    """Build a ground truth Zillow URL from parts (URL-encoded for browser use)."""
    qs = json.dumps({"filterState": filter_state_dict}, separators=(",", ":"))
    loc = f"{location_slug}/" if location_slug else ""
    return f"{base}{loc}?searchQueryState={quote(qs)}"


def make_row(idx, l2, task_text, gt_url, *, location, timezone,
             difficulty="medium", hint=None, max_steps=None,
             split="validation", url=BASE_URL):
    config = {
        "_target_": TARGET,
        "url": url,
        "task": task_text,
        "location": location,
        "timezone": timezone,
        "ground_truth_url": gt_url,
    }
    return {
        "task_id": f"navi_bench/zillow/{l2}/{idx}",
        "task_generation_config_json": json.dumps(config),
        "env": "real",
        "domain": "zillow",
        "l1_category": "realestate",
        "l2_category": l2,
        "suggested_difficulty": difficulty,
        "suggested_hint": hint or "",
        "suggested_max_steps": max_steps or "",
        "suggested_split": split,
        "metadata_json": "",
    }

rows = []
idx = 0

# ======================================================================
# CATEGORY 1: FOR SALE — BASIC PRICE/BEDS/BATHS (10 tasks)
# ======================================================================
l2 = "for_sale_basic"

# 1
gt = make_gt_url(BASE_URL, "Los-Angeles,-CA_rb", {"beds": {"min": 3}, "price": {"max": 800000}})
rows.append(make_row(idx, l2, "Find homes for sale in Los Angeles, CA with at least 3 bedrooms priced under $800,000.", gt,
    location="Los Angeles, CA, United States", timezone="America/Los_Angeles", difficulty="easy")); idx += 1

# 2
gt = make_gt_url(BASE_URL, "San-Francisco,-CA_rb", {"price": {"min": 500000, "max": 1500000}})
rows.append(make_row(idx, l2, "Search for properties for sale in San Francisco, CA priced between $500,000 and $1,500,000.", gt,
    location="San Francisco, CA, United States", timezone="America/Los_Angeles", difficulty="easy")); idx += 1

# 3
gt = make_gt_url(BASE_URL, "Austin,-TX_rb", {"beds": {"min": 4}, "baths": {"min": 3}})
rows.append(make_row(idx, l2, "Find homes for sale in Austin, TX with at least 4 bedrooms and 3 bathrooms.", gt,
    location="Austin, TX, United States", timezone="America/Chicago", difficulty="easy")); idx += 1

# 4
gt = make_gt_url(BASE_URL, "Miami,-FL_rb", {"beds": {"min": 2}, "price": {"max": 500000}})
rows.append(make_row(idx, l2, "Search for homes for sale in Miami, FL with 2 or more bedrooms under $500,000.", gt,
    location="Miami, FL, United States", timezone="America/New_York", difficulty="easy")); idx += 1

# 5
gt = make_gt_url(BASE_URL, "Seattle,-WA_rb", {"price": {"min": 300000, "max": 700000}, "beds": {"min": 2}, "baths": {"min": 2}})
rows.append(make_row(idx, l2, "Find homes in Seattle, WA priced between $300,000 and $700,000 with at least 2 beds and 2 baths.", gt,
    location="Seattle, WA, United States", timezone="America/Los_Angeles", difficulty="easy")); idx += 1

# 6
gt = make_gt_url(BASE_URL, "Denver,-CO_rb", {"price": {"max": 450000}})
rows.append(make_row(idx, l2, "Search for all properties for sale in Denver, CO priced under $450,000.", gt,
    location="Denver, CO, United States", timezone="America/Denver", difficulty="easy")); idx += 1

# 7
gt = make_gt_url(BASE_URL, "Chicago,-IL_rb", {"beds": {"min": 3}, "baths": {"min": 2}, "price": {"min": 200000, "max": 600000}})
rows.append(make_row(idx, l2, "Find properties for sale in Chicago, IL with 3+ bedrooms, 2+ bathrooms, priced between $200,000 and $600,000.", gt,
    location="Chicago, IL, United States", timezone="America/Chicago", difficulty="easy")); idx += 1

# 8
gt = make_gt_url(BASE_URL, "Phoenix,-AZ_rb", {"beds": {"min": 5}, "price": {"max": 900000}})
rows.append(make_row(idx, l2, "Search for homes with at least 5 bedrooms in Phoenix, AZ priced under $900,000.", gt,
    location="Phoenix, AZ, United States", timezone="America/Phoenix", difficulty="easy")); idx += 1

# 9
gt = make_gt_url(BASE_URL, "Nashville,-TN_rb", {"baths": {"min": 3}})
rows.append(make_row(idx, l2, "Find homes for sale in Nashville, TN with 3 or more bathrooms.", gt,
    location="Nashville, TN, United States", timezone="America/Chicago", difficulty="easy")); idx += 1

# 10
gt = make_gt_url(BASE_URL, "Portland,-OR_rb", {"price": {"min": 400000}, "beds": {"min": 3}})
rows.append(make_row(idx, l2, "Search for 3+ bedroom homes in Portland, OR starting at $400,000.", gt,
    location="Portland, OR, United States", timezone="America/Los_Angeles", difficulty="easy")); idx += 1

# ======================================================================
# CATEGORY 2: FOR SALE — PROPERTY TYPES (10 tasks)
# ======================================================================
l2 = "for_sale_property_type"

# 11 — Houses only
filters = {**property_type_filters("isHouse")}
gt = make_gt_url(BASE_URL, "Los-Angeles,-CA_rb", filters)
rows.append(make_row(idx, l2, "Find only houses for sale in Los Angeles, CA.", gt,
    location="Los Angeles, CA, United States", timezone="America/Los_Angeles", difficulty="easy")); idx += 1

# 12 — Condos only + price
filters = {**property_type_filters("isCondo"), "price": {"max": 1000000}}
gt = make_gt_url(BASE_URL, "New-York,-NY_rb", filters)
rows.append(make_row(idx, l2, "Search for condos for sale in New York, NY priced under $1,000,000.", gt,
    location="New York, NY, United States", timezone="America/New_York", difficulty="medium")); idx += 1

# 13 — Townhomes + beds
filters = {**property_type_filters("isTownhouse"), "beds": {"min": 3}}
gt = make_gt_url(BASE_URL, "Dallas,-TX_rb", filters)
rows.append(make_row(idx, l2, "Find townhomes for sale in Dallas, TX with at least 3 bedrooms.", gt,
    location="Dallas, TX, United States", timezone="America/Chicago", difficulty="medium")); idx += 1

# 14 — Houses + Townhomes
filters = {**property_type_filters("isHouse", "isTownhouse")}
gt = make_gt_url(BASE_URL, "San-Diego,-CA_rb", filters)
rows.append(make_row(idx, l2, "Search for houses and townhomes for sale in San Diego, CA.", gt,
    location="San Diego, CA, United States", timezone="America/Los_Angeles", difficulty="medium")); idx += 1

# 15 — Multi-family
filters = {**property_type_filters("isMultiFamily")}
gt = make_gt_url(BASE_URL, "Atlanta,-GA_rb", filters)
rows.append(make_row(idx, l2, "Find multi-family properties for sale in Atlanta, GA.", gt,
    location="Atlanta, GA, United States", timezone="America/New_York", difficulty="medium")); idx += 1

# 16 — Lots/Land + price
filters = {**property_type_filters("isLotLand"), "price": {"max": 200000}}
gt = make_gt_url(BASE_URL, "Houston,-TX_rb", filters)
rows.append(make_row(idx, l2, "Search for lots and land for sale in Houston, TX under $200,000.", gt,
    location="Houston, TX, United States", timezone="America/Chicago", difficulty="medium")); idx += 1

# 17 — Manufactured + price
filters = {**property_type_filters("isManufactured"), "price": {"max": 150000}}
gt = make_gt_url(BASE_URL, "Tampa,-FL_rb", filters)
rows.append(make_row(idx, l2, "Find manufactured homes for sale in Tampa, FL priced under $150,000.", gt,
    location="Tampa, FL, United States", timezone="America/New_York", difficulty="medium")); idx += 1

# 18 — Condos + beds + price range
filters = {**property_type_filters("isCondo"), "beds": {"min": 2}, "price": {"min": 300000, "max": 800000}}
gt = make_gt_url(BASE_URL, "Boston,-MA_rb", filters)
rows.append(make_row(idx, l2, "Find condos in Boston, MA with 2+ bedrooms priced between $300,000 and $800,000.", gt,
    location="Boston, MA, United States", timezone="America/New_York", difficulty="medium")); idx += 1

# 19 — Houses + Condos + Townhomes
filters = {**property_type_filters("isHouse", "isCondo", "isTownhouse")}
gt = make_gt_url(BASE_URL, "Charlotte,-NC_rb", filters)
rows.append(make_row(idx, l2, "Search for houses, condos, and townhomes for sale in Charlotte, NC.", gt,
    location="Charlotte, NC, United States", timezone="America/New_York", difficulty="medium")); idx += 1

# 20 — Apartments
filters = {**property_type_filters("isApartment"), "price": {"max": 350000}}
gt = make_gt_url(BASE_URL, "Raleigh,-NC_rb", filters)
rows.append(make_row(idx, l2, "Find apartments for sale in Raleigh, NC under $350,000.", gt,
    location="Raleigh, NC, United States", timezone="America/New_York", difficulty="medium")); idx += 1

# ======================================================================
# CATEGORY 3: FOR SALE — SIZE & FEATURES (10 tasks)
# ======================================================================
l2 = "for_sale_features"

# 21
gt = make_gt_url(BASE_URL, "Scottsdale,-AZ_rb", {"hasPool": {"value": True}, "price": {"max": 1000000}})
rows.append(make_row(idx, l2, "Find homes for sale in Scottsdale, AZ with a pool priced under $1,000,000.", gt,
    location="Scottsdale, AZ, United States", timezone="America/Phoenix", difficulty="medium")); idx += 1

# 22
gt = make_gt_url(BASE_URL, "San-Francisco,-CA_rb", {"hasView": {"value": True}, "price": {"min": 800000}})
rows.append(make_row(idx, l2, "Search for homes with a view in San Francisco, CA starting at $800,000.", gt,
    location="San Francisco, CA, United States", timezone="America/Los_Angeles", difficulty="medium")); idx += 1

# 23
gt = make_gt_url(BASE_URL, "Denver,-CO_rb", {"hasGarage": {"value": True}, "beds": {"min": 3}})
rows.append(make_row(idx, l2, "Find homes in Denver, CO with a garage and at least 3 bedrooms.", gt,
    location="Denver, CO, United States", timezone="America/Denver", difficulty="medium")); idx += 1

# 24
gt = make_gt_url(BASE_URL, "Austin,-TX_rb", {"sqft": {"min": 2000, "max": 4000}})
rows.append(make_row(idx, l2, "Search for homes in Austin, TX between 2,000 and 4,000 square feet.", gt,
    location="Austin, TX, United States", timezone="America/Chicago", difficulty="medium")); idx += 1

# 25
gt = make_gt_url(BASE_URL, "Nashville,-TN_rb", {"built": {"min": 2015}})
rows.append(make_row(idx, l2, "Find homes built after 2015 in Nashville, TN.", gt,
    location="Nashville, TN, United States", timezone="America/Chicago", difficulty="medium")); idx += 1

# 26
gt = make_gt_url(BASE_URL, "Minneapolis,-MN_rb", {"singleStory": {"value": True}})
rows.append(make_row(idx, l2, "Search for single-story homes in Minneapolis, MN.", gt,
    location="Minneapolis, MN, United States", timezone="America/Chicago", difficulty="medium")); idx += 1

# 27
gt = make_gt_url(BASE_URL, "Miami,-FL_rb", {"isWaterfront": {"value": True}, "hasPool": {"value": True}})
rows.append(make_row(idx, l2, "Find waterfront properties with a pool in Miami, FL.", gt,
    location="Miami, FL, United States", timezone="America/New_York", difficulty="medium")); idx += 1

# 28
gt = make_gt_url(BASE_URL, "Seattle,-WA_rb", {"beds": {"min": 3}, "hasAC": {"value": True}})
rows.append(make_row(idx, l2, "Search for 3+ bedroom homes with air conditioning in Seattle, WA.", gt,
    location="Seattle, WA, United States", timezone="America/Los_Angeles", difficulty="medium")); idx += 1

# 29
gt = make_gt_url(BASE_URL, "Sacramento,-CA_rb", {"hasPool": {"value": True}, "beds": {"min": 4}})
rows.append(make_row(idx, l2, "Find homes in Sacramento, CA with a pool and at least 4 bedrooms.", gt,
    location="Sacramento, CA, United States", timezone="America/Los_Angeles", difficulty="medium")); idx += 1

# 30
gt = make_gt_url(BASE_URL, "Orlando,-FL_rb", {**property_type_filters("isHouse"), "lotSize": {"min": 10000}})
rows.append(make_row(idx, l2, "Search for houses in Orlando, FL with a lot size of at least 10,000 square feet.", gt,
    location="Orlando, FL, United States", timezone="America/New_York", difficulty="medium")); idx += 1

# ======================================================================
# CATEGORY 4: FOR SALE — LISTING STATUS (8 tasks)
# ======================================================================
l2 = "for_sale_listing_status"

# 31
gt = make_gt_url(BASE_URL, "Phoenix,-AZ_rb", {"nc": {"value": True}, "price": {"max": 600000}})
rows.append(make_row(idx, l2, "Find new construction homes for sale in Phoenix, AZ priced under $600,000.", gt,
    location="Phoenix, AZ, United States", timezone="America/Phoenix", difficulty="medium")); idx += 1

# 32
gt = make_gt_url(BASE_URL, "Detroit,-MI_rb", {"fore": {"value": True}})
rows.append(make_row(idx, l2, "Search for foreclosure properties in Detroit, MI.", gt,
    location="Detroit, MI, United States", timezone="America/New_York", difficulty="medium")); idx += 1

# 33
gt = make_gt_url(BASE_URL, "Las-Vegas,-NV_rb", {"auc": {"value": True}})
rows.append(make_row(idx, l2, "Find auction properties for sale in Las Vegas, NV.", gt,
    location="Las Vegas, NV, United States", timezone="America/Los_Angeles", difficulty="medium")); idx += 1

# 34
gt = make_gt_url(BASE_URL, "San-Antonio,-TX_rb", {"fsbo": {"value": True}, "beds": {"min": 3}})
rows.append(make_row(idx, l2, "Search for homes for sale by owner (FSBO) in San Antonio, TX with at least 3 bedrooms.", gt,
    location="San Antonio, TX, United States", timezone="America/Chicago", difficulty="medium")); idx += 1

# 35
gt = make_gt_url(BASE_URL, "Boise,-ID_rb", {"cmsn": {"value": True}})
rows.append(make_row(idx, l2, "Find coming soon listings in Boise, ID.", gt,
    location="Boise, ID, United States", timezone="America/Boise", difficulty="medium")); idx += 1

# 36
gt = make_gt_url(BASE_URL, "Tampa,-FL_rb", {"pf": {"value": True}})
rows.append(make_row(idx, l2, "Search for pre-foreclosure properties in Tampa, FL.", gt,
    location="Tampa, FL, United States", timezone="America/New_York", difficulty="medium")); idx += 1

# 37
gt = make_gt_url(BASE_URL, "Columbus,-OH_rb", {"pnd": {"value": True}, "price": {"max": 400000}})
rows.append(make_row(idx, l2, "Find pending and under-contract listings in Columbus, OH under $400,000.", gt,
    location="Columbus, OH, United States", timezone="America/New_York", difficulty="medium")); idx += 1

# 38
gt = make_gt_url(BASE_URL, "Charlotte,-NC_rb", {**property_type_filters("isHouse"), "nc": {"value": True}, "beds": {"min": 4}})
rows.append(make_row(idx, l2, "Find newly built houses in Charlotte, NC with at least 4 bedrooms.", gt,
    location="Charlotte, NC, United States", timezone="America/New_York", difficulty="hard")); idx += 1

# ======================================================================
# CATEGORY 5: FOR SALE — HOA & FINANCIALS (5 tasks)
# ======================================================================
l2 = "for_sale_financials"

# 39
gt = make_gt_url(BASE_URL, "Scottsdale,-AZ_rb", {"hoa": {"max": 0}})
rows.append(make_row(idx, l2, "Find homes in Scottsdale, AZ with no HOA fees.", gt,
    location="Scottsdale, AZ, United States", timezone="America/Phoenix", difficulty="medium")); idx += 1

# 40
gt = make_gt_url(BASE_URL, "San-Diego,-CA_rb", {**property_type_filters("isCondo"), "hoa": {"max": 300}})
rows.append(make_row(idx, l2, "Search for condos in San Diego, CA with HOA fees under $300 per month.", gt,
    location="San Diego, CA, United States", timezone="America/Los_Angeles", difficulty="medium")); idx += 1

# 41
gt = make_gt_url(BASE_URL, "Fort-Worth,-TX_rb", {**property_type_filters("isHouse"), "hoa": {"max": 0}, "price": {"max": 350000}})
rows.append(make_row(idx, l2, "Find houses in Fort Worth, TX with no HOA under $350,000.", gt,
    location="Fort Worth, TX, United States", timezone="America/Chicago", difficulty="medium")); idx += 1

# 42
gt = make_gt_url(BASE_URL, "Tucson,-AZ_rb", {"hoa": {"max": 200}})
rows.append(make_row(idx, l2, "Search for homes in Tucson, AZ with maximum HOA of $200 per month.", gt,
    location="Tucson, AZ, United States", timezone="America/Phoenix", difficulty="medium")); idx += 1

# 43
gt = make_gt_url(BASE_URL, "Henderson,-NV_rb", {"hoa": {"max": 0}, "beds": {"min": 3}, "pool": {"value": True}})
rows.append(make_row(idx, l2, "Find homes in Henderson, NV with no HOA, at least 3 bedrooms, and a pool.", gt,
    location="Henderson, NV, United States", timezone="America/Los_Angeles", difficulty="hard")); idx += 1

# ======================================================================
# CATEGORY 6: FOR SALE — DAYS ON ZILLOW & TOURS (5 tasks)
# ======================================================================
l2 = "for_sale_recency"

# 44
gt = make_gt_url(BASE_URL, "Austin,-TX_rb", {"doz": {"value": "7"}})
rows.append(make_row(idx, l2, "Find homes newly listed in the last 7 days in Austin, TX.", gt,
    location="Austin, TX, United States", timezone="America/Chicago", difficulty="medium")); idx += 1

# 45
gt = make_gt_url(BASE_URL, "Portland,-OR_rb", {"doz": {"value": "1"}, "price": {"max": 600000}})
rows.append(make_row(idx, l2, "Search for properties listed today in Portland, OR under $600,000.", gt,
    location="Portland, OR, United States", timezone="America/Los_Angeles", difficulty="medium")); idx += 1

# 46
gt = make_gt_url(BASE_URL, "Chicago,-IL_rb", {"3d": {"value": True}})
rows.append(make_row(idx, l2, "Find homes with 3D tours available in Chicago, IL.", gt,
    location="Chicago, IL, United States", timezone="America/Chicago", difficulty="medium")); idx += 1

# 47
gt = make_gt_url(BASE_URL, "San-Jose,-CA_rb", {"oh": {"value": True}, "price": {"max": 1200000}})
rows.append(make_row(idx, l2, "Search for open houses in San Jose, CA under $1,200,000.", gt,
    location="San Jose, CA, United States", timezone="America/Los_Angeles", difficulty="medium")); idx += 1

# 48
gt = make_gt_url(BASE_URL, "Dallas,-TX_rb", {"doz": {"value": "30"}, "beds": {"min": 4}})
rows.append(make_row(idx, l2, "Find 4+ bedroom homes listed in the last 30 days in Dallas, TX.", gt,
    location="Dallas, TX, United States", timezone="America/Chicago", difficulty="medium")); idx += 1

# ======================================================================
# CATEGORY 7: FOR SALE — COMPLEX MULTI-FILTER (12 tasks)
# ======================================================================
l2 = "for_sale_complex"

# 49 — Houses + beds + price
filters = {**property_type_filters("isHouse"), "beds": {"min": 3}, "price": {"max": 800000}}
gt = make_gt_url(BASE_URL, "Los-Angeles,-CA_rb", filters)
rows.append(make_row(idx, l2, "Find houses for sale in Los Angeles, CA with at least 3 bedrooms priced under $800,000.", gt,
    location="Los Angeles, CA, United States", timezone="America/Los_Angeles", difficulty="medium")); idx += 1

# 50 — Condos + beds + baths + price range + view
filters = {**property_type_filters("isCondo"), "beds": {"min": 2}, "baths": {"min": 2},
           "price": {"min": 600000, "max": 1500000}, "view": {"value": True}}
gt = make_gt_url(BASE_URL, "San-Francisco,-CA_rb", filters)
rows.append(make_row(idx, l2, "Search for condos in San Francisco, CA with 2+ beds, 2+ baths, priced $600K-$1.5M, with a view.", gt,
    location="San Francisco, CA, United States", timezone="America/Los_Angeles", difficulty="hard")); idx += 1

# 51 — Houses + pool + waterfront
filters = {**property_type_filters("isHouse"), "pool": {"value": True}, "wat": {"value": True},
           "price": {"min": 500000}}
gt = make_gt_url(BASE_URL, "Miami,-FL_rb", filters)
rows.append(make_row(idx, l2, "Find waterfront houses with a pool in Miami, FL starting at $500,000.", gt,
    location="Miami, FL, United States", timezone="America/New_York", difficulty="hard")); idx += 1

# 52 — New construction houses + beds + baths + price
filters = {**property_type_filters("isHouse"), "nc": {"value": True},
           "beds": {"min": 4}, "baths": {"min": 3}, "price": {"max": 700000}}
gt = make_gt_url(BASE_URL, "Austin,-TX_rb", filters)
rows.append(make_row(idx, l2, "Find new construction houses in Austin, TX with 4+ beds, 3+ baths, under $700,000.", gt,
    location="Austin, TX, United States", timezone="America/Chicago", difficulty="hard")); idx += 1

# 53 — Houses + single story + garage + price
filters = {**property_type_filters("isHouse"), "isSingleStory": {"value": True},
           "gar": {"value": True}, "price": {"max": 900000}}
gt = make_gt_url(BASE_URL, "Seattle,-WA_rb", filters)
rows.append(make_row(idx, l2, "Search for single-story houses with a garage in Seattle, WA under $900,000.", gt,
    location="Seattle, WA, United States", timezone="America/Los_Angeles", difficulty="hard")); idx += 1

# 54 — beds + baths + sqft + year built + price
gt = make_gt_url(BASE_URL, "Denver,-CO_rb", {
    "beds": {"min": 3}, "baths": {"min": 2}, "sqft": {"min": 1500},
    "built": {"min": 2000}, "price": {"max": 600000}})
rows.append(make_row(idx, l2, "Find homes in Denver, CO with 3+ beds, 2+ baths, 1,500+ sqft, built after 2000, under $600,000.", gt,
    location="Denver, CO, United States", timezone="America/Denver", difficulty="hard")); idx += 1

# 55 — Houses + pool + no HOA + beds + price
filters = {**property_type_filters("isHouse"), "pool": {"value": True},
           "hoa": {"max": 0}, "beds": {"min": 4}, "price": {"max": 500000}}
gt = make_gt_url(BASE_URL, "Phoenix,-AZ_rb", filters)
rows.append(make_row(idx, l2, "Find houses in Phoenix, AZ with a pool, no HOA, 4+ bedrooms, under $500,000.", gt,
    location="Phoenix, AZ, United States", timezone="America/Phoenix", difficulty="hard")); idx += 1

# 56 — Townhomes + beds + baths + price range + days on Zillow
filters = {**property_type_filters("isTownhouse"), "beds": {"min": 3}, "baths": {"min": 2},
           "price": {"min": 250000, "max": 500000}, "doz": {"value": "14"}}
gt = make_gt_url(BASE_URL, "Nashville,-TN_rb", filters)
rows.append(make_row(idx, l2, "Search for townhomes in Nashville, TN with 3+ beds, 2+ baths, $250K-$500K, listed in the last 14 days.", gt,
    location="Nashville, TN, United States", timezone="America/Chicago", difficulty="hard")); idx += 1

# 57 — Houses + beds + price range
filters = {**property_type_filters("isHouse"),
           "beds": {"min": 3}, "price": {"min": 700000, "max": 2000000}}
gt = make_gt_url(BASE_URL, "San-Diego,-CA_rb", filters)
rows.append(make_row(idx, l2, "Find houses in San Diego, CA with 3+ bedrooms priced between $700,000 and $2,000,000.", gt,
    location="San Diego, CA, United States", timezone="America/Los_Angeles", difficulty="hard")); idx += 1

# 58 — Condos + 3D tour + price + beds
filters = {**property_type_filters("isCondo"), "3d": {"value": True},
           "price": {"max": 500000}, "beds": {"min": 2}}
gt = make_gt_url(BASE_URL, "Chicago,-IL_rb", filters)
rows.append(make_row(idx, l2, "Search for condos with 3D tours in Chicago, IL with 2+ bedrooms under $500,000.", gt,
    location="Chicago, IL, United States", timezone="America/Chicago", difficulty="hard")); idx += 1

# 59 — Houses + beds + price range
filters = {**property_type_filters("isHouse"),
           "beds": {"min": 4}, "price": {"min": 300000, "max": 600000}}
gt = make_gt_url(BASE_URL, "Atlanta,-GA_rb", filters)
rows.append(make_row(idx, l2, "Find houses in Atlanta, GA with 4+ beds priced $300K-$600K.", gt,
    location="Atlanta, GA, United States", timezone="America/New_York", difficulty="hard")); idx += 1

# 60 — New construction houses + garage + no HOA + beds + baths + price
filters = {**property_type_filters("isHouse"), "nc": {"value": True},
           "gar": {"value": True}, "beds": {"min": 4}, "baths": {"min": 3},
           "price": {"max": 550000}, "hoa": {"max": 0}}
gt = make_gt_url(BASE_URL, "Raleigh,-NC_rb", filters)
rows.append(make_row(idx, l2, "Find new construction houses in Raleigh, NC with a garage, no HOA, 4+ beds, 3+ baths, under $550,000.", gt,
    location="Raleigh, NC, United States", timezone="America/New_York", difficulty="hard")); idx += 1

# ======================================================================
# CATEGORY 8: FOR RENT (5 tasks)
#
# Zillow rental URLs use different filter keys:
#   fr=true (for rent), fsba/fsbo/nc/cmsn/auc/fore=false (disable sale types)
#   mp = monthly price (NOT "price")
#   ldog = allows large dogs, sdog = allows small dogs
#   cat = allows cats
# ======================================================================
l2 = "for_rent"

# Base filters that Zillow includes for all rental searches
RENT_FILTER_BASE = {
    "fr": {"value": True},
    "fsba": {"value": False},
    "fsbo": {"value": False},
    "nc": {"value": False},
    "cmsn": {"value": False},
    "auc": {"value": False},
    "fore": {"value": False},
}

# 61
rent_filters = {**RENT_FILTER_BASE, "beds": {"min": 1}, "mp": {"max": 3000}}
gt_url = RENT_URL + "New-York,-NY_rb/?searchQueryState=" + quote(json.dumps(
    {"filterState": rent_filters}, separators=(",", ":")))
rows.append(make_row(idx, l2, "Find apartments for rent in New York, NY with at least 1 bedroom under $3,000 per month.", gt_url,
    location="New York, NY, United States", timezone="America/New_York", difficulty="easy", url=RENT_URL)); idx += 1

# 62 — Dog-friendly (both large + small dogs)
rent_filters = {**RENT_FILTER_BASE, "beds": {"min": 2}, "mp": {"max": 2500},
                "ldog": {"value": True}, "sdog": {"value": True}}
gt_url = RENT_URL + "Los-Angeles,-CA_rb/?searchQueryState=" + quote(json.dumps(
    {"filterState": rent_filters}, separators=(",", ":")))
rows.append(make_row(idx, l2, "Search for dog-friendly 2+ bedroom rentals in Los Angeles, CA under $2,500 per month.", gt_url,
    location="Los Angeles, CA, United States", timezone="America/Los_Angeles", difficulty="medium", url=RENT_URL)); idx += 1

# 63 — In-unit laundry
rent_filters = {**RENT_FILTER_BASE, "beds": {"min": 1}, "lau": {"value": True}, "mp": {"max": 3500}}
gt_url = RENT_URL + "San-Francisco,-CA_rb/?searchQueryState=" + quote(json.dumps(
    {"filterState": rent_filters}, separators=(",", ":")))
rows.append(make_row(idx, l2, "Find rentals in San Francisco, CA with in-unit washer/dryer and 1+ bedroom under $3,500/month.", gt_url,
    location="San Francisco, CA, United States", timezone="America/Los_Angeles", difficulty="medium", url=RENT_URL)); idx += 1

# 64 — Pool + beds + baths
rent_filters = {**RENT_FILTER_BASE, "beds": {"min": 2}, "baths": {"min": 2},
                "pool": {"value": True}, "mp": {"max": 2000}}
gt_url = RENT_URL + "Austin,-TX_rb/?searchQueryState=" + quote(json.dumps(
    {"filterState": rent_filters}, separators=(",", ":")))
rows.append(make_row(idx, l2, "Search for 2-bed, 2-bath rentals with a pool in Austin, TX under $2,000 per month.", gt_url,
    location="Austin, TX, United States", timezone="America/Chicago", difficulty="medium", url=RENT_URL)); idx += 1

# 65 — Cat-friendly
rent_filters = {**RENT_FILTER_BASE, "beds": {"min": 1}, "cat": {"value": True}, "mp": {"max": 2500}}
gt_url = RENT_URL + "Miami,-FL_rb/?searchQueryState=" + quote(json.dumps(
    {"filterState": rent_filters}, separators=(",", ":")))
rows.append(make_row(idx, l2, "Find cat-friendly 1+ bedroom rentals in Miami, FL under $2,500/month.", gt_url,
    location="Miami, FL, United States", timezone="America/New_York", difficulty="medium", url=RENT_URL)); idx += 1

# ======================================================================
# CATEGORY 9: RECENTLY SOLD (5 tasks)
# ======================================================================
l2 = "recently_sold"

# 66 — Houses only (recently sold)
sold_filters = property_type_filters("isHouse")
gt_url = SOLD_URL + "San-Francisco,-CA_rb/?searchQueryState=" + quote(json.dumps(
    {"filterState": sold_filters}, separators=(",", ":")))
rows.append(make_row(idx, l2, "Search for recently sold houses in San Francisco, CA.", gt_url,
    location="San Francisco, CA, United States", timezone="America/Los_Angeles", difficulty="easy", url=SOLD_URL)); idx += 1

# 67
gt_url = SOLD_URL + "Austin,-TX_rb/?searchQueryState=" + quote(json.dumps(
    {"filterState": {"beds": {"min": 3}, "price": {"min": 300000, "max": 700000}}}, separators=(",", ":")))
rows.append(make_row(idx, l2, "Find recently sold homes in Austin, TX with 3+ bedrooms that sold between $300,000 and $700,000.", gt_url,
    location="Austin, TX, United States", timezone="America/Chicago", difficulty="medium", url=SOLD_URL)); idx += 1

# 68 — Condos only (recently sold)
sold_filters = property_type_filters("isCondo")
sold_filters["price"] = {"max": 500000}
gt_url = SOLD_URL + "Denver,-CO_rb/?searchQueryState=" + quote(json.dumps(
    {"filterState": sold_filters}, separators=(",", ":")))
rows.append(make_row(idx, l2, "Search for recently sold condos in Denver, CO that sold under $500,000.", gt_url,
    location="Denver, CO, United States", timezone="America/Denver", difficulty="medium", url=SOLD_URL)); idx += 1

# 69
gt_url = SOLD_URL + "Miami,-FL_rb/?searchQueryState=" + quote(json.dumps(
    {"filterState": {"isWaterfront": {"value": True}, "hasPool": {"value": True}}}, separators=(",", ":")))
rows.append(make_row(idx, l2, "Find recently sold waterfront properties with pools in Miami, FL.", gt_url,
    location="Miami, FL, United States", timezone="America/New_York", difficulty="medium", url=SOLD_URL)); idx += 1

# 70 — Houses only (recently sold) + beds + baths + price
sold_filters = property_type_filters("isHouse")
sold_filters.update({"beds": {"min": 4}, "baths": {"min": 3}, "price": {"min": 500000}})
gt_url = SOLD_URL + "Seattle,-WA_rb/?searchQueryState=" + quote(json.dumps(
    {"filterState": sold_filters}, separators=(",", ":")))
rows.append(make_row(idx, l2, "Search for recently sold houses in Seattle, WA with 4+ beds, 3+ baths, that sold for over $500,000.", gt_url,
    location="Seattle, WA, United States", timezone="America/New_York", difficulty="hard", url=SOLD_URL)); idx += 1

# ======================================================================
# Write CSV
# ======================================================================
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} tasks -> {OUTPUT_FILE}")
