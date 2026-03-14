"""Generate trip_benchmark_tasks.csv with 70 extreme-hard tasks.

All URLs are browser-verified against us.trip.com (Mar 2026).
All tasks combine 3-7+ filters for maximum difficulty.
"""
import csv
import json
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "trip_benchmark_tasks.csv")
TARGET = "navi_bench.trip.trip_url_match.generate_task_config"
BASE_URL = "https://us.trip.com"

# Browser-verified city IDs (Mar 2026)
CITIES = {
    "New York":      {"id": "633", "loc": "New York, NY, United States",       "tz": "America/New_York"},
    "Los Angeles":   {"id": "347", "loc": "Los Angeles, CA, United States",    "tz": "America/Los_Angeles"},
    "London":        {"id": "338", "loc": "London, United Kingdom",            "tz": "Europe/London"},
    "Paris":         {"id": "192", "loc": "Paris, France",                     "tz": "Europe/Paris"},
    "Tokyo":         {"id": "228", "loc": "Tokyo, Japan",                      "tz": "Asia/Tokyo"},
    "Dubai":         {"id": "266", "loc": "Dubai, United Arab Emirates",       "tz": "Asia/Dubai"},
}

# ── Filter building helpers ─────────────────────────────────────────────
def star(n):        return f"16~{n}*16*{n}"
def stars(*ns):     return ",".join(star(n) for n in ns)
def price(lo, hi):  return f"15~Range*15*{lo}~{hi}"
def rating(v):      return f"6~{v}*6*{v}"         # 7=6+, 8=7+, 9=8+, 10=9+
def amenity(aid):   return f"3~{aid}*3*{aid}"      # 605=pool, 42=gym, 2=wifi, 7=parking, 22=spa, 10=restaurant, 103=shuttle, 104=pet
def breakfast():    return "5~1*5*1"
def cancel():      return "23~10*23*10"
def ptype(tid):     return f"75~TAG_{tid}*75*{tid}" # 495=hotel, 496=hostel, 497=apt, 498=villa, 499=resort, 500=guesthouse
def sort(sid):      return f"17~{sid}*17*{sid}"     # 1=recommended, 3=lowest_price, 10=guest_rating
def combo(*parts):  return ",".join(parts)

def url(city_name, checkin, checkout, adults, children, ages, rooms, filters):
    c = CITIES[city_name]
    cn = city_name.replace(" ", "%20")
    u = (f"https://us.trip.com/hotels/list?cityId={c['id']}"
         f"&cityName={cn}"
         f"&checkin={checkin}&checkout={checkout}"
         f"&adult={adults}")
    if children > 0:
        u += f"&children={children}&ages={','.join(str(a) for a in ages)}"
    u += f"&crn={rooms}"
    if filters:
        u += f"&listFilters={filters}"
    return u

def row(task_id, city, task_desc, checkin, checkout, adults, children, ages, rooms, filters, l2, difficulty="hard"):
    c = CITIES[city]
    gt = url(city, checkin, checkout, adults, children, ages, rooms, filters)
    config = {
        "_target_": TARGET,
        "url": BASE_URL,
        "task": task_desc,
        "location": c["loc"],
        "timezone": c["tz"],
        "gt_url": [gt],
    }
    return {
        "task_id": f"navi_bench/trip/{l2}/{task_id}",
        "task_generation_config_json": json.dumps(config),
        "env": "real",
        "domain": "trip",
        "l1_category": "travel",
        "l2_category": l2,
        "suggested_difficulty": difficulty,
        "suggested_hint": "",
        "suggested_max_steps": "null",
        "suggested_split": "validation",
        "metadata_json": "",
    }

# ── 70 tasks ────────────────────────────────────────────────────────────
tasks = []
n = 0

# ═══════════════════════════════════════════════════════════════════════
# TIER 1: Star + Price + Sort (10 tasks)
# ═══════════════════════════════════════════════════════════════════════

tasks.append(row(n, "New York",
    "Search for 5-star hotels in New York for April 1-5, 2 adults, sorted by lowest price with rooms under $500 per night.",
    "2026-04-01","2026-04-05", 2, 0, [], 1,
    combo(star(5), price(0,500), sort(3)),
    "star_price_sort")); n+=1

