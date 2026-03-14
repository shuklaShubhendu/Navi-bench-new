"""Pytest unit tests for Realtor.com URL Match verifier.

Tests the RealtorUrlMatch class for property search navigation verification.
"""

import pytest

from navi_bench.realtor.realtor_url_match import (
    RealtorUrlMatch,
    generate_task_config,
)


# =============================================================================
# URL Parsing Tests
# =============================================================================


class TestRealtorUrlParsing:
    """Test URL parsing via _parse_realtor_url."""

    def _parse(self, url):
        v = RealtorUrlMatch(gt_urls=[["https://www.realtor.com/realestateandhomes-search/X_Y"]])
        return v._parse_realtor_url(url)

    def test_basic_for_sale_url(self):
        result = self._parse("https://www.realtor.com/realestateandhomes-search/San-Francisco_CA")
        assert result["search_type"] == "sale"
        assert "san-francisco_ca" in result["location"].lower()

    def test_rental_apartments_url(self):
        result = self._parse("https://www.realtor.com/apartments/Austin_TX/type-apartments/beds-2")
        assert result["search_type"] == "rent"
        assert "austin_tx" in result["location"].lower()
        assert result["filters"].get("beds") is not None

    def test_sold_homes_url(self):
        result = self._parse(
            "https://www.realtor.com/realestateandhomes-search/Miami_FL/show-recently-sold"
        )
        # show-recently-sold is parsed as a filter on a 'sale' search type
        assert result["search_type"] == "sale"

    def test_open_houses_url(self):
        result = self._parse(
            "https://www.realtor.com/realestateandhomes-search/Denver_CO/show-open-house"
        )
        # show-open-house is parsed as a filter on a 'sale' search type
        assert result["search_type"] == "sale"

    def test_zip_code_location(self):
        result = self._parse("https://www.realtor.com/realestateandhomes-search/90210")
        assert "90210" in result["location"]

    def test_url_case_insensitivity(self):
        result1 = self._parse("https://www.realtor.com/realestateandhomes-search/San-Francisco_CA")
        result2 = self._parse("https://WWW.REALTOR.COM/realestateandhomes-search/San-Francisco_CA")
        assert result1["location"] == result2["location"]

    def test_multi_word_city_parsing(self):
        result = self._parse("https://www.realtor.com/realestateandhomes-search/New-York_NY")
        assert "new-york_ny" in result["location"].lower()

    def test_apartments_for_rent_path(self):
        result = self._parse("https://www.realtor.com/apartments-for-rent/Houston_TX")
        assert result["search_type"] == "rent"

    def test_houses_for_rent_path(self):
        result = self._parse("https://www.realtor.com/houses-for-rent/Portland_OR")
        assert result["search_type"] == "rent"


# =============================================================================
# Filter Segment Detection Tests
# =============================================================================


class TestFilterSegmentDetection:
    """Test _is_filter_segment for recognizing filter vs location segments."""

    def _is_filter(self, seg):
        v = RealtorUrlMatch(gt_urls=[["https://www.realtor.com/realestateandhomes-search/X_Y"]])
        return v._is_filter_segment(seg)

    def test_beds_is_filter(self):
        assert self._is_filter("beds-3") is True

    def test_baths_is_filter(self):
        assert self._is_filter("baths-2") is True

    def test_price_is_filter(self):
        assert self._is_filter("price-500000-1000000") is True

    def test_type_is_filter(self):
        assert self._is_filter("type-condo") is True

    def test_show_flag_is_filter(self):
        assert self._is_filter("show-recently-sold") is True

    def test_shw_abbreviation_is_filter(self):
        assert self._is_filter("shw-nc") is True

    def test_shw_rs_abbreviation_is_filter(self):
        assert self._is_filter("shw-rs") is True

    def test_soldwithin_is_filter(self):
        assert self._is_filter("soldwithin-1") is True

    def test_hoa_is_filter(self):
        assert self._is_filter("hoa-500,known") is True

    def test_dom_is_filter(self):
        assert self._is_filter("dom-7") is True

    def test_sqft_is_filter(self):
        assert self._is_filter("sqft-2000-3000") is True

    def test_lot_sqft_is_filter(self):
        assert self._is_filter("lot-sqft-5000-7500") is True

    def test_age_is_filter(self):
        assert self._is_filter("age-10") is True

    def test_radius_is_filter(self):
        assert self._is_filter("radius-25") is True


    def test_with_prefix_is_filter(self):
        assert self._is_filter("with_inunitlaundry") is True

    def test_dog_friendly_is_filter(self):
        assert self._is_filter("dog-friendly") is True

    def test_cat_friendly_is_filter(self):
        assert self._is_filter("cat-friendly") is True

    def test_location_is_not_filter(self):
        assert self._is_filter("San-Francisco_CA") is False

    def test_zip_code_is_not_filter(self):
        assert self._is_filter("90210") is False

    def test_realestateandhomes_search_not_filter(self):
        assert self._is_filter("realestateandhomes-search") is False


