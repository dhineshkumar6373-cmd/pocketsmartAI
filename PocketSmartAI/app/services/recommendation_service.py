from datetime import datetime, timezone
from typing import Any
from app.models.schemas import HomeBudgetInput, PartyBudgetInput, JewelryBudgetInput
from app.services.gemini_service import GeminiService
from app.services.platform_links import CATEGORY_PLATFORMS, shopping_links


gemini = GeminiService()


def money(value: float) -> float:
    return round(max(0.0, float(value)), 2)


def _home_fallback(data: HomeBudgetInput) -> dict[str, Any]:
    requested = [
        ("Lighting", data.num_lights, 0.08, "Energy-efficient LED lighting", "warm white LED bulbs"),
        ("Ceiling Fans", data.num_fans, 0.16, "Efficient ceiling fan", "energy efficient ceiling fan"),
        ("Furniture", data.num_furniture, 0.22, "Practical furniture piece", "modern furniture"),
        ("Dining Tables", data.num_dining_tables, 0.16, "Compact dining table", "4 seater dining table"),
    ]
    active = [(c, q, share, desc, term) for c, q, share, desc, term in requested if q > 0]
    if not active:
        active = [("Decor", 1, 0.35, "Budget-friendly accent decor", "home decor"), ("Lighting", 2, 0.15, "LED ambient lights", "LED ambient lights")]
    total_share = sum(x[2] for x in active)
    categories = []
    allocated = 0.0
    for i, (category, qty, share, desc, term) in enumerate(active):
        allocation = data.total_budget * share / total_share
        allocation = money(allocation)
        allocated += allocation
        unit = money(allocation / max(qty, 1))
        categories.append({
            "category": category.lower().replace(" ", "_"),
            "allocation": allocation,
            "items": [{
                "name": desc,
                "description": f"Suggested quantity: {qty}",
                "estimated_price": unit,
                "quantity": qty,
                "search_terms": term,
                "shopping_links": shopping_links(term, CATEGORY_PLATFORMS["home"]),
            }],
        })
    remaining = money(data.total_budget - allocated)
    return {
        "total_budget": money(data.total_budget),
        "budget_breakdown": categories,
        "remaining_budget": remaining,
        "additional_suggestions": [
            "Prioritize essential fixtures before decorative purchases.",
            "Compare the same search term across multiple platforms before buying.",
            "Keep a small portion of the budget for installation and delivery.",
        ],
        "ai_mode": "fallback",
    }


def _party_fallback(data: PartyBudgetInput) -> dict[str, Any]:
    weights = []
    if data.venue_type or data.party_type:
        weights.append(("venue", 0.20, "Venue option", "event venue"))
    if data.needs_catering:
        weights.append(("catering", 0.40, "Catering package", f"{data.party_type} catering"))
    if data.needs_decoration:
        weights.append(("decoration", 0.15, "Event decoration set", "party decoration"))
    if data.needs_entertainment:
        weights.append(("entertainment", 0.15, "Entertainment package", "party entertainment"))
    weights.append(("contingency", 0.10, "Contingency reserve", "event emergency supplies"))
    total = sum(w for _, w, _, _ in weights)
    breakdown = []
    allocated = 0.0
    for category, weight, name, term in weights:
        allocation = money(data.total_budget * weight / total)
        allocated += allocation
        platforms = CATEGORY_PLATFORMS.get("food" if category == "catering" else category, CATEGORY_PLATFORMS["decoration"])
        breakdown.append({
            "category": category,
            "allocation": allocation,
            "items": [{
                "name": name,
                "description": f"Plan for {data.num_guests} guests",
                "estimated_price": allocation,
                "quantity": 1,
                "search_terms": term,
                "shopping_links": shopping_links(term, platforms),
            }],
        })
    return {
        "total_budget": money(data.total_budget),
        "budget_breakdown": breakdown,
        "remaining_budget": money(data.total_budget - allocated),
        "venue_suggestions": [{
            "name": data.venue_type or "Local event venue",
            "type": data.venue_type or "flexible",
            "capacity": data.num_guests,
            "estimated_cost": money(data.total_budget * 0.20),
            "search_terms": f"{data.party_type} venue {data.num_guests} guests",
            "shopping_links": shopping_links(f"{data.party_type} venue {data.num_guests} guests", CATEGORY_PLATFORMS["venue"]),
        }],
        "additional_suggestions": [
            "Ask vendors for per-person package pricing.",
            "Keep contingency funds untouched until the final booking stage.",
            "Compare food and venue packages before committing.",
        ],
        "ai_mode": "fallback",
    }