tasks.append(row(n, "London",
    "Find 4- and 5-star hotels in London for April 10-15, 2 adults, priced between $200 and $600 per night.",
    "2026-04-10","2026-04-15", 2, 0, [], 1,
    combo(stars(4,5), price(200,600)),
    "star_price_sort")); n+=1

tasks.append(row(n, "Paris",
    "Search for 3-star hotels in Paris for May 1-7, 2 adults, 1 room, sorted by guest rating.",
    "2026-05-01","2026-05-07", 2, 0, [], 1,
    combo(star(3), sort(10)),
    "star_price_sort")); n+=1

tasks.append(row(n, "Tokyo",
    "Find 5-star hotels in Tokyo for June 15-20, 2 adults, priced under $400 per night, sorted by lowest price.",
    "2026-06-15","2026-06-20", 2, 0, [], 1,
    combo(star(5), price(0,400), sort(3)),
    "star_price_sort")); n+=1

tasks.append(row(n, "Dubai",
    "Search for 4-star hotels in Dubai for March 20-25, 2 adults, priced between $150 and $350 per night.",
    "2026-03-20","2026-03-25", 2, 0, [], 1,
    combo(star(4), price(150,350)),
    "star_price_sort")); n+=1

tasks.append(row(n, "Los Angeles",
    "Find 5-star hotels in Los Angeles for April 5-10, 2 adults, 1 room, sorted by guest rating, priced under $800.",
    "2026-04-05","2026-04-10", 2, 0, [], 1,
    combo(star(5), price(0,800), sort(10)),
    "star_price_sort")); n+=1

tasks.append(row(n, "New York",
    "Search for 3- and 4-star hotels in New York for May 10-14, 2 adults, priced $100-$300 per night, sorted by lowest price.",
    "2026-05-10","2026-05-14", 2, 0, [], 1,
    combo(stars(3,4), price(100,300), sort(3)),
    "star_price_sort")); n+=1

tasks.append(row(n, "London",
    "Find 5-star hotels in London for July 1-7, 2 adults, priced under $1000 per night, sorted by guest rating.",
    "2026-07-01","2026-07-07", 2, 0, [], 1,
    combo(star(5), price(0,1000), sort(10)),
    "star_price_sort")); n+=1

tasks.append(row(n, "Paris",
    "Search for 4-star hotels in Paris for August 5-12, 2 adults, priced between $150 and $400 per night, sorted by lowest price.",
    "2026-08-05","2026-08-12", 2, 0, [], 1,
    combo(star(4), price(150,400), sort(3)),
    "star_price_sort")); n+=1

tasks.append(row(n, "Tokyo",
    "Find 4- and 5-star hotels in Tokyo for September 1-5, 2 adults, priced under $600 per night.",
    "2026-09-01","2026-09-05", 2, 0, [], 1,
    combo(stars(4,5), price(0,600)),
    "star_price_sort")); n+=1

# ═══════════════════════════════════════════════════════════════════════
# TIER 2: Star + Amenities + Price (10 tasks)
# ═══════════════════════════════════════════════════════════════════════

tasks.append(row(n, "New York",
    "Find 5-star hotels in New York with a swimming pool for April 1-5, 2 adults, priced under $600 per night.",
    "2026-04-01","2026-04-05", 2, 0, [], 1,
    combo(star(5), amenity(605), price(0,600)),
    "star_amenity_price")); n+=1

tasks.append(row(n, "Dubai",
    "Search for 5-star hotels in Dubai with a pool and gym for May 1-7, 2 adults, priced under $500.",
    "2026-05-01","2026-05-07", 2, 0, [], 1,
    combo(star(5), amenity(605), amenity(42), price(0,500)),
    "star_amenity_price")); n+=1

tasks.append(row(n, "Los Angeles",
    "Find 4-star hotels in Los Angeles with free WiFi and parking for April 10-14, 2 adults, priced $100-$300.",
    "2026-04-10","2026-04-14", 2, 0, [], 1,
    combo(star(4), amenity(2), amenity(7), price(100,300)),
    "star_amenity_price")); n+=1

