"""
Logic for turning raw data (the LLM's one-time guess + real user ratings)
into the single "current spice score" the frontend actually displays.

This deliberately lives in its own file, separate from app.py (routes)
and models.py (table definitions). Keeping "business logic" — rules
about how your app actually behaves — out of your route functions makes
routes easier to read (they become "get the data, call the logic,
return the result" rather than a wall of math), and makes this function
independently testable without spinning up a whole Flask server.
"""

# Once a restaurant has this many real ratings, we trust the crowd
# completely and stop factoring in the LLM's original guess at all.
CONFIDENCE_THRESHOLD = 5


def compute_blended_score(restaurant):
    """
    Takes a Restaurant object (with its .ratings relationship already
    available) and returns a single float — or None if we know nothing
    about this restaurant's spice level yet at all.
    """
    real_scores = [r.spice_rating for r in restaurant.ratings]

    # No real ratings yet: fall back entirely to the LLM's guess.
    # (Which might itself be None, if the LLM pass hasn't run on this
    # restaurant yet — that's fine, it just means "unknown," and the
    # frontend will need to handle a null score gracefully.)
    if not real_scores:
        return restaurant.llm_spice_score

    real_average = sum(real_scores) / len(real_scores)

    # We have real ratings but no LLM guess to blend with — just use
    # the real average as-is.
    if restaurant.llm_spice_score is None:
        return round(real_average, 2)

    # We have both: blend them, weighting toward the real average as
    # more real ratings accumulate. With 0 real ratings weight_real
    # would be 0 (100% LLM) — but we already returned early in that
    # case above, so here it's always > 0.
    weight_real = min(len(real_scores) / CONFIDENCE_THRESHOLD, 1.0)
    blended = (weight_real * real_average) + ((1 - weight_real) * restaurant.llm_spice_score)
    return round(blended, 2)
