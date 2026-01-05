import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration (Important for Projectors)
st.set_page_config(page_title="Netflix Analytics Dashboard", layout="wide")

# 2. Load Data (Using a public URL so you don't have to upload the CSV separately)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/lex-p-98/netflix_titles_visualisation/main/netflix_titles.csv"
    df = pd.read_csv(url)
    df['date_added'] = pd.to_datetime(df['date_added'].str.strip())
    df['year_added'] = df['date_added'].dt.year
    return df

df = load_data()

# 3. Sidebar Filters
st.sidebar.header("Filter Options")
content_type = st.sidebar.multiselect("Select Content Type:", 
                                     options=df["type"].unique(), 
                                     default=df["type"].unique())

year_range = st.sidebar.slider("Select Release Year Range:", 
                               int(df["release_year"].min()), 
                               int(df["release_year"].max()), 
                               (2010, 2021))

# Filter dataframe based on selection
filtered_df = df[(df["type"].isin(content_type)) & 
                 (df["release_year"].between(year_range[0], year_range[1]))]

# 4. Main Dashboard UI
st.title("🎬 Netflix Global Content Insights")
st.markdown("Analyzing trends in Movies and TV Shows over the years.")

# Top Row: Key Metrics (KPIs)
col1, col2, col3 = st.columns(3)
col1.metric("Total Titles", len(filtered_df))
col2.metric("Countries Represented", filtered_df['country'].nunique())
col3.metric("Latest Release Year", int(filtered_df['release_year'].max()))

st.divider()

# Second Row: Visualizations
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Content Distribution: Movies vs TV Shows")
    fig_pie = px.pie(filtered_df, names='type', hole=0.4, 
                     color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig_pie, use_container_width=True)

with chart_col2:
    st.subheader("Top 10 Genres")
    top_genres = filtered_df['listed_in'].str.split(', ').explode().value_counts().head(10)
    fig_bar = px.bar(top_genres, x=top_genres.values, y=top_genres.index, orientation='h',
                     labels={'x': 'Count', 'y': 'Genre'},
                     color=top_genres.values, color_continuous_scale='Reds')
    st.plotly_chart(fig_bar, use_container_width=True)

# Third Row: Time Series Trend
st.subheader("Content Growth Over Time")
trend_df = filtered_df.groupby(['release_year', 'type']).size().reset_index(name='count')
fig_line = px.line(trend_df, x='release_year', y='count', color='type',
                   markers=True, line_shape='spline',
                   color_discrete_map={'Movie': '#E50914', 'TV Show': '#000000'})
st.plotly_chart(fig_line, use_container_width=True)

# Data Table (Optional)
if st.checkbox("Show Raw Data"):
    st.dataframe(filtered_df.head(100))