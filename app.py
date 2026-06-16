import streamlit as st
import pandas as pd
from datetime import date, timedelta
from supabase import create_client

st.set_page_config(page_title="The Soap Lab", layout="wide")
PINK = "#C989A3"; DARK = "#8F5268"; LIGHT = "#F7E6EC"
st.markdown(f"""
<style>
.stApp {{background:#fff9fb;}}
h1,h2,h3 {{color:{DARK};}}
section[data-testid="stSidebar"] {{background-color:{LIGHT};}}
div[data-testid="stMetric"] {{background-color:{LIGHT};padding:16px;border-radius:16px;border:1px solid #e5b8c8;}}
.stButton button {{background-color:{PINK};color:white;border-radius:10px;border:none;}}
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
    st.success("No low stock alerts right now.") if low.empty else st.dataframe(low[["item_name","category","current_quantity","unit","reorder_point"]], use_container_width=True)

elif page == "Inventory":
    st.title("Inventory Manager")
    with st.form("inventory"):
        c1,c2,c3 = st.columns(3)
        item_name = c1.text_input("Item Name"); category = c2.selectbox("Category", ["Ingredient","Fragrance","Colorant","Packaging","Shipping","Equipment"]); subcategory = c3.text_input("Subcategory")
        c4,c5,c6 = st.columns(3)
        supplier = c4.text_input("Supplier"); qty = c5.number_input("Quantity Purchased", min_value=0.0, step=.01); unit = c6.selectbox("Unit", ["oz","lb","g","kg","fl oz","each"])
        c7,c8,c9 = st.columns(3)
        total = c7.number_input("Total Cost Paid", min_value=0.0, step=.01); current = c8.number_input("Current Quantity", min_value=0.0, step=.01); reorder = c9.number_input("Reorder Point", min_value=0.0, step=.01)
        label = st.text_input("Label Display / INCI Name"); notes = st.text_area("Notes")
        if st.form_submit_button("Save Item") and item_name:
            insert("inventory", {"item_name":item_name,"category":category,"subcategory":subcategory,"supplier":supplier,"quantity_purchased":qty,"unit":unit,"total_cost":total,"current_quantity":current,"reorder_point":reorder,"label_display_name":label,"notes":notes}); st.rerun()
    inv = df("inventory")
    if not inv.empty:
        inv["cost_per_unit"] = inv.apply(cpu, axis=1); st.dataframe(inv.sort_values(["category","item_name"]), use_container_width=True)

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
