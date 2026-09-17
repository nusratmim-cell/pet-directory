# Bangladesh Pet Business Directory

Pet shops, pet food, vets, pet hotels/boarding, grooming and government vet hospitals across all 64 districts of Bangladesh.

- `index.html`: the site (static; Vercel serves it at `/`)
- `bangladesh_pet_business_directory.xlsx`: same data as a spreadsheet
- `build_directory.py`: merges every source into the site and spreadsheet
- `apify/run_apify.py`: collects Google Maps places with Apify's free plan (token in `~/.apify_token`, never committed)
- `data/`: source data (Posha Ghor, OpenStreetMap, Chonk stockists, Overture Maps/Facebook pages, DLS office lists, 2022 census, district boundaries)

## Update

```
python3 apify/run_apify.py --status          # remaining free credit
python3 apify/run_apify.py --phase 2          # next month's batch
python3 build_directory.py                    # rebuild index.html + xlsx
git add -A && git commit -m "Update directory" && git push
```

## Deploy on Vercel

Import this repo in Vercel with Framework Preset "Other", no build command, output directory `.` (root).
