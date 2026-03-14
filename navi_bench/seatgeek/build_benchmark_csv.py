"""
Generate seatgeek_benchmark_tasks.csv with 73 benchmark tasks.
Run: python navi_bench/seatgeek/build_benchmark_csv.py

Difficulty distribution (hard-weighted per reviewer feedback):
  - easy:    ~5 tasks  (single filter — baseline navigation)
  - medium: ~15 tasks  (2 filters)
  - hard:   ~53 tasks  (3+ filters, combined constraints, advanced scenarios)

Categories:
  - sports_nba, sports_nfl, sports_mlb, sports_nhl, sports_mls
  - concerts, theater, comedy
  - filters_price, filters_quantity, filters_combined
  - browsing, negative
"""

import csv
import json
import os
import sys


def build_tasks():
    """Build the SeatGeek benchmark task list (73 tasks, hard-weighted)."""
    _T = "navi_bench.seatgeek.seatgeek_info_gathering.generate_task_config_deterministic"

    tasks = []

    def add(task_id, task, queries, location, timezone, l2_category, difficulty,
            url="https://seatgeek.com", mode="any", hint=None, split="validation"):
        # Auto-set suggested_max_steps based on difficulty
        max_steps = {"easy": 15, "medium": 30, "hard": 50}.get(difficulty, 30)
        config = {
            "_target_": _T,
            "url": url,
            "task": task,
            "mode": mode,
            "queries": queries,
            "location": location,
            "timezone": timezone,
        }
        tasks.append({
            "task_id": task_id,
            "task_generation_config_json": json.dumps(config),
            "env": "real",
            "domain": "seatgeek",
            "l1_category": "e_commerce",
            "l2_category": l2_category,
            "suggested_difficulty": difficulty,
            "suggested_hint": hint if hint else "null",
            "suggested_max_steps": max_steps,
            "suggested_split": split,
            "metadata_json": "null",
        })

    # =========================================================================
    # SPORTS — NBA  (10 tasks: 0 easy, 2 medium, 8 hard)
    # =========================================================================

    add(
        task_id="navi_bench/seatgeek/sports_nba/0",
        task="Find 2 tickets for a Golden State Warriors game in San Francisco for under $250 each.",
        queries=[[{
            "event_names": ["warriors", "golden state warriors"],
            "cities": ["san francisco"],
            "url_quantity": 2,
            "max_price": 250,
        }]],
        location="San Francisco, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="sports_nba",
        difficulty="medium",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nba/1",
        task="Find Chicago Bulls NBA tickets at United Center for under $150.",
        queries=[[{
            "event_names": ["bulls", "chicago bulls"],
            "event_categories": ["sports", "nba"],
            "venues": ["united center"],
            "max_price": 150,
        }]],
        location="Chicago, IL, United States",
        timezone="America/Chicago",
        l2_category="sports_nba",
        difficulty="medium",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nba/2",
        task="Find 4 tickets to a Lakers game at Crypto.com Arena for under $200 each.",
        queries=[[{
            "event_names": ["lakers", "los angeles lakers"],
            "venues": ["crypto.com arena"],
            "url_quantity": 4,
            "max_price": 200,
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="sports_nba",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nba/3",
        task="Find 4 tickets to a Lakers game at Crypto.com Arena in Los Angeles for under $200 each on the event listing page.",
        queries=[[{
            "event_names": ["lakers", "los angeles lakers"],
            "venues": ["crypto.com arena"],
            "cities": ["los angeles"],
            "url_quantity": 4,
            "max_price": 200,
            "require_page_type": "event_listing",
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="sports_nba",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nba/4",
        task="Find Boston Celtics home game tickets at TD Garden for under $300 with 2 tickets.",
        queries=[[{
            "event_names": ["celtics", "boston celtics"],
            "venues": ["td garden"],
            "cities": ["boston"],
            "url_quantity": 2,
            "max_price": 300,
        }]],
        location="Boston, MA, United States",
        timezone="America/New_York",
        l2_category="sports_nba",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nba/5",
        task="Find 2 Miami Heat tickets at Kaseya Center for under $150 each on the event listing page.",
        queries=[[{
            "event_names": ["heat", "miami heat"],
            "venues": ["kaseya center"],
            "url_quantity": 2,
            "max_price": 150,
            "require_page_type": "event_listing",
        }]],
        location="Miami, FL, United States",
        timezone="America/New_York",
        l2_category="sports_nba",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nba/6",
        task="Find 4 tickets to a New York Knicks game at Madison Square Garden for under $250 each on the event listing page.",
        queries=[[{
            "event_names": ["knicks", "new york knicks"],
            "venues": ["madison square garden"],
            "cities": ["new york"],
            "url_quantity": 4,
            "max_price": 250,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="sports_nba",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nba/7",
        task="Find 2 Golden State Warriors tickets at Chase Center in San Francisco for under $200 each on the event listing page.",
        queries=[[{
            "event_names": ["warriors", "golden state warriors"],
            "venues": ["chase center"],
            "cities": ["san francisco"],
            "url_quantity": 2,
            "max_price": 200,
            "require_page_type": "event_listing",
        }]],
        location="San Francisco, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="sports_nba",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nba/8",
        task="Find 4 NBA tickets in Los Angeles for under $100 each on the event listing page.",
        queries=[[{
            "event_categories": ["sports", "nba"],
            "cities": ["los angeles", "inglewood"],
            "url_quantity": 4,
            "max_price": 100,
            "require_page_type": "event_listing",
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="sports_nba",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nba/9",
        task="Find 2 Chicago Bulls tickets at United Center in Chicago for under $120 each on the event listing page.",
        queries=[[{
            "event_names": ["bulls", "chicago bulls"],
            "venues": ["united center"],
            "cities": ["chicago"],
            "url_quantity": 2,
            "max_price": 120,
            "require_page_type": "event_listing",
        }]],
        location="Chicago, IL, United States",
        timezone="America/Chicago",
        l2_category="sports_nba",
        difficulty="hard",
    )

    # =========================================================================
    # SPORTS — NFL  (8 tasks: 0 easy, 1 medium, 7 hard)
    # =========================================================================

    add(
        task_id="navi_bench/seatgeek/sports_nfl/0",
        task="Find Dallas Cowboys tickets at AT&T Stadium for under $200.",
        queries=[[{
            "event_names": ["cowboys", "dallas cowboys"],
            "venues": ["at&t stadium"],
            "max_price": 200,
        }]],
        location="Dallas, TX, United States",
        timezone="America/Chicago",
        l2_category="sports_nfl",
        difficulty="medium",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nfl/1",
        task="Find 4 Dallas Cowboys tickets at AT&T Stadium for under $300 each.",
        queries=[[{
            "event_names": ["cowboys", "dallas cowboys"],
            "venues": ["at&t stadium"],
            "url_quantity": 4,
            "max_price": 300,
        }]],
        location="Dallas, TX, United States",
        timezone="America/Chicago",
        l2_category="sports_nfl",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nfl/2",
        task="Find 2 tickets to a San Francisco 49ers home game at Levi's Stadium for under $180 each.",
        queries=[[{
            "event_names": ["49ers", "san francisco 49ers"],
            "venues": ["levi's stadium"],
            "cities": ["santa clara", "san francisco"],
            "url_quantity": 2,
            "max_price": 180,
        }]],
        location="San Francisco, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="sports_nfl",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nfl/3",
        task="Find 2 Philadelphia Eagles tickets at Lincoln Financial Field for under $250 each on the event listing page.",
        queries=[[{
            "event_names": ["eagles", "philadelphia eagles"],
            "venues": ["lincoln financial field"],
            "url_quantity": 2,
            "max_price": 250,
            "require_page_type": "event_listing",
        }]],
        location="Philadelphia, PA, United States",
        timezone="America/New_York",
        l2_category="sports_nfl",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nfl/4",
        task="Find 4 Green Bay Packers tickets at Lambeau Field for under $200 each on the event listing page.",
        queries=[[{
            "event_names": ["packers", "green bay packers"],
            "venues": ["lambeau field"],
            "url_quantity": 4,
            "max_price": 200,
            "require_page_type": "event_listing",
        }]],
        location="Green Bay, WI, United States",
        timezone="America/Chicago",
        l2_category="sports_nfl",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nfl/5",
        task="Find 4 Dallas Cowboys tickets at AT&T Stadium in Arlington for under $250 each on the event listing page.",
        queries=[[{
            "event_names": ["cowboys", "dallas cowboys"],
            "venues": ["at&t stadium"],
            "cities": ["arlington", "dallas"],
            "url_quantity": 4,
            "max_price": 250,
            "require_page_type": "event_listing",
        }]],
        location="Dallas, TX, United States",
        timezone="America/Chicago",
        l2_category="sports_nfl",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nfl/6",
        task="Find 2 San Francisco 49ers tickets at Levi's Stadium for under $150 each on the event listing page.",
        queries=[[{
            "event_names": ["49ers", "san francisco 49ers"],
            "venues": ["levi's stadium"],
            "url_quantity": 2,
            "max_price": 150,
            "require_page_type": "event_listing",
        }]],
        location="San Francisco, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="sports_nfl",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nfl/7",
        task="Find 4 NFL tickets in Dallas for under $150 each on the event listing page.",
        queries=[[{
            "event_categories": ["sports", "nfl"],
            "cities": ["arlington", "dallas"],
            "url_quantity": 4,
            "max_price": 150,
            "require_page_type": "event_listing",
        }]],
        location="Dallas, TX, United States",
        timezone="America/Chicago",
        l2_category="sports_nfl",
        difficulty="hard",
    )

    # =========================================================================
    # SPORTS — MLB  (7 tasks: 0 easy, 2 medium, 5 hard)
    # =========================================================================

    add(
        task_id="navi_bench/seatgeek/sports_mlb/0",
        task="Find 2 New York Yankees tickets at Yankee Stadium for under $150 each.",
        queries=[[{
            "event_names": ["yankees", "new york yankees"],
            "venues": ["yankee stadium"],
            "url_quantity": 2,
            "max_price": 150,
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="sports_mlb",
        difficulty="medium",
    )

    add(
        task_id="navi_bench/seatgeek/sports_mlb/1",
        task="Find Los Angeles Dodgers tickets at Dodger Stadium for under $100.",
        queries=[[{
            "event_names": ["dodgers", "los angeles dodgers"],
            "venues": ["dodger stadium"],
            "max_price": 100,
            "cities": ["los angeles"],
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="sports_mlb",
        difficulty="medium",
    )

    add(
        task_id="navi_bench/seatgeek/sports_mlb/2",
        task="Find 4 New York Yankees tickets at Yankee Stadium for under $150 each on the event listing page.",
        queries=[[{
            "event_names": ["yankees", "new york yankees"],
            "venues": ["yankee stadium"],
            "url_quantity": 4,
            "max_price": 150,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="sports_mlb",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_mlb/3",
        task="Find 2 Boston Red Sox tickets at Fenway Park for under $120 each on the event listing page.",
        queries=[[{
            "event_names": ["red sox", "boston red sox"],
            "venues": ["fenway park"],
            "cities": ["boston"],
            "url_quantity": 2,
            "max_price": 120,
            "require_page_type": "event_listing",
        }]],
        location="Boston, MA, United States",
        timezone="America/New_York",
        l2_category="sports_mlb",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_mlb/4",
        task="Find 4 Los Angeles Dodgers tickets at Dodger Stadium for under $80 each on the event listing page.",
        queries=[[{
            "event_names": ["dodgers", "los angeles dodgers"],
            "venues": ["dodger stadium"],
            "url_quantity": 4,
            "max_price": 80,
            "require_page_type": "event_listing",
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="sports_mlb",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_mlb/5",
        task="Find 2 Chicago Cubs tickets at Wrigley Field in Chicago for under $100 each on the event listing page.",
        queries=[[{
            "event_names": ["cubs", "chicago cubs"],
            "venues": ["wrigley field"],
            "cities": ["chicago"],
            "url_quantity": 2,
            "max_price": 100,
            "require_page_type": "event_listing",
        }]],
        location="Chicago, IL, United States",
        timezone="America/Chicago",
        l2_category="sports_mlb",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_mlb/6",
        task="Find 4 MLB tickets in New York for under $80 each on the event listing page.",
        queries=[[{
            "event_categories": ["sports", "mlb"],
            "cities": ["new york", "bronx"],
            "url_quantity": 4,
            "max_price": 80,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="sports_mlb",
        difficulty="hard",
    )

    # =========================================================================
    # SPORTS — NHL  (5 tasks: 0 easy, 1 medium, 4 hard)
    # =========================================================================

    add(
        task_id="navi_bench/seatgeek/sports_nhl/0",
        task="Find 2 New York Rangers tickets at Madison Square Garden for under $200 each.",
        queries=[[{
            "event_names": ["rangers", "new york rangers"],
            "venues": ["madison square garden"],
            "url_quantity": 2,
            "max_price": 200,
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="sports_nhl",
        difficulty="medium",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nhl/1",
        task="Find 2 Boston Bruins tickets at TD Garden for under $200 each on the event listing page.",
        queries=[[{
            "event_names": ["bruins", "boston bruins"],
            "venues": ["td garden"],
            "cities": ["boston"],
            "url_quantity": 2,
            "max_price": 200,
            "require_page_type": "event_listing",
        }]],
        location="Boston, MA, United States",
        timezone="America/New_York",
        l2_category="sports_nhl",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nhl/2",
        task="Find 4 Toronto Maple Leafs tickets at Scotiabank Arena for under $150 each on the event listing page.",
        queries=[[{
            "event_names": ["maple leafs", "toronto maple leafs"],
            "venues": ["scotiabank arena"],
            "url_quantity": 4,
            "max_price": 150,
            "require_page_type": "event_listing",
        }]],
        location="Toronto, ON, Canada",
        timezone="America/Toronto",
        l2_category="sports_nhl",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nhl/3",
        task="Find 2 New York Rangers tickets at Madison Square Garden in New York for under $250 each on the event listing page.",
        queries=[[{
            "event_names": ["rangers", "new york rangers"],
            "venues": ["madison square garden"],
            "cities": ["new york"],
            "url_quantity": 2,
            "max_price": 250,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="sports_nhl",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_nhl/4",
        task="Find 4 NHL hockey tickets in Boston for under $150 each on the event listing page.",
        queries=[[{
            "event_categories": ["sports", "nhl"],
            "cities": ["boston"],
            "url_quantity": 4,
            "max_price": 150,
            "require_page_type": "event_listing",
        }]],
        location="Boston, MA, United States",
        timezone="America/New_York",
        l2_category="sports_nhl",
        difficulty="hard",
    )

    # =========================================================================
    # SPORTS — MLS  (3 tasks: 0 easy, 0 medium, 3 hard)
    # =========================================================================

    add(
        task_id="navi_bench/seatgeek/sports_mls/0",
        task="Find 2 LAFC tickets at BMO Stadium in Los Angeles for under $80 each.",
        queries=[[{
            "event_names": ["lafc", "los angeles fc", "los angeles football club"],
            "venues": ["bmo stadium"],
            "cities": ["los angeles"],
            "url_quantity": 2,
            "max_price": 80,
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="sports_mls",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_mls/1",
        task="Find 4 LAFC tickets at BMO Stadium in Los Angeles for under $60 each on the event listing page.",
        queries=[[{
            "event_names": ["lafc", "los angeles fc"],
            "venues": ["bmo stadium"],
            "cities": ["los angeles"],
            "url_quantity": 4,
            "max_price": 60,
            "require_page_type": "event_listing",
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="sports_mls",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/sports_mls/2",
        task="Find 2 MLS soccer tickets in Los Angeles for under $50 each on the event listing page.",
        queries=[[{
            "event_categories": ["sports", "mls", "soccer"],
            "cities": ["los angeles"],
            "url_quantity": 2,
            "max_price": 50,
            "require_page_type": "event_listing",
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="sports_mls",
        difficulty="hard",
    )

    # =========================================================================
    # CONCERTS  (10 tasks: 1 easy, 2 medium, 7 hard)
    # =========================================================================

    add(
        task_id="navi_bench/seatgeek/concerts/0",
        task="Find Taylor Swift concert tickets.",
        queries=[[{
            "event_names": ["taylor swift"],
            "event_categories": ["concerts", "music"],
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="concerts",
        difficulty="easy",
    )

    add(
        task_id="navi_bench/seatgeek/concerts/1",
        task="Find Drake concert tickets in Los Angeles for under $300.",
        queries=[[{
            "event_names": ["drake"],
            "cities": ["los angeles", "inglewood"],
            "max_price": 300,
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="concerts",
        difficulty="medium",
    )

    add(
        task_id="navi_bench/seatgeek/concerts/2",
        task="Find 2 tickets to a Coldplay concert for under $200 each.",
        queries=[[{
            "event_names": ["coldplay"],
            "event_categories": ["concerts", "music"],
            "url_quantity": 2,
            "max_price": 200,
        }]],
        location="Chicago, IL, United States",
        timezone="America/Chicago",
        l2_category="concerts",
        difficulty="medium",
    )

    add(
        task_id="navi_bench/seatgeek/concerts/3",
        task="Find 2 Drake concert tickets in Los Angeles for under $250 each on the event listing page.",
        queries=[[{
            "event_names": ["drake"],
            "cities": ["los angeles", "inglewood"],
            "url_quantity": 2,
            "max_price": 250,
            "require_page_type": "event_listing",
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="concerts",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/concerts/4",
        task="Find 4 Coldplay concert tickets for under $200 each on the event listing page.",
        queries=[[{
            "event_names": ["coldplay"],
            "url_quantity": 4,
            "max_price": 200,
            "require_page_type": "event_listing",
        }]],
        location="Chicago, IL, United States",
        timezone="America/Chicago",
        l2_category="concerts",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/concerts/5",
        task="Find 2 Taylor Swift concert tickets in New York for under $400 each on the event listing page.",
        queries=[[{
            "event_names": ["taylor swift"],
            "cities": ["new york"],
            "url_quantity": 2,
            "max_price": 400,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="concerts",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/concerts/6",
        task="Find 4 concert tickets in Los Angeles for under $150 each on the event listing page.",
        queries=[[{
            "event_categories": ["concerts", "music"],
            "cities": ["los angeles", "inglewood"],
            "url_quantity": 4,
            "max_price": 150,
            "require_page_type": "event_listing",
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="concerts",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/concerts/7",
        task="Find 2 concert tickets in Chicago for under $100 each on the event listing page.",
        queries=[[{
            "event_categories": ["concerts", "music"],
            "cities": ["chicago"],
            "url_quantity": 2,
            "max_price": 100,
            "require_page_type": "event_listing",
        }]],
        location="Chicago, IL, United States",
        timezone="America/Chicago",
        l2_category="concerts",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/concerts/8",
        task="Find 4 concert tickets in New York for between $100 and $300 each on the event listing page.",
        queries=[[{
            "event_categories": ["concerts", "music"],
            "cities": ["new york"],
            "url_quantity": 4,
            "min_price": 100,
            "max_price": 300,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="concerts",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/concerts/9",
        task="Find 2 concert tickets in San Francisco for under $200 each on the event listing page.",
        queries=[[{
            "event_categories": ["concerts", "music"],
            "cities": ["san francisco"],
            "url_quantity": 2,
            "max_price": 200,
            "require_page_type": "event_listing",
        }]],
        location="San Francisco, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="concerts",
        difficulty="hard",
    )

    # =========================================================================
    # THEATER  (8 tasks: 1 easy, 1 medium, 6 hard)
    # =========================================================================

    add(
        task_id="navi_bench/seatgeek/theater/0",
        task="Find Hamilton tickets on Broadway in New York.",
        queries=[[{
            "event_names": ["hamilton"],
            "event_categories": ["theater"],
            "cities": ["new york"],
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="theater",
        difficulty="easy",
    )

    add(
        task_id="navi_bench/seatgeek/theater/1",
        task="Find Wicked theater tickets in New York for under $200.",
        queries=[[{
            "event_names": ["wicked"],
            "event_categories": ["theater"],
            "cities": ["new york"],
            "max_price": 200,
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="theater",
        difficulty="medium",
    )

    add(
        task_id="navi_bench/seatgeek/theater/2",
        task="Find 2 Wicked tickets in New York for under $250 each on the event listing page.",
        queries=[[{
            "event_names": ["wicked"],
            "cities": ["new york"],
            "url_quantity": 2,
            "max_price": 250,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="theater",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/theater/3",
        task="Find 4 The Lion King tickets in New York for under $200 each on the event listing page.",
        queries=[[{
            "event_names": ["lion king", "the lion king"],
            "cities": ["new york"],
            "url_quantity": 4,
            "max_price": 200,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="theater",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/theater/4",
        task="Find 2 tickets to a Broadway show in New York for under $150 each on the event listing page.",
        queries=[[{
            "event_categories": ["theater"],
            "cities": ["new york"],
            "url_quantity": 2,
            "max_price": 150,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="theater",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/theater/5",
        task="Find 2 Hamilton tickets in New York for under $300 each on the event listing page.",
        queries=[[{
            "event_names": ["hamilton"],
            "cities": ["new york"],
            "url_quantity": 2,
            "max_price": 300,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="theater",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/theater/6",
        task="Find 4 theater tickets in New York for under $100 each on the event listing page.",
        queries=[[{
            "event_categories": ["theater"],
            "cities": ["new york"],
            "url_quantity": 4,
            "max_price": 100,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="theater",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/theater/7",
        task="Find 2 theater tickets in Chicago for under $150 each on the event listing page.",
        queries=[[{
            "event_categories": ["theater"],
            "cities": ["chicago"],
            "url_quantity": 2,
            "max_price": 150,
            "require_page_type": "event_listing",
        }]],
        location="Chicago, IL, United States",
        timezone="America/Chicago",
        l2_category="theater",
        difficulty="hard",
    )

    # =========================================================================
    # COMEDY  (3 tasks: 0 easy, 1 medium, 2 hard)
    # =========================================================================

    add(
        task_id="navi_bench/seatgeek/comedy/0",
        task="Find comedy show tickets in New York for under $100.",
        queries=[[{
            "event_categories": ["comedy"],
            "cities": ["new york"],
            "max_price": 100,
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="comedy",
        difficulty="medium",
    )

    add(
        task_id="navi_bench/seatgeek/comedy/1",
        task="Find 2 comedy show tickets in Los Angeles for under $80 each on the event listing page.",
        queries=[[{
            "event_categories": ["comedy"],
            "cities": ["los angeles"],
            "url_quantity": 2,
            "max_price": 80,
            "require_page_type": "event_listing",
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="comedy",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/comedy/2",
        task="Find 4 comedy show tickets in Chicago for under $60 each on the event listing page.",
        queries=[[{
            "event_categories": ["comedy"],
            "cities": ["chicago"],
            "url_quantity": 4,
            "max_price": 60,
            "require_page_type": "event_listing",
        }]],
        location="Chicago, IL, United States",
        timezone="America/Chicago",
        l2_category="comedy",
        difficulty="hard",
    )

    # =========================================================================
    # FILTERS — Price  (5 tasks: 0 easy, 1 medium, 4 hard)
    # =========================================================================

    add(
        task_id="navi_bench/seatgeek/filters_price/0",
        task="Find NBA tickets for under $50 on the event listing page.",
        queries=[[{
            "event_categories": ["sports", "nba"],
            "max_price": 50,
            "require_page_type": "event_listing",
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="filters_price",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/filters_price/1",
        task="Find concert tickets in New York for between $100 and $300 each.",
        queries=[[{
            "event_categories": ["concerts", "music"],
            "cities": ["new york"],
            "min_price": 100,
            "max_price": 300,
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="filters_price",
        difficulty="medium",
    )

    add(
        task_id="navi_bench/seatgeek/filters_price/2",
        task="Find theater tickets in New York for under $100 on the event listing page.",
        queries=[[{
            "event_categories": ["theater"],
            "cities": ["new york"],
            "max_price": 100,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="filters_price",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/filters_price/3",
        task="Find NFL tickets for under $100 on the event listing page.",
        queries=[[{
            "event_categories": ["sports", "nfl"],
            "max_price": 100,
            "require_page_type": "event_listing",
        }]],
        location="Dallas, TX, United States",
        timezone="America/Chicago",
        l2_category="filters_price",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/filters_price/4",
        task="Find 2 MLB tickets for between $50 and $150 each on the event listing page.",
        queries=[[{
            "event_categories": ["sports", "mlb"],
            "url_quantity": 2,
            "min_price": 50,
            "max_price": 150,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="filters_price",
        difficulty="hard",
    )

    # =========================================================================
    # FILTERS — Quantity  (3 tasks: 0 easy, 0 medium, 3 hard)
    # =========================================================================

    add(
        task_id="navi_bench/seatgeek/filters_quantity/0",
        task="Find 4 NBA tickets for under $100 each on the event listing page.",
        queries=[[{
            "event_categories": ["sports", "nba"],
            "url_quantity": 4,
            "max_price": 100,
            "require_page_type": "event_listing",
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="filters_quantity",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/filters_quantity/1",
        task="Find 6 concert tickets for under $200 each on the event listing page.",
        queries=[[{
            "event_categories": ["concerts", "music"],
            "url_quantity": 6,
            "max_price": 200,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="filters_quantity",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/filters_quantity/2",
        task="Find 2 theater tickets in New York for under $150 each on the event listing page.",
        queries=[[{
            "event_categories": ["theater"],
            "cities": ["new york"],
            "url_quantity": 2,
            "max_price": 150,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="filters_quantity",
        difficulty="hard",
    )

    # =========================================================================
    # FILTERS — Combined / Advanced  (7 tasks: 0 easy, 0 medium, 7 hard)
    # =========================================================================

    add(
        task_id="navi_bench/seatgeek/filters_combined/0",
        task="Find 4 Lakers tickets at Crypto.com Arena in Los Angeles for under $200 each on the event listing page.",
        queries=[[{
            "event_names": ["lakers", "los angeles lakers"],
            "venues": ["crypto.com arena"],
            "cities": ["los angeles"],
            "url_quantity": 4,
            "max_price": 200,
            "require_page_type": "event_listing",
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="filters_combined",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/filters_combined/1",
        task="Find 2 New York Knicks tickets at Madison Square Garden for under $300 each on the event listing page.",
        queries=[[{
            "event_names": ["knicks", "new york knicks"],
            "venues": ["madison square garden"],
            "cities": ["new york"],
            "url_quantity": 2,
            "max_price": 300,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="filters_combined",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/filters_combined/2",
        task="Find 2 Broadway show tickets in New York for under $250 each on the event listing page.",
        queries=[[{
            "event_categories": ["theater"],
            "cities": ["new york"],
            "url_quantity": 2,
            "max_price": 250,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="filters_combined",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/filters_combined/3",
        task="Find 2 MLB baseball tickets in Chicago for under $100 each on the event listing page.",
        queries=[[{
            "event_categories": ["sports", "mlb"],
            "cities": ["chicago"],
            "url_quantity": 2,
            "max_price": 100,
            "require_page_type": "event_listing",
        }]],
        location="Chicago, IL, United States",
        timezone="America/Chicago",
        l2_category="filters_combined",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/filters_combined/4",
        task="Find 2 NBA tickets in Boston for between $50 and $200 each on the event listing page.",
        queries=[[{
            "event_categories": ["sports", "nba"],
            "cities": ["boston"],
            "url_quantity": 2,
            "min_price": 50,
            "max_price": 200,
            "require_page_type": "event_listing",
        }]],
        location="Boston, MA, United States",
        timezone="America/New_York",
        l2_category="filters_combined",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/filters_combined/5",
        task="Find 4 NFL tickets in Philadelphia for under $200 each on the event listing page.",
        queries=[[{
            "event_categories": ["sports", "nfl"],
            "cities": ["philadelphia"],
            "url_quantity": 4,
            "max_price": 200,
            "require_page_type": "event_listing",
        }]],
        location="Philadelphia, PA, United States",
        timezone="America/New_York",
        l2_category="filters_combined",
        difficulty="hard",
    )

    add(
        task_id="navi_bench/seatgeek/filters_combined/6",
        task="Find 2 comedy tickets in New York for under $60 each on the event listing page.",
        queries=[[{
            "event_categories": ["comedy"],
            "cities": ["new york"],
            "url_quantity": 2,
            "max_price": 60,
            "require_page_type": "event_listing",
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="filters_combined",
        difficulty="hard",
    )

    # =========================================================================
    # BROWSING — Performer/Category pages  (3 tasks: 2 easy, 1 medium)
    # (Minimal easy tasks — just baseline navigation)
    # =========================================================================

    add(
        task_id="navi_bench/seatgeek/browsing/0",
        task="Browse upcoming Los Angeles Lakers games on SeatGeek.",
        queries=[[{
            "event_names": ["lakers"],
            "require_page_type": ["performer", "event_listing"],
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="browsing",
        difficulty="easy",
    )

    add(
        task_id="navi_bench/seatgeek/browsing/1",
        task="Search for Taylor Swift and view upcoming concerts on SeatGeek.",
        queries=[[{
            "event_names": ["taylor swift"],
            "require_page_type": ["performer", "event_listing", "search"],
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="browsing",
        difficulty="easy",
    )

    add(
        task_id="navi_bench/seatgeek/browsing/2",
        task="Browse upcoming Hamilton shows and find tickets for under $300.",
        queries=[[{
            "event_names": ["hamilton"],
            "max_price": 300,
        }]],
        location="New York, NY, United States",
        timezone="America/New_York",
        l2_category="browsing",
        difficulty="medium",
    )

    # =========================================================================
    # NEGATIVE TESTS — Tricky scenarios  (3 tasks: 0 easy, 3 medium)
    # =========================================================================

    add(
        task_id="navi_bench/seatgeek/negative/0",
        task="Find Lakers home game tickets in Los Angeles on the event listing page.",
        queries=[[{
            "event_names": ["lakers"],
            "cities": ["los angeles"],
            "require_page_type": "event_listing",
        }]],
        location="Chicago, IL, United States",
        timezone="America/Chicago",
        l2_category="negative",
        difficulty="medium",
        hint="Agent may navigate to Bulls vs Lakers in Chicago (wrong city for query).",
    )

    add(
        task_id="navi_bench/seatgeek/negative/1",
        task="Find NBA basketball tickets on the event listing page.",
        queries=[[{
            "event_categories": ["sports", "nba"],
            "require_page_type": "event_listing",
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="negative",
        difficulty="medium",
        hint="Agent may navigate to a concert page instead of sports.",
    )

    add(
        task_id="navi_bench/seatgeek/negative/2",
        task="Find Lakers tickets for an upcoming game on the event listing page.",
        queries=[[{
            "event_names": ["lakers", "los angeles lakers"],
            "require_page_type": "event_listing",
        }]],
        location="Los Angeles, CA, United States",
        timezone="America/Los_Angeles",
        l2_category="negative",
        difficulty="medium",
        hint="Agent may navigate to wrong team's game page.",
    )

    return tasks


def write_csv(tasks, path):
    """Write tasks to CSV in the same format as realtor_benchmark_tasks.csv."""
    fieldnames = [
        "task_id",
        "task_generation_config_json",
        "env",
        "domain",
        "l1_category",
        "l2_category",
        "suggested_difficulty",
        "suggested_hint",
        "suggested_max_steps",
        "suggested_split",
        "metadata_json",
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for task in tasks:
            row = {}
            for k, v in task.items():
                if v is None:
                    row[k] = ""
                else:
                    row[k] = v
            writer.writerow(row)


if __name__ == "__main__":
    tasks = build_tasks()

    csv_path = os.path.join(os.path.dirname(__file__), "seatgeek_benchmark_tasks.csv")
    write_csv(tasks, csv_path)

    print(f"Written {len(tasks)} tasks to {csv_path}")
    print()

    # Print distribution
    cats = {}
    diffs = {}
    for t in tasks:
        c = t["l2_category"]
        d = t["suggested_difficulty"]
        cats[c] = cats.get(c, 0) + 1
        diffs[d] = diffs.get(d, 0) + 1

    print("Category distribution:")
    for c, n in sorted(cats.items()):
        print(f"  {c}: {n}")
    print(f"\nDifficulty distribution:")
    for d, n in sorted(diffs.items(), key=lambda x: ["easy", "medium", "hard"].index(x[0])):
        print(f"  {d}: {n}")
    print(f"\nTotal: {len(tasks)} tasks")