tasks.append(row(n, "Paris",
    "Search for 4-star hotels in Paris with a spa and restaurant for June 5-10, 2 adults, priced under $400.",
    "2026-06-05","2026-06-10", 2, 0, [], 1,
    combo(star(4), amenity(22), amenity(10), price(0,400)),
    "star_amenity_price")); n+=1

tasks.append(row(n, "Tokyo",
    "Find 5-star hotels in Tokyo with a gym and free WiFi for July 1-5, 2 adults, priced under $500.",
    "2026-07-01","2026-07-05", 2, 0, [], 1,
    combo(star(5), amenity(42), amenity(2), price(0,500)),
    "star_amenity_price")); n+=1

tasks.append(row(n, "London",
    "Search for 4- and 5-star hotels in London with a pool for August 10-17, 2 adults, priced $200-$600.",
    "2026-08-10","2026-08-17", 2, 0, [], 1,
    combo(stars(4,5), amenity(605), price(200,600)),
    "star_amenity_price")); n+=1

tasks.append(row(n, "New York",
    "Find 5-star hotels in New York with a pool, gym, and spa for May 20-25, 2 adults, priced under $800.",
    "2026-05-20","2026-05-25", 2, 0, [], 1,
    combo(star(5), amenity(605), amenity(42), amenity(22), price(0,800)),
    "star_amenity_price")); n+=1

tasks.append(row(n, "Dubai",
    "Search for 5-star hotels in Dubai with a pool, spa, and restaurant for April 15-20, 2 adults, sorted by guest rating.",
    "2026-04-15","2026-04-20", 2, 0, [], 1,
    combo(star(5), amenity(605), amenity(22), amenity(10), sort(10)),
    "star_amenity_price")); n+=1

tasks.append(row(n, "Los Angeles",
    "Find 3-star hotels in Los Angeles with free WiFi for March 25-30, 2 adults, priced under $150, sorted by lowest price.",
    "2026-03-25","2026-03-30", 2, 0, [], 1,
    combo(star(3), amenity(2), price(0,150), sort(3)),
    "star_amenity_price")); n+=1

tasks.append(row(n, "Paris",
    "Search for 5-star hotels in Paris with a pool and gym for September 1-8, 2 adults, priced $300-$700.",
    "2026-09-01","2026-09-08", 2, 0, [], 1,
    combo(star(5), amenity(605), amenity(42), price(300,700)),
    "star_amenity_price")); n+=1

# ═══════════════════════════════════════════════════════════════════════
# TIER 3: Property Type + Star + Price + Amenities (10 tasks)
# ═══════════════════════════════════════════════════════════════════════

tasks.append(row(n, "New York",
    "Find 5-star resort hotels in New York with a pool for April 1-5, 2 adults, priced under $700.",
    "2026-04-01","2026-04-05", 2, 0, [], 1,
    combo(ptype(499), star(5), amenity(605), price(0,700)),
    "type_star_price_amenity")); n+=1

tasks.append(row(n, "Dubai",
    "Search for 5-star resort hotels in Dubai with a pool, spa, and gym for May 10-17, 2 adults, priced under $800.",
    "2026-05-10","2026-05-17", 2, 0, [], 1,
    combo(ptype(499), star(5), amenity(605), amenity(22), amenity(42), price(0,800)),
    "type_star_price_amenity")); n+=1

tasks.append(row(n, "London",
    "Find hostels in London with free WiFi for June 1-5, 2 adults, priced under $100 per night, sorted by lowest price.",
    "2026-06-01","2026-06-05", 2, 0, [], 1,
    combo(ptype(496), amenity(2), price(0,100), sort(3)),
    "type_star_price_amenity")); n+=1

tasks.append(row(n, "Tokyo",
    "Search for 4-star hotels (hotel type) in Tokyo with free WiFi and a restaurant for July 10-15, 2 adults, priced $150-$400.",
    "2026-07-10","2026-07-15", 2, 0, [], 1,
    combo(ptype(495), star(4), amenity(2), amenity(10), price(150,400)),
    "type_star_price_amenity")); n+=1

