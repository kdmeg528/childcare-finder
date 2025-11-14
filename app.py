"""
Simple Streamlit App for Childcare Finder
Uses only Google Places data - no complex setup needed!

SAVE THIS FILE AS: app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Childcare Finder",
    page_icon="👶",
    layout="wide"
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_match_score(row, max_distance, max_budget, values):
    """Calculate match score for a provider"""
    score = 0
    
    # Distance (35 points)
    if pd.notna(row.get('distance_miles')):
        if row['distance_miles'] <= max_distance:
            score += 35 * (1 - row['distance_miles'] / max_distance)
    
    # Price (30 points)
    if pd.notna(row.get('estimated_price')):
        if row['estimated_price'] <= max_budget:
            score += 30 * (1 - row['estimated_price'] / max_budget)
    
    # Rating (20 points)
    if pd.notna(row.get('rating')):
        score += 20 * (row['rating'] / 5.0)
    
    # Values (15 points)
    if values:
        matches = sum(1 for v in values if row.get(f'mentions_{v}', 0) > 0)
        score += 15 * (matches / len(values))
    
    return min(score, 100)

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Header
    st.title("🏠 Childcare Finder")
    st.markdown("Find the perfect childcare based on location, budget, and values")
    
    # Check if data exists
    try:
        df = pd.read_csv('childcare_processed.csv')
    except FileNotFoundError:
        st.error("""
        ❌ No data found! 
        
        Please run the data collection script first:
        ```
        python3 collect_data.py
        ```
        """)
        st.stop()
    
    st.success(f"✓ Loaded {len(df)} childcare providers")
    
    # Sidebar for preferences
    st.sidebar.header("🎯 Your Preferences")
    
    # Distance
    max_distance = st.sidebar.slider(
        "Maximum Distance (miles)",
        min_value=1,
        max_value=30,
        value=10,
        help="How far are you willing to travel?"
    )
    
    # Budget
    max_budget = st.sidebar.slider(
        "Maximum Monthly Budget ($)",
        min_value=500,
        max_value=3000,
        value=1500,
        step=100,
        help="What's your monthly budget?"
    )
    
    # Minimum rating
    min_rating = st.sidebar.slider(
        "Minimum Rating",
        min_value=1.0,
        max_value=5.0,
        value=3.5,
        step=0.5,
        help="Only show providers with this rating or higher"
    )
    
    # Values/Philosophy
    st.sidebar.subheader("📚 Educational Values")
    values = []
    
    if st.sidebar.checkbox("Montessori"):
        values.append('montessori')
    if st.sidebar.checkbox("Play-Based Learning"):
        values.append('play_based')
    if st.sidebar.checkbox("STEM Focused"):
        values.append('stem')
    if st.sidebar.checkbox("Reggio Emilia"):
        values.append('reggio')
    
    # Calculate match scores
    df['match_score'] = df.apply(
        lambda row: calculate_match_score(row, max_distance, max_budget, values),
        axis=1
    )
    
    # Filter results
    filtered_df = df[
        (df['distance_miles'] <= max_distance * 1.2) &  # Allow 20% over
        (df['rating'].fillna(0) >= min_rating)
    ].copy()
    
    # Sort by match score
    filtered_df = filtered_df.sort_values('match_score', ascending=False)
    
    # Main content
    st.header("📊 Results")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Providers Found", len(filtered_df))
    
    with col2:
        avg_price = filtered_df['estimated_price'].mean()
        st.metric("Avg. Price", f"${avg_price:.0f}/mo")
    
    with col3:
        avg_rating = filtered_df['rating'].mean()
        st.metric("Avg. Rating", f"{avg_rating:.1f} ⭐")
    
    with col4:
        avg_distance = filtered_df['distance_miles'].mean()
        st.metric("Avg. Distance", f"{avg_distance:.1f} mi")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Recommendations", "🗺️ Map", "📈 Analytics"])
    
    # TAB 1: Recommendations
    with tab1:
        st.subheader("Top 10 Matches")
        
        if len(filtered_df) == 0:
            st.warning("No providers match your criteria. Try adjusting your filters.")
        else:
            for idx, row in filtered_df.head(10).iterrows():
                with st.expander(f"**{row['name']}** - Match: {row['match_score']:.0f}/100"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"📍 **Address:** {row['address']}")
                        st.write(f"📞 **Phone:** {row.get('phone', 'Not available')}")
                        st.write(f"⭐ **Rating:** {row['rating']:.1f} ({int(row['review_count'])} reviews)")
                        st.write(f"💵 **Est. Price:** ${row['estimated_price']:.0f}/month")
                        st.write(f"🚗 **Distance:** {row['distance_miles']:.1f} miles")
                        
                        # Show matching values
                        matching_values = []
                        if row.get('mentions_montessori', 0) > 0:
                            matching_values.append("Montessori")
                        if row.get('mentions_play_based', 0) > 0:
                            matching_values.append("Play-Based")
                        if row.get('mentions_stem', 0) > 0:
                            matching_values.append("STEM")
                        
                        if matching_values:
                            st.write(f"📚 **Approach:** {', '.join(matching_values)}")
                    
                    with col2:
                        # Progress bar for match score
                        st.progress(row['match_score'] / 100)
                        st.caption(f"Match: {row['match_score']:.0f}/100")
                        
                        # Website link
                        if pd.notna(row.get('website')) and row.get('website'):
                            st.link_button("🌐 Visit Website", row['website'])
    
    # TAB 2: Map
    with tab2:
        st.subheader("Provider Locations")
        
        map_data = filtered_df[['latitude', 'longitude', 'name', 'rating', 'match_score']].dropna()
        
        if len(map_data) > 0:
            fig = px.scatter_mapbox(
                map_data,
                lat='latitude',
                lon='longitude',
                hover_name='name',
                hover_data={'rating': ':.1f', 'match_score': ':.0f'},
                color='match_score',
                size='match_score',
                color_continuous_scale='RdYlGn',
                zoom=10,
                height=600
            )
            
            fig.update_layout(
                mapbox_style="open-street-map",
                margin={"r": 0, "t": 0, "l": 0, "b": 0}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No location data available for map view")
    
    # TAB 3: Analytics
    with tab3:
        st.subheader("Market Insights")
        
        if len(filtered_df) == 0:
            st.warning("No data to display. Adjust your filters.")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                # Price distribution
                fig_price = px.histogram(
                    filtered_df,
                    x='estimated_price',
                    nbins=20,
                    title='Price Distribution',
                    labels={'estimated_price': 'Monthly Price ($)'}
                )
                fig_price.add_vline(x=max_budget, line_dash="dash", line_color="red", 
                                   annotation_text="Your Budget")
                st.plotly_chart(fig_price, use_container_width=True)
            
            with col2:
                # Rating distribution
                fig_rating = px.histogram(
                    filtered_df,
                    x='rating',
                    nbins=10,
                    title='Rating Distribution',
                    labels={'rating': 'Google Rating (stars)'}
                )
                st.plotly_chart(fig_rating, use_container_width=True)
            
            # Scatter: Price vs Rating
            fig_scatter = px.scatter(
                filtered_df,
                x='estimated_price',
                y='rating',
                size='review_count',
                color='match_score',
                hover_name='name',
                title='Price vs. Rating',
                labels={
                    'estimated_price': 'Monthly Price ($)',
                    'rating': 'Rating (stars)',
                    'review_count': 'Number of Reviews'
                },
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Distance vs Match Score
            fig_distance = px.scatter(
                filtered_df,
                x='distance_miles',
                y='match_score',
                size='rating',
                color='estimated_price',
                hover_name='name',
                title='Distance vs. Match Score',
                labels={
                    'distance_miles': 'Distance (miles)',
                    'match_score': 'Match Score',
                    'estimated_price': 'Price ($)'
                },
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_distance, use_container_width=True)

if __name__ == "__main__":
    main()