import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Affiliate Revenue Intelligence",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.metric-card {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 15px;
    border: 1px solid #e5e7eb;
}

.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 20px;
}

.insight-box {
    background-color: #f8f9fa;
    border-left: 5px solid #4f46e5;
    padding: 15px;
    border-radius: 5px;
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# TITLE
# ============================================================

st.title("📊 Affiliate Revenue Intelligence Dashboard")

st.markdown(
    """
    **R-based statistical analysis presented through Streamlit**

    Upload your affiliate marketing data and analyze revenue,
    clicks, conversions, publishers and revenue concentration.
    """
)


# ============================================================
# TEAM CONFIGURATION
# ============================================================

team_options = {

    "Overall Data": [],

    "Arshia Sharma": [
        "Arshia Sharma",
        "Retesh Pal",
        "Akash Choudhary",
        "Kritika Jaiswal",
        "Akansha Rawat"
    ],

    "Jitendra Ojha": [
        "Jitendra Ojha",
        "Harshil Vaishnav",
        "Vanshul Gupta",
        "Amit Kumar"
    ],

    "Anmol Mahajan": [
        "Anmol Mahajan",
        "Tanishq Tiwari",
        "Rashi Sharma",
        "Devika Dolas"
    ]
}


# ============================================================
# FILE UPLOAD
# ============================================================

st.sidebar.header("📁 Data Input")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx", "xls"]
)


if uploaded_file is None:

    st.info(
        "Please upload your affiliate marketing CSV/XLSX file "
        "from the sidebar to begin the analysis."
    )

    st.stop()


# ============================================================
# READ FILE
# ============================================================

try:

    if uploaded_file.name.lower().endswith(".csv"):

        df = pd.read_csv(uploaded_file)

    else:

        df = pd.read_excel(uploaded_file)

except Exception as e:

    st.error(f"Unable to read the uploaded file: {e}")

    st.stop()


# ============================================================
# ORIGINAL ROW COUNT
# ============================================================

original_row_count = len(df)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Publisher ID",
    "Publisher Manager",
    "Date",
    "Clicks",
    "Pending Conversions",
    "pendingRevenue_in_INR",
    "pendingPayout_in_INR"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]


if missing_columns:

    st.error(
        "The following required columns are missing from the uploaded file:"
    )

    for col in missing_columns:
        st.write(f"- {col}")

    st.stop()


# ============================================================
# DATA CLEANING
# ============================================================

# Numeric conversion

numeric_columns = [
    "Clicks",
    "Pending Conversions",
    "Pending Payout",
    "pendingPayout_in_INR",
    "Pending Revenue",
    "pendingRevenue_in_INR"
]


for col in numeric_columns:

    if col in df.columns:

        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("₹", "", regex=False)
            .str.strip()
        )

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# Date conversion

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)


# Fill important numeric columns

for col in [
    "Clicks",
    "Pending Conversions",
    "pendingRevenue_in_INR",
    "pendingPayout_in_INR"
]:

    df[col] = df[col].fillna(0)


# ============================================================
# TEAM FILTER SELECTION
# ============================================================

st.sidebar.markdown("---")

st.sidebar.subheader("👥 Select Team")

selected_team = st.sidebar.selectbox(
    "Team / Manager",
    list(team_options.keys()),
    index=0
)


# ============================================================
# TEAM FILTERING
# ============================================================

filtered_df = df.copy()


if selected_team != "Overall Data":

    team_members = {
        member.strip().casefold()
        for member in team_options[selected_team]
    }


    def belongs_to_team(value):

        if pd.isna(value):

            return False

        manager_names = {
            name.strip().casefold()
            for name in str(value).split(",")
            if name.strip()
        }

        return bool(
            manager_names.intersection(team_members)
        )


    filtered_df = filtered_df[
        filtered_df["Publisher Manager"].apply(
            belongs_to_team
        )
    ].copy()


# ============================================================
# TEAM INFORMATION
# ============================================================

if selected_team == "Overall Data":

    st.success(
        f"Overall Data selected | "
        f"{len(filtered_df):,} records available for analysis"
    )

else:

    st.success(
        f"Team selected: {selected_team} | "
        f"{len(filtered_df):,} records available for analysis"
    )


# ============================================================
# STOP IF NO DATA
# ============================================================

if filtered_df.empty:

    st.warning(
        "No records found for the selected team."
    )

    st.stop()


# ============================================================
# CALCULATIONS
# ============================================================

total_revenue = filtered_df[
    "pendingRevenue_in_INR"
].sum()


