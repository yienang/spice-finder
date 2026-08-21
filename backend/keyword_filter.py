"""
Step 1 of spice detection: quick, cheap keyword filtering across review
text, before we spend any money or time calling Claude.

Why bother with keywords first instead of just sending every review to
Claude? Cost and speed — an LLM call costs a small amount of money and
takes a second or two, for every single restaurant. Keyword filtering
is instant and free, and lets us skip calling Claude entirely for
restaurants where literally no review mentions anything spice-related.
It's a cheap first pass that narrows down to only the restaurants
actually worth spending an LLM call on.
"""

SPICE_KEYWORDS = [
    # Core spice words
    "spicy", "spice", "spiced", "hot", "chili", "chilli", "chile",
    # Heat/sensation words people actually use in reviews
    "fire", "fiery", "burn", "burning", "heat", "sweat", "sweating",
    "tongue", "scorching", "blazing", "sinus", "watering eyes",
    # Specific peppers/sauces that signal spice even without the word "spicy"
    "habanero", "jalapeno", "jalapeño", "ghost pepper", "carolina reaper",
    "scoville", "sriracha", "gochujang", "wasabi", "peri peri", "piri piri",
    "vindaloo", "diablo", "szechuan", "sichuan",
]


def review_mentions_spice(review_text):
    """
    Returns True if any spice-related keyword appears anywhere in this
    one review's text (case-insensitive), False otherwise.
    """
    lowercase_review = review_text.lower()
    for keyword in SPICE_KEYWORDS:
        if keyword in lowercase_review:
            return True
    return False
