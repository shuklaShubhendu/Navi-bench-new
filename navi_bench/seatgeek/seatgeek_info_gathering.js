/**
 * SeatGeek Info Gathering - JavaScript DOM Scraper
 * 
 * Injected into SeatGeek pages via page.evaluate() to extract:
 * 1. URL parsing (page type, event ID, filters)
 * 2. LD+JSON structured data (event details, pricing, inventory)
 * 3. DOM elements (ticket listings, meta tags)
 * 
 * Returns an array of InfoDict objects for the Python verifier.
 */
(() => {
    'use strict';

    // ==================== HELPERS ====================

    /**
     * Safely get text content from a selector.
     */
    function getText(selector) {
        const el = document.querySelector(selector);
        return el ? el.textContent.trim() : '';
    }

    /**
     * Safely get attribute value from a selector.
     */
    function getAttr(selector, attr) {
        const el = document.querySelector(selector);
        return el ? el.getAttribute(attr) : '';
    }

    /**
     * Safely get meta tag content.
     */
    function getMeta(name) {
        return getAttr(`meta[name="${name}"], meta[property="${name}"]`, 'content') || '';
    }

    /**
     * Parse a price string like "$321" or "$1,500" to a float.
     */
    function parsePrice(priceStr) {
        if (!priceStr) return null;
        const cleaned = priceStr.replace(/[^0-9.]/g, '');
        const val = parseFloat(cleaned);
        return isNaN(val) ? null : val;
    }

    // ==================== URL PARSING ====================

    /**
     * Detect page type from URL.
     */
    function detectPageType(url) {
        try {
            const urlObj = new URL(url);
            const path = urlObj.pathname;

            // Event listing: /{team}-tickets/{date-venue}/{category}/{id}
            // Pattern: at least 4 path segments, last one is numeric
            const segments = path.split('/').filter(Boolean);
            if (segments.length >= 4 && /^\d+$/.test(segments[segments.length - 1]) &&
                segments[0].endsWith('-tickets')) {
                return 'event_listing';
            }

            // Search page
            if (path === '/search') return 'search';

            // Performer page: /{slug}-tickets (exactly 1 segment ending in -tickets)
            if (segments.length === 1 && segments[0].endsWith('-tickets')) {
                return 'performer';
            }

            // Category pages (known categories)
            const knownCategories = [
                'sports', 'concert', 'theater', 'comedy', 'festival',
                'nba', 'nfl', 'mlb', 'nhl', 'mls', 'ncaa',
                'boxing', 'wrestling', 'tennis', 'golf', 'soccer', 'wwe'
            ];
            if (segments.length === 1) {
                const slug = segments[0].replace('-tickets', '');
                if (knownCategories.some(c => slug.includes(c))) {
                    return 'category';
                }
            }

            // Homepage
            if (path === '/' || path === '') return 'homepage';

            // Fallback: check if it looks like a performer page
            if (segments.length === 1 && segments[0].endsWith('-tickets')) {
                return 'performer';
            }

            return 'unknown';
        } catch (e) {
            return 'unknown';
        }
    }

    /**
     * Extract URL filter parameters.
     */
    function extractUrlFilters(url) {
        try {
            const urlObj = new URL(url);
            const filters = {};

            if (urlObj.searchParams.has('quantity')) {
                filters.quantity = parseInt(urlObj.searchParams.get('quantity'));
            }
            if (urlObj.searchParams.has('max_price')) {
                filters.max_price = parseFloat(urlObj.searchParams.get('max_price'));
            }
            if (urlObj.searchParams.has('city')) {
                filters.city = urlObj.searchParams.get('city');
            }
            if (urlObj.searchParams.has('search')) {
                filters.search = urlObj.searchParams.get('search');
            }
            if (urlObj.searchParams.has('oq')) {
                filters.oq = urlObj.searchParams.get('oq');
            }

            return filters;
        } catch (e) {
            return {};
        }
    }

    /**
     * Extract event ID from URL path.
     */
    function extractEventId(url) {
        try {
            const path = new URL(url).pathname;
            const segments = path.split('/').filter(Boolean);
            const lastSegment = segments[segments.length - 1];
            if (/^\d+$/.test(lastSegment)) return lastSegment;
            return null;
        } catch (e) {
            return null;
        }
    }

    /**
     * Extract category from event URL path.
     */
    function extractCategory(url) {
        try {
            const path = new URL(url).pathname;
            const segments = path.split('/').filter(Boolean);
            // Category is the second-to-last segment in event URLs
            if (segments.length >= 4) {
                return segments[segments.length - 2];
            }
            // For category pages, extract from the slug
            if (segments.length === 1) {
                return segments[0].replace('-tickets', '');
            }
            return null;
        } catch (e) {
            return null;
        }
    }

    // ==================== LD+JSON EXTRACTION ====================

    /**
     * Extract all LD+JSON data from the page.
     */
    function extractLdJson() {
        const scripts = document.querySelectorAll('script[type="application/ld+json"]');
        const results = [];
        scripts.forEach(script => {
            try {
                const data = JSON.parse(script.textContent);
                if (Array.isArray(data)) {
                    results.push(...data);
                } else {
                    results.push(data);
                }
            } catch (e) {
                // Skip invalid JSON
            }
        });
        return results;
    }

    /**
     * Find events in LD+JSON data (handles nested structures).
     */
    function findEvents(ldJsonItems) {
        const events = [];
        for (const item of ldJsonItems) {
            if (!item) continue;
            const type = item['@type'];

            // Direct event
            if (['SportsEvent', 'MusicEvent', 'TheaterEvent', 'ComedyEvent', 'Event', 'DanceEvent'].includes(type)) {
                events.push(item);
            }

            // Events nested under SportsTeam, MusicGroup, etc.
            if (item.event) {
                const nested = Array.isArray(item.event) ? item.event : [item.event];
                events.push(...nested);
            }

            // Events in performer objects
            if (item.subEvent) {
                const nested = Array.isArray(item.subEvent) ? item.subEvent : [item.subEvent];
                events.push(...nested);
            }
        }
        return events;
    }

    /**
     * Extract info from a single LD+JSON event object.
     */
    function extractEventInfo(event) {
        const info = {};

        info.eventName = event.name || '';
        info.eventType = event['@type'] || 'Event';

        // Map @type to category
        const typeMap = {
            'SportsEvent': 'sports',
            'MusicEvent': 'concerts',
            'TheaterEvent': 'theater',
            'ComedyEvent': 'comedy',
            'DanceEvent': 'concerts',
            'Event': 'events'
        };
        info.eventCategory = typeMap[info.eventType] || 'events';

        // Date/Time
        if (event.startDate) {
            info.startDate = event.startDate;
            // Parse date part
            const datePart = event.startDate.split('T')[0];
            info.date = datePart;
            // Parse time part
            const timePart = event.startDate.split('T')[1];
            if (timePart) {
                info.time = timePart.substring(0, 5); // HH:MM
            }
        }

        // Location
        if (event.location) {
            const loc = event.location;
            info.venue = loc.name || '';

            if (loc.address) {
                const addr = loc.address;
                info.city = addr.addressLocality || '';
                info.state = addr.addressRegion || '';
                info.country = addr.addressCountry || '';
                info.postalCode = addr.postalCode || '';
                if (addr.streetAddress) {
                    info.streetAddress = addr.streetAddress;
                }
            }

            if (loc.geo) {
                info.latitude = loc.geo.latitude;
                info.longitude = loc.geo.longitude;
            }
        }

        // Competitors / Performers
        if (event.competitor) {
            const competitors = Array.isArray(event.competitor) ? event.competitor : [event.competitor];
            info.competitors = competitors.map(c => c.name || '').filter(Boolean);
        }

        if (event.performer) {
            const performers = Array.isArray(event.performer) ? event.performer : [event.performer];
            info.performers = performers.map(p => p.name || '').filter(Boolean);
        }

        // Offers / Pricing
        if (event.offers) {
            const offers = event.offers;
            info.lowPrice = offers.lowPrice != null ? parseFloat(offers.lowPrice) : null;
            info.highPrice = offers.highPrice != null ? parseFloat(offers.highPrice) : null;
            info.inventoryLevel = offers.inventoryLevel != null ? parseInt(offers.inventoryLevel) : null;
            if (offers.url) info.offerUrl = offers.url;
            if (offers.priceCurrency) info.currency = offers.priceCurrency;
        }

        return info;
    }

    // ==================== DOM LISTING EXTRACTION ====================

    /**
     * Parse a listing button's aria-label.
     * Format: "Section 110, Row 9, 1 to 3 tickets at $321 each, Deal Score 10"
     */
    function parseListingLabel(label) {
        if (!label) return null;

        const match = label.match(
            /Section\s+(.+?),\s*Row\s+(.+?),\s*(\d+)\s+to\s+(\d+)\s+tickets?\s+at\s+\$?([\d,.]+)\s+each(?:,\s*Deal Score\s+(\d+))?/i
        );

        if (!match) return null;

        return {
            section: match[1].trim(),
            row: match[2].trim(),
            minQty: parseInt(match[3]),
            maxQty: parseInt(match[4]),
            price: parseFloat(match[5].replace(/,/g, '')),
            dealScore: match[6] ? parseInt(match[6]) : null
        };
    }

    /**
     * Extract all ticket listings from the DOM.
     */
    function extractListings() {
        const listings = [];

        // Method 1: Parse aria-label on listing buttons
        const buttons = document.querySelectorAll(
            'button[aria-label*="Section"], button[aria-label*="section"]'
        );
        buttons.forEach(btn => {
            const parsed = parseListingLabel(btn.getAttribute('aria-label'));
            if (parsed) listings.push(parsed);
        });

        // Method 2: If no aria-label listings, try data-testid based
        if (listings.length === 0) {
            const testIdListings = document.querySelectorAll('[data-testid="all-listings"] button');
            testIdListings.forEach(btn => {
                const label = btn.getAttribute('aria-label');
                if (label) {
                    const parsed = parseListingLabel(label);
                    if (parsed) listings.push(parsed);
                }
            });
        }

        return listings;
    }

    /**
     * Count total listings visible on page.
     */
    function countListings() {
        const container = document.querySelector('[data-testid="all-listings"]');
        if (container) {
            return container.querySelectorAll('button[aria-label]').length;
        }
        return document.querySelectorAll('button[aria-label*="Section"]').length;
    }

    // ==================== MAIN SCRAPER ====================

    /**
     * Main entry point - scrape the current page and return InfoDict array.
     */
    function scrape() {
        const url = window.location.href;
        const pageType = detectPageType(url);
        const urlFilters = extractUrlFilters(url);
        const eventId = extractEventId(url);
        const category = extractCategory(url);
        const ldJsonItems = extractLdJson();
        const events = findEvents(ldJsonItems);

        const infos = [];

        // ===== Common fields =====
        const commonFields = {
            url: url,
            pageType: pageType,
            title: document.title || '',
            h1: getText('h1'),
            metaDescription: getMeta('description'),
            ogTitle: getMeta('og:title'),
            ogUrl: getMeta('og:url'),
            eventId: eventId,
            category: category,
            urlQuantity: urlFilters.quantity || null,
            urlMaxPrice: urlFilters.max_price || null,
            urlCity: urlFilters.city || null,
            urlSearch: urlFilters.search || null,
            source: 'seatgeek'
        };

        // ===== Event listing page =====
        if (pageType === 'event_listing') {
            const listings = extractListings();
            const totalListings = countListings();

            // Get primary event from LD+JSON
            if (events.length > 0) {
                const eventInfo = extractEventInfo(events[0]);
                const info = {
                    ...commonFields,
                    ...eventInfo,
                    totalListings: totalListings,
                    source: 'ld+json'
                };

                // Add listing details if available
                if (listings.length > 0) {
                    // Get price range from listings
                    const prices = listings.map(l => l.price).filter(p => p != null);
                    if (prices.length > 0) {
                        info.listingLowPrice = Math.min(...prices);
                        info.listingHighPrice = Math.max(...prices);
                    }

                    // Get sections available
                    info.availableSections = [...new Set(listings.map(l => l.section))];

                    // First listing details
                    info.section = listings[0].section;
                    info.row = listings[0].row;
                    info.price = listings[0].price;
                    info.dealScore = listings[0].dealScore;
                    info.ticketCount = listings[0].maxQty;
                }

                // Availability check
                if (totalListings > 0 || (eventInfo.inventoryLevel && eventInfo.inventoryLevel > 0)) {
                    info.availabilityStatus = 'available';
                    info.info = 'available';
                } else {
                    info.availabilityStatus = 'sold_out';
                    info.info = 'sold_out';
                }

                infos.push(info);
            } else {
                // No LD+JSON events — build from DOM + URL
                infos.push({
                    ...commonFields,
                    eventName: getText('h1') || commonFields.ogTitle || commonFields.title,
                    totalListings: countListings(),
                    availabilityStatus: countListings() > 0 ? 'available' : 'sold_out',
                    info: countListings() > 0 ? 'available' : 'sold_out',
                    source: 'dom'
                });
            }

            // Add individual listing infos (for section/row matching)
            const listings2 = extractListings();
            listings2.forEach(listing => {
                infos.push({
                    ...commonFields,
                    eventName: infos[0]?.eventName || getText('h1'),
                    eventCategory: infos[0]?.eventCategory || category,
                    city: infos[0]?.city || '',
                    venue: infos[0]?.venue || '',
                    section: listing.section,
                    row: listing.row,
                    price: listing.price,
                    dealScore: listing.dealScore,
                    ticketCount: listing.maxQty,
                    availableQuantities: Array.from(
                        { length: listing.maxQty - listing.minQty + 1 },
                        (_, i) => listing.minQty + i
                    ),
                    availabilityStatus: 'available',
                    info: 'available',
                    source: 'dom_listing'
                });
            });
        }

        // ===== Performer page =====
        else if (pageType === 'performer') {
            // Extract all events from LD+JSON
            if (events.length > 0) {
                events.forEach(event => {
                    const eventInfo = extractEventInfo(event);
                    infos.push({
                        ...commonFields,
                        ...eventInfo,
                        pageType: 'performer',
                        source: 'ld+json'
                    });
                });
            }

            // Also push a summary info with performer data
            const teamData = ldJsonItems.find(item =>
                item && (item['@type'] === 'SportsTeam' || item['@type'] === 'MusicGroup' ||
                    item['@type'] === 'PerformingGroup' || item['@type'] === 'Person')
            );
            if (teamData) {
                infos.push({
                    ...commonFields,
                    eventName: teamData.name || '',
                    eventCategory: teamData['@type'] === 'SportsTeam' ? 'sports' : 'concerts',
                    totalListings: events.length,
                    source: 'ld+json_performer'
                });
            }
        }

        // ===== Search results page =====
        else if (pageType === 'search') {
            // Extract search result links
            const resultLinks = document.querySelectorAll('a[href*="-tickets"]');
            resultLinks.forEach(link => {
                const href = link.getAttribute('href');
                const text = link.textContent.trim().substring(0, 200);
                if (text && href) {
                    infos.push({
                        ...commonFields,
                        eventName: text,
                        pageType: 'search',
                        offerUrl: href,
                        source: 'dom_search'
                    });
                }
            });

            // Also add LD+JSON events if present
            events.forEach(event => {
                infos.push({
                    ...commonFields,
                    ...extractEventInfo(event),
                    pageType: 'search',
                    source: 'ld+json'
                });
            });
        }

        // ===== Category page =====
        else if (pageType === 'category') {
            // Extract events from LD+JSON
            events.forEach(event => {
                infos.push({
                    ...commonFields,
                    ...extractEventInfo(event),
                    pageType: 'category',
                    source: 'ld+json'
                });
            });

            // Fallback: extract from DOM
            if (infos.length === 0) {
                const eventLinks = document.querySelectorAll('a[href*="-tickets/"]');
                eventLinks.forEach(link => {
                    const text = link.textContent.trim().substring(0, 200);
                    if (text) {
                        infos.push({
                            ...commonFields,
                            eventName: text,
                            pageType: 'category',
                            source: 'dom_category'
                        });
                    }
                });
            }
        }

        // ===== Fallback: Unknown page =====
        else {
            infos.push({
                ...commonFields,
                eventName: getText('h1') || commonFields.title,
                source: 'dom_fallback'
            });
        }

        // Ensure we always return at least one info
        if (infos.length === 0) {
            infos.push({
                ...commonFields,
                eventName: commonFields.title || 'Unknown',
                source: 'empty_fallback'
            });
        }

        return infos;
    }

    // Execute and return
    return scrape();
})();