tasks.append(row(n, "Paris",
    "Find apartment-type accommodations in Paris for August 1-10, 2 adults, priced under $200, sorted by lowest price.",
    "2026-08-01","2026-08-10", 2, 0, [], 1,
    combo(ptype(497), price(0,200), sort(3)),
    "type_star_price_amenity")); n+=1

tasks.append(row(n, "Los Angeles",
    "Search for 4-star hotels in Los Angeles with a pool, parking, and free WiFi for April 20-25, 2 adults, priced $150-$350.",
    "2026-04-20","2026-04-25", 2, 0, [], 1,
    combo(ptype(495), star(4), amenity(605), amenity(7), amenity(2), price(150,350)),
    "type_star_price_amenity")); n+=1

tasks.append(row(n, "New York",
    "Find guesthouse accommodations in New York for May 5-9, 2 adults, priced under $120, with free WiFi.",
    "2026-05-05","2026-05-09", 2, 0, [], 1,
    combo(ptype(500), amenity(2), price(0,120)),
    "type_star_price_amenity")); n+=1

tasks.append(row(n, "Dubai",
    "Search for 5-star villa accommodations in Dubai with a pool for June 20-27, 2 adults, sorted by guest rating.",
    "2026-06-20","2026-06-27", 2, 0, [], 1,
    combo(ptype(498), star(5), amenity(605), sort(10)),
    "type_star_price_amenity")); n+=1

tasks.append(row(n, "London",
    "Find 3-star hotels in London with parking and free WiFi for September 5-10, 2 adults, priced $80-$200.",
    "2026-09-05","2026-09-10", 2, 0, [], 1,
    combo(ptype(495), star(3), amenity(7), amenity(2), price(80,200)),
    "type_star_price_amenity")); n+=1

tasks.append(row(n, "Tokyo",
    "Search for hostel accommodations in Tokyo with free WiFi for October 1-5, 2 adults, priced under $80, sorted by lowest price.",
    "2026-10-01","2026-10-05", 2, 0, [], 1,
    combo(ptype(496), amenity(2), price(0,80), sort(3)),
    "type_star_price_amenity")); n+=1

# ═══════════════════════════════════════════════════════════════════════
# TIER 4: Breakfast + Cancellation + Rating + Star + Price (10 tasks)
# ═══════════════════════════════════════════════════════════════════════

tasks.append(row(n, "New York",
    "Find 4-star hotels in New York with breakfast included and free cancellation for April 1-5, 2 adults, priced under $400.",
    "2026-04-01","2026-04-05", 2, 0, [], 1,
    combo(star(4), breakfast(), cancel(), price(0,400)),
    "breakfast_cancel_rating")); n+=1

tasks.append(row(n, "London",
    "Search for hotels in London with breakfast included, free cancellation, and guest rating 8+ for May 5-10, 2 adults, priced under $300.",
    "2026-05-05","2026-05-10", 2, 0, [], 1,
    combo(breakfast(), cancel(), rating(9), price(0,300)),
    "breakfast_cancel_rating")); n+=1

tasks.append(row(n, "Paris",
    "Find 5-star hotels in Paris with breakfast included, guest rating 9+, and a pool for June 1-7, 2 adults.",
    "2026-06-01","2026-06-07", 2, 0, [], 1,
    combo(star(5), breakfast(), rating(10), amenity(605)),
    "breakfast_cancel_rating")); n+=1

tasks.append(row(n, "Tokyo",
    "Search for 4-star hotels in Tokyo with breakfast included and free cancellation for August 1-5, 2 adults, priced $100-$350, sorted by lowest price.",
    "2026-08-01","2026-08-05", 2, 0, [], 1,
    combo(star(4), breakfast(), cancel(), price(100,350), sort(3)),
    "breakfast_cancel_rating")); n+=1