def _jewelry_fallback(data: JewelryBudgetInput, image_used: bool) -> dict[str, Any]:
    items = [
        ("Earrings", 0.25, "Elegant earrings", "minimal elegant earrings"),
        ("Necklace", 0.40, "Occasion-appropriate necklace", "occasion necklace"),
        ("Bracelet", 0.15, "Minimal bracelet", "minimal bracelet"),
    ]
    recommendations = []
    allocated = 0.0
    for kind, share, name, term in items:
        price = money(data.total_budget * share)
        allocated += price
        recommendations.append({
            "item_type": kind,
            "description": f"{name} for {data.occasion}. Style preferences: {data.preferences or 'versatile and elegant'}.",
            "style": "versatile",
            "estimated_price": price,
            "search_terms": term,
            "shopping_links": shopping_links(term, CATEGORY_PLATFORMS["jewelry"]),
        })
    return {
        "outfit_analysis": {
            "colors": "Image analysis unavailable in fallback mode" if image_used else "Not provided",
            "style": data.preferences or "versatile",
            "formality": "occasion-appropriate",
        },
        "total_budget": money(data.total_budget),
        "jewelry_recommendations": recommendations,
        "remaining_budget": money(data.total_budget - allocated),
        "styling_tips": [
            "Match metal tone to the outfit's overall color temperature.",
            "For statement jewelry, keep the other pieces simpler.",
            "Consider the occasion's formality when selecting size and shine.",
        ],
        "ai_mode": "fallback",
    }


def _home_prompt(data: HomeBudgetInput) -> str:
    return f"""You are PocketSmart AI, a budget planning assistant for India. Create practical home interior recommendations. Return ONLY valid JSON with keys total_budget, budget_breakdown, remaining_budget, additional_suggestions, ai_mode. The budget must never be exceeded. Each budget_breakdown entry needs category, allocation, items. Each item needs name, description, estimated_price, quantity, search_terms, shopping_links. Use INR numbers only and do not claim live inventory or exact current prices. Inputs: {data.model_dump_json()}"""


def _party_prompt(data: PartyBudgetInput) -> str:
    return f"""You are PocketSmart AI, a budget planning assistant for India. Plan an event within the exact INR budget. Return ONLY valid JSON with keys total_budget, budget_breakdown, remaining_budget, venue_suggestions, additional_suggestions, ai_mode. Include venue, catering, decoration and entertainment only when requested. Each item needs name, description, estimated_price, quantity, search_terms, shopping_links. Do not claim live inventory or exact current prices. Inputs: {data.model_dump_json()}"""


def _jewelry_prompt(data: JewelryBudgetInput) -> str:
    return f"""You are PocketSmart AI, a jewelry styling assistant for India. Analyze the outfit image if one is supplied and recommend jewelry within the exact INR budget. Return ONLY valid JSON with keys outfit_analysis, total_budget, jewelry_recommendations, remaining_budget, styling_tips, ai_mode. Each recommendation needs item_type, description, style, estimated_price, search_terms, shopping_links. Never claim exact live prices. Inputs: {data.model_dump_json()}"""


def _normalize_budget(result: dict[str, Any], budget: float) -> dict[str, Any]:
    result["total_budget"] = money(budget)
    # Do not silently trust an AI total: compute remaining from allocations where possible.
    allocated = 0.0
    for group in result.get("budget_breakdown", []):
        group["allocation"] = money(group.get("allocation", 0))
        allocated += group["allocation"]
        for item in group.get("items", []):
            item["estimated_price"] = money(item.get("estimated_price", 0))
            item["quantity"] = max(0, int(item.get("quantity", 1) or 1))
    result["remaining_budget"] = money(budget - allocated)
    return result


def get_home_recommendations(data: HomeBudgetInput) -> dict[str, Any]:
    try:
        return _normalize_budget(gemini.generate_json(_home_prompt(data)), data.total_budget) | {"generated_at": datetime.now(timezone.utc).isoformat()}
    except Exception:
        return _home_fallback(data) | {"generated_at": datetime.now(timezone.utc).isoformat()}


def get_party_recommendations(data: PartyBudgetInput) -> dict[str, Any]:
    try:
        return _normalize_budget(gemini.generate_json(_party_prompt(data)), data.total_budget) | {"generated_at": datetime.now(timezone.utc).isoformat()}
    except Exception:
        return _party_fallback(data) | {"generated_at": datetime.now(timezone.utc).isoformat()}


def get_jewelry_recommendations(data: JewelryBudgetInput, image_path=None) -> dict[str, Any]:
    try:
        result = gemini.generate_json(_jewelry_prompt(data), image_path=image_path)
        result["total_budget"] = money(data.total_budget)
        result["jewelry_recommendations"] = result.get("jewelry_recommendations", [])
        spent = sum(money(x.get("estimated_price", 0)) for x in result["jewelry_recommendations"])
        result["remaining_budget"] = money(data.total_budget - spent)
        result["generated_at"] = datetime.now(timezone.utc).isoformat()
        return result
    except Exception:
        return _jewelry_fallback(data, image_used=image_path is not None) | {"generated_at": datetime.now(timezone.utc).isoformat()}