average_revenue = filtered_df[
    "pendingRevenue_in_INR"
].mean()


median_revenue = filtered_df[
    "pendingRevenue_in_INR"
].median()


maximum_revenue = filtered_df[
    "pendingRevenue_in_INR"
].max()


total_clicks = filtered_df[
    "Clicks"
].sum()


total_conversions = filtered_df[
    "Pending Conversions"
].sum()


unique_publishers = filtered_df[
    "Publisher ID"
].nunique()


# ============================================================
# CORRELATIONS
# ============================================================

correlation_clicks = filtered_df[
    ["Clicks", "pendingRevenue_in_INR"]
].corr().iloc[0, 1]


correlation_conversions = filtered_df[
    ["Pending Conversions", "pendingRevenue_in_INR"]
].corr().iloc[0, 1]


# Handle NaN correlations

if pd.isna(correlation_clicks):

    correlation_clicks = 0


if pd.isna(correlation_conversions):

    correlation_conversions = 0


# ============================================================
# PUBLISHER ANALYSIS
# ============================================================

publisher_analysis = (

    filtered_df
    .groupby("Publisher ID", dropna=False)
    .agg(
        Total_Clicks=("Clicks", "sum"),
        Total_Conversions=("Pending Conversions", "sum"),
        Total_Revenue=("pendingRevenue_in_INR", "sum")
    )
    .reset_index()
)


# ============================================================
# PUBLISHER METRICS
# ============================================================

publisher_analysis["Conversion_Rate"] = np.where(

    publisher_analysis["Total_Clicks"] > 0,

    publisher_analysis["Total_Conversions"]
    / publisher_analysis["Total_Clicks"],

    0
)


publisher_analysis["Revenue_per_Click"] = np.where(

    publisher_analysis["Total_Clicks"] > 0,

    publisher_analysis["Total_Revenue"]
    / publisher_analysis["Total_Clicks"],

    0
)


publisher_analysis["Revenue_per_Conversion"] = np.where(

    publisher_analysis["Total_Conversions"] > 0,

    publisher_analysis["Total_Revenue"]
    / publisher_analysis["Total_Conversions"],

    0
)


# Revenue share

if total_revenue > 0:

    publisher_analysis["Revenue_Share"] = (

        publisher_analysis["Total_Revenue"]
        / total_revenue
        * 100

    )

else:

    publisher_analysis["Revenue_Share"] = 0


# ============================================================
# TOP 10 PUBLISHER CONTRIBUTION
# ============================================================

publisher_analysis = publisher_analysis.sort_values(
    "Total_Revenue",
    ascending=False
)


top_10_publishers = publisher_analysis.head(10)


top_10_revenue = top_10_publishers[
    "Total_Revenue"
].sum()


if total_revenue > 0:

    top_10_share = (
        top_10_revenue
        / total_revenue
        * 100
    )

else:

    top_10_share = 0


# ============================================================
# DASHBOARD HEADER
# ============================================================

st.markdown("---")

st.subheader("📌 Executive Summary")


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "Pending Revenue",
        f"₹{total_revenue:,.0f}"
    )


with col2:

    st.metric(
        "Avg Revenue / Record",
        f"₹{average_revenue:,.2f}"
    )


with col3:

    st.metric(
        "Median Revenue",
        f"₹{median_revenue:,.0f}"
    )


with col4:

    st.metric(
        "Maximum Record",
        f"₹{maximum_revenue:,.0f}"
    )


with col5:

    st.metric(
        "Top 10 Revenue Share",
        f"{top_10_share:.2f}%"
    )


# ============================================================
# SECOND KPI ROW
# ============================================================

st.markdown("")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Clicks",
        f"{total_clicks:,.0f}"
    )


with col2:

    st.metric(
        "Total Conversions",
        f"{total_conversions:,.0f}"
    )


with col3:

    st.metric(
        "Unique Publishers",
        f"{unique_publishers:,}"
    )


with col4:

    st.metric(
        "Records Analyzed",
        f"{len(filtered_df):,}"
    )


# ============================================================
# REVENUE DISTRIBUTION
# ============================================================

st.markdown("---")

st.subheader("📈 Revenue Distribution")

distribution_df = filtered_df[
    ["pendingRevenue_in_INR"]
].copy()


fig_distribution = px.histogram(

    distribution_df,

    x="pendingRevenue_in_INR",

    nbins=50,

    title="Distribution of Pending Revenue",

    labels={
        "pendingRevenue_in_INR": "Pending Revenue (INR)"
    }
)


fig_distribution.update_layout(

    height=450,

    showlegend=False

)


