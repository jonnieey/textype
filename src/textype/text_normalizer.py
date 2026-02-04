"""Text normalization for typing practice.

This module provides functions to normalize Unicode text to keyboard-typable
ASCII equivalents, replacing fancy quotes, dashes, ellipsis, and other
special characters with standard keyboard characters.
"""

import unicodedata


def normalize_text(text: str) -> str:
    """Normalize Unicode text to keyboard-typable ASCII equivalents.

    Replaces fancy quotes, dashes, ellipsis, and other special Unicode
    characters with their standard keyboard-typable equivalents.

    Args:
        text: Input string possibly containing Unicode characters

    Returns:
        Normalized string with Unicode characters replaced by ASCII equivalents
    """
    # Step 1: Replace specific Unicode characters with keyboard-typable equivalents
    replacements = {
        # Smart quotes and apostrophes
        "\u2018": "'",  # Left single quotation mark
        "\u2019": "'",  # Right single quotation mark
        "\u201a": "'",  # Single low-9 quotation mark
        "\u201b": "'",  # Single high-reversed-9 quotation mark
        "\u201c": '"',  # Left double quotation mark
        "\u201d": '"',  # Right double quotation mark
        "\u201e": '"',  # Double low-9 quotation mark
        "\u201f": '"',  # Double high-reversed-9 quotation mark
        "\u2032": "'",  # Prime
        "\u2033": '"',  # Double prime
        "\u2034": "'''",  # Triple prime
        "\u2035": "'",  # Reversed prime
        "\u2036": '"',  # Reversed double prime
        "\u2037": "'''",  # Reversed triple prime
        # Dashes and hyphens
        "\u2010": "-",  # Hyphen
        "\u2011": "-",  # Non-breaking hyphen
        "\u2012": "-",  # Figure dash
        "\u2013": "-",  # En dash
        "\u2014": "--",  # Em dash (common replacement)
        "\u2015": "--",  # Horizontal bar
        "\u2053": "~",  # Swung dash
        # Ellipsis
        "\u2026": "...",  # Horizontal ellipsis
        # Spaces
        "\u00a0": " ",  # Non-breaking space
        "\u2000": " ",  # En quad
        "\u2001": " ",  # Em quad
        "\u2002": " ",  # En space
        "\u2003": " ",  # Em space
        "\u2004": " ",  # Three-per-em space
        "\u2005": " ",  # Four-per-em space
        "\u2006": " ",  # Six-per-em space
        "\u2007": " ",  # Figure space
        "\u2008": " ",  # Punctuation space
        "\u2009": " ",  # Thin space
        "\u200a": " ",  # Hair space
        "\u200b": "",  # Zero width space (remove)
        "\u200c": "",  # Zero width non-joiner (remove)
        "\u200d": "",  # Zero width joiner (remove)
        "\u202f": " ",  # Narrow no-break space
        # Mathematical symbols (common in text)
        "\u00d7": "x",  # Multiplication sign
        "\u00f7": "/",  # Division sign
        "\u00b1": "+/-",  # Plus-minus sign
        "\u2260": "!=",  # Not equal to
        "\u2264": "<=",  # Less-than or equal to
        "\u2265": ">=",  # Greater-than or equal to
        "\u2212": "-",  # Minus sign
        "\u2217": "*",  # Asterisk operator
        # Currency symbols (replace with abbreviations)
        "\u00a2": "cents",  # Cent sign
        "\u00a3": "GBP",  # Pound sign
        "\u00a4": "USD",  # Currency sign
        "\u00a5": "JPY",  # Yen sign
        "\u20ac": "EUR",  # Euro sign
        # Copyright and trademark symbols
        "\u00a9": "(c)",  # Copyright sign
        "\u00ae": "(r)",  # Registered sign
        "\u2122": "TM",  # Trade mark sign
        # Letter-like symbols
        "\u2117": "(p)",  # Sound recording copyright
        "\u2120": "SM",  # Service mark
        # Fractions (replace with ASCII equivalents)
        "\u00bc": "1/4",  # Vulgar fraction one quarter
        "\u00bd": "1/2",  # Vulgar fraction one half
        "\u00be": "3/4",  # Vulgar fraction three quarters
        "\u2044": "/",  # Fraction slash
        # Degree and other symbols
        "\u00b0": "deg",  # Degree sign
        "\u00b5": "u",  # Micro sign (mu)
        # Punctuation (rare but possible)
        "\u2022": "*",  # Bullet
        "\u2023": ">",  # Triangular bullet
        "\u2043": "-",  # Hyphen bullet
        "\u204e": "*",  # Low asterisk
        "\u204f": ";",  # Reversed semicolon
        "\u2051": "**",  # Two asterisks aligned vertically
        "\u2052": "%",  # Commercial minus sign
        "\u2056": "...",  # Three dot punctuation
        "\u2058": "....",  # Four dot punctuation
        "\u2059": ".....",  # Five dot punctuation
        # Arrows (replace with text)
        "\u2190": "<-",  # Leftwards arrow
        "\u2191": "^",  # Upwards arrow
        "\u2192": "->",  # Rightwards arrow
        "\u2193": "v",  # Downwards arrow
        "\u2194": "<->",  # Left right arrow
        "\u2195": "^v",  # Up down arrow
        # Other symbols
        "\u00ab": "<<",  # Left-pointing double angle quotation mark
        "\u00bb": ">>",  # Right-pointing double angle quotation mark
        "\u00a1": "!",  # Inverted exclamation mark
        "\u00bf": "?",  # Inverted question mark
        "\u00b7": "*",  # Middle dot
        "\u00b6": "P",  # Pilcrow sign
        "\u00a7": "S",  # Section sign
        "\u2126": "Ohm",  # Ohm sign
        "\u212b": "A",  # Angstrom sign
    }

    # Create translation table
    trans_table = str.maketrans(replacements)

    # Apply translations first (so mathematical symbols are replaced before decomposition)
    translated = text.translate(trans_table)

    # Step 2: Decompose Unicode characters and remove diacritical marks
    # Normalize to NFKD form (decompose characters into base + combining marks)
    decomposed = unicodedata.normalize("NFKD", translated)
    # Remove combining diacritical marks (Unicode category starts with 'M')
    stripped = "".join(char for char in decomposed if not unicodedata.combining(char))

    return stripped
