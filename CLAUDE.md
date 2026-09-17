# Bangladesh pet directory & pet food / silage research

Built for a CEO launching a pet food and silage business in Bangladesh. Free data sources only.

## What's here

| File | What it is |
|---|---|
| `index.html` | Website home: directory of pet shops, vets, pet hotels, grooming, govt vet offices in all 64 districts (generated) |
| `research.html` | Pet food & silage market research page (generated) |
| `bangladesh-pet-directory.html` | Same directory without the `<html>` wrapper, for the Claude artifact (generated) |
| `bangladesh_pet_business_directory.xlsx` | Directory + 64-district sheet (generated) |
| `build_directory.py` | Merges every source and writes the four files above |
| `data/page_template.html` | Directory page template (edit this, not index.html) |
| `data/research_template.html` | Research page template (edit this, not research.html) |
| `data/districts.csv` | 64 districts, division, 2022 census population, area |
| `data/bgd_adm2.geojson` | District boundaries (geoBoundaries) used to place map points in districts |
| `data/sources/` | Posha Ghor, OpenStreetMap, Chonk stockists, Overture (Facebook pages), DLS govt vet office list + PDFs |
| `apify/run_apify.py` | Google Maps collection through Apify's free plan |
| `apify/results/` | Raw Google Maps results (one JSON per run) |

## Common tasks

```bash
python3 apify/run_apify.py --status            # Apify credit used this cycle ($5 free, resets monthly on the 17th)
python3 apify/run_apify.py --phase 2 --dry-run  # preview searches and max cost, spends nothing
python3 apify/run_apify.py --phase 2            # run (token in ~/.apify_token; never commit it)
python3 build_directory.py                      # rebuild site + Excel
git add -A && git commit -m "Update directory" && git push   # Vercel redeploys from main
```

Apify phases (one per month, each fits the $5 free credit):
1. Pet shops + vet clinics in 63 districts outside Dhaka; pet hotels/boarding/grooming in Dhaka & Chattogram (ran 2026-09-17)
2. 25 Dhaka neighbourhoods: pet shops, vets, cat food shops
3. 20 largest districts: aquarium, bird, pet food, pet hospital, grooming, boarding

## Publishing

- GitHub: https://github.com/nusratmim-cell/pet-directory (`main`), hosted on Vercel (static, no build step; `.vercelignore` keeps data/scripts out of the deploy)
- Claude artifacts: directory https://claude.ai/artifact/6xTnt9hF77qU4APgQa35ma (publish `bangladesh-pet-directory.html`), research https://claude.ai/artifact/HBnj6sYRKHa8Y9cHW8u6f8 (publish research.html's body without the wrapper, back link pointed to the directory artifact)
- Pages use an off-white, light-only theme

## Data notes

- Counts are "known businesses", not totals (reports estimate 4,000+ pet shops nationwide)
- Duplicates merge on normalised name + district, or same 10-digit phone
- Govt vet offices (category `gov`) are excluded from "Known", stage and people-per-business counts
- gov.bd websites don't load from this machine; open them in the user's Chrome instead
- Unverified: silage price ~৳12/kg; 2022 dairy cost figures; import duty rates are customs duty only (VAT etc. extra)

## Ideas not done yet

- Phone numbers for the 554 DLS offices (on each office website's officer pages)
- District-level cattle population (BBS Agriculture Census) for silage targeting
- Primary research: shop margins, farmer willingness to pay for silage, maize sourcing cost
