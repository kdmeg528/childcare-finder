"""
Simple Childcare Finder - Google Places API Only
Complete end-to-end project using just one data source

SAVE THIS FILE AS: collect_data.py
"""

import requests
import pandas as pd
import numpy as np
import time
from typing import List, Dict, Optional
import json
from tqdm import tqdm

# ============================================================================
# STEP 1: DATA COLLECTION FROM GOOGLE PLACES
# ============================================================================

class SimpleChildcareCollector:
    """
    Collect childcare data using Google Places API
    This is your ONLY data source - no state databases needed!
    """
    
    def __init__(self, api_key: str):
        """
        Get your free API key from: https://console.cloud.google.com/
        Free tier: $200/month credit = ~4000 searches
        """
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.session = requests.Session()
        
    def search_childcare_in_area(self, location: tuple, radius_miles: int = 10, 
                                  query: str = "childcare") -> List[Dict]:
        """
        Search for all childcare providers in an area
        
        Args:
            location: (latitude, longitude) tuple
            radius_miles: search radius
            query: search term (try: "childcare", "daycare", "preschool")
        
        Returns:
            List of provider dictionaries
        """
        providers = []
        radius_meters = radius_miles * 1609.34  # Convert miles to meters
        
        # Nearby Search API
        url = f"{self.base_url}/nearbysearch/json"
        params = {
            'location': f"{location[0]},{location[1]}",
            'radius': min(radius_meters, 50000),  # Max 50km
            'keyword': query,
            'type': 'school',  # or 'point_of_interest'
            'key': self.api_key
        }
        
        while True:
            response = self.session.get(url, params=params)
            data = response.json()
            
            if data['status'] != 'OK':
                print(f"Search ended: {data.get('status', 'Unknown error')}")
                break
            
            providers.extend(data.get('results', []))
            
            # Check for next page
            next_page_token = data.get('next_page_token')
            if not next_page_token:
                break
            
            # Need to wait before requesting next page
            time.sleep(2)
            params = {'pagetoken': next_page_token, 'key': self.api_key}
        
        print(f"Found {len(providers)} providers in area")
        return providers
    
    def get_detailed_info(self, place_id: str) -> Dict:
        """
        Get detailed information for a specific provider
        This is where you get reviews, photos, hours, etc.
        """
        url = f"{self.base_url}/details/json"
        params = {
            'place_id': place_id,
            'fields': 'name,rating,user_ratings_total,reviews,formatted_address,'
                     'formatted_phone_number,website,opening_hours,geometry,types,'
                     'price_level,business_status',
            'key': self.api_key
        }
        
        response = self.session.get(url, params=params)
        data = response.json()
        
        if data['status'] == 'OK':
            return data['result']
        return {}
    
    def collect_all_providers(self, location: tuple, radius: int = 10) -> pd.DataFrame:
        """
        Main function: Collect all childcare providers in area with details
        """
        print(f"Searching for childcare providers near {location}")
        print(f"Radius: {radius} miles")
        print("-" * 70)
        
        # Step 1: Search for providers
        providers = self.search_childcare_in_area(location, radius)
        
        if not providers:
            print("No providers found!")
            return pd.DataFrame()
        
        # Step 2: Get detailed info for each
        detailed_providers = []
        
        for provider in tqdm(providers, desc="Getting details"):
            place_id = provider.get('place_id')
            if not place_id:
                continue
            
            # Get full details
            details = self.get_detailed_info(place_id)
            
            if details:
                # Combine basic + detailed info
                combined = {
                    'place_id': place_id,
                    'name': details.get('name', provider.get('name', 'Unknown')),
                    'address': details.get('formatted_address', ''),
                    'phone': details.get('formatted_phone_number', ''),
                    'website': details.get('website', ''),
                    'rating': details.get('rating', None),
                    'review_count': details.get('user_ratings_total', 0),
                    'latitude': details.get('geometry', {}).get('location', {}).get('lat'),
                    'longitude': details.get('geometry', {}).get('location', {}).get('lng'),
                    'business_status': details.get('business_status', 'UNKNOWN'),
                    'reviews': details.get('reviews', [])
                }
                
                detailed_providers.append(combined)
            
            time.sleep(0.1)  # Rate limiting
        
        # Convert to DataFrame
        df = pd.DataFrame(detailed_providers)
        
        print(f"\n✓ Collected {len(df)} providers with full details")
        return df

