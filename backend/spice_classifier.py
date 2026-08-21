"""
Step 2 of spice detection: for restaurants that passed the keyword
filter, ask Claude to actually judge whether the flagged reviews
describe genuine spice/heat, and produce a 0-5 score.

This catches things keyword matching alone would miss — a review
saying "this dish set my mouth on fire" doesn't contain the word
"spicy" at all, but obviously means the same thing. It also filters
OUT false positives keyword matching would wrongly flag, like "no
spice available, sadly" or a menu item just being named "Spicy Chicken
Burger" while the reviewer actually says it was pretty mild.
"""

import json

from anthropic import Anthropic

from config import Config

client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)

MODEL = "claude-haiku-4-5"  # cheap + fast — a good fit for a simple classification task


def classify_spice_level(review_texts):
    """
    Takes a list of review strings for one restaurant (already
    pre-filtered by keyword_filter.py, so these all contain SOME
    spice-related word), sends them to Claude, and returns a float
    spice score from 0-5, or None if Claude found no genuine evidence
    of real spiciness in them.
    """
    reviews_block = "\n".join(f"- {r}" for r in review_texts)

    prompt = f"""You are judging whether restaurant reviews describe genuinely spicy food.

Some reviews mention spice-related words without actually describing real
heat — for example, a dish just being named "Spicy Chicken Burger" while
the review itself says it was mild, or a review saying "no spicy options
available." Do not count these as evidence of genuine spiciness.

Based on the reviews below, rate how spicy this restaurant's food genuinely
is, on a scale from 0 to 5:
0 = no genuine evidence of spice (false positives only)
5 = extremely spicy, reviewers repeatedly describe intense heat

Respond with ONLY a JSON object in this exact shape, nothing else:
{{"spice_score": <number 0-5>, "reasoning": "<one sentence>"}}

Reviews:
{reviews_block}
"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text

    try:
        result = json.loads(raw_text)
        return result.get("spice_score")
    except (json.JSONDecodeError, IndexError):
        # Claude didn't return valid JSON for some reason — better to
        # treat this restaurant as "unknown" than crash the whole
        # pipeline over one bad response.
        return None