tasks.append(row(n, "Dubai",
    "Find 5-star hotels in Dubai with breakfast, free cancellation, guest rating 8+, and a pool for April 10-15, 2 adults.",
    "2026-04-10","2026-04-15", 2, 0, [], 1,
    combo(star(5), breakfast(), cancel(), rating(9), amenity(605)),
    "breakfast_cancel_rating")); n+=1

tasks.append(row(n, "Los Angeles",
    "Search for hotels in Los Angeles with free cancellation and guest rating 7+ for May 15-20, 2 adults, priced under $250, sorted by guest rating.",
    "2026-05-15","2026-05-20", 2, 0, [], 1,
    combo(cancel(), rating(8), price(0,250), sort(10)),
    "breakfast_cancel_rating")); n+=1

tasks.append(row(n, "New York",
    "Find 5-star hotels in New York with breakfast included, free cancellation, and a gym for July 1-5, 2 adults, priced under $700.",
    "2026-07-01","2026-07-05", 2, 0, [], 1,
    combo(star(5), breakfast(), cancel(), amenity(42), price(0,700)),
    "breakfast_cancel_rating")); n+=1

tasks.append(row(n, "London",
    "Search for 4-star hotels in London with breakfast, guest rating 8+, and free WiFi for September 10-15, 2 adults, priced $150-$400.",
    "2026-09-10","2026-09-15", 2, 0, [], 1,
    combo(star(4), breakfast(), rating(9), amenity(2), price(150,400)),
    "breakfast_cancel_rating")); n+=1

tasks.append(row(n, "Paris",
    "Find hotels in Paris with breakfast included, free cancellation, and guest rating 7+ for October 5-12, 2 adults, priced under $250, sorted by lowest price.",
    "2026-10-05","2026-10-12", 2, 0, [], 1,
    combo(breakfast(), cancel(), rating(8), price(0,250), sort(3)),
    "breakfast_cancel_rating")); n+=1

tasks.append(row(n, "Tokyo",
    "Search for 5-star hotels in Tokyo with breakfast, free cancellation, guest rating 9+, and spa for November 1-5, 2 adults.",
    "2026-11-01","2026-11-05", 2, 0, [], 1,
    combo(star(5), breakfast(), cancel(), rating(10), amenity(22)),
    "breakfast_cancel_rating")); n+=1

# ═══════════════════════════════════════════════════════════════════════
# TIER 5: Family trips — children + multiple filters (10 tasks)
# ═══════════════════════════════════════════════════════════════════════

tasks.append(row(n, "New York",
    "Find 4-star hotels in New York with a pool for a family of 2 adults and 2 children (ages 5 and 10), April 1-5, priced under $400.",
    "2026-04-01","2026-04-05", 2, 2, [5,10], 1,
    combo(star(4), amenity(605), price(0,400)),
    "family_multi_filter")); n+=1

tasks.append(row(n, "London",
    "Search for 4-star hotels in London with breakfast included for 2 adults and 1 child (age 8), May 10-15, priced under $350, with free cancellation.",
    "2026-05-10","2026-05-15", 2, 1, [8], 1,
    combo(star(4), breakfast(), cancel(), price(0,350)),
    "family_multi_filter")); n+=1

tasks.append(row(n, "Paris",
    "Find 5-star hotels in Paris with a pool and gym for 2 adults and 3 children (ages 3, 7, and 12), June 5-12, priced under $600.",
    "2026-06-05","2026-06-12", 2, 3, [3,7,12], 1,
    combo(star(5), amenity(605), amenity(42), price(0,600)),
    "family_multi_filter")); n+=1

tasks.append(row(n, "Tokyo",
    "Search for 4-star hotels in Tokyo with breakfast and free WiFi for 2 adults and 1 child (age 5), July 15-20, priced $100-$350, sorted by lowest price.",
    "2026-07-15","2026-07-20", 2, 1, [5], 1,
    combo(star(4), breakfast(), amenity(2), price(100,350), sort(3)),
    "family_multi_filter")); n+=1