# ============================================================================
# STEP 2: FEATURE ENGINEERING FROM GOOGLE DATA
# ============================================================================

class FeatureEngineer:
    """
    Extract useful features from Google Places data
    """
    
    @staticmethod
    def extract_review_features(reviews: List[Dict]) -> Dict:
        """
        Extract features from review text using simple keyword analysis
        This replaces needing a separate "values" dataset!
        """
        if not reviews:
            return {
                'mentions_clean': 0,
                'mentions_safe': 0,
                'mentions_caring': 0,
                'mentions_educational': 0,
                'mentions_montessori': 0,
                'mentions_play_based': 0,
                'mentions_affordable': 0,
                'mentions_expensive': 0,
                'negative_keywords_count': 0,
                'positive_keywords_count': 0,
                'avg_review_length': 0
            }
        
        # Combine all review text
        all_text = ' '.join([r.get('text', '').lower() for r in reviews])
        
        # Educational philosophy keywords
        features = {
            'mentions_montessori': 1 if 'montessori' in all_text else 0,
            'mentions_reggio': 1 if 'reggio' in all_text else 0,
            'mentions_play_based': 1 if any(word in all_text for word in ['play-based', 'play based', 'child-led']) else 0,
            'mentions_stem': 1 if 'stem' in all_text else 0,
            
            # Quality indicators from reviews
            'mentions_clean': all_text.count('clean'),
            'mentions_safe': all_text.count('safe'),
            'mentions_caring': all_text.count('caring') + all_text.count('nurturing'),
            'mentions_educational': all_text.count('educational') + all_text.count('learning'),
            
            # Price indicators
            'mentions_affordable': all_text.count('affordable') + all_text.count('reasonable'),
            'mentions_expensive': all_text.count('expensive') + all_text.count('pricey'),
            
            # Sentiment
            'positive_keywords_count': sum([
                all_text.count(word) for word in 
                ['excellent', 'amazing', 'wonderful', 'great', 'love', 'best', 'professional']
            ]),
            'negative_keywords_count': sum([
                all_text.count(word) for word in 
                ['poor', 'bad', 'terrible', 'disappointed', 'worst', 'unprofessional']
            ]),
            
            'avg_review_length': np.mean([len(r.get('text', '')) for r in reviews])
        }
        
        return features
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in miles using Haversine formula"""
        from math import radians, sin, cos, sqrt, asin
        
        R = 3959  # Earth radius in miles
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        return R * c
    
    @staticmethod
    def estimate_price_from_reviews(reviews: List[Dict], rating: float) -> float:
        """
        Estimate price category from reviews and rating
        Returns estimated monthly price
        """
        if not reviews:
            # Use rating as rough proxy (higher rated = higher price)
            base_price = 1200
            if rating:
                return base_price + (rating - 3.5) * 200
            return base_price
        
        all_text = ' '.join([r.get('text', '').lower() for r in reviews])
        
        # Look for price mentions
        affordable_count = all_text.count('affordable') + all_text.count('reasonable')
        expensive_count = all_text.count('expensive') + all_text.count('pricey')
        
        # Base estimate
        base_price = 1200
        
        # Adjust based on keywords
        if affordable_count > expensive_count:
            estimated_price = base_price * 0.85  # 15% discount
        elif expensive_count > affordable_count:
            estimated_price = base_price * 1.25  # 25% premium
        else:
            estimated_price = base_price
        
        # Adjust based on rating (higher rated = typically higher price)
        if rating:
            estimated_price += (rating - 3.5) * 150
        
        return estimated_price
    
    def engineer_all_features(self, df: pd.DataFrame, user_location: tuple) -> pd.DataFrame:
        """
        Add all engineered features to dataframe
        """
        print("\nEngineering features from Google data...")
        
        # Distance from user
        df['distance_miles'] = df.apply(
            lambda row: self.calculate_distance(
                user_location[0], user_location[1],
                row['latitude'], row['longitude']
            ) if pd.notna(row['latitude']) else 999,
            axis=1
        )
        
        # Review-based features
        review_features = df['reviews'].apply(self.extract_review_features)
        review_df = pd.DataFrame(review_features.tolist())
        df = pd.concat([df, review_df], axis=1)
        
        # Price estimation
        df['estimated_price'] = df.apply(
            lambda row: self.estimate_price_from_reviews(
                row['reviews'], row['rating']
            ),
            axis=1
        )
        
        # Quality score (combining rating and review sentiment)
        df['quality_score'] = (
            (df['rating'].fillna(3) / 5) * 0.6 +  # 60% weight to rating
            ((df['positive_keywords_count'] - df['negative_keywords_count']) / 
             (df['positive_keywords_count'] + df['negative_keywords_count'] + 1)) * 0.4  # 40% to sentiment
        )
        
        print(f"✓ Added {len(review_df.columns) + 3} engineered features")
        
        return df

# ============================================================================
# STEP 3: SIMPLE ML MODEL (NO TRAINING NEEDED!)
# ============================================================================

class SimpleRecommender:
    """
    Rule-based recommendation system
    No training data needed - just uses user preferences!
    """
    
    @staticmethod
    def calculate_match_score(row: pd.Series, preferences: Dict) -> float:
        """
        Calculate how well a provider matches user preferences
        Returns score 0-100
        """
        score = 0
        
        # 1. Distance Score (35 points)
        if pd.notna(row['distance_miles']):
            if row['distance_miles'] <= preferences['max_distance']:
                score += 35 * (1 - row['distance_miles'] / preferences['max_distance'])
        
        # 2. Price Score (30 points)
        if pd.notna(row['estimated_price']):
            if row['estimated_price'] <= preferences['max_budget']:
                score += 30 * (1 - row['estimated_price'] / preferences['max_budget'])
            else:
                # Penalty for over budget
                score += max(0, 30 * (1 - (row['estimated_price'] - preferences['max_budget']) / preferences['max_budget']))
        
        # 3. Rating Score (20 points)
        if pd.notna(row['rating']):
            score += 20 * (row['rating'] / 5.0)
        
        # 4. Values Match (15 points)
        values_score = 0
        for value in preferences.get('values', []):
            col_name = f'mentions_{value}'
            if col_name in row and row[col_name] > 0:
                values_score += 1
        
        if preferences.get('values'):
            score += 15 * (values_score / len(preferences['values']))
        
        return min(score, 100)
    
    def recommend(self, df: pd.DataFrame, preferences: Dict, top_n: int = 10) -> pd.DataFrame:
        """
        Get top N recommendations
        """
        print(f"\nGenerating recommendations based on preferences...")
        print(f"  Max distance: {preferences['max_distance']} miles")
        print(f"  Max budget: ${preferences['max_budget']}/month")
        print(f"  Values: {preferences.get('values', [])}")
        
        # Calculate match scores
        df['match_score'] = df.apply(
            lambda row: self.calculate_match_score(row, preferences),
            axis=1
        )
        
        # Get top recommendations
        recommendations = df.nlargest(top_n, 'match_score')
        
        print(f"\n✓ Found {len(recommendations)} recommendations")
        
        return recommendations

# ============================================================================
# STEP 4: MAIN EXECUTION
# ============================================================================

def main():
    """
    Complete workflow using ONLY Google Places API
    """
    print("="*70)
    print("SIMPLE CHILDCARE FINDER - GOOGLE PLACES ONLY")
    print("="*70)
    
    # Configuration
    print("\n1. SETUP")
    print("-" * 70)
    
    API_KEY = input("Enter your Google Places API key (or 'demo' for sample): ").strip()
    
    if API_KEY.lower() == 'demo':
        print("\nDemo mode: Using sample data")
        # Create sample data
        sample_data = {
            'name': ['Little Learners Academy', 'Sunshine Daycare', 'Montessori School'],
            'address': ['123 Main St', '456 Oak Ave', '789 Pine Rd'],
            'rating': [4.8, 4.2, 4.9],
            'review_count': [45, 28, 67],
            'latitude': [42.5001, 42.5102, 42.4950],
            'longitude': [-70.8578, -70.8650, -70.8520],
            'phone': ['555-0001', '555-0002', '555-0003'],
            'website': ['', '', ''],
            'reviews': [
                [{'text': 'Clean and caring environment. Great teachers!'}],
                [{'text': 'Affordable and safe place for kids'}],
                [{'text': 'Amazing montessori program. Educational and fun!'}]
            ]
        }
        df = pd.DataFrame(sample_data)
        
    else:
        # Real data collection
        print("\n2. DATA COLLECTION")
        print("-" * 70)
        
        # User location (CHANGE THIS TO YOUR LOCATION!)
        location = (42.5001, -70.8578)  # Marblehead, MA
        radius = 10  # miles
        
        print(f"Collecting childcare providers near {location}")
        print(f"This will use ~{radius * 20} API calls (est. ${radius * 20 * 0.032:.2f})")
        
        proceed = input("Proceed? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Cancelled")
            return
        
        collector = SimpleChildcareCollector(API_KEY)
        df = collector.collect_all_providers(location, radius)
        
        if df.empty:
            print("No data collected. Exiting.")
            return
        
        # Save raw data
        df.to_csv('childcare_raw_google.csv', index=False)
        print("\n✓ Saved raw data to 'childcare_raw_google.csv'")
    
    # Feature engineering
    print("\n3. FEATURE ENGINEERING")
    print("-" * 70)
    
    user_location = (42.5001, -70.8578)
    engineer = FeatureEngineer()
    df = engineer.engineer_all_features(df, user_location)
    
    # Save processed data
    df.to_csv('childcare_processed.csv', index=False)
    print("✓ Saved processed data to 'childcare_processed.csv'")
    
    # Generate recommendations
    print("\n4. GENERATE RECOMMENDATIONS")
    print("-" * 70)
    
    user_preferences = {
        'max_distance': 10,  # miles
        'max_budget': 1500,  # monthly
        'values': ['montessori', 'play_based']  # educational approaches
    }
    
    recommender = SimpleRecommender()
    recommendations = recommender.recommend(df, user_preferences, top_n=10)
    
    # Display results
    print("\n5. TOP RECOMMENDATIONS")
    print("="*70)
    
    for idx, row in recommendations.iterrows():
        print(f"\n#{recommendations.index.get_loc(idx) + 1}. {row['name']}")
        print(f"   Match Score: {row['match_score']:.1f}/100")
        print(f"   Rating: {row['rating']:.1f} ⭐ ({int(row['review_count'])} reviews)")
        print(f"   Distance: {row['distance_miles']:.1f} miles")
        print(f"   Est. Price: ${row['estimated_price']:.0f}/month")
        print(f"   Address: {row['address']}")
        if row.get('website'):
            print(f"   Website: {row['website']}")
    
    # Save recommendations
    recommendations.to_csv('top_recommendations.csv', index=False)
    print("\n✓ Saved recommendations to 'top_recommendations.csv'")
    
    print("\n" + "="*70)
    print("COMPLETE! 🎉")
    print("="*70)
    print("""
Next steps:
1. Review 'childcare_processed.csv' to see all features
2. Check 'top_recommendations.csv' for top matches
3. Customize user_preferences to test different scenarios
4. Build a Streamlit app using this data (optional)
    """)

if __name__ == "__main__":
    main()