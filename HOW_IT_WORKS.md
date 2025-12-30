# StubHub Verifier - How It Works

## Overview

The StubHub Verifier validates that an AI agent correctly navigates to and finds the right event tickets. It uses **stack-based navigation tracking** for accurate verification.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    StubHub Verifier                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   Browser (Playwright)                                       │
│        │                                                     │
│        ▼                                                     │
│   ┌─────────────────┐    ┌─────────────────────────────┐    │
│   │  JavaScript     │    │  Python Verifier            │    │
│   │  Scraper        │───▶│  (Navigation Stack)         │    │
│   │  (DOM + LD+JSON)│    │                             │    │
│   └─────────────────┘    └─────────────────────────────┘    │
│                                    │                         │
│                                    ▼                         │
│                          ┌─────────────────────────────┐    │
│                          │  Query Matching              │    │
│                          │  (Strict vs Lenient)         │    │
│                          └─────────────────────────────┘    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## How Verification Works

### Step 1: Agent Navigates
The AI agent or user browses StubHub pages.

### Step 2: JavaScript Scrapes Each Page
For each page visited, the JS scraper extracts:
- Event name, venue, city, country
- Date, price, ticket count
- Availability status
- Page type (event_listing, event_category, etc.)

**Data Sources (Priority Order):**
1. **LD+JSON** (most reliable) - Structured data from `<script type="application/ld+json">`
2. **data-listing-id** attributes - StubHub's ticket listing elements
3. **DOM fallback** - Text parsing from visible elements

### Step 3: Push to Navigation Stack
Each page visit is pushed to a stack:
```python
navigation_stack = [
    {"url": "https://stubhub.com/", "page_type": "home", "infos": [...]},
    {"url": "https://stubhub.com/.../performer/...", "page_type": "event_category", "infos": [...]},
    {"url": "https://stubhub.com/.../event/12345", "page_type": "event_listing", "infos": [...]}
]
```

**URL De-duplication:** Same pages are updated, not duplicated.

### Step 4: Walk Stack Backwards (on Compute)
When verification runs:

```
Priority 1: Find event_listing → STRICT match
Priority 2: No event_listing → LENIENT match on category pages
```

| Page Type | Matching | Example |
|-----------|----------|---------|
| `event_listing` | **STRICT** - Only match that event | User clicked into Brno event → check Brno only |
| `event_category` | **LENIENT** - Match any visible | Sold-out event visible in list → still passes |
| `search_results` | **LENIENT** - Match any visible | Search results show matching event |

---

## Query Structure

Tasks define what to verify:

```python
queries=[[{
    "event_names": ["coldplay"],        # Match "coldplay" in event name
    "cities": ["haifa", "tel aviv"],    # Must be in Israel
    "require_available": False,         # Sold-out OK
}]]
```

### Matching Logic
- `event_names`: Case-insensitive substring match
- `cities`: Case-insensitive substring match  
- `require_available`: If True, event must have tickets

---

## Demo Scenarios

| Scenario | Location | Verification |
|----------|----------|--------------|
| Coldplay Concert | Israel | Event name + city match |
| Zakir Khan Concert | Pune, India | Event name + city match |
| NBA Game | USA | Event name + category match |

**Run Demo:**
```powershell
cd navi_bench/stubhub
python demo_stubhub.py
```

---

## File Structure

```
navi_bench/stubhub/
├── stubhub_info_gathering.js   # JavaScript scraper (1500+ lines)
├── stubhub_info_gathering.py   # Python verifier (900+ lines)
├── demo_stubhub.py             # Interactive demo
├── batch_demo_stubhub.py       # Batch testing
└── test_stubhub_unit.py        # Unit tests
```

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Stack-Based Tracking** | Tracks all page visits, walks backwards for accuracy |
| **URL De-duplication** | Same page updates existing entry, prevents bloat |
| **Multi-Tab Safe** | Handles StubHub opening events in new tabs |
| **LD+JSON Priority** | Uses reliable structured data when available |
| **Multi-Currency** | Supports USD, INR, EUR, GBP |
| **30+ Query Fields** | Comprehensive matching options |

---

## Example Flow

**Task:** Find Coldplay concert in Israel

1. User opens StubHub homepage
2. User searches "Coldplay"
3. User lands on category page (sees Haifa, Brno events)
4. User clicks **Brno** event (Czech Republic)

**Verification:**
```
Stack: [home, category, event_listing(Brno)]
       
compute() finds event_listing → STRICT check:
  - Event: "Coldplay..." ✅
  - City: "brno" ❌ (not in ["haifa", "tel aviv", "israel"])
  
Result: FAIL (0%)
```

**If user clicked Haifa instead:**
```
  - Event: "Coldplay..." ✅
  - City: "haifa" ✅
  
Result: PASS (100%)
```