tasks.append(row(n, "Dubai",
    "Find 5-star resort hotels in Dubai with a pool and spa for 2 adults and 2 children (ages 6 and 9), August 1-7, 2 rooms, sorted by guest rating.",
    "2026-08-01","2026-08-07", 2, 2, [6,9], 2,
    combo(ptype(499), star(5), amenity(605), amenity(22), sort(10)),
    "family_multi_filter")); n+=1

tasks.append(row(n, "Los Angeles",
    "Search for 4-star hotels in Los Angeles with a pool, parking, and breakfast for 2 adults and 1 child (age 4), April 15-20, priced under $300.",
    "2026-04-15","2026-04-20", 2, 1, [4], 1,
    combo(star(4), amenity(605), amenity(7), breakfast(), price(0,300)),
    "family_multi_filter")); n+=1

tasks.append(row(n, "New York",
    "Find 5-star hotels in New York with breakfast, pool, and free cancellation for 2 adults and 2 children (ages 3 and 7), May 5-10, 2 rooms, priced under $500.",
    "2026-05-05","2026-05-10", 2, 2, [3,7], 2,
    combo(star(5), breakfast(), amenity(605), cancel(), price(0,500)),
    "family_multi_filter")); n+=1

tasks.append(row(n, "London",
    "Search for hotels in London with free cancellation, guest rating 8+, and free WiFi for 2 adults and 1 child (age 11), September 1-7, priced under $300.",
    "2026-09-01","2026-09-07", 2, 1, [11], 1,
    combo(cancel(), rating(9), amenity(2), price(0,300)),
    "family_multi_filter")); n+=1

tasks.append(row(n, "Paris",
    "Find 4-star hotels in Paris with breakfast, gym, and parking for 2 adults and 2 children (ages 8 and 14), October 10-17, priced $200-$500.",
    "2026-10-10","2026-10-17", 2, 2, [8,14], 1,
    combo(star(4), breakfast(), amenity(42), amenity(7), price(200,500)),
    "family_multi_filter")); n+=1

tasks.append(row(n, "Tokyo",
    "Search for 5-star hotels in Tokyo with breakfast, pool, free cancellation, and guest rating 8+ for 2 adults and 1 child (age 6), November 5-10, sorted by guest rating.",
    "2026-11-05","2026-11-10", 2, 1, [6], 1,
    combo(star(5), breakfast(), amenity(605), cancel(), rating(9), sort(10)),
    "family_multi_filter")); n+=1

# ═══════════════════════════════════════════════════════════════════════
# TIER 6: Extreme combos — 5-7 filters + sort + type + rating (10 tasks)
# ═══════════════════════════════════════════════════════════════════════

tasks.append(row(n, "New York",
    "Find 5-star resort hotels in New York with a pool, spa, gym, breakfast included, free cancellation, guest rating 8+, for 2 adults, April 1-5, priced under $900.",
    "2026-04-01","2026-04-05", 2, 0, [], 1,
    combo(ptype(499), star(5), amenity(605), amenity(22), amenity(42), breakfast(), cancel(), rating(9), price(0,900)),
    "extreme_combo")); n+=1

tasks.append(row(n, "Dubai",
    "Search for 5-star hotels in Dubai with pool, gym, spa, restaurant, breakfast, free cancellation, and guest rating 9+ for 2 adults, May 1-7, sorted by guest rating.",
    "2026-05-01","2026-05-07", 2, 0, [], 1,
    combo(star(5), amenity(605), amenity(42), amenity(22), amenity(10), breakfast(), cancel(), rating(10), sort(10)),
    "extreme_combo")); n+=1

tasks.append(row(n, "London",
    "Find 4-star hotels in London with free WiFi, parking, breakfast included, free cancellation, guest rating 7+, priced $100-$300, sorted by lowest price, for 2 adults, June 1-5.",
    "2026-06-01","2026-06-05", 2, 0, [], 1,
    combo(star(4), amenity(2), amenity(7), breakfast(), cancel(), rating(8), price(100,300), sort(3)),
    "extreme_combo")); n+=1

