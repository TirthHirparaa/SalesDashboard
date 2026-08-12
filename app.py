import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Sales Analytics Dashboard")

st.write("Analyze sales performance with interactive charts and filters.")

df = pd.read_excel("sales.xls")

df["Order Date"] = pd.to_datetime(df["Order Date"])

st.sidebar.header("Filters")

min_date = df["Order Date"].min()
max_date = df["Order Date"].max()

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

filtered_df = df[
    (df["Order Date"] >= pd.to_datetime(start_date)) &
    (df["Order Date"] <= pd.to_datetime(end_date))
]

regions = st.sidebar.multiselect(
    "Select Region",
    options=filtered_df["Region"].unique(),
    default=filtered_df["Region"].unique()
)

filtered_df = filtered_df[
    filtered_df["Region"].isin(regions)
]

states = st.sidebar.multiselect(
    "Select State",
    options=filtered_df["State"].unique(),
    default=filtered_df["State"].unique()
)

filtered_df = filtered_df[
    filtered_df["State"].isin(states)
]

categories = st.sidebar.multiselect(
    "Select Category",
    options=filtered_df["Category"].unique(),
    default=filtered_df["Category"].unique()
)

filtered_df = filtered_df[
    filtered_df["Category"].isin(categories)
]

total_sales = filtered_df["Sales"].sum()

total_profit = filtered_df["Profit"].sum()

total_orders = filtered_df.shape[0]

total_customers = filtered_df["Customer Name"].nunique()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💰 Total Sales",
    f"${total_sales:,.0f}"
)

col2.metric(
    "📈 Total Profit",
    f"${total_profit:,.0f}"
)

col3.metric(
    "🛒 Orders",
    total_orders
)

col4.metric(
    "👥 Customers",
    total_customers
)

st.divider()

st.subheader("📄 Sales Dataset")

st.dataframe(
    filtered_df,
    use_container_width=True
)

st.divider()


st.subheader("📊 Sales by Category")

sales_category = (
    filtered_df.groupby("Category")["Sales"]
    .sum()
    .reset_index()
)

fig1 = px.bar(
    sales_category,
    x="Category",
    y="Sales",
    color="Category",
    text_auto=".2s",
    title="Category-wise Sales"
)

st.plotly_chart(fig1, use_container_width=True)

st.subheader("🥧 Profit Distribution")

profit_category = (
    filtered_df.groupby("Category")["Profit"]
    .sum()
    .reset_index()
)

fig2 = px.pie(
    profit_category,
    values="Profit",
    names="Category",
    hole=0.4
)

st.plotly_chart(fig2, use_container_width=True)

st.subheader("📈 Monthly Sales Trend")

filtered_df["Month"] = (
    filtered_df["Order Date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_sales = (
    filtered_df.groupby("Month")["Sales"]
    .sum()
    .reset_index()
)

fig3 = px.line(
    monthly_sales,
    x="Month",
    y="Sales",
    markers=True,
    title="Monthly Sales Trend"
)

st.plotly_chart(fig3, use_container_width=True)

st.subheader("🔥 Sales by Region & Category")

heatmap = filtered_df.pivot_table(
    values="Sales",
    index="Region",
    columns="Category",
    aggfunc="sum",
    fill_value=0
)

st.dataframe(
    heatmap.style.format("${:,.0f}"),
    use_container_width=True
)

st.subheader("🏆 Top 10 Products")

top_products = (
    filtered_df.groupby("Product Name")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig4 = px.bar(
    top_products,
    x="Sales",
    y="Product Name",
    orientation="h",
    color="Sales",
    title="Top 10 Products"
)

fig4.update_layout(yaxis={'categoryorder':'total ascending'})

st.plotly_chart(fig4, use_container_width=True)

st.subheader("👥 Top 10 Customers")

top_customers = (
    filtered_df.groupby("Customer Name")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig5 = px.bar(
    top_customers,
    x="Sales",
    y="Customer Name",
    orientation="h",
    color="Sales",
    title="Top Customers"
)

fig5.update_layout(yaxis={'categoryorder':'total ascending'})

st.plotly_chart(fig5, use_container_width=True)

st.subheader("💡 Business Insights")

highest_region = (
    filtered_df.groupby("Region")["Sales"]
    .sum()
    .idxmax()
)

best_category = (
    filtered_df.groupby("Category")["Sales"]
    .sum()
    .idxmax()
)

best_product = (
    filtered_df.groupby("Product Name")["Profit"]
    .sum()
    .idxmax()
)

highest_state = (
    filtered_df.groupby("State")["Sales"]
    .sum()
    .idxmax()
)

avg_order = filtered_df["Sales"].mean()

profit_margin = (
    filtered_df["Profit"].sum() /
    filtered_df["Sales"].sum()
) * 100

st.success(f"🏆 Highest Sales Region : **{highest_region}**")
st.success(f"📦 Best Selling Category : **{best_category}**")
st.success(f"⭐ Most Profitable Product : **{best_product}**")
st.success(f"📍 Highest Sales State : **{highest_state}**")
st.success(f"💰 Average Order Value : **${avg_order:.2f}**")
st.success(f"📈 Profit Margin : **{profit_margin:.2f}%**")

st.subheader("📋 Summary Statistics")

st.dataframe(filtered_df.describe())

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Filtered Data (CSV)",
    data=csv,
    file_name="filtered_sales.csv",
    mime="text/csv"
)

st.markdown("---")

st.markdown(
    """
    <center>
    <h5>📊 Sales Analytics Dashboard</h5>
    <p>Built with ❤️ using Python, Streamlit, Pandas & Plotly</p>
    </center>
    """,
    unsafe_allow_html=True
)