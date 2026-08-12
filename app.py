import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown('<p class="dashboard-title">📊 Sales Analytics Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="dashboard-subtitle">Analyze sales performance with interactive charts and filters.</p>', unsafe_allow_html=True)

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

# --- KPI METRIC CARDS ---
col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
col2.metric("📈 Total Profit", f"${total_profit:,.0f}")
col3.metric("🛒 Orders", total_orders)
col4.metric("👥 Customers", total_customers)

st.divider()

# --- HELPER TO STYLE PLOTLY FIGURES ---
def style_plotly_fig(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="Inter, sans-serif",
            size=11,
            color="#E6EDF3"
        ),
        title_font=dict(
            family="Inter, sans-serif",
            size=14,
            color="#F3F4F6"
        ),
        margin=dict(l=30, r=30, t=50, b=30),
    )
    # Check if axes exist in the layout structure before updating them
    if fig.data and hasattr(fig.data[0], 'x') and hasattr(fig, 'update_xaxes'):
        fig.update_xaxes(
            showgrid=False,
            gridcolor='rgba(255,255,255,0.05)',
            zeroline=False,
            tickfont=dict(color="#A0AEC0")
        )
        fig.update_yaxes(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            zeroline=False,
            tickfont=dict(color="#A0AEC0")
        )
    return fig

# --- ROW 2: Category Analysis ---
cat_col1, cat_col2 = st.columns(2)

with cat_col1:
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
        color_discrete_sequence=['#6C5DD3', '#00FFA3', '#FF6B6B']
    )
    style_plotly_fig(fig1)
    st.plotly_chart(fig1, use_container_width=True)

with cat_col2:
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
        hole=0.4,
        color_discrete_sequence=['#6C5DD3', '#00FFA3', '#FF6B6B']
    )
    style_plotly_fig(fig2)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# --- ROW 3: Trends & Segments ---
trend_col1, trend_col2 = st.columns(2)

with trend_col1:
    st.subheader("📈 Monthly Sales Trend")
    temp_df = filtered_df.copy()
    temp_df["Month"] = temp_df["Order Date"].dt.to_period("M").astype(str)
    monthly_sales = (
        temp_df.groupby("Month")["Sales"]
        .sum()
        .reset_index()
    )
    fig3 = px.line(
        monthly_sales,
        x="Month",
        y="Sales",
        markers=True
    )
    fig3.update_traces(
        line_color="#00FFA3",
        marker=dict(color="#6C5DD3", size=8, line=dict(color="#00FFA3", width=2))
    )
    style_plotly_fig(fig3)
    st.plotly_chart(fig3, use_container_width=True)

with trend_col2:
    st.subheader("🔥 Sales by Region & Category")
    heatmap = filtered_df.pivot_table(
        values="Sales",
        index="Region",
        columns="Category",
        aggfunc="sum",
        fill_value=0
    )
    st.dataframe(
        heatmap.style.format("${:,.0f}")
        .background_gradient(cmap="Purples", axis=None),
        use_container_width=True
    )

st.divider()

# --- ROW 4: Rankings ---
rank_col1, rank_col2 = st.columns(2)

with rank_col1:
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
        color_continuous_scale=['#151A22', '#6C5DD3', '#00FFA3']
    )
    style_plotly_fig(fig4)
    fig4.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
    st.plotly_chart(fig4, use_container_width=True)

with rank_col2:
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
        color_continuous_scale=['#151A22', '#6C5DD3', '#00FFA3']
    )
    style_plotly_fig(fig5)
    fig5.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
    st.plotly_chart(fig5, use_container_width=True)

st.divider()

# --- ROW 5: Insights & Stats ---
info_col1, info_col2 = st.columns(2)

with info_col1:
    st.subheader("💡 Business Insights")
    
    if not filtered_df.empty:
        highest_region = filtered_df.groupby("Region")["Sales"].sum().idxmax()
        best_category = filtered_df.groupby("Category")["Sales"].sum().idxmax()
        best_product = filtered_df.groupby("Product Name")["Profit"].sum().idxmax()
        highest_state = filtered_df.groupby("State")["Sales"].sum().idxmax()
        avg_order = filtered_df["Sales"].mean()
        profit_margin = (filtered_df["Profit"].sum() / filtered_df["Sales"].sum()) * 100
    else:
        highest_region = "N/A"
        best_category = "N/A"
        best_product = "N/A"
        highest_state = "N/A"
        avg_order = 0
        profit_margin = 0

    st.success(f"🏆 Highest Sales Region : **{highest_region}**")
    st.success(f"📦 Best Selling Category : **{best_category}**")
    st.success(f"⭐ Most Profitable Product : **{best_product}**")
    st.success(f"📍 Highest Sales State : **{highest_state}**")
    st.success(f"💰 Average Order Value : **${avg_order:.2f}**")
    st.success(f"📈 Profit Margin : **{profit_margin:.2f}%**")

with info_col2:
    st.subheader("📋 Summary Statistics")
    if not filtered_df.empty:
        st.dataframe(filtered_df.describe(), use_container_width=True)
    else:
        st.warning("No data to generate statistics.")

st.divider()

# --- ROW 6: Dataset & Export ---
st.subheader("📄 Sales Dataset")
st.dataframe(
    filtered_df,
    use_container_width=True
)

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