st.plotly_chart(
    fig_distribution,
    use_container_width=True
)


st.info(
    f"""
    **R Analysis Insight:** Revenue is highly skewed.
    
    Median revenue per record is **₹{median_revenue:,.0f}**,
    while the maximum single record is **₹{maximum_revenue:,.0f}**.
    
    This indicates that a relatively small number of records
    contribute disproportionately to total revenue.
    """
)


# ============================================================
# CORRELATION ANALYSIS
# ============================================================

st.markdown("---")

st.subheader("🔎 Traffic & Revenue Relationship")


col1, col2 = st.columns(2)


# ------------------------------------------------------------
# CLICKS VS REVENUE
# ------------------------------------------------------------

with col1:

    scatter_clicks = filtered_df[
        [
            "Clicks",
            "pendingRevenue_in_INR"
        ]
    ].copy()


    # Remove extreme missing values

    scatter_clicks = scatter_clicks.dropna()


    fig_clicks = px.scatter(

        scatter_clicks,

        x="Clicks",

        y="pendingRevenue_in_INR",

        opacity=0.45,

        title="Clicks vs Revenue",

        labels={
            "Clicks": "Clicks",
            "pendingRevenue_in_INR": "Revenue (INR)"
        },

        trendline="ols"

    )


    fig_clicks.update_layout(
        height=450
    )


    st.plotly_chart(
        fig_clicks,
        use_container_width=True
    )


    st.metric(
        "Clicks → Revenue Correlation",
        f"{correlation_clicks:.3f}"
    )


    st.caption(
        "A value closer to 1 indicates a stronger positive "
        "linear relationship."
    )


# ------------------------------------------------------------
# CONVERSIONS VS REVENUE
# ------------------------------------------------------------

with col2:

    scatter_conversion = filtered_df[
        [
            "Pending Conversions",
            "pendingRevenue_in_INR"
        ]
    ].copy()


    scatter_conversion = scatter_conversion.dropna()


    fig_conversion = px.scatter(

        scatter_conversion,

        x="Pending Conversions",

        y="pendingRevenue_in_INR",

        opacity=0.45,

        title="Conversions vs Revenue",

        labels={
            "Pending Conversions": "Conversions",
            "pendingRevenue_in_INR": "Revenue (INR)"
        },

        trendline="ols"

    )


    fig_conversion.update_layout(
        height=450
    )


    st.plotly_chart(
        fig_conversion,
        use_container_width=True
    )


    st.metric(
        "Conversions → Revenue Correlation",
        f"{correlation_conversions:.3f}"
    )


    st.caption(
        "This indicates how strongly conversions and revenue "
        "move together linearly."
    )


# ============================================================
# CORRELATION INSIGHT
# ============================================================

if correlation_clicks < correlation_conversions:

    st.info(
        f"""
        **R Analysis Insight:** Conversions have a stronger
        relationship with revenue than clicks in the selected data.
        
        Clicks → Revenue: **{correlation_clicks:.3f}**
        
        Conversions → Revenue: **{correlation_conversions:.3f}**
        
        This suggests that traffic volume alone may not be a strong
        indicator of revenue performance.
        """
    )

else:

    st.info(
        f"""
        **R Analysis Insight:** Clicks have a stronger relationship
        with revenue than conversions in the selected data.
        
        Clicks → Revenue: **{correlation_clicks:.3f}**
        
        Conversions → Revenue: **{correlation_conversions:.3f}**
        """
    )


# ============================================================
# TOP PUBLISHERS
# ============================================================

st.markdown("---")

st.subheader("🏆 Publisher Revenue Analysis")


top_n = st.slider(
    "Number of publishers to display",
    min_value=5,
    max_value=20,
    value=10
)


top_publishers_chart = publisher_analysis.head(
    top_n
).copy()


fig_top_publishers = px.bar(

    top_publishers_chart,

    x="Total_Revenue",

    y="Publisher ID",

    orientation="h",

    title=f"Top {top_n} Publishers by Revenue",

    labels={
        "Total_Revenue": "Revenue (INR)",
        "Publisher ID": "Publisher"
    }
)


fig_top_publishers.update_layout(
    height=500,
    yaxis={
        "categoryorder": "total ascending"
    }
)


st.plotly_chart(
    fig_top_publishers,
    use_container_width=True
)


# ============================================================
# TOP PUBLISHER TABLE
# ============================================================

display_publishers = publisher_analysis.head(
    top_n
).copy()


display_publishers["Conversion Rate"] = (
    display_publishers["Conversion_Rate"] * 100
).round(2).astype(str) + "%"


