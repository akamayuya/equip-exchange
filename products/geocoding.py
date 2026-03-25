import requests


def populate_product_coordinates(product):
    address = (
        product.geocode_address() if hasattr(product, "geocode_address") else product.location
    )

    if not address:
        product.latitude = None
        product.longitude = None
        return False

    url = "https://msearch.gsi.go.jp/address-search/AddressSearch"
    params = {"q": address}

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
    except Exception:
        product.latitude = None
        product.longitude = None
        return False

    if not data or not isinstance(data, list):
        product.latitude = None
        product.longitude = None
        return False

    coords = data[0].get("geometry", {}).get("coordinates")
    if not coords or len(coords) != 2:
        product.latitude = None
        product.longitude = None
        return False

    try:
        product.longitude = float(coords[0])
        product.latitude = float(coords[1])
    except (TypeError, ValueError):
        product.latitude = None
        product.longitude = None
        return False

    return True