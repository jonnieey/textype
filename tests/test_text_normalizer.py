"""Unit tests for the text_normalizer module."""

import pytest
from textype.text_normalizer import normalize_text


class TestNormalizeText:
    """Tests the normalize_text function for Unicode to ASCII conversion."""

    @pytest.mark.parametrize(
        "input_text, expected_output",
        [
            # Smart quotes and apostrophes
            ("‘Hello’", "'Hello'"),
            ("“World”", '"World"'),
            ("It’s a test", "It's a test"),
            # Dashes and hyphens
            ("endash –", "endash -"),
            ("emdash —", "emdash --"),
            # Ellipsis
            ("Wait…", "Wait..."),
            # Spaces
            ("Non-breaking space", "Non-breaking space"),
            ("Zero​width space", "Zerowidth space"),
            # Mathematical symbols
            ("2 × 2 = 4", "2 x 2 = 4"),
            ("10 ÷ 5 ≠ 1", "10 / 5 != 1"),
            # Currency symbols
            ("Cost: 5€", "Cost: 5EUR"),
            ("Price: 10£", "Price: 10GBP"),
            # Copyright and trademark symbols
            ("Copyright © 2024", "Copyright (c) 2024"),
            ("Company™", "CompanyTM"),
            # Fractions
            ("½ cup of sugar", "1/2 cup of sugar"),
            # Arrows
            ("Go right →", "Go right ->"),
            # Other symbols
            ("«Guillemets»", "<<Guillemets>>"),
            # Combining characters (diacritics)
            ("Crème brûlée", "Creme brulee"),
            ("résumé", "resume"),
            # Mixed Unicode and ASCII
            ("“¡Hola, señorita!” – a greeting.", '"!Hola, senorita!" - a greeting.'),
        ],
    )
    def test_various_normalizations(self, input_text, expected_output):
        """
        Tests a wide range of Unicode character normalizations.
        This parameterized test covers multiple categories of special characters
        to ensure they are correctly converted to their ASCII equivalents.
        """
        assert normalize_text(input_text) == expected_output

    def test_empty_string(self):
        """Tests that an empty string remains empty after normalization."""
        assert normalize_text("") == ""

    def test_no_special_characters(self):
        """Tests that a string with no special characters remains unchanged."""
        text = "This is a simple ASCII string with no special characters."
        assert normalize_text(text) == text
