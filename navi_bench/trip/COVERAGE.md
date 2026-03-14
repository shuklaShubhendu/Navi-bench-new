# Trip.com Filter Coverage Documentation

## Overview

This document catalogs all common filters available on Trip.com's hotel search with **actual URL examples** as they appear in the query string parameters.

---

## IMPORTANT: Value Format Rules

Trip.com primarily uses flat query parameters passed in the URL (e.g., `?city=2&star=4,5`) rather than nested JSON structures.

### Format 1: Comma-Separated IDs
For properties with multiple selections (like star ratings, facilities), Trip.com typically concatenates the selected IDs with commas:
`&star=4,5`
`&facility=20,38,103`

### Format 2: Direct Values
For simple string, number, or boolean toggles, the raw value is passed:
`&adult=2`
`&price=50-200`

---

## 1. SEARCH MODE & LOCATION

### Location Search
**Location**: URL path and query parameters

| URL Parameter | Meaning | Example |
|---------------|---------|---------|
| `city` | The internal integer ID for the city | `city=2` (London) |
| `cityName` | The display name of the city | `cityName=London` |

```url
https://www.trip.com/hotels/list?city=2&cityName=London
```

---

## 2. GUESTS & ROOMS

### Example: 2 Adults, 1 Room
```url
&adult=2&crn=1
```

### Example: 2 Adults, 2 Children
```url
&adult=2&children=2
```

| Parameter | Meaning | 
|-----------|---------|
| `adult` | Number of adults |
| `children` | Number of children |
| `crn` | Number of rooms (stands for Count Roon Number or similar) |
| `ages` | Ages of children if specified (e.g., `ages=5,10`) |

---

## 3. DATES

### Example: Check-in March 20, Check-out March 25
```url
&checkin=2026-03-20&checkout=2026-03-25
```

> Dates always use the format `YYYY-MM-DD`.

---

## 4. PRICE

### Example: Price Range $50 - $200
```url
&price=50-200
```

### Example: Minimum Price $100+
```url
&price=100-
```

### Example: Maximum Price Up to $300
```url
&price=0-300
```

---

## 5. STAR RATING

Star ratings are typically passed as comma-separated digits in the `star` parameter.

### Example: 4-Star and 5-Star Hotels
```url
&star=4,5
```

| Star Rating | Value |
|-------------|-------|
| 1 Star | `1` |
| 2 Stars | `2` |
| 3 Stars | `3` |
| 4 Stars | `4` |
| 5 Stars | `5` |
| Unrated | `0` (sometimes omitted) |

---

## 6. PROPERTY TYPE

Trip.com categorizes accommodations and allows filtering via `hotelType` or `propertyType`.

### Example: Apartments and Hostels
```url
&hotelType=2,4
```

*Note: IDs vary by region, but numerical IDs map directly to property types like Hotel, Resort, Apartment, Villa, Hostel.*

---

## 7. AMENITIES & FACILITIES

Trip.com uses a `facility` parameter with comma-separated IDs to represent checked amenities. 

### Example: Pool and Free Wi-Fi
```url
&facility=20,38
```

Common standard amenity IDs (illustrative, varies slightly by region setting):

| Filter | URL Parameter | Illustrative ID |
|--------|---------------|-----------------|
| Swimming Pool | `facility` | `20` |
| Free Wi-Fi | `facility` | `5` |
| Parking | `facility` | `7` |
| Gym/Fitness Center | `facility` | `38` |
| Restaurant | `facility` | `10` |
| Airport Shuttle | `facility` | `103` |

---

## 8. GUEST RATING

Filtering by minimum review scores.

### Example: Outstanding (4.5+)
```url
&reviewScore=4.5
```

| Rating Tier | URL Parameter |
|-------------|---------------|
| 3.5+ (Good) | `reviewScore=3.5` |
| 4.0+ (Very Good) | `reviewScore=4.0` |
| 4.5+ (Outstanding) | `reviewScore=4.5` |

---

## 9. MEALS & BED TYPE

### Bed Type
```url
&bedType=1
```
*(1=Double/King, 2=Twin/Single)*

### Meals (Breakfast)
```url
&mealType=1
```
*(1=Breakfast Included)*

---

## 10. BRANDS & CHAINS

Trip.com groups hotel chains using a `brand` parameter.

### Example: Marriott and Hilton
```url
&brand=14,25
```

---

## 11. PAYMENT & POLICIES

### Example: Free Cancellation
```url
&freecancellation=T
```
*(Often passed as boolean flags like `T` (True) or `F` (False))*

### Example: Pay at Hotel
```url
&payAtHotel=T
```

---

## 12. SORT OPTIONS

The order of search results is governed by `sortType` or `listSort`.

### Example: Sort by Lowest Price
```url
&listSort=price
```

| Sort Option | Value |
|-------------|-------|
| Recommended | *(default, omitted)* |
| Price (Low to High) | `price` |
| Price (High to Low) | `price_desc` |
| Best Rating | `score` |
| Distance to Center | `distance` |

---

## Complete Example URL

**Task**: Find a 4+ star hotel in London for 2 adults with free Wi-Fi, pool, between $100 and $300, sorted by price.

**Full URL**:
```
https://uk.trip.com/hotels/list?city=2&cityName=London&checkin=2026-03-20&checkout=2026-03-25&adult=2&crn=1&star=4,5&price=100-300&facility=5,20&listSort=price
```

---

## Coverage Summary

| Category | Filters |
|----------|---------|
| Search Mode & Location | 2 |
| Guests & Rooms | 4 |
| Dates | 2 |
| Price | 1 |
| Star Rating | 1 |
| Property Type | 1 |
| Amenities & Facilities | 1 (many nested IDs) |
| Guest Rating | 1 |
| Meals & Bed Type | 2 |
| Brands & Chains | 1 |
| Payment & Policies | 2 |
| Sort Options | 1 |
| **TOTAL** | **~19 Core Parameters** |

---