# =============================================================================
# Filter Parsing Tests
# =============================================================================


class TestFilterParsing:
    """Test _parse_filter_segment for various filter formats."""

    def _parse_filter(self, seg):
        v = RealtorUrlMatch(gt_urls=[["https://www.realtor.com/realestateandhomes-search/X_Y"]])
        return v._parse_filter_segment(seg)

    def test_beds_basic(self):
        key, val = self._parse_filter("beds-3")
        assert key == "beds"
        assert val == "3"

    def test_beds_range(self):
        key, val = self._parse_filter("beds-3-4")
        assert key == "beds"
        assert val == "3-4"

    def test_baths_basic(self):
        key, val = self._parse_filter("baths-2")
        assert key == "baths"
        assert val == "2"

    def test_price_range(self):
        key, val = self._parse_filter("price-500000-1000000")
        assert key == "price"
        assert "500000" in val
        assert "1000000" in val

    def test_price_open_max(self):
        key, val = self._parse_filter("price-na-800000")
        assert key == "price"
        assert "800000" in val

    def test_price_open_min(self):
        key, val = self._parse_filter("price-500000-na")
        assert key == "price"
        assert "500000" in val

    def test_type_condo(self):
        key, val = self._parse_filter("type-condo")
        assert key == "type"
        assert "condo" in val

    def test_type_single_family_home(self):
        key, val = self._parse_filter("type-single-family-home")
        assert key == "type"
        assert "single-family-home" in val

    def test_type_multi_family_home(self):
        key, val = self._parse_filter("type-multi-family-home")
        assert key == "type"
        assert "multi-family-home" in val

    def test_type_townhome(self):
        key, val = self._parse_filter("type-townhome")
        assert key == "type"

    def test_sqft_range(self):
        key, val = self._parse_filter("sqft-2000-3000")
        assert key == "sqft"

    def test_lot_sqft_range(self):
        key, val = self._parse_filter("lot-sqft-5000-7500")
        assert key == "lot"

    def test_dom_days_on_market(self):
        key, val = self._parse_filter("dom-7")
        assert key == "days-on-market"
        assert val == "7"

    def test_dom_14(self):
        key, val = self._parse_filter("dom-14")
        assert key == "days-on-market"
        assert val == "14"

    def test_radius(self):
        key, val = self._parse_filter("radius-25")
        assert key == "radius"
        assert val == "25"

    def test_sby_ignored(self):
        """Sort-by segments should be ignored."""
        key, val = self._parse_filter("sby-2")
        assert key == ""

    def test_pg_ignored(self):
        """Pagination segments should be ignored."""
        key, val = self._parse_filter("pg-3")
        assert key == ""


# =============================================================================
# Show Flag & Abbreviation Tests (Browser-Verified)
# =============================================================================


class TestShowFlagAbbreviations:
    """Test show flag and shw- abbreviation parsing.

    Browser-verified (Feb 2026): shw-nc is the REAL pattern on Realtor.com.
    show-new-construction redirects to unfiltered page.
    """

    def _parse_filter(self, seg):
        v = RealtorUrlMatch(gt_urls=[["https://www.realtor.com/realestateandhomes-search/X_Y"]])
        return v._parse_filter_segment(seg)

    def test_shw_nc_to_show_new_construction(self):
        key, val = self._parse_filter("shw-nc")
        assert key == "show-new-construction"
        assert val == "true"

    def test_show_new_construction_long_form(self):
        key, val = self._parse_filter("show-new-construction")
        assert key == "show-new-construction"
        assert val == "true"

    def test_show_recently_sold(self):
        key, val = self._parse_filter("show-recently-sold")
        assert key == "show-recently-sold"
        assert val == "true"

    def test_show_open_house(self):
        key, val = self._parse_filter("show-open-house")
        assert key == "show-open-house"
        assert val == "true"

    def test_show_foreclosure(self):
        key, val = self._parse_filter("show-foreclosure")
        assert key == "show-foreclosure"
        assert val == "true"

    def test_show_price_reduced(self):
        key, val = self._parse_filter("show-price-reduced")
        assert key == "show-price-reduced"
        assert val == "true"

    def test_show_55_plus(self):
        key, val = self._parse_filter("show-55-plus")
        assert key == "show-55-plus"
        assert val == "true"


