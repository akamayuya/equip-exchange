import requests


def _fetch_coordinates(address):
    if not address:
        return None

    url = "https://msearch.gsi.go.jp/address-search/AddressSearch"
    params = {"q": address}

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return None

    if not data or not isinstance(data, list):
        return None

    coords = data[0].get("geometry", {}).get("coordinates")
    if not coords or len(coords) != 2:
        return None

    try:
        return float(coords[1]), float(coords[0])
    except (TypeError, ValueError):
        return None


def get_product_map_address(product):
    seller = getattr(product, "seller", None)
    seller_company = getattr(seller, "company", None) if seller else None
    seller_address = getattr(seller_company, "address", "")
    return seller_address or ""


def get_product_map_coordinates(product):
    address = get_product_map_address(product)
    return _fetch_coordinates(address)


def populate_product_coordinates(product):
    coordinates = get_product_map_coordinates(product)
    if not coordinates:
        product.latitude = None
        product.longitude = None
        return False

    product.latitude, product.longitude = coordinates
    return True