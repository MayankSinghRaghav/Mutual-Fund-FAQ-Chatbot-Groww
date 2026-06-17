import pytest
from runtime.safety import SafetyFilter


@pytest.fixture
def safety():
    return SafetyFilter()


# ---------------------------------------------------------------------------
# Advisory keyword tests
# ---------------------------------------------------------------------------

class TestAdvisoryKeywords:
    def test_should_i_invest_is_blocked(self, safety):
        safe, msg = safety.is_safe("should I invest in HDFC Mid-Cap?")
        assert safe is False
        assert msg is not None

    def test_which_fund_is_better_blocked(self, safety):
        safe, msg = safety.is_safe("Which fund is better for me?")
        assert safe is False

    def test_give_me_advice_blocked(self, safety):
        safe, msg = safety.is_safe("give me advice on mutual funds")
        assert safe is False

    def test_predict_blocked(self, safety):
        safe, msg = safety.is_safe("Can you predict the market next year?")
        assert safe is False

    def test_future_returns_blocked(self, safety):
        safe, msg = safety.is_safe("What are the future returns of this fund?")
        assert safe is False

    def test_best_fund_blocked(self, safety):
        safe, msg = safety.is_safe("What is the best fund to buy now?")
        assert safe is False

    def test_buy_or_sell_blocked(self, safety):
        safe, msg = safety.is_safe("Should I buy or sell HDFC equity?")
        assert safe is False

    def test_advisory_keyword_case_insensitive(self, safety):
        safe, _ = safety.is_safe("SHOULD I INVEST in something?")
        assert safe is False

    def test_advisory_keyword_mixed_case(self, safety):
        safe, _ = safety.is_safe("Should I Invest in HDFC?")
        assert safe is False

    def test_advisory_refusal_message_is_string(self, safety):
        _, msg = safety.is_safe("should i invest in funds")
        assert isinstance(msg, str)
        assert len(msg) > 0


# ---------------------------------------------------------------------------
# Safe factual query tests
# ---------------------------------------------------------------------------

class TestSafeQueries:
    def test_factual_query_is_allowed(self, safety):
        safe, msg = safety.is_safe("What is the expense ratio of HDFC Mid-Cap Fund?")
        assert safe is True
        assert msg is None

    def test_nav_query_is_allowed(self, safety):
        safe, msg = safety.is_safe("What is the NAV of HDFC Equity Fund?")
        assert safe is True
        assert msg is None

    def test_fund_category_query_allowed(self, safety):
        safe, msg = safety.is_safe("What category does HDFC ELSS fall under?")
        assert safe is True
        assert msg is None

    def test_empty_string_is_allowed(self, safety):
        safe, msg = safety.is_safe("")
        assert safe is True
        assert msg is None


# ---------------------------------------------------------------------------
# PII pattern tests
# ---------------------------------------------------------------------------

class TestPIIDetection:
    def test_phone_number_blocked(self, safety):
        safe, msg = safety.is_safe("Call me at 9876543210")
        assert safe is False
        assert msg is not None

    def test_email_blocked(self, safety):
        safe, msg = safety.is_safe("Email me at user@example.com")
        assert safe is False

    def test_pan_card_blocked(self, safety):
        safe, msg = safety.is_safe("My PAN is ABCDE1234F")
        assert safe is False

    def test_pan_lowercase_not_blocked(self, safety):
        # PAN regex requires uppercase; lowercase should pass
        safe, _ = safety.is_safe("abcde1234f is not a valid PAN format here")
        assert safe is True

    def test_pii_refusal_message_is_string(self, safety):
        _, msg = safety.is_safe("9876543210")
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_short_number_not_blocked(self, safety):
        # 9-digit number should not trigger the 10-digit phone pattern
        safe, _ = safety.is_safe("Fund launched in 123456789")
        assert safe is True

    def test_eleven_digit_number_not_blocked(self, safety):
        # 11-digit number should not match \b\d{10}\b
        safe, _ = safety.is_safe("Number 12345678901 is too long")
        assert safe is True
