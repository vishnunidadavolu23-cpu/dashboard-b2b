import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="B2B Order Fulfillment Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d2e 0%, #0f1117 100%);
        border-right: 1px solid #2d3748;
    }
    
    /* KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #1a1d2e 0%, #252841 100%);
        border: 1px solid #2d3748;
        border-radius: 16px;
        padding: 24px 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: transform 0.2s;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .kpi-card:hover { transform: translateY(-2px); }
    .kpi-title {
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #718096;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 32px;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 6px;
    }
    .kpi-sub {
        font-size: 11px;
        color: #718096;
    }
    
    /* Insight cards */
    .insight-card {
        background: #1a1d2e;
        border-left: 4px solid;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .insight-title { font-weight: 700; font-size: 14px; margin-bottom: 6px; }
    .insight-body { font-size: 13px; color: #a0aec0; line-height: 1.5; }
    
    /* Section headers */
    .section-header {
        font-size: 18px;
        font-weight: 700;
        color: #e2e8f0;
        margin: 8px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #2d3748;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── Load & Prepare Data ───────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("B2BOrder_Dataset.xlsx")
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    df["Delivery_Date"] = pd.to_datetime(df["Delivery_Date"])
    df["Delivery_Days"] = (df["Delivery_Date"] - df["Order_Date"]).dt.days
    df["Month"] = df["Order_Date"].dt.to_period("M").astype(str)
    return df

df = load_data()

# ── Sidebar Filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filters")
    st.markdown("---")

    regions = ["All"] + sorted(df["Region"].unique().tolist())
    selected_region = st.selectbox("🌍 Region", regions)

    categories = ["All"] + sorted(df["Product_Category"].unique().tolist())
    selected_category = st.selectbox("📦 Product Category", categories)

    statuses = ["All"] + sorted(df["Status"].unique().tolist())
    selected_status = st.selectbox("🔄 Order Status", statuses)

    st.markdown("---")
    st.markdown("### 📅 Date Range")
    min_date = df["Order_Date"].min().date()
    max_date = df["Order_Date"].max().date()
    date_range = st.date_input(
        "Select range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    st.markdown("---")
    st.markdown(
        "<div style='color:#718096;font-size:11px;text-align:center;'>B2B Order Fulfillment<br>Analytics Dashboard v1.0</div>",
        unsafe_allow_html=True,
    )

# ── Apply Filters ─────────────────────────────────────────────────────────────
filtered = df.copy()
if selected_region != "All":
    filtered = filtered[filtered["Region"] == selected_region]
if selected_category != "All":
    filtered = filtered[filtered["Product_Category"] == selected_category]
if selected_status != "All":
    filtered = filtered[filtered["Status"] == selected_status]
if len(date_range) == 2:
    filtered = filtered[
        (filtered["Order_Date"] >= pd.Timestamp(date_range[0]))
        & (filtered["Order_Date"] <= pd.Timestamp(date_range[1]))
    ]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='font-size:26px;font-weight:800;color:#e2e8f0;margin-bottom:4px;'>"
    "📦 B2B Order Fulfillment Analytics Dashboard</h1>"
    "<p style='color:#718096;font-size:13px;margin-bottom:20px;'>"
    f"Showing {len(filtered):,} of {len(df):,} orders · Last updated: {df['Order_Date'].max().strftime('%b %d, %Y')}</p>",
    unsafe_allow_html=True,
)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)

total_orders = len(filtered)
completed = len(filtered[filtered["Status"] == "Completed"])
pending = len(filtered[filtered["Status"] == "Pending"])
avg_delivery = filtered["Delivery_Days"].mean() if len(filtered) > 0 else 0

comp_pct = (completed / total_orders * 100) if total_orders > 0 else 0
pend_pct = (pending / total_orders * 100) if total_orders > 0 else 0

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Orders</div>
        <div class="kpi-value" style="color:#60a5fa;">{total_orders:,}</div>
        <div class="kpi-sub">📊 All selected orders</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Completed Orders</div>
        <div class="kpi-value" style="color:#34d399;">{completed:,}</div>
        <div class="kpi-sub">✅ {comp_pct:.1f}% completion rate</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Pending Orders</div>
        <div class="kpi-value" style="color:#fbbf24;">{pending:,}</div>
        <div class="kpi-sub">⏳ {pend_pct:.1f}% of total orders</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Avg Delivery Time</div>
        <div class="kpi-value" style="color:#f87171;">{avg_delivery:.1f} days</div>
        <div class="kpi-sub">🚚 Average across filtered orders</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Orders by Region + Delivery Time Analysis ─────────────────────────
CHART_BG = "#1a1d2e"
GRID_COLOR = "#2d3748"
TEXT_COLOR = "#e2e8f0"
PALETTE = ["#60a5fa", "#34d399", "#fbbf24", "#f87171", "#a78bfa"]

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">🌍 Orders by Region</div>', unsafe_allow_html=True)
    region_data = (
        filtered.groupby(["Region", "Status"])
        .size()
        .reset_index(name="Count")
    )
    if not region_data.empty:
        fig1 = px.bar(
            region_data,
            x="Region",
            y="Count",
            color="Status",
            barmode="group",
            color_discrete_map={
                "Completed": "#34d399",
                "Pending": "#fbbf24",
                "Delayed": "#f87171",
            },
            template="plotly_dark",
        )
        fig1.update_layout(
            plot_bgcolor=CHART_BG,
            paper_bgcolor=CHART_BG,
            font_color=TEXT_COLOR,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            xaxis=dict(gridcolor=GRID_COLOR),
            yaxis=dict(gridcolor=GRID_COLOR),
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No data for selected filters.")

with col2:
    st.markdown('<div class="section-header">⏱️ Delivery Time Analysis</div>', unsafe_allow_html=True)
    delivery_region = (
        filtered.groupby("Region")["Delivery_Days"]
        .agg(["mean", "min", "max", "std"])
        .reset_index()
        .round(2)
    )
    if not delivery_region.empty:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=delivery_region["Region"],
            y=delivery_region["mean"],
            name="Avg Days",
            marker_color=PALETTE[0],
            error_y=dict(
                type="data",
                array=delivery_region["std"].fillna(0),
                visible=True,
                color="#718096",
            ),
        ))
        fig2.add_trace(go.Scatter(
            x=delivery_region["Region"],
            y=delivery_region["max"],
            name="Max Days",
            mode="markers",
            marker=dict(symbol="diamond", size=10, color="#f87171"),
        ))
        fig2.update_layout(
            plot_bgcolor=CHART_BG,
            paper_bgcolor=CHART_BG,
            font_color=TEXT_COLOR,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            xaxis=dict(gridcolor=GRID_COLOR),
            yaxis=dict(gridcolor=GRID_COLOR, title="Days"),
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data for selected filters.")

# ── Row 2: Order Value Trend + Status Distribution ────────────────────────────
col3, col4 = st.columns([3, 2])

with col3:
    st.markdown('<div class="section-header">💰 Order Value Trend</div>', unsafe_allow_html=True)
    monthly = (
        filtered.groupby("Month")
        .agg(Total_Value=("Order_Value", "sum"), Order_Count=("Order_ID", "count"))
        .reset_index()
        .sort_values("Month")
    )
    if not monthly.empty:
        fig3 = make_subplots(specs=[[{"secondary_y": True}]])
        fig3.add_trace(
            go.Bar(
                x=monthly["Month"],
                y=monthly["Total_Value"],
                name="Total Value (₹)",
                marker_color="#60a5fa",
                opacity=0.8,
            ),
            secondary_y=False,
        )
        fig3.add_trace(
            go.Scatter(
                x=monthly["Month"],
                y=monthly["Order_Count"],
                name="Order Count",
                mode="lines+markers",
                line=dict(color="#fbbf24", width=2),
                marker=dict(size=5),
            ),
            secondary_y=True,
        )
        fig3.update_layout(
            plot_bgcolor=CHART_BG,
            paper_bgcolor=CHART_BG,
            font_color=TEXT_COLOR,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            xaxis=dict(gridcolor=GRID_COLOR, tickangle=-30),
            yaxis=dict(gridcolor=GRID_COLOR, title="Order Value (₹)"),
            yaxis2=dict(title="Order Count", showgrid=False),
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No data for selected filters.")

with col4:
    st.markdown('<div class="section-header">📊 Status Distribution</div>', unsafe_allow_html=True)
    status_data = filtered["Status"].value_counts().reset_index()
    status_data.columns = ["Status", "Count"]
    if not status_data.empty:
        color_map = {"Completed": "#34d399", "Pending": "#fbbf24", "Delayed": "#f87171"}
        fig4 = go.Figure(data=[go.Pie(
            labels=status_data["Status"],
            values=status_data["Count"],
            hole=0.55,
            marker_colors=[color_map.get(s, "#718096") for s in status_data["Status"]],
            textinfo="label+percent",
            textfont_size=12,
        )])
        fig4.update_layout(
            plot_bgcolor=CHART_BG,
            paper_bgcolor=CHART_BG,
            font_color=TEXT_COLOR,
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            annotations=[dict(
                text=f"{total_orders}<br><span style='font-size:10px'>Orders</span>",
                x=0.5, y=0.5, font_size=16, showarrow=False, font_color=TEXT_COLOR
            )],
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No data for selected filters.")

# ── Row 3: Category Performance ───────────────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.markdown('<div class="section-header">🏷️ Order Value by Product Category</div>', unsafe_allow_html=True)
    cat_value = (
        filtered.groupby("Product_Category")["Order_Value"]
        .agg(["sum", "mean", "count"])
        .reset_index()
        .sort_values("sum", ascending=True)
        .rename(columns={"sum": "Total", "mean": "Average", "count": "Orders"})
    )
    if not cat_value.empty:
        fig5 = go.Figure(go.Bar(
            x=cat_value["Total"],
            y=cat_value["Product_Category"],
            orientation="h",
            marker=dict(
                color=cat_value["Total"],
                colorscale=[[0, "#1a3a5c"], [0.5, "#2563eb"], [1, "#60a5fa"]],
                showscale=False,
            ),
            text=[f"₹{v/1e5:.1f}L" for v in cat_value["Total"]],
            textposition="outside",
            textfont=dict(color=TEXT_COLOR, size=11),
        ))
        fig5.update_layout(
            plot_bgcolor=CHART_BG,
            paper_bgcolor=CHART_BG,
            font_color=TEXT_COLOR,
            margin=dict(l=10, r=60, t=10, b=10),
            height=280,
            xaxis=dict(gridcolor=GRID_COLOR, title="Total Order Value (₹)"),
            yaxis=dict(gridcolor=GRID_COLOR),
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No data for selected filters.")

with col6:
    st.markdown('<div class="section-header">🔥 Delay Rate by Region</div>', unsafe_allow_html=True)
    delay_rate = (
        filtered.groupby("Region")
        .apply(lambda x: pd.Series({
            "Delay_Rate": (x["Status"] == "Delayed").mean() * 100,
            "Delayed_Orders": (x["Status"] == "Delayed").sum(),
            "Total_Orders": len(x),
        }))
        .reset_index()
    )
    if not delay_rate.empty:
        fig6 = go.Figure(go.Bar(
            x=delay_rate["Region"],
            y=delay_rate["Delay_Rate"],
            marker=dict(
                color=delay_rate["Delay_Rate"],
                colorscale=[[0, "#1a2e1a"], [0.5, "#d97706"], [1, "#dc2626"]],
                showscale=False,
            ),
            text=[f"{v:.1f}%" for v in delay_rate["Delay_Rate"]],
            textposition="outside",
            textfont=dict(color=TEXT_COLOR, size=12),
        ))
        fig6.update_layout(
            plot_bgcolor=CHART_BG,
            paper_bgcolor=CHART_BG,
            font_color=TEXT_COLOR,
            margin=dict(l=10, r=10, t=10, b=10),
            height=280,
            xaxis=dict(gridcolor=GRID_COLOR),
            yaxis=dict(gridcolor=GRID_COLOR, title="Delay Rate (%)", range=[0, delay_rate["Delay_Rate"].max() * 1.3]),
        )
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("No data for selected filters.")

# ── Part D: Business Insights & Recommendations ───────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-header">🧠 Business Insights & Recommendations</div>', unsafe_allow_html=True)

# Compute insights from FULL dataset for accuracy
full_delayed = df[df["Status"] == "Delayed"].groupby("Region").size()
worst_region = full_delayed.idxmax()
worst_count = full_delayed.max()
delay_pct = (worst_count / df[df["Region"] == worst_region].shape[0]) * 100

cat_values = df.groupby("Product_Category")["Order_Value"].sum()
top_cat = cat_values.idxmax()
top_cat_value = cat_values.max()

region_std = df.groupby("Region")["Delivery_Days"].std()
max_std_region = region_std.idxmax()
overall_cv = (df["Delivery_Days"].std() / df["Delivery_Days"].mean()) * 100

ins1, ins2, ins3 = st.columns(3)

with ins1:
    st.markdown(f"""
    <div class="insight-card" style="border-color:#f87171;">
        <div class="insight-title" style="color:#f87171;">📍 Highest Delivery Delays</div>
        <div class="insight-body">
            <strong style="color:#e2e8f0;">{worst_region} Region</strong> has the most delayed orders 
            with <strong style="color:#f87171;">{worst_count} delays ({delay_pct:.1f}% delay rate)</strong>. 
            South region follows closely at 44 delays. These two regions 
            need priority intervention in logistics operations.
        </div>
    </div>""", unsafe_allow_html=True)

with ins2:
    st.markdown(f"""
    <div class="insight-card" style="border-color:#34d399;">
        <div class="insight-title" style="color:#34d399;">💰 Top Revenue Category</div>
        <div class="insight-body">
            <strong style="color:#e2e8f0;">{top_cat}</strong> generates the highest order value at 
            <strong style="color:#34d399;">₹{top_cat_value/1e5:.1f} Lakhs</strong>. 
            Pharma is a close second. Electronics and Automotive lag behind, 
            indicating potential pricing or volume optimization opportunities.
        </div>
    </div>""", unsafe_allow_html=True)

with ins3:
    st.markdown(f"""
    <div class="insight-card" style="border-color:#fbbf24;">
        <div class="insight-title" style="color:#fbbf24;">⏱️ Delivery Consistency</div>
        <div class="insight-body">
            Average delivery is <strong style="color:#e2e8f0;">8.16 days</strong> with a 
            coefficient of variation of <strong style="color:#fbbf24;">{overall_cv:.1f}%</strong>. 
            <strong style="color:#e2e8f0;">{max_std_region} region</strong> has the most variability. 
            Delivery times are <em>moderately inconsistent</em> — std dev suggests 
            unpredictable fulfilment windows across regions.
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("**🚀 Strategic Recommendations**")

r1, r2, r3 = st.columns(3)
recs = [
    ("🏭", "#60a5fa", "Regional Logistics Optimization",
     "Deploy dedicated last-mile delivery partners in South and West regions where delay rates exceed 15%. Implement real-time GPS tracking and SLA-based vendor contracts with penalty clauses to reduce delays by an estimated 30%."),
    ("📊", "#a78bfa", "Predictive Inventory Planning",
     "Leverage order value trends in Textiles and Pharma (combined ~₹11.7L) to pre-position inventory closer to high-demand regions. Use ML-based demand forecasting to cut lead times and improve fill rates by 20–25%."),
    ("🔔", "#34d399", "Proactive Order Alerts & Escalation",
     "Build an automated escalation system that flags orders at risk of delay (>7 days in processing) and sends real-time alerts to account managers. Target reducing Pending orders (22.3%) by converting them faster through automated follow-ups."),
]
for col, (icon, color, title, body) in zip([r1, r2, r3], recs):
    with col:
        st.markdown(f"""
        <div style="background:#1a1d2e;border:1px solid #2d3748;border-radius:12px;padding:20px;height:180px;">
            <div style="font-size:24px;margin-bottom:8px;">{icon}</div>
            <div style="font-size:13px;font-weight:700;color:{color};margin-bottom:8px;">{title}</div>
            <div style="font-size:12px;color:#a0aec0;line-height:1.5;">{body}</div>
        </div>""", unsafe_allow_html=True)

# ── Raw Data Table ────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📋 View Raw Data", expanded=False):
    st.dataframe(
        filtered.sort_values("Order_Date", ascending=False)
        .reset_index(drop=True)
        .style.format({"Order_Value": "₹{:,.2f}", "Delivery_Days": "{:.0f} days"}),
        height=350,
        use_container_width=True,
    )
    col_dl1, col_dl2 = st.columns([1, 4])
    with col_dl1:
        csv_data = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV",
            data=csv_data,
            file_name="filtered_orders.csv",
            mime="text/csv",
        )