display_publishers["Revenue Share"] = (
    display_publishers["Revenue_Share"]
).round(2).astype(str) + "%"


display_publishers["Revenue / Click"] = (
    display_publishers["Revenue_per_Click"]
).round(2)


display_publishers["Revenue / Conversion"] = (
    display_publishers["Revenue_per_Conversion"]
).round(2)


display_publishers = display_publishers[
    [
        "Publisher ID",
        "Total_Clicks",
        "Total_Conversions",
        "Total_Revenue",
        "Conversion Rate",
        "Revenue / Click",
        "Revenue / Conversion",
        "Revenue Share"
    ]
]


display_publishers = display_publishers.rename(
    columns={
        "Total_Clicks": "Clicks",
        "Total_Conversions": "Conversions",
        "Total_Revenue": "Revenue"
    }
)


st.dataframe(
    display_publishers,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# REVENUE CONCENTRATION
# ============================================================

st.markdown("---")

st.subheader("📊 Revenue Concentration")


# Sort publishers

pareto_df = publisher_analysis[
    publisher_analysis["Total_Revenue"] > 0
].copy()


pareto_df = pareto_df.sort_values(
    "Total_Revenue",
    ascending=False
)


pareto_df["Cumulative_Revenue"] = (
    pareto_df["Total_Revenue"].cumsum()
)


pareto_df["Cumulative_Revenue_Percentage"] = (

    pareto_df["Cumulative_Revenue"]
    / total_revenue
    * 100

)


# Number of publishers needed to reach 80%

publishers_for_80 = (

    pareto_df[
        pareto_df["Cumulative_Revenue_Percentage"] >= 80
    ]

    .index

)


if len(publishers_for_80) > 0:

    first_80_index = publishers_for_80[0]

    publishers_needed_80 = (
        pareto_df.index.get_loc(first_80_index) + 1
    )

else:

    publishers_needed_80 = len(pareto_df)


col1, col2 = st.columns(2)


with col1:

    st.metric(
        "Top 10 Publisher Revenue Share",
        f"{top_10_share:.2f}%"
    )


with col2:

    st.metric(
        "Publishers Needed for ~80% Revenue",
        f"{publishers_needed_80:,}"
    )


# Pareto chart

pareto_display = pareto_df.head(
    min(20, len(pareto_df))
).copy()


fig_pareto = px.bar(

    pareto_display,

    x="Publisher ID",

    y="Total_Revenue",

    title="Revenue Contribution — Top Publishers",

    labels={
        "Publisher ID": "Publisher",
        "Total_Revenue": "Revenue (INR)"
    }
)


fig_pareto.update_layout(
    height=450
)


st.plotly_chart(
    fig_pareto,
    use_container_width=True
)


st.info(
    f"""
    **R Analysis Insight:** The top 10 publishers contribute
    **{top_10_share:.2f}%** of total revenue.
    
    This indicates significant revenue concentration among
    high-performing publishers.
    """
)


# ============================================================
# EFFICIENCY ANALYSIS
# ============================================================

st.markdown("---")

st.subheader("⚡ Publisher Efficiency")


efficiency_df = publisher_analysis[
    publisher_analysis["Total_Revenue"] > 0
].copy()


if not efficiency_df.empty:

    efficiency_df["Efficiency Segment"] = "Standard"


    revenue_threshold = efficiency_df[
        "Total_Revenue"
    ].quantile(0.75)


    rpc_threshold = efficiency_df[
        "Revenue_per_Click"
    ].quantile(0.75)


    # High revenue + high RPC

    efficiency_df.loc[
        (
            efficiency_df["Total_Revenue"] >= revenue_threshold
        )
        &
        (
            efficiency_df["Revenue_per_Click"] >= rpc_threshold
        ),
        "Efficiency Segment"
    ] = "High Value"


    # High RPC but lower revenue

    efficiency_df.loc[
        (
            efficiency_df["Total_Revenue"] < revenue_threshold
        )
        &
        (
            efficiency_df["Revenue_per_Click"] >= rpc_threshold
        ),
        "Efficiency Segment"
    ] = "Growth Opportunity"


    # High revenue but lower RPC

    efficiency_df.loc[
        (
            efficiency_df["Total_Revenue"] >= revenue_threshold
        )
        &
        (
            efficiency_df["Revenue_per_Click"] < rpc_threshold
        ),
        "Efficiency Segment"
    ] = "Scale / Optimize"


    segment_counts = (
        efficiency_df["Efficiency Segment"]
        .value_counts()
        .reset_index()
    )


    segment_counts.columns = [
        "Segment",
        "Publishers"
    ]


    fig_segments = px.bar(

        segment_counts,

        x="Segment",

        y="Publishers",

        title="Publisher Efficiency Segmentation",

        labels={
            "Segment": "Segment",
            "Publishers": "Number of Publishers"
        }
    )


    st.plotly_chart(
        fig_segments,
        use_container_width=True
    )


    st.markdown(
        """
        **Segment definitions**

        **High Value**  
        High revenue + high revenue per click.

        **Growth Opportunity**  
        Strong revenue efficiency but comparatively lower scale.

        **Scale / Optimize**  
        High revenue but comparatively lower revenue efficiency.

        **Standard**  
        Publishers that do not fall into the above groups.
        """
    )


# ============================================================
# BUSINESS INSIGHTS
# ============================================================

st.markdown("---")

st.subheader("💡 Automated Business Insights")


# Revenue concentration

st.markdown(
    f"""
    <div class="insight-box">

    <b>Revenue Concentration</b><br>

    The top 10 publishers contribute
    <b>{top_10_share:.2f}%</b> of total revenue.

    This indicates that a relatively small publisher base
    contributes a significant portion of revenue.

    </div>
    """,
    unsafe_allow_html=True
)


# Click relationship

if correlation_clicks < 0.2:

    click_message = (
        "Clicks have a very weak linear relationship with revenue."
    )

elif correlation_clicks < 0.4:

    click_message = (
        "Clicks have a weak linear relationship with revenue."
    )

elif correlation_clicks < 0.6:

    click_message = (
        "Clicks have a moderate relationship with revenue."
    )

else:

    click_message = (
        "Clicks have a strong relationship with revenue."
    )


st.markdown(
    f"""
    <div class="insight-box">

    <b>Traffic vs Revenue</b><br>

    Clicks → Revenue correlation:
    <b>{correlation_clicks:.3f}</b>

    <br><br>

    {click_message}

    </div>
    """,
    unsafe_allow_html=True
)


# Conversion relationship

if correlation_conversions < 0.2:

    conversion_message = (
        "Conversions have a very weak linear relationship with revenue."
    )

elif correlation_conversions < 0.4:

    conversion_message = (
        "Conversions have a weak linear relationship with revenue."
    )

elif correlation_conversions < 0.6:

    conversion_message = (
        "Conversions have a moderate relationship with revenue."
    )

else:

    conversion_message = (
        "Conversions have a strong relationship with revenue."
    )


st.markdown(
    f"""
    <div class="insight-box">

    <b>Conversion vs Revenue</b><br>

    Conversions → Revenue correlation:
    <b>{correlation_conversions:.3f}</b>

    <br><br>

    {conversion_message}

    </div>
    """,
    unsafe_allow_html=True
)


# Distribution

st.markdown(
    f"""
    <div class="insight-box">

    <b>Revenue Distribution</b><br>

    Median revenue per record is
    <b>₹{median_revenue:,.0f}</b>,
    compared with an average of
    <b>₹{average_revenue:,.2f}</b>.

    This difference indicates that revenue is highly
    concentrated rather than evenly distributed across records.

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATA SUMMARY
# ============================================================

st.markdown("---")

st.subheader("📋 Dataset Summary")


summary_data = pd.DataFrame({

    "Metric": [
        "Original Records",
        "Records Analyzed",
        "Unique Publishers",
        "Total Clicks",
        "Total Conversions",
        "Total Revenue",
        "Average Revenue",
        "Median Revenue",
        "Maximum Revenue"
    ],

    "Value": [
        f"{original_row_count:,}",
        f"{len(filtered_df):,}",
        f"{unique_publishers:,}",
        f"{total_clicks:,.0f}",
        f"{total_conversions:,.0f}",
        f"₹{total_revenue:,.0f}",
        f"₹{average_revenue:,.2f}",
        f"₹{median_revenue:,.0f}",
        f"₹{maximum_revenue:,.0f}"
    ]

})


st.dataframe(
    summary_data,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DOWNLOAD PUBLISHER ANALYSIS
# ============================================================

st.markdown("---")

st.subheader("⬇️ Download Analysis")


download_df = publisher_analysis.copy()


csv_data = download_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(

    label="Download Publisher Analysis CSV",

    data=csv_data,

    file_name="publisher_revenue_analysis.csv",

    mime="text/csv"

)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Affiliate Revenue Intelligence Dashboard | "
    "Statistical analysis based on R methodology | "
    "Built with Python & Streamlit"
)
