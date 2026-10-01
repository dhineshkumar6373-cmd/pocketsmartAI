from urllib.parse import quote_plus

PLATFORMS = {
    "Amazon": "https://www.amazon.in/s?k={q}",
    "Flipkart": "https://www.flipkart.com/search?q={q}",
    "IKEA": "https://www.ikea.com/in/en/search/?q={q}",
    "Myntra": "https://www.myntra.com/{q}",
    "Ajio": "https://www.ajio.com/search/?text={q}",
    "Swiggy": "https://www.swiggy.com/search?query={q}",
    "Zomato": "https://www.zomato.com/search?q={q}",
    "OYO": "https://www.oyorooms.com/search?location={q}",
    "Booking.com": "https://www.booking.com/searchresults.html?ss={q}",
}

CATEGORY_PLATFORMS = {
    "home": ["Amazon", "Flipkart", "IKEA", "Myntra", "Ajio"],
    "jewelry": ["Amazon", "Flipkart", "Myntra", "Ajio"],
    "food": ["Swiggy", "Zomato"],
    "venue": ["OYO", "Booking.com"],
    "decoration": ["Amazon", "Flipkart", "Myntra"],
    "entertainment": ["Amazon", "Flipkart"],
}

def shopping_links(search_terms: str, platforms: list[str]) -> dict[str, str]:
    q = quote_plus(search_terms.strip())
    return {name: PLATFORMS[name].format(q=q) for name in platforms if name in PLATFORMS}
