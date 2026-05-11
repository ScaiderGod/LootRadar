# LootRadar V1.3

LootRadar is a Streamlit game deal scanner focused on PC game offers.

This version uses CheapShark data and adds a cleaner visual identity, quick scans, deal cards, filters, comparison tools, Vault favorites, CSV export, and manual currency conversion.

## What it does

- Search PC game deals by title
- Filter by store, content type, discount, score and price
- Sort by deal score, lowest price, biggest discount, store or title
- Hide most DLC and extras with Clean Mode
- Show the best deal per title
- Compare offers in a table
- Save session favorites in the Vault
- Export filtered results as CSV
- Change display currency using a manual exchange rate

## Currency conversion

CheapShark returns prices in USD.

LootRadar V1.3 lets you choose a display currency and set your own exchange rate:

- USD
- MXN
- EUR
- GBP
- CAD
- BRL
- COP
- CLP
- ARS
- JPY
- Custom

The app keeps USD columns in the comparison and export data, while also adding converted price columns using your manual rate.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload all files from this folder.
3. Create a new app in Streamlit Community Cloud.
4. Select the repository.
5. Set the main file path to `app.py`.
6. Deploy.

## Notes

This V1.3 is focused on PC deals. Future versions can add IsThereAnyDeal, permanent user accounts, watchlists and alerts.

Always verify the final price in the store before buying. Prices can change quickly.
