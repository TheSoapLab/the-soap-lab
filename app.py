import streamlit as st
import pandas as pd
from datetime import date, timedelta
from supabase import create_client

st.set_page_config(page_title="The Soap Lab", layout="wide")
PINK = "#D63384"
PINK_DARK = "#B91E63"
PINK_SOFT = "#F8DDE8"
PINK_PALE = "#FFF7FA"
TEXT = "#111827"
MUTED = "#4B5563"
BORDER = "#E5E7EB"
CARD = "#FFFFFF"

st.markdown(f"""
<style>
/* GLOBAL */
html, body, .stApp {{
    background: {PINK_PALE} !important;
    color: {TEXT} !important;
}}

* {{
    color: {TEXT} !important;
}}

h1, h2, h3, h4, h5, h6 {{
    color: {TEXT} !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
}}

p, span, label, div {{
    color: {TEXT} !important;
}}

/* SIDEBAR */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #FBE7EF 0%, #FFF7FA 100%) !important;
    border-right: 1px solid #F3C6D7 !important;
}}

section[data-testid="stSidebar"] * {{
    color: {TEXT} !important;
}}

section[data-testid="stSidebar"] h1 {{
    color: {PINK_DARK} !important;
    font-size: 1.8rem !important;
}}

/* RADIO NAV */
div[role="radiogroup"] label {{
    background: transparent !important;
    border-radius: 12px !important;
    padding: 8px 10px !important;
}}

div[role="radiogroup"] label:hover {{
    background: {PINK_SOFT} !important;
}}

/* FORMS AND INPUTS */
.stTextInput label,
.stNumberInput label,
.stTextArea label,
.stSelectbox label,
.stCheckbox label {{
    color: {TEXT} !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
}}

input, textarea {{
    background-color: #FFFFFF !important;
    color: {TEXT} !important;
    border: 1px solid #D1D5DB !important;
    border-radius: 10px !important;
}}

input::placeholder, textarea::placeholder {{
    color: #6B7280 !important;
}}

[data-baseweb="input"],
[data-baseweb="textarea"],
[data-baseweb="select"] > div {{
    background-color: #FFFFFF !important;
    color: {TEXT} !important;
    border-color: #D1D5DB !important;
    border-radius: 10px !important;
}}

[data-baseweb="input"] *,
[data-baseweb="textarea"] *,
[data-baseweb="select"] * {{
    color: {TEXT} !important;
    background-color: transparent !important;
}}

/* NUMBER INPUT BUTTONS */
button[kind="secondary"] {{
    background-color: #FFFFFF !important;
    color: {TEXT} !important;
    border: 1px solid #D1D5DB !important;
}}

/* PRIMARY BUTTONS */
.stButton button,
.stFormSubmitButton button {{
    background: {PINK} !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
    border: none !important;
    font-weight: 700 !important;
    padding: 0.6rem 1rem !important;
}}

.stButton button:hover,
.stFormSubmitButton button:hover {{
    background: {PINK_DARK} !important;
    color: #FFFFFF !important;
}}

/* METRIC CARDS */
div[data-testid="stMetric"] {{
    background: {CARD} !important;
    padding: 20px !important;
    border-radius: 16px !important;
    border: 1px solid {BORDER} !important;
    box-shadow: 0 6px 18px rgba(17,24,39,0.05) !important;
}}

div[data-testid="stMetric"] * {{
    color: {TEXT} !important;
}}

div[data-testid="stMetricValue"] {{
    color: {PINK_DARK} !important;
    font-weight: 800 !important;
}}

/* ALERTS */
div[data-testid="stAlert"] {{
    border-radius: 12px !important;
}}

div[data-testid="stAlert"] * {{
    color: {TEXT} !important;
}}

/* TABLES */
[data-testid="stDataFrame"] {{
    background: #FFFFFF !important;
    border-radius: 14px !important;
    border: 1px solid {BORDER} !important;
    overflow: hidden !important;
}}

/* EXPANDERS / FORM AREAS */
.streamlit-expanderHeader {{
    color: {TEXT} !important;
    font-weight: 700 !important;
}}

/* CAPTIONS AND SMALL TEXT */
small, .caption, [data-testid="stCaptionContainer"] * {{
    color: {MUTED} !important;
}}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def db():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase = db()
except Exception:
    st.error("Add SUPABASE_URL and SUPABASE_KEY in Streamlit secrets first.")
    st.stop()

def df(table):
    try:
        return pd.DataFrame(supabase.table(table).select("*").execute().data)
    except Exception as e:
        st.error(f"Could not load {table}: {e}")
        return pd.DataFrame()

def insert(table, data):
    return supabase.table(table).insert(data).execute()

# Compatibility helpers for newer Inventory Manager code
def table_df(table):
    return df(table)

def cost_per_unit(row):
    return cpu(row)

def insert_row(table, data):
    return insert(table, data)

def update_row(table, row_id, data):
    return supabase.table(table).update(data).eq("id", row_id).execute()

def delete_row(table, row_id):
    return supabase.table(table).delete().eq("id", row_id).execute()

def cpu(row):
    q = float(row.get("quantity_purchased") or 0)
    t = float(row.get("total_cost") or 0)
    return t / q if q else 0

def recipe_lines(recipe_id):
    inv = df("inventory"); lines = df("recipe_lines")
    if inv.empty or lines.empty: return pd.DataFrame()
    lines = lines[lines["recipe_id"] == recipe_id]
    if lines.empty: return pd.DataFrame()
    m = lines.merge(inv, left_on="inventory_id", right_on="id", suffixes=("_line","_inv"))
    m["cost_per_unit"] = m.apply(cpu, axis=1)
    m["line_cost"] = m["amount_used"].astype(float) * m["cost_per_unit"]
    m["enough_inventory"] = m["current_quantity"].astype(float) >= m["amount_used"].astype(float)
    return m

def recipe_row(recipe_id):
    r = df("recipes")
    if r.empty: return None
    r = r[r["id"] == recipe_id]
    return r.iloc[0] if not r.empty else None

st.sidebar.title("The Soap Lab")
page = st.sidebar.radio("Go to", ["Dashboard","Inventory","Fragrance Library","Recipes","Recipe Cost Summary","Can I Make This?","Batch Production","Finished Goods","Ingredient Label Generator","Product Type View","Sales Tracker"])

if page == "Dashboard":
    st.title("The Soap Lab Dashboard")
    inv, recipes, batches, goods, sales = df("inventory"), df("recipes"), df("batches"), df("finished_goods"), df("sales")
    raw_value = 0; finished_value = 0; low = pd.DataFrame()
    if not inv.empty:
        inv["cost_per_unit"] = inv.apply(cpu, axis=1)
        raw_value = (inv["current_quantity"].astype(float) * inv["cost_per_unit"]).sum()
        low = inv[inv["current_quantity"].astype(float) <= inv["reorder_point"].astype(float)]
    if not goods.empty:
        finished_value = (goods["quantity_on_hand"].astype(float) * goods["cost_per_item"].astype(float)).sum()
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Raw Inventory Value", f"${raw_value:,.2f}"); c2.metric("Finished Goods Value", f"${finished_value:,.2f}"); c3.metric("Recipes", len(recipes)); c4.metric("Batches", len(batches))
    st.subheader("Low Stock Alerts")
    if low.empty:
        st.success("No low stock alerts right now.")
    else:
        st.dataframe(low[["item_name","category","current_quantity","unit","reorder_point"]], use_container_width=True)

elif page == "Inventory":
    st.title("Inventory Manager")
    st.caption("Search, view, add, edit, delete, and report on your raw materials, packaging, shipping supplies, and equipment.")

    df = table_df("inventory")

    if not df.empty:
        for col in ["item_name", "category", "subcategory", "supplier", "label_display_name", "notes"]:
            if col not in df.columns:
                df[col] = ""
        for col in ["quantity_purchased", "total_cost", "current_quantity", "reorder_point"]:
            if col not in df.columns:
                df[col] = 0

        df["cost_per_unit"] = df.apply(cost_per_unit, axis=1)
        df["inventory_value"] = df["current_quantity"].astype(float) * df["cost_per_unit"].astype(float)
        df["stock_status"] = df.apply(
            lambda r: "LOW" if float(r.get("current_quantity") or 0) <= float(r.get("reorder_point") or 0) else "OK",
            axis=1
        )

    tab_list, tab_add, tab_manage, tab_reports = st.tabs([
        "Inventory List",
        "Add New",
        "Edit / Delete",
        "Reports"
    ])

    with tab_list:
        st.subheader("Current Inventory")

        c_search, c_filter = st.columns([2, 1])
        search_term = c_search.text_input("Search inventory", placeholder="Search by item, supplier, category, INCI name, or notes...", key="inventory_search")
        category_filter = c_filter.selectbox(
            "Filter by category",
            ["All", "Ingredient", "Fragrance", "Colorant", "Packaging", "Shipping", "Equipment"],
            key="inventory_category_filter"
        )

        display_df = df.copy()

        if not display_df.empty:
            if search_term:
                term = search_term.lower()
                display_df = display_df[
                    display_df["item_name"].fillna("").str.lower().str.contains(term) |
                    display_df["category"].fillna("").str.lower().str.contains(term) |
                    display_df["subcategory"].fillna("").str.lower().str.contains(term) |
                    display_df["supplier"].fillna("").str.lower().str.contains(term) |
                    display_df["label_display_name"].fillna("").str.lower().str.contains(term) |
                    display_df["notes"].fillna("").str.lower().str.contains(term)
                ]

            if category_filter != "All":
                display_df = display_df[display_df["category"] == category_filter]

        if display_df.empty:
            st.info("No inventory items found.")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Items", len(display_df))
            c2.metric("Inventory Value", f"${display_df['inventory_value'].sum():.2f}")
            c3.metric("Low Stock Items", int((display_df["stock_status"] == "LOW").sum()))
            c4.metric("Categories", display_df["category"].nunique())

            show_cols = [
                "id", "item_name", "category", "subcategory", "supplier",
                "current_quantity", "unit", "reorder_point", "stock_status",
                "cost_per_unit", "inventory_value"
            ]
            st.dataframe(
                display_df[show_cols].sort_values(["stock_status", "category", "item_name"]),
                use_container_width=True,
                hide_index=True
            )

            st.info("To edit or delete an item, go to the Edit / Delete tab and select it from the dropdown.")

    with tab_add:
        st.subheader("Add New Inventory Item")

        with st.form("add_inventory", clear_on_submit=False):
            c1, c2, c3 = st.columns(3)
            item_name = c1.text_input("Item Name", key="add_item_name")
            category = c2.selectbox("Category", ["Ingredient", "Fragrance", "Colorant", "Packaging", "Shipping", "Equipment"], key="add_category")
            subcategory = c3.text_input("Subcategory", key="add_subcategory")

            c4, c5, c6 = st.columns(3)
            supplier = c4.text_input("Supplier", key="add_supplier")
            quantity = c5.number_input("Quantity Purchased", min_value=0.0, step=0.01, key="add_quantity")
            unit = c6.selectbox("Unit", ["oz", "lb", "g", "kg", "fl oz", "each"], key="add_unit")

            c7, c8, c9 = st.columns(3)
            total_cost = c7.number_input("Total Cost Paid", min_value=0.0, step=0.01, key="add_total_cost")
            current_quantity = c8.number_input("Current Quantity Left", min_value=0.0, step=0.01, key="add_current_quantity")
            reorder_point = c9.number_input("Reorder Point", min_value=0.0, step=0.01, key="add_reorder_point")

            label_display_name = st.text_input("Label Display / INCI Name", key="add_label_display_name")
            notes = st.text_area("Notes", key="add_notes")
            submitted = st.form_submit_button("Save New Item")

            if submitted:
                if not item_name.strip():
                    st.error("Item Name is required.")
                else:
                    insert_row("inventory", {
                        "item_name": item_name.strip(),
                        "category": category,
                        "subcategory": subcategory.strip(),
                        "supplier": supplier.strip(),
                        "quantity_purchased": quantity,
                        "unit": unit,
                        "total_cost": total_cost,
                        "current_quantity": current_quantity,
                        "reorder_point": reorder_point,
                        "label_display_name": label_display_name.strip(),
                        "notes": notes.strip()
                    })
                    st.success(f"Added {item_name}")
                    st.rerun()

    with tab_manage:
        st.subheader("Edit / Delete Inventory Item")

        if df.empty:
            st.info("Add inventory first, then you can edit it here.")
        else:
            df_edit = df.sort_values("item_name").copy()
            item_options = df_edit["id"].astype(str) + " - " + df_edit["item_name"].fillna("Unnamed Item")
            selected_item = st.selectbox("Select an inventory item", item_options, key="manage_selected_inventory")

            selected_id = int(selected_item.split(" - ")[0])
            selected = df_edit[df_edit["id"] == selected_id].iloc[0]

            cost_unit = cost_per_unit(selected)
            inv_value = float(selected.get("current_quantity") or 0) * cost_unit
            status = "LOW STOCK" if float(selected.get("current_quantity") or 0) <= float(selected.get("reorder_point") or 0) else "OK"

            st.markdown(f"### {selected.get('item_name')}")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Status", status)
            m2.metric("Cost Per Unit", f"${cost_unit:.4f}")
            m3.metric("Quantity Left", f"{float(selected.get('current_quantity') or 0):.2f} {selected.get('unit') or ''}")
            m4.metric("Inventory Value", f"${inv_value:.2f}")

            edit_tab, adjust_tab, delete_tab = st.tabs(["Edit Details", "Quick Quantity Update", "Delete"])

            with edit_tab:
                with st.form("edit_inventory"):
                    c1, c2, c3 = st.columns(3)
                    edit_item_name = c1.text_input("Item Name", value=str(selected.get("item_name") or ""))
                    categories = ["Ingredient", "Fragrance", "Colorant", "Packaging", "Shipping", "Equipment"]
                    units = ["oz", "lb", "g", "kg", "fl oz", "each"]

                    edit_category = c2.selectbox(
                        "Category",
                        categories,
                        index=categories.index(selected.get("category")) if selected.get("category") in categories else 0
                    )
                    edit_subcategory = c3.text_input("Subcategory", value=str(selected.get("subcategory") or ""))

                    c4, c5, c6 = st.columns(3)
                    edit_supplier = c4.text_input("Supplier", value=str(selected.get("supplier") or ""))
                    edit_quantity = c5.number_input("Original Quantity Purchased", min_value=0.0, step=0.01, value=float(selected.get("quantity_purchased") or 0))
                    edit_unit = c6.selectbox(
                        "Unit",
                        units,
                        index=units.index(selected.get("unit")) if selected.get("unit") in units else 0
                    )

                    c7, c8, c9 = st.columns(3)
                    edit_total_cost = c7.number_input("Total Cost Paid", min_value=0.0, step=0.01, value=float(selected.get("total_cost") or 0))
                    edit_current_quantity = c8.number_input("Current Quantity Left", min_value=0.0, step=0.01, value=float(selected.get("current_quantity") or 0))
                    edit_reorder_point = c9.number_input("Reorder Point", min_value=0.0, step=0.01, value=float(selected.get("reorder_point") or 0))

                    edit_label = st.text_input("Label Display / INCI Name", value=str(selected.get("label_display_name") or ""))
                    edit_notes = st.text_area("Notes", value=str(selected.get("notes") or ""))

                    save_edit = st.form_submit_button("Save Changes")

                    if save_edit:
                        update_row("inventory", selected_id, {
                            "item_name": edit_item_name.strip(),
                            "category": edit_category,
                            "subcategory": edit_subcategory.strip(),
                            "supplier": edit_supplier.strip(),
                            "quantity_purchased": edit_quantity,
                            "unit": edit_unit,
                            "total_cost": edit_total_cost,
                            "current_quantity": edit_current_quantity,
                            "reorder_point": edit_reorder_point,
                            "label_display_name": edit_label.strip(),
                            "notes": edit_notes.strip()
                        })
                        st.success(f"Updated {edit_item_name}")
                        st.rerun()

            with adjust_tab:
                st.write("Use this when you only need to update how much you have left.")
                with st.form("quick_quantity_update"):
                    new_qty = st.number_input(
                        "New Current Quantity Left",
                        min_value=0.0,
                        step=0.01,
                        value=float(selected.get("current_quantity") or 0)
                    )
                    quick_note = st.text_area("Optional note about this adjustment", placeholder="Example: Used 12 oz in batch, found extra bottle, corrected count...")
                    quick_save = st.form_submit_button("Update Quantity Left")

                    if quick_save:
                        existing_notes = str(selected.get("notes") or "")
                        if quick_note.strip():
                            updated_notes = existing_notes + f"\nQuantity adjustment: {quick_note.strip()}"
                        else:
                            updated_notes = existing_notes
                        update_row("inventory", selected_id, {
                            "current_quantity": new_qty,
                            "notes": updated_notes
                        })
                        st.success("Quantity updated.")
                        st.rerun()

            with delete_tab:
                st.error("Delete is permanent. Only delete test items or inventory you are sure you do not need.")
                confirm_text = st.text_input("Type DELETE to confirm")
                if confirm_text == "DELETE":
                    if st.button("Permanently Delete This Inventory Item"):
                        try:
                            delete_row("inventory", selected_id)
                            st.success("Inventory item deleted.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not delete this item. It may be used in a recipe. Error: {e}")

    with tab_reports:
        st.subheader("Inventory Reports")

        if df.empty:
            st.info("No inventory available for reports yet.")
        else:
            report_type = st.selectbox(
                "Choose report",
                [
                    "Low Stock / Reorder Needed",
                    "Lowest Stock First",
                    "Highest Stock First",
                    "Highest Inventory Value",
                    "Lowest Inventory Value",
                    "By Category Summary",
                    "By Supplier Summary"
                ]
            )

            if report_type == "Low Stock / Reorder Needed":
                report = df[df["current_quantity"].astype(float) <= df["reorder_point"].astype(float)].copy()
                st.write("Items where current quantity is at or below reorder point.")
                if report.empty:
                    st.success("Nothing needs reordering right now.")
                else:
                    st.dataframe(report[["item_name", "category", "supplier", "current_quantity", "unit", "reorder_point"]], use_container_width=True, hide_index=True)

            elif report_type == "Lowest Stock First":
                report = df.sort_values("current_quantity", ascending=True)
                st.dataframe(report[["item_name", "category", "supplier", "current_quantity", "unit", "reorder_point"]], use_container_width=True, hide_index=True)

            elif report_type == "Highest Stock First":
                report = df.sort_values("current_quantity", ascending=False)
                st.dataframe(report[["item_name", "category", "supplier", "current_quantity", "unit", "reorder_point"]], use_container_width=True, hide_index=True)

            elif report_type == "Highest Inventory Value":
                report = df.sort_values("inventory_value", ascending=False)
                st.dataframe(report[["item_name", "category", "supplier", "current_quantity", "unit", "cost_per_unit", "inventory_value"]], use_container_width=True, hide_index=True)

            elif report_type == "Lowest Inventory Value":
                report = df.sort_values("inventory_value", ascending=True)
                st.dataframe(report[["item_name", "category", "supplier", "current_quantity", "unit", "cost_per_unit", "inventory_value"]], use_container_width=True, hide_index=True)

            elif report_type == "By Category Summary":
                report = df.groupby("category", dropna=False).agg(
                    item_count=("id", "count"),
                    total_inventory_value=("inventory_value", "sum"),
                    low_stock_items=("stock_status", lambda x: int((x == "LOW").sum()))
                ).reset_index()
                st.dataframe(report, use_container_width=True, hide_index=True)

            elif report_type == "By Supplier Summary":
                report = df.groupby("supplier", dropna=False).agg(
                    item_count=("id", "count"),
                    total_inventory_value=("inventory_value", "sum")
                ).reset_index().sort_values("total_inventory_value", ascending=False)
                st.dataframe(report, use_container_width=True, hide_index=True)

elif page == "Fragrance Library":
    st.title("Fragrance Library")
    with st.form("fragrance"):
        c1,c2,c3 = st.columns(3)
        name = c1.text_input("Fragrance Name"); supplier = c2.text_input("Supplier"); qty = c3.number_input("Quantity oz", min_value=0.0, step=.01)
        c4,c5,c6 = st.columns(3)
        total = c4.number_input("Total Cost", min_value=0.0, step=.01); vanillin = c5.text_input("Vanillin %"); ifra = c6.text_input("IFRA Notes")
        cp = st.text_area("Cold Process / Cure Notes"); s = st.slider("Strength Rating",1,5,3); o = st.slider("Overall Rating",1,5,3); notes = st.text_area("Other Notes")
        if st.form_submit_button("Save Fragrance") and name:
            insert("fragrances", {"fragrance_name":name,"supplier":supplier,"quantity_oz":qty,"total_cost":total,"vanillin":vanillin,"ifra_notes":ifra,"cp_notes":cp,"strength_rating":s,"overall_rating":o,"notes":notes}); st.rerun()
    f = df("fragrances")
    if not f.empty: st.dataframe(f.sort_values("fragrance_name"), use_container_width=True)

elif page == "Recipes":
    st.title("Recipe Builder")
    inv = df("inventory")
    with st.form("recipe"):
        name = st.text_input("Recipe Name"); ptype = st.selectbox("Product Type", ["Soap","Bath Bomb","Shower Steamer","Body Butter","Body Oil","Lotion","Cuticle Oil","Melt & Pour"])
        made = st.number_input("Number Made", min_value=1, step=1); retail = st.number_input("Retail Price Per Item", min_value=0.0, step=.01); cure = st.number_input("Cure / Ready Days", min_value=0, value=42, step=1); notes = st.text_area("Recipe Notes")
        if st.form_submit_button("Create Recipe") and name:
            insert("recipes", {"recipe_name":name,"product_type":ptype,"bars_made":made,"retail_price":retail,"cure_days":cure,"notes":notes}); st.rerun()
    recipes = df("recipes")
    if not recipes.empty:
        choice = st.selectbox("Choose Recipe", recipes["id"].astype(str)+" - "+recipes["recipe_name"]); rid = int(choice.split(" - ")[0])
        if not inv.empty:
            with st.form("line"):
                inv = inv.sort_values("item_name"); item = st.selectbox("Inventory Item", inv["id"].astype(str)+" - "+inv["item_name"]); iid = int(item.split(" - ")[0])
                amt = st.number_input("Amount Used", min_value=0.0, step=.01); unit = st.selectbox("Unit Used", ["oz","g","each"]); incl = st.checkbox("Include on ingredient label", value=True); override = st.text_input("Label Name Override")
                if st.form_submit_button("Add Ingredient Line"):
                    insert("recipe_lines", {"recipe_id":rid,"inventory_id":iid,"amount_used":amt,"unit":unit,"include_on_label":incl,"label_name_override":override}); st.rerun()
        lines = recipe_lines(rid)
        if not lines.empty: st.dataframe(lines[["item_name","category","amount_used","unit_line","line_cost"]], use_container_width=True)

elif page == "Recipe Cost Summary":
    st.title("Recipe Cost Summary")
    recipes = df("recipes")
    if recipes.empty: st.warning("Create a recipe first.")
    else:
        choice = st.selectbox("Choose Recipe", recipes["id"].astype(str)+" - "+recipes["recipe_name"]); rid = int(choice.split(" - ")[0]); r = recipe_row(rid); lines = recipe_lines(rid)
        if lines.empty: st.info("No ingredients added yet.")
        else:
            total = lines["line_cost"].sum(); made = int(r["bars_made"] or 1); cpi = total/made; retail = float(r["retail_price"] or 0); profit = retail-cpi; margin = profit/retail*100 if retail else 0
            c1,c2,c3,c4 = st.columns(4); c1.metric("Total Batch Cost", f"${total:.2f}"); c2.metric("Cost Per Item", f"${cpi:.2f}"); c3.metric("Profit Per Item", f"${profit:.2f}"); c4.metric("Margin", f"{margin:.1f}%")
            st.dataframe(lines[["item_name","category","amount_used","unit_line","line_cost"]], use_container_width=True)

elif page == "Can I Make This?":
    st.title("Can I Make This?")
    recipes = df("recipes")
    if recipes.empty: st.warning("Create a recipe first.")
    else:
        choice = st.selectbox("Choose Recipe", recipes["id"].astype(str)+" - "+recipes["recipe_name"]); rid = int(choice.split(" - ")[0]); lines = recipe_lines(rid)
        if lines.empty: st.info("No ingredients added yet.")
        else:
            batches = [(float(x.current_quantity)//float(x.amount_used)) if float(x.amount_used or 0) else 0 for x in lines.itertuples()]
            st.success(f"Yes — maximum full batches possible: {int(min(batches))}") if all(lines["enough_inventory"]) else st.error("Not enough inventory for this recipe.")
            st.dataframe(lines[["item_name","amount_used","unit_line","current_quantity","enough_inventory"]], use_container_width=True)

elif page == "Batch Production":
    st.title("Batch Production")
    recipes = df("recipes")
    if recipes.empty: st.warning("Create a recipe first.")
    else:
        choice = st.selectbox("Choose Recipe", recipes["id"].astype(str)+" - "+recipes["recipe_name"]); rid = int(choice.split(" - ")[0]); r = recipe_row(rid); lines = recipe_lines(rid)
        c1,c2 = st.columns(2); batch = c1.text_input("Batch Number", value=f"{str(r['product_type'])[:2].upper()}-{date.today().strftime('%Y%m%d')}"); made_date = c2.date_input("Date Made", value=date.today())
        cure_date = made_date + timedelta(days=int(r["cure_days"] or 0)); qty = st.number_input("Quantity Made", min_value=1, value=int(r["bars_made"] or 1)); notes = st.text_area("Batch Notes")
        total = float(lines["line_cost"].sum()) if not lines.empty else 0; cpi = total/qty if qty else 0
        st.metric("Batch Cost", f"${total:.2f}"); st.metric("Cost Per Item", f"${cpi:.2f}"); st.write(f"Ready/Cure Date: **{cure_date}**")
        if st.button("Save Batch and Add to Finished Goods"):
            res = insert("batches", {"batch_number":batch,"recipe_id":rid,"date_made":str(made_date),"cure_date":str(cure_date),"quantity_made":qty,"batch_cost":total,"cost_per_item":cpi,"notes":notes})
            bid = res.data[0]["id"] if res.data else None
            insert("finished_goods", {"product_name":r["recipe_name"],"product_type":r["product_type"],"recipe_id":rid,"batch_id":bid,"quantity_on_hand":qty,"cost_per_item":cpi,"retail_price":float(r["retail_price"] or 0),"notes":notes}); st.rerun()
        ingredients = "\n".join([f"- {x.item_name}: {x.amount_used} {x.unit_line}" for x in lines.itertuples()]) if not lines.empty else ""
        st.text_area("Printable Batch Card", value=f"THE SOAP LAB BATCH CARD\n\nBatch: {batch}\nRecipe: {r['recipe_name']}\nDate Made: {made_date}\nReady Date: {cure_date}\nQuantity: {qty}\nBatch Cost: ${total:.2f}\nCost Per Item: ${cpi:.2f}\n\nIngredients:\n{ingredients}\n\nNotes:\n{notes}", height=350)

elif page == "Finished Goods":
    st.title("Finished Goods Inventory")
    goods = df("finished_goods")
    if goods.empty: st.info("No finished goods yet.")
    else:
        goods["total_value"] = goods["quantity_on_hand"].astype(float)*goods["cost_per_item"].astype(float)
        st.dataframe(goods.sort_values("product_name"), use_container_width=True)

elif page == "Ingredient Label Generator":
    st.title("Ingredient Label Generator")
    recipes = df("recipes")
    if recipes.empty: st.warning("Create a recipe first.")
    else:
        choice = st.selectbox("Choose Recipe", recipes["id"].astype(str)+" - "+recipes["recipe_name"]); rid = int(choice.split(" - ")[0]); r = recipe_row(rid); lines = recipe_lines(rid)
        if lines.empty: st.info("No ingredients added yet.")
        else:
            label_lines = lines[lines["include_on_label"] == True].sort_values("amount_used", ascending=False)
            names=[]
            for _, row in label_lines.iterrows():
                names.append(row.get("label_name_override") or row.get("label_display_name") or row.get("item_name"))
            unique=[]
            for n in names:
                if n and n not in unique: unique.append(n)
            statement = "Ingredients: " + ", ".join(unique) + "."
            st.text_area("Generated Ingredient Statement", value=statement, height=120)
            st.text_area("Simple Label Template", value=f"{r['recipe_name']}\n\n{statement}\n\nNet Wt: ______\nMade by The Soap Lab / Fizzebath", height=250)

elif page == "Product Type View":
    st.title("Product Type View")
    ptype = st.selectbox("Product Type", ["Soap","Bath Bomb","Shower Steamer","Body Butter","Body Oil","Lotion","Cuticle Oil","Melt & Pour"])
    recipes, goods = df("recipes"), df("finished_goods")
    if not recipes.empty: st.dataframe(recipes[recipes["product_type"] == ptype], use_container_width=True)
    if not goods.empty: st.dataframe(goods[goods["product_type"] == ptype], use_container_width=True)

elif page == "Sales Tracker":
    st.title("Sales Tracker")
    with st.form("sale"):
        c1,c2,c3 = st.columns(3); sale_date = c1.date_input("Sale Date", value=date.today()); channel = c2.selectbox("Channel", ["Etsy","Shopify","Craft Show","Facebook","Direct","Other"]); product = c3.text_input("Product Name")
        c4,c5,c6 = st.columns(3); qty = c4.number_input("Quantity Sold", min_value=1, step=1); price = c5.number_input("Sale Price Each", min_value=0.0, step=.01); fees = c6.number_input("Fees", min_value=0.0, step=.01)
        ship = st.number_input("Shipping / Packing Material Cost", min_value=0.0, step=.01); cname = st.text_input("Customer Name"); email = st.text_input("Customer Email"); notes = st.text_area("Notes")
        if st.form_submit_button("Save Sale"):
            insert("sales", {"sale_date":str(sale_date),"channel":channel,"product_name":product,"quantity_sold":qty,"sale_price_each":price,"fees":fees,"shipping_material_cost":ship,"customer_name":cname,"customer_email":email,"notes":notes}); st.rerun()
    sales = df("sales")
    if not sales.empty: st.dataframe(sales.sort_values("sale_date", ascending=False), use_container_width=True)