# =============================================================================
# HOA Filter Tests (Browser-Verified)
# =============================================================================


class TestHoaFilterParsing:
    """Test HOA filter parsing.

    Browser-verified: hoa-500,known is the REAL pattern on Realtor.com,
    displaying 'HOA fees max $500/month' chip.
    """

    def _parse_filter(self, seg):
        v = RealtorUrlMatch(gt_urls=[["https://www.realtor.com/realestateandhomes-search/X_Y"]])
        return v._parse_filter_segment(seg)

    def test_hoa_known_format(self):
        key, val = self._parse_filter("hoa-500,known")
        assert key == "hoa"
        assert "500" in val

    def test_hoa_range_format(self):
        key, val = self._parse_filter("hoa-na-500")
        assert key == "hoa"
        assert "500" in val


# =============================================================================
# Sold Within Tests (Browser-Verified)
# =============================================================================


class TestSoldWithinParsing:
    """Test soldwithin-N month-based segment parsing.

    Browser-verified: soldwithin-1 displays 'Sold within 1 month' chip.
    """

    def _parse_filter(self, seg):
        v = RealtorUrlMatch(gt_urls=[["https://www.realtor.com/realestateandhomes-search/X_Y"]])
        return v._parse_filter_segment(seg)

    def test_soldwithin_1_month(self):
        key, val = self._parse_filter("soldwithin-1")
        assert key == "sold-within"
        assert val == "30"

    def test_soldwithin_3_months(self):
        key, val = self._parse_filter("soldwithin-3")
        assert key == "sold-within"
        assert val == "90"

    def test_soldwithin_6_months(self):
        key, val = self._parse_filter("soldwithin-6")
        assert key == "sold-within"
        assert val == "180"

    def test_soldwithin_12_months(self):
        key, val = self._parse_filter("soldwithin-12")
        assert key == "sold-within"
        assert val == "365"


# =============================================================================
# Comma-Separated Type Tests (Browser-Verified)
# =============================================================================


class TestCommaSeparatedTypes:
    """Test comma-separated type parsing like type-townhome,condo.

    Browser-verified: type-townhome,condo displays both Townhome and Condo chips.
    """

    def _parse_filter(self, seg):
        v = RealtorUrlMatch(gt_urls=[["https://www.realtor.com/realestateandhomes-search/X_Y"]])
        return v._parse_filter_segment(seg)

    def test_comma_separated_types(self):
        key, val = self._parse_filter("type-townhome,condo")
        assert key == "type"
        assert "townhome" in val
        assert "condo" in val

    def test_comma_separated_house_condo(self):
        key, val = self._parse_filter("type-single-family-home,condo")
        assert key == "type"
        assert "condo" in val


# =============================================================================
# Age Filter Tests (Browser-Verified)
# =============================================================================


class TestAgeFilterParsing:
    """Test age filter parsing.

    Browser-verified: age-10 displays 'Up to 10 years' chip.
    """

    def _parse_filter(self, seg):
        v = RealtorUrlMatch(gt_urls=[["https://www.realtor.com/realestateandhomes-search/X_Y"]])
        return v._parse_filter_segment(seg)

    def test_age_single_value(self):
        key, val = self._parse_filter("age-10")
        assert key == "age"

    def test_age_range(self):
        key, val = self._parse_filter("age-0-10")
        assert key == "age"


# =============================================================================
# URL Matching Tests
# =============================================================================