tasks.append(row(n, "Paris",
    "Search for 5-star resort hotels in Paris with a pool, spa, breakfast, guest rating 9+, and free cancellation for 2 adults and 1 child (age 7), July 10-17, priced under $700.",
    "2026-07-10","2026-07-17", 2, 1, [7], 1,
    combo(ptype(499), star(5), amenity(605), amenity(22), breakfast(), rating(10), cancel(), price(0,700)),
    "extreme_combo")); n+=1

tasks.append(row(n, "Tokyo",
    "Find 4-star hotels in Tokyo with free WiFi, gym, breakfast, free cancellation, and guest rating 8+ for 2 adults, August 5-10, priced $100-$400, sorted by guest rating.",
    "2026-08-05","2026-08-10", 2, 0, [], 1,
    combo(star(4), amenity(2), amenity(42), breakfast(), cancel(), rating(9), price(100,400), sort(10)),
    "extreme_combo")); n+=1

tasks.append(row(n, "Los Angeles",
    "Search for 5-star hotels in Los Angeles with pool, gym, parking, breakfast, free cancellation, guest rating 8+, priced under $600, for 2 adults and 2 children (ages 4 and 9), September 1-7, 2 rooms.",
    "2026-09-01","2026-09-07", 2, 2, [4,9], 2,
    combo(star(5), amenity(605), amenity(42), amenity(7), breakfast(), cancel(), rating(9), price(0,600)),
    "extreme_combo")); n+=1

tasks.append(row(n, "New York",
    "Find 5-star hotels in New York with pool, spa, gym, free WiFi, restaurant, breakfast, free cancellation, for 2 adults, October 1-5, sorted by lowest price.",
    "2026-10-01","2026-10-05", 2, 0, [], 1,
    combo(star(5), amenity(605), amenity(22), amenity(42), amenity(2), amenity(10), breakfast(), cancel(), sort(3)),
    "extreme_combo")); n+=1

tasks.append(row(n, "Dubai",
    "Search for 5-star villa accommodations in Dubai with pool, spa, breakfast, free cancellation, guest rating 9+, for 2 adults and 3 children (ages 2, 6, and 11), November 10-17, 2 rooms, sorted by guest rating.",
    "2026-11-10","2026-11-17", 2, 3, [2,6,11], 2,
    combo(ptype(498), star(5), amenity(605), amenity(22), breakfast(), cancel(), rating(10), sort(10)),
    "extreme_combo")); n+=1

tasks.append(row(n, "London",
    "Find 3-star hotels in London with free WiFi, breakfast included, free cancellation, and guest rating 7+ for 2 adults, December 20-27, priced under $200, sorted by lowest price.",
    "2026-12-20","2026-12-27", 2, 0, [], 1,
    combo(star(3), amenity(2), breakfast(), cancel(), rating(8), price(0,200), sort(3)),
    "extreme_combo")); n+=1

tasks.append(row(n, "Paris",
    "Search for 4-star hotels in Paris with pool, gym, free WiFi, breakfast, free cancellation, guest rating 8+, priced $200-$500, for 2 adults and 1 child (age 10), January 5-12, sorted by guest rating.",
    "2027-01-05","2027-01-12", 2, 1, [10], 1,
    combo(star(4), amenity(605), amenity(42), amenity(2), breakfast(), cancel(), rating(9), price(200,500), sort(10)),
    "extreme_combo")); n+=1

# ═══════════════════════════════════════════════════════════════════════
# TIER 7: Multi-room + pet-friendly + airport shuttle + edge cases (10 tasks)
# ═══════════════════════════════════════════════════════════════════════

tasks.append(row(n, "New York",
    "Find pet-friendly 4-star hotels in New York with a pool and free cancellation for 2 adults, April 5-10, 2 rooms, priced under $350.",
    "2026-04-05","2026-04-10", 2, 0, [], 2,
    combo(star(4), amenity(104), amenity(605), cancel(), price(0,350)),
    "special_filters")); n+=1

tasks.append(row(n, "London",
    "Search for hotels in London with airport shuttle, free WiFi, breakfast, and free cancellation for 2 adults, May 15-20, priced under $250, sorted by lowest price.",
    "2026-05-15","2026-05-20", 2, 0, [], 1,
    combo(amenity(103), amenity(2), breakfast(), cancel(), price(0,250), sort(3)),
    "special_filters")); n+=1

