"""Collect pet businesses from Google Maps with Apify's Google Maps Scraper (free plan).

Free plan: $5 credit per month, $0.004 per place => about 1,250 places a month.
Each phase is sized to fit in one month's credit. Run one phase per month.

Usage:
  python3 apify/run_apify.py --phase 1 --dry-run   # show the searches and max cost, spend nothing
  python3 apify/run_apify.py --phase 1             # run it (needs token in ~/.apify_token)
  python3 apify/run_apify.py --status              # show this month's Apify usage
"""
import argparse, csv, json, os, sys, time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
ACTOR = "compass~crawler-google-places"
PRICE_PER_PLACE = 0.004   # free-plan price, checked 2026-09-17
API = "https://api.apify.com/v2"

DISTRICTS = [r for r in csv.DictReader(open(ROOT / "data" / "districts.csv"))]
BY_POP = sorted(DISTRICTS, key=lambda r: -int(r["population_2022"]))
OUTSIDE_DHAKA = [r["district"] for r in BY_POP if r["district"] != "Dhaka"]
DHAKA_AREAS = ["Mirpur", "Uttara", "Dhanmondi", "Mohammadpur", "Gulshan", "Banani", "Bashundhara", "Badda",
               "Rampura", "Khilgaon", "Jatrabari", "Old Dhaka", "Motijheel", "Tejgaon", "Farmgate", "Shyamoli",
               "Pallabi", "Banasree", "Wari", "Lalbagh", "Keraniganj", "Savar", "Tongi", "Dakshinkhan", "Khilkhet"]


def phase_searches(phase):
    """Return a list of (search string, max places) for a phase."""
    s = []
    if phase == 1:
        # Every district outside Dhaka: shops and vets (biggest gap in current data)
        for d in OUTSIDE_DHAKA:
            s.append((f"pet shop in {d}, Bangladesh", 8))
            s.append((f"veterinary clinic in {d}, Bangladesh", 8))
        # Services that are rare everywhere: hotels, boarding, grooming in the two big cities
        for term in ["pet hotel", "pet boarding", "pet grooming"]:
            s.append((f"{term} in Dhaka, Bangladesh", 25))
            s.append((f"{term} in Chattogram, Bangladesh", 10))
    elif phase == 2:
        # Dhaka neighbourhood by neighbourhood (Google shows at most ~120 per search)
        for a in DHAKA_AREAS:
            s.append((f"pet shop in {a}, Dhaka", 20))
            s.append((f"veterinary clinic in {a}, Dhaka", 15))
            s.append((f"cat food shop in {a}, Dhaka", 10))
    elif phase == 3:
        # Second pass: aquarium/bird shops, pet food and services in the 20 largest districts
        for d in OUTSIDE_DHAKA[:20]:
            for term, n in [("aquarium fish shop", 8), ("bird shop", 6), ("pet food shop", 8), ("pet hospital", 6), ("pet grooming", 4), ("pet boarding", 4)]:
                s.append((f"{term} in {d}, Bangladesh", n))
    else:
        sys.exit(f"Unknown phase {phase}. Use 1, 2 or 3.")
    return s


def token():
    t = os.environ.get("APIFY_TOKEN")
    f = Path.home() / ".apify_token"
    if not t and f.exists():
        t = f.read_text().strip()
    if not t:
        sys.exit("No Apify token. Save it with:  echo 'apify_api_XXXX' > ~/.apify_token")
    return t


def usage(tok):
    r = requests.get(f"{API}/users/me/limits", params={"token": tok}, timeout=60)
    r.raise_for_status()
    d = r.json()["data"]
    used = d.get("current", {}).get("monthlyUsageUsd", 0)
    limit = d.get("limits", {}).get("maxMonthlyUsageUsd", 5)
    return used, limit, d.get("monthlyUsageCycle", {})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", type=int)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--budget", type=float, default=None, help="max USD to spend (default: remaining free credit minus $0.10)")
    a = ap.parse_args()

    if a.status:
        used, limit, cycle = usage(token())
        print(f"Used ${used:.2f} of ${limit:.2f} this cycle {cycle}")
        return
    if not a.phase:
        ap.error("--phase is required")

    searches = phase_searches(a.phase)
    max_places = sum(n for _, n in searches)
    print(f"Phase {a.phase}: {len(searches)} searches, at most {max_places} places, at most ${max_places * PRICE_PER_PLACE:.2f}")
    if a.dry_run:
        for q, n in searches:
            print(f"  {n:>3}  {q}")
        return

    tok = token()
    used, limit, _ = usage(tok)
    budget = a.budget if a.budget is not None else round(limit - used - 0.10, 2)
    if budget < 0.5:
        sys.exit(f"Only ${limit - used:.2f} credit left this cycle. Wait for the monthly reset.")
    print(f"Credit left: ${limit - used:.2f}. Spending cap for this run: ${budget:.2f}")

    # Group by max-places so each run uses one maxCrawledPlacesPerSearch value
    groups = {}
    for q, n in searches:
        groups.setdefault(n, []).append(q)

    out_dir = ROOT / "apify" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    spent = 0.0
    for n, qs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        remaining = round(budget - spent, 2)
        if remaining < 0.5:
            print("Budget reached; stopping. Remaining searches can run next month.")
            break
        body = {
            "searchStringsArray": qs,
            "maxCrawledPlacesPerSearch": n,
            "language": "en",
            "countryCode": "bd",
            "skipClosedPlaces": False,
            "scrapePlaceDetailPage": False,
            "scrapeContacts": False,
            "maxImages": 0,
            "maxReviews": 0,
        }
        print(f"Starting run: {len(qs)} searches x up to {n} places (cap ${remaining:.2f})")
        r = requests.post(f"{API}/acts/{ACTOR}/runs", params={"token": tok, "maxTotalChargeUsd": remaining}, json=body, timeout=60)
        r.raise_for_status()
        run = r.json()["data"]
        while run["status"] in ("READY", "RUNNING"):
            time.sleep(20)
            run = requests.get(f"{API}/actor-runs/{run['id']}", params={"token": tok}, timeout=60).json()["data"]
            print(f"  {run['status']}  charged so far ${run.get('usageTotalUsd') or 0:.2f}")
        items = requests.get(f"{API}/datasets/{run['defaultDatasetId']}/items", params={"token": tok, "clean": "true", "format": "json"}, timeout=300).json()
        f = out_dir / f"phase{a.phase}_max{n}_{run['id']}.json"
        f.write_text(json.dumps(items, ensure_ascii=False))
        spent += run.get("usageTotalUsd") or len(items) * PRICE_PER_PLACE
        print(f"  saved {len(items)} places -> {f.relative_to(ROOT)}  (status {run['status']})")
    print(f"Done. Approx. spent ${spent:.2f}. Now run: python3 build_directory.py")


if __name__ == "__main__":
    main()