class TestUrlMatching:
    """Test _urls_match for matching two URLs."""

    def _match(self, agent_url, gt_url):
        v = RealtorUrlMatch(gt_urls=[[gt_url]])
        return v._urls_match(agent_url, gt_url)

    def test_exact_match(self):
        url = "https://www.realtor.com/realestateandhomes-search/San-Francisco_CA/beds-3/price-na-1000000"
        match, details = self._match(url, url)
        assert match is True

    def test_filter_order_independence(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Seattle_WA/beds-3/price-500000-1000000"
        agent = "https://www.realtor.com/realestateandhomes-search/Seattle_WA/price-500000-1000000/beds-3"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_case_insensitivity(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3"
        agent = "HTTPS://WWW.REALTOR.COM/realestateandhomes-search/Austin_TX/beds-3"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_location_mismatch_different_city(self):
        gt = "https://www.realtor.com/realestateandhomes-search/San-Francisco_CA/beds-3"
        agent = "https://www.realtor.com/realestateandhomes-search/Los-Angeles_CA/beds-3"
        match, _ = self._match(agent, gt)
        assert match is False

    def test_location_mismatch_different_state(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Portland_OR/beds-3"
        agent = "https://www.realtor.com/realestateandhomes-search/Portland_ME/beds-3"
        match, _ = self._match(agent, gt)
        assert match is False

    def test_filter_value_mismatch(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3"
        agent = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-4"
        match, _ = self._match(agent, gt)
        assert match is False

    def test_missing_filter_fails(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3/baths-2"
        agent = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3"
        match, _ = self._match(agent, gt)
        assert match is False

    def test_extra_filter_still_matches(self):
        """Extra filters from agent don't cause mismatch (verifier is lenient)."""
        gt = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3"
        agent = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3/baths-2"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_search_type_mismatch_sale_vs_rent(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3"
        agent = "https://www.realtor.com/apartments/Austin_TX/beds-3"
        match, _ = self._match(agent, gt)
        assert match is False

    def test_no_filters_exact_location_match(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Denver_CO"
        match, _ = self._match(gt, gt)
        assert match is True


# =============================================================================
# Search Type Equivalence Tests
# =============================================================================


class TestSearchTypeEquivalence:
    """Test equivalence matching between different search type representations."""

    def _match(self, agent_url, gt_url):
        v = RealtorUrlMatch(gt_urls=[[gt_url]])
        return v._urls_match(agent_url, gt_url)

    def test_soldwithin_implies_sold_with_matching_days(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Miami_FL/type-condo/beds-2/price-300000-700000/soldwithin-1"
        agent = "https://www.realtor.com/realestateandhomes-search/Miami_FL/show-recently-sold/type-condo/beds-2/price-300000-700000/sold-within-30"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_shw_nc_matches_show_new_construction(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Phoenix_AZ/shw-nc"
        agent = "https://www.realtor.com/realestateandhomes-search/Phoenix_AZ/show-new-construction"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_shw_nc_reverse_direction(self):
        """Agent uses shw-nc, GT uses show-new-construction."""
        gt = "https://www.realtor.com/realestateandhomes-search/Phoenix_AZ/show-new-construction"
        agent = "https://www.realtor.com/realestateandhomes-search/Phoenix_AZ/shw-nc"
        match, _ = self._match(agent, gt)
        assert match is True


# =============================================================================
# Rental Type-Apartments Stripping Tests
# =============================================================================


class TestRentalTypeApartmentsStripping:
    """Test that redundant type-apartments is stripped in rental URL comparison."""

    def _match(self, agent_url, gt_url):
        v = RealtorUrlMatch(gt_urls=[[gt_url]])
        return v._urls_match(agent_url, gt_url)

    def test_gt_has_type_apartments_agent_doesnt(self):
        gt = "https://www.realtor.com/apartments/Austin_TX/type-apartments/beds-2/price-na-2000"
        agent = "https://www.realtor.com/apartments/Austin_TX/beds-2/price-na-2000"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_agent_has_type_apartments_gt_doesnt(self):
        gt = "https://www.realtor.com/apartments/Austin_TX/beds-2/price-na-2000"
        agent = "https://www.realtor.com/apartments/Austin_TX/type-apartments/beds-2/price-na-2000"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_both_have_type_apartments(self):
        gt = "https://www.realtor.com/apartments/Austin_TX/type-apartments/beds-2"
        agent = "https://www.realtor.com/apartments/Austin_TX/type-apartments/beds-2"
        match, _ = self._match(agent, gt)
        assert match is True


# =============================================================================
# Age Normalization Tests
# =============================================================================


class TestAgeNormalization:
    """Test single-value age normalization (age-10 ↔ age-0-10)."""

    def _match(self, agent_url, gt_url):
        v = RealtorUrlMatch(gt_urls=[[gt_url]])
        return v._urls_match(agent_url, gt_url)

    def test_age_single_matches_range(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Denver_CO/age-10"
        agent = "https://www.realtor.com/realestateandhomes-search/Denver_CO/age-0-10"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_age_range_matches_single(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Denver_CO/age-0-10"
        agent = "https://www.realtor.com/realestateandhomes-search/Denver_CO/age-10"
        match, _ = self._match(agent, gt)
        assert match is True


# =============================================================================
# Price Normalization Tests
# =============================================================================


class TestPriceNormalization:
    """Test price value normalization and matching."""

    def _match(self, agent_url, gt_url):
        v = RealtorUrlMatch(gt_urls=[[gt_url]])
        return v._urls_match(agent_url, gt_url)

    def test_same_price_range_matches(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Austin_TX/price-500000-1000000"
        agent = "https://www.realtor.com/realestateandhomes-search/Austin_TX/price-500000-1000000"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_different_price_range_fails(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Austin_TX/price-500000-1000000"
        agent = "https://www.realtor.com/realestateandhomes-search/Austin_TX/price-400000-900000"
        match, _ = self._match(agent, gt)
        assert match is False

    def test_na_max_price_matches(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Austin_TX/price-na-800000"
        match, _ = self._match(gt, gt)
        assert match is True

    def test_na_min_price_matches(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Austin_TX/price-500000-na"
        match, _ = self._match(gt, gt)
        assert match is True


# =============================================================================
# RealtorUrlMatch Async Tests
# =============================================================================


class TestRealtorUrlMatchBasic:
    """Test basic RealtorUrlMatch async functionality."""

    @pytest.mark.asyncio
    async def test_exact_match_scores_1(self):
        gt_url = "https://www.realtor.com/realestateandhomes-search/San-Francisco_CA/beds-3"
        metric = RealtorUrlMatch(gt_urls=[[gt_url]])
        await metric.reset()
        await metric.update(url=gt_url)
        result = await metric.compute()
        assert result.score == 1.0

    @pytest.mark.asyncio
    async def test_no_match_scores_0(self):
        gt_url = "https://www.realtor.com/realestateandhomes-search/San-Francisco_CA/beds-3"
        metric = RealtorUrlMatch(gt_urls=[[gt_url]])
        await metric.reset()
        await metric.update(url="https://www.realtor.com/realestateandhomes-search/San-Francisco_CA/beds-5")
        result = await metric.compute()
        assert result.score == 0.0

    @pytest.mark.asyncio
    async def test_empty_url_scores_0(self):
        gt_url = "https://www.realtor.com/realestateandhomes-search/San-Francisco_CA/beds-3"
        metric = RealtorUrlMatch(gt_urls=[[gt_url]])
        await metric.reset()
        await metric.update(url="")
        result = await metric.compute()
        assert result.score == 0.0

    @pytest.mark.asyncio
    async def test_non_realtor_url_ignored(self):
        gt_url = "https://www.realtor.com/realestateandhomes-search/San-Francisco_CA/beds-3"
        metric = RealtorUrlMatch(gt_urls=[[gt_url]])
        await metric.reset()
        await metric.update(url="https://www.google.com/search?q=homes")
        result = await metric.compute()
        assert result.score == 0.0

    @pytest.mark.asyncio
    async def test_reset_clears_match(self):
        gt_url = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3"
        metric = RealtorUrlMatch(gt_urls=[[gt_url]])
        await metric.update(url=gt_url)
        result1 = await metric.compute()
        assert result1.score == 1.0

        await metric.reset()
        result2 = await metric.compute()
        assert result2.score == 0.0

    @pytest.mark.asyncio
    async def test_first_match_sticks(self):
        """Once matched, subsequent URLs don't overwrite."""
        gt_url = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3"
        metric = RealtorUrlMatch(gt_urls=[[gt_url]])
        await metric.reset()
        await metric.update(url=gt_url)  # Match
        await metric.update(url="https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-5")
        result = await metric.compute()
        assert result.score == 1.0

    @pytest.mark.asyncio
    async def test_multiple_updates_before_match(self):
        """Multiple non-matching updates followed by eventual match."""
        gt_url = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3"
        metric = RealtorUrlMatch(gt_urls=[[gt_url]])
        await metric.reset()
        await metric.update(url="https://www.realtor.com")
        await metric.update(url="https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-5")
        await metric.update(url=gt_url)
        result = await metric.compute()
        assert result.score == 1.0


class TestRealtorUrlMatchMultipleGT:
    """Test RealtorUrlMatch with multiple ground truth URLs (AND→OR semantics)."""

    @pytest.mark.asyncio
    async def test_match_any_or_url(self):
        """Match any URL within an OR group."""
        gt_urls = [
            [
                "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3",
                "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-4",
            ]
        ]
        metric = RealtorUrlMatch(gt_urls=gt_urls)
        await metric.reset()
        await metric.update(url="https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-4")
        result = await metric.compute()
        assert result.score == 1.0

    @pytest.mark.asyncio
    async def test_no_match_any_or_url(self):
        """No match when none of the OR URLs match."""
        gt_urls = [
            [
                "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3",
                "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-4",
            ]
        ]
        metric = RealtorUrlMatch(gt_urls=gt_urls)
        await metric.reset()
        await metric.update(url="https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-5")
        result = await metric.compute()
        assert result.score == 0.0

    @pytest.mark.asyncio
    async def test_match_first_or_alternative(self):
        """Match the first URL in an OR group."""
        gt_urls = [
            [
                "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3",
                "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-4",
            ]
        ]
        metric = RealtorUrlMatch(gt_urls=gt_urls)
        await metric.reset()
        await metric.update(url="https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3")
        result = await metric.compute()
        assert result.score == 1.0


# =============================================================================
# Real-World Scenario Tests (Browser-Verified, Hard Cases)
# =============================================================================


class TestRealWorldScenarios:
    """Test real-world scenarios from the benchmark.

    All GT URLs have been browser-verified on live Realtor.com (Feb 2026).
    These are the hardest cases combining multiple features.
    """

    def _match(self, agent_url, gt_url):
        v = RealtorUrlMatch(gt_urls=[[gt_url]])
        return v._urls_match(agent_url, gt_url)

    def test_new_construction_condo_with_hoa_and_price(self):
        """shw-nc + type-condo + beds + baths + price + hoa-500,known"""
        gt = "https://www.realtor.com/realestateandhomes-search/Miami_FL/type-condo/beds-2/baths-2/shw-nc/price-na-800000/hoa-500,known"
        agent = "https://www.realtor.com/realestateandhomes-search/Miami_FL/show-new-construction/type-condo/beds-2/baths-2/price-na-800000/hoa-na-500"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_dog_friendly_rental_with_laundry(self):
        """Rental + dog-friendly + in-unit laundry + beds + baths + price"""
        gt = "https://www.realtor.com/apartments/San-Francisco_CA/type-apartments/dog-friendly/with_inunitlaundry/beds-2/baths-1/price-na-4000"
        agent = "https://www.realtor.com/apartments/San-Francisco_CA/dog-friendly/with_inunitlaundry/beds-2/baths-1/price-na-4000"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_sold_condo_within_1_month(self):
        """soldwithin-1 + type-condo + beds + price range"""
        gt = "https://www.realtor.com/realestateandhomes-search/Miami_FL/type-condo/beds-2/price-300000-700000/soldwithin-1"
        agent = "https://www.realtor.com/realestateandhomes-search/Miami_FL/show-recently-sold/type-condo/beds-2/price-300000-700000/sold-within-30"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_sold_sfh_within_3_months(self):
        """soldwithin-3 + type-single-family-home + beds + baths + price"""
        gt = "https://www.realtor.com/realestateandhomes-search/Chicago_IL/type-single-family-home/beds-3/baths-2/price-200000-500000/soldwithin-3"
        agent = "https://www.realtor.com/realestateandhomes-search/Chicago_IL/show-recently-sold/type-single-family-home/beds-3/baths-2/price-200000-500000/sold-within-90"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_new_construction_sfh_with_filters(self):
        """shw-nc only with type"""
        gt = "https://www.realtor.com/realestateandhomes-search/Phoenix_AZ/type-single-family-home/shw-nc"
        agent = "https://www.realtor.com/realestateandhomes-search/Phoenix_AZ/show-new-construction/type-single-family-home"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_condo_dom_hoa_combined(self):
        """Condo + days-on-market + HOA + beds + baths + price"""
        gt = "https://www.realtor.com/realestateandhomes-search/San-Francisco_CA/type-condo/beds-2/baths-1/dom-14/price-na-1200000/hoa-500,known"
        agent = "https://www.realtor.com/realestateandhomes-search/San-Francisco_CA/type-condo/beds-2/baths-1/dom-14/price-na-1200000/hoa-na-500"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_townhome_condo_comma_type(self):
        """Comma-separated types: type-townhome,condo"""
        gt = "https://www.realtor.com/realestateandhomes-search/San-Francisco_CA/type-townhome,condo"
        agent = "https://www.realtor.com/realestateandhomes-search/San-Francisco_CA/type-condo/type-townhome"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_age_single_with_all_filters(self):
        """age-5 + type + beds + baths + price"""
        gt = "https://www.realtor.com/realestateandhomes-search/Denver_CO/type-single-family-home/beds-4/baths-3/age-5/price-500000-900000"
        agent = "https://www.realtor.com/realestateandhomes-search/Denver_CO/type-single-family-home/beds-4/baths-3/age-0-5/price-500000-900000"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_zip_code_rental(self):
        """Rental search by zip code"""
        gt = "https://www.realtor.com/apartments/60601/type-apartments/beds-2/baths-1/price-na-3000"
        agent = "https://www.realtor.com/apartments/60601/beds-2/baths-1/price-na-3000"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_lot_sqft_range(self):
        """Lot size filter (lot-sqft-5000-7500)"""
        gt = "https://www.realtor.com/realestateandhomes-search/Austin_TX/lot-sqft-5000-7500"
        match, _ = self._match(gt, gt)
        assert match is True

    def test_complex_sold_with_pool_and_sqft(self):
        """Sold + type + beds + sqft + pool + price"""
        gt = "https://www.realtor.com/realestateandhomes-search/Scottsdale_AZ/type-single-family-home/beds-4/sqft-2500-na/show-recently-sold/with_pool/price-700000-1500000"
        match, _ = self._match(gt, gt)
        assert match is True

    def test_foreclosure_with_beds_and_price(self):
        """Foreclosure flag + beds + price"""
        gt = "https://www.realtor.com/realestateandhomes-search/Las-Vegas_NV/beds-3/price-200000-400000/show-foreclosure"
        match, _ = self._match(gt, gt)
        assert match is True

    def test_open_house_with_price_reduced(self):
        """Open house + price reduced flags"""
        gt = "https://www.realtor.com/realestateandhomes-search/Portland_OR/show-open-house/show-price-reduced"
        match, _ = self._match(gt, gt)
        assert match is True

    def test_55_plus_community(self):
        """55+ community filter"""
        gt = "https://www.realtor.com/realestateandhomes-search/Tucson_AZ/show-55-plus/type-single-family-home"
        match, _ = self._match(gt, gt)
        assert match is True

    def test_cat_and_dog_friendly_rental(self):
        """Both cat and dog friendly filters"""
        gt = "https://www.realtor.com/apartments/Boston_MA/dog-friendly/cat-friendly/beds-1"
        match, _ = self._match(gt, gt)
        assert match is True


# =============================================================================
# Negative Matching Tests (Should NOT match)
# =============================================================================


class TestNegativeMatching:
    """Test cases that should explicitly NOT match."""

    def _match(self, agent_url, gt_url):
        v = RealtorUrlMatch(gt_urls=[[gt_url]])
        return v._urls_match(agent_url, gt_url)

    def test_different_property_type_fails(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Austin_TX/type-condo"
        agent = "https://www.realtor.com/realestateandhomes-search/Austin_TX/type-single-family-home"
        match, _ = self._match(agent, gt)
        assert match is False

    def test_different_bed_count_fails(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3"
        agent = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-2"
        match, _ = self._match(agent, gt)
        assert match is False

    def test_different_bath_count_fails(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Austin_TX/baths-2"
        agent = "https://www.realtor.com/realestateandhomes-search/Austin_TX/baths-3"
        match, _ = self._match(agent, gt)
        assert match is False

    def test_sale_vs_rental_fails(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Austin_TX"
        agent = "https://www.realtor.com/apartments/Austin_TX"
        match, _ = self._match(agent, gt)
        assert match is False

    def test_completely_different_url_fails(self):
        gt = "https://www.realtor.com/realestateandhomes-search/San-Francisco_CA/beds-3/price-na-1000000"
        agent = "https://www.realtor.com/realestateandhomes-search/Chicago_IL/type-condo/baths-2/price-200000-500000"
        match, _ = self._match(agent, gt)
        assert match is False

    def test_wrong_price_range_fails(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Austin_TX/price-500000-1000000"
        agent = "https://www.realtor.com/realestateandhomes-search/Austin_TX/price-300000-800000"
        match, _ = self._match(agent, gt)
        assert match is False


# =============================================================================
# generate_task_config Tests
# =============================================================================


class TestGenerateTaskConfig:
    """Test task configuration generation."""

    def test_generates_valid_config(self):
        config = generate_task_config(
            task="Find homes for sale in San Francisco, CA with 3+ bedrooms",
            gt_urls=[["https://www.realtor.com/realestateandhomes-search/San-Francisco_CA/beds-3"]],
            location="San Francisco, CA, United States",
            timezone="America/Los_Angeles",
        )
        assert config.task == "Find homes for sale in San Francisco, CA with 3+ bedrooms"
        assert config.url == "https://www.realtor.com"
        assert "gt_urls" in config.eval_config

    def test_gt_urls_format_in_eval_config(self):
        config = generate_task_config(
            task="Test task",
            gt_urls=[["https://www.realtor.com/realestateandhomes-search/Austin_TX"]],
            location="Austin, TX, United States",
            timezone="America/Chicago",
        )
        assert config.eval_config["gt_urls"] == [
            ["https://www.realtor.com/realestateandhomes-search/Austin_TX"]
        ]

    def test_accepts_custom_url(self):
        config = generate_task_config(
            task="Test task",
            gt_urls=[["https://www.realtor.com/realestateandhomes-search/Austin_TX"]],
            location="Austin, TX, United States",
            timezone="America/Chicago",
            url="https://www.realtor.com/realestateandhomes-search/Austin_TX",
        )
        assert config.url == "https://www.realtor.com/realestateandhomes-search/Austin_TX"

    def test_accepts_single_gt_url_string(self):
        config = generate_task_config(
            task="Test task",
            gt_urls=[["https://www.realtor.com/realestateandhomes-search/Austin_TX"]],
            location="Austin, TX, United States",
            timezone="America/Los_Angeles",
        )
        assert config.eval_config["gt_urls"] == [
            ["https://www.realtor.com/realestateandhomes-search/Austin_TX"]
        ]


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def _match(self, agent_url, gt_url):
        v = RealtorUrlMatch(gt_urls=[[gt_url]])
        return v._urls_match(agent_url, gt_url)

    def test_url_with_trailing_slash(self):
        gt = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3/"
        agent = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3"
        match, _ = self._match(agent, gt)
        assert match is True

    def test_url_without_filters(self):
        url = "https://www.realtor.com/realestateandhomes-search/Seattle_WA"
        match, _ = self._match(url, url)
        assert match is True

    def test_pet_friendly_segments(self):
        gt = "https://www.realtor.com/apartments/LA_CA/dog-friendly/cat-friendly"
        match, _ = self._match(gt, gt)
        assert match is True

    def test_url_with_percent_encoding(self):
        """URL with percent-encoded characters."""
        gt = "https://www.realtor.com/realestateandhomes-search/San%20Francisco_CA/beds-3"
        agent = "https://www.realtor.com/realestateandhomes-search/San-Francisco_CA/beds-3"
        match, _ = self._match(agent, gt)
        # Should at least not crash
        assert isinstance(match, bool)

    @pytest.mark.asyncio
    async def test_repr_method(self):
        gt_url = "https://www.realtor.com/realestateandhomes-search/Austin_TX"
        metric = RealtorUrlMatch(gt_urls=[[gt_url]])
        repr_str = repr(metric)
        assert "RealtorUrlMatch" in repr_str
        assert "gt_urls" in repr_str

    @pytest.mark.asyncio
    async def test_compute_detailed_returns_result(self):
        gt_url = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3"
        metric = RealtorUrlMatch(gt_urls=[[gt_url]])
        await metric.reset()
        await metric.update(url=gt_url)
        result = await metric.compute_detailed()
        assert result.score == 1.0
        assert result.match is True

    @pytest.mark.asyncio
    async def test_compute_detailed_no_match(self):
        gt_url = "https://www.realtor.com/realestateandhomes-search/Austin_TX/beds-3"
        metric = RealtorUrlMatch(gt_urls=[[gt_url]])
        await metric.reset()
        result = await metric.compute_detailed()
        assert result.score == 0.0
        assert result.match is False