tasks.append(row(n, "Dubai",
    "Find 5-star hotels in Dubai with airport shuttle, pool, spa, and breakfast for 2 adults and 1 child (age 3), June 10-15, 2 rooms, sorted by guest rating.",
    "2026-06-10","2026-06-15", 2, 1, [3], 2,
    combo(star(5), amenity(103), amenity(605), amenity(22), breakfast(), sort(10)),
    "special_filters")); n+=1

tasks.append(row(n, "Paris",
    "Search for pet-friendly 3-star hotels in Paris with free WiFi and parking for 2 adults, July 5-10, priced under $180.",
    "2026-07-05","2026-07-10", 2, 0, [], 1,
    combo(star(3), amenity(104), amenity(2), amenity(7), price(0,180)),
    "special_filters")); n+=1

tasks.append(row(n, "Tokyo",
    "Find 4-star hotels in Tokyo with a restaurant, gym, and free WiFi for 2 adults, August 15-20, 3 rooms, priced $150-$400.",
    "2026-08-15","2026-08-20", 2, 0, [], 3,
    combo(star(4), amenity(10), amenity(42), amenity(2), price(150,400)),
    "special_filters")); n+=1

tasks.append(row(n, "Los Angeles",
    "Search for 5-star resort hotels in Los Angeles with pool, gym, spa, and airport shuttle for 2 adults and 2 children (ages 7 and 13), September 10-17, priced under $700.",
    "2026-09-10","2026-09-17", 2, 2, [7,13], 1,
    combo(ptype(499), star(5), amenity(605), amenity(42), amenity(22), amenity(103), price(0,700)),
    "special_filters")); n+=1

tasks.append(row(n, "New York",
    "Find 4-star hotels in New York with pet-friendly policy, gym, free WiFi, breakfast, and free cancellation for 2 adults, October 15-20, priced $200-$500, sorted by guest rating.",
    "2026-10-15","2026-10-20", 2, 0, [], 1,
    combo(star(4), amenity(104), amenity(42), amenity(2), breakfast(), cancel(), price(200,500), sort(10)),
    "special_filters")); n+=1

tasks.append(row(n, "London",
    "Search for 5-star hotels in London with pool, spa, restaurant, guest rating 9+, and breakfast for 2 adults, November 5-12, 2 rooms, priced under $800.",
    "2026-11-05","2026-11-12", 2, 0, [], 2,
    combo(star(5), amenity(605), amenity(22), amenity(10), rating(10), breakfast(), price(0,800)),
    "special_filters")); n+=1

tasks.append(row(n, "Dubai",
    "Find 5-star hotels in Dubai with pool, gym, spa, restaurant, parking, free WiFi, breakfast, free cancellation for 2 adults and 1 child (age 5), December 1-7, priced under $600.",
    "2026-12-01","2026-12-07", 2, 1, [5], 1,
    combo(star(5), amenity(605), amenity(42), amenity(22), amenity(10), amenity(7), amenity(2), breakfast(), cancel(), price(0,600)),
    "special_filters")); n+=1

tasks.append(row(n, "Tokyo",
    "Search for 3-star hotels in Tokyo with free WiFi, breakfast, free cancellation, and guest rating 7+ for 2 adults, January 10-15, priced under $150, sorted by lowest price.",
    "2027-01-10","2027-01-15", 2, 0, [], 1,
    combo(star(3), amenity(2), breakfast(), cancel(), rating(8), price(0,150), sort(3)),
    "special_filters")); n+=1

# ── Write CSV ───────────────────────────────────────────────────────────
HEADERS = [
    "task_id", "task_generation_config_json", "env", "domain",
    "l1_category", "l2_category", "suggested_difficulty",
    "suggested_hint", "suggested_max_steps", "suggested_split",
    "metadata_json",
]

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=HEADERS)
    writer.writeheader()
    for t in tasks:
        writer.writerow(t)

print(f"✅ Wrote {len(tasks)} tasks to {OUTPUT}")
