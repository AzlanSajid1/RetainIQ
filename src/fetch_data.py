import requests, os, json
from dotenv import load_dotenv

load_dotenv()

STORE = os.getenv("SHOPIFY_STORE_URL")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
HEADERS = {"X-Shopify-Access-Token": TOKEN}
BASE = f"https://{STORE}/admin/api/2026-04"

def fetch_all(endpoint):
    url = f"{BASE}/{endpoint}?limit=250"
    all_data = []
    while url:
        r = requests.get(url, headers=HEADERS)
        data = r.json()
        key = list(data.keys())[0]
        all_data.extend(data[key])
        link = r.headers.get("Link", "")
        url = None
        if 'rel="next"' in link:
            url = link.split("<")[1].split(">")[0]
    return all_data

if __name__ == "__main__":
    print("Fetching orders...")
    orders = fetch_all("orders.json")
    print(f"  Got {len(orders)} orders")

    print("Fetching products...")
    products = fetch_all("products.json")
    print(f"  Got {len(products)} products")

    print("Fetching customers...")
    customers = fetch_all("customers.json")
    print(f"  Got {len(customers)} customers")

    os.makedirs("data/raw", exist_ok=True)
    json.dump(orders, open("data/raw/orders.json", "w"))
    json.dump(products, open("data/raw/products.json", "w"))
    json.dump(customers, open("data/raw/customers.json", "w"))

    print("\nAll data saved to data/raw/")