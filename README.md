# The Soap Lab v0.3 Cloud Edition

This version is built for Streamlit + Supabase.

## Includes
- Supabase database setup SQL
- Cloud-connected Inventory
- Fragrance Library
- Recipe Builder
- Recipe Cost Summary
- Can I Make This?
- Batch creation
- Finished Goods inventory by quantity
- Ingredient Label Generator
- Product Type View
- Sales Tracker

## Setup Overview
1. Run `supabase_schema.sql` in Supabase SQL Editor.
2. Upload these files to your GitHub repository.
3. Deploy with Streamlit Community Cloud.
4. Add your Supabase secrets in Streamlit.

## Streamlit Secrets
In Streamlit Cloud, add:

```toml
SUPABASE_URL = "your-project-url"
SUPABASE_KEY = "your-publishable-or-anon-key"
```

Use your Supabase project URL and publishable/anon key.
Do not paste your secret service key into Streamlit.
