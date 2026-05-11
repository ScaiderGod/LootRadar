# LootRadar V1

LootRadar is a Streamlit app for scanning PC game deals by title, comparing discounts, filtering stores, and spotting the best current offers.

## What this V1 includes

- Streamlit interface with a dark gamer style
- Live search using CheapShark public API
- Filters by store, price, discount, score and content type
- Clean Mode to hide most DLC, soundtracks and extras
- Deal Score calculation
- Compare table
- Temporary Vault favorites during the active session
- CSV export

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload these files:
   - `app.py`
   - `requirements.txt`
   - `.gitignore`
   - `.streamlit/config.toml`
   - `README.md`
3. Go to Streamlit Community Cloud.
4. Create a new app from the GitHub repository.
5. Main file path: `app.py`
6. Deploy.

## Notes

This V1 is focused on PC deals through CheapShark. Future versions can add IsThereAnyDeal, Deku Deals style console coverage, permanent user accounts, watchlists and alerts.
