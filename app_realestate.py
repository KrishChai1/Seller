"""
🏡 Brydje Complete Platform - Seller-Agent Matching with ML
Tinder-style matching for sellers to find perfect agents
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import re
import random
import hashlib
from typing import Dict, List, Tuple

# ================== PAGE CONFIGURATION ==================
st.set_page_config(
    page_title="Brydje - Smart Agent Matching",
    page_icon="🏡",
    layout="wide"
)

# ================== SESSION STATE ==================
if 'agents_pool' not in st.session_state:
    st.session_state.agents_pool = []
if 'current_matches' not in st.session_state:
    st.session_state.current_matches = []
if 'swipe_index' not in st.session_state:
    st.session_state.swipe_index = 0
if 'liked_agents' not in st.session_state:
    st.session_state.liked_agents = []
if 'rejected_agents' not in st.session_state:
    st.session_state.rejected_agents = []
if 'seller_profile' not in st.session_state:
    st.session_state.seller_profile = {}
if 'selected_agents' not in st.session_state:
    st.session_state.selected_agents = []

# ================== CUSTOM CSS ==================
st.markdown("""
<style>
    .tinder-card {
        background: white;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        padding: 30px;
        max-width: 500px;
        margin: 20px auto;
        position: relative;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .match-score-badge {
        position: absolute;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 30px;
        font-size: 24px;
        font-weight: bold;
    }
    
    .agent-photo {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin: 0 auto 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 60px;
        color: white;
    }
    
    .swipe-button {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        border: none;
        color: white;
        font-size: 30px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .reject-button {
        background: #ff4458;
    }
    
    .reject-button:hover {
        background: #ff6b7d;
        transform: scale(1.1);
    }
    
    .like-button {
        background: #44d362;
    }
    
    .like-button:hover {
        background: #6ee885;
        transform: scale(1.1);
    }
    
    .super-like-button {
        background: #2196F3;
    }
    
    .super-like-button:hover {
        background: #42a5f5;
        transform: scale(1.1);
    }
    
    .seller-form-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px;
        border-radius: 20px;
        margin: 20px 0;
    }
    
    .match-result-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .match-result-card:hover {
        border-color: #667eea;
        transform: translateY(-2px);
    }
    
    .perfect-match {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .feature-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        padding: 5px 15px;
        border-radius: 20px;
        margin: 5px;
        font-size: 14px;
    }
    
    .progress-bar {
        background: #e0e0e0;
        height: 30px;
        border-radius: 15px;
        overflow: hidden;
        margin: 20px 0;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 100%;
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# ================== ML MATCHING ENGINE ==================
class MLMatchingEngine:
    """Advanced ML-based matching system for seller-agent pairing"""
    
    @staticmethod
    def calculate_match_score(seller: Dict, agent: Dict) -> Tuple[float, Dict]:
        """
        Calculate comprehensive match score using ML-style algorithms
        Returns: (score, breakdown)
        """
        
        score_breakdown = {
            'location': 0,
            'price_compatibility': 0,
            'timeline': 0,
            'communication': 0,
            'experience': 0,
            'specialization': 0,
            'personality': 0,
            'tech_savvy': 0
        }
        
        # 1. Location Match (25 points)
        if seller.get('zip_code') == agent.get('zip_code'):
            score_breakdown['location'] = 25
        elif seller.get('city') == agent.get('city'):
            score_breakdown['location'] = 20
        elif seller.get('state') == agent.get('state'):
            score_breakdown['location'] = 10
        
        # 2. Price Range Compatibility (20 points)
        seller_price = seller.get('home_value', 500000)
        agent_avg_price = agent.get('avg_sale_price', 500000)
        
        price_diff_ratio = abs(seller_price - agent_avg_price) / seller_price
        if price_diff_ratio < 0.1:
            score_breakdown['price_compatibility'] = 20
        elif price_diff_ratio < 0.25:
            score_breakdown['price_compatibility'] = 15
        elif price_diff_ratio < 0.5:
            score_breakdown['price_compatibility'] = 10
        else:
            score_breakdown['price_compatibility'] = 5
        
        # 3. Timeline Match (15 points)
        seller_timeline = seller.get('timeline', '3-6 months')
        agent_availability = agent.get('availability', 'immediate')
        
        if seller_timeline == 'ASAP' and agent_availability == 'immediate':
            score_breakdown['timeline'] = 15
        elif seller_timeline in ['1-3 months', '3-6 months']:
            score_breakdown['timeline'] = 12
        else:
            score_breakdown['timeline'] = 8
        
        # 4. Communication Preferences (10 points)
        seller_comm = seller.get('communication_preference', 'balanced')
        agent_style = agent.get('communication_style', 'balanced')
        
        if seller_comm == agent_style:
            score_breakdown['communication'] = 10
        elif (seller_comm == 'frequent' and agent_style in ['frequent', 'balanced']):
            score_breakdown['communication'] = 8
        else:
            score_breakdown['communication'] = 5
        
        # 5. Experience Level Match (10 points)
        if seller.get('first_time_seller'):
            # First-time sellers need experienced agents
            if agent.get('years_experience', 5) > 7:
                score_breakdown['experience'] = 10
            elif agent.get('years_experience', 5) > 3:
                score_breakdown['experience'] = 7
            else:
                score_breakdown['experience'] = 4
        else:
            # Experienced sellers are okay with any experience level
            score_breakdown['experience'] = 8
        
        # 6. Specialization Match (10 points)
        seller_property_type = seller.get('property_type', 'Single Family')
        agent_specializations = agent.get('specializations', [])
        
        if seller_property_type in agent_specializations:
            score_breakdown['specialization'] = 10
        elif 'All Types' in agent_specializations:
            score_breakdown['specialization'] = 7
        else:
            score_breakdown['specialization'] = 4
        
        # 7. Personality Match (5 points)
        seller_personality = seller.get('personality', 'professional')
        agent_personality = agent.get('personality', 'professional')
        
        if seller_personality == agent_personality:
            score_breakdown['personality'] = 5
        else:
            score_breakdown['personality'] = 3
        
        # 8. Tech Preference Match (5 points)
        if seller.get('prefers_digital'):
            if agent.get('tech_score', 50) > 70:
                score_breakdown['tech_savvy'] = 5
            elif agent.get('tech_score', 50) > 50:
                score_breakdown['tech_savvy'] = 3
            else:
                score_breakdown['tech_savvy'] = 1
        else:
            score_breakdown['tech_savvy'] = 3
        
        # Calculate total score
        total_score = sum(score_breakdown.values())
        
        # Apply ML-style adjustments
        if agent.get('rating', 0) >= 4.5:
            total_score += 5
        
        if agent.get('recent_sales', 0) > 20:
            total_score += 3
        
        # Normalize to 0-100
        total_score = min(100, total_score)
        
        return total_score, score_breakdown
    
    @staticmethod
    def rank_agents(seller: Dict, agents: List[Dict]) -> List[Dict]:
        """Rank agents based on match score"""
        
        for agent in agents:
            score, breakdown = MLMatchingEngine.calculate_match_score(seller, agent)
            agent['match_score'] = score
            agent['match_breakdown'] = breakdown
        
        # Sort by match score
        agents.sort(key=lambda x: x['match_score'], reverse=True)
        
        return agents

# ================== AGENT GENERATOR ==================
class AgentGenerator:
    """Generate realistic agents with full profiles"""
    
    @staticmethod
    def generate_agents_for_location(zip_code: str, city: str, state: str, count: int = 30) -> List[Dict]:
        """Generate diverse, realistic agents for a location"""
        
        agents = []
        
        # Name pools
        first_names_male = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Charles', 'Thomas']
        first_names_female = ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                     'Chen', 'Park', 'Kim', 'Lee', 'Wong', 'Singh', 'Patel', 'Anderson', 'Taylor', 'Thomas']
        
        # Brokerages by state
        brokerages_by_state = {
            'CA': ['Compass', 'Coldwell Banker', 'Keller Williams', 'RE/MAX', 'Sotheby\'s', 'Berkshire Hathaway'],
            'NY': ['Douglas Elliman', 'Compass', 'Corcoran', 'Brown Harris Stevens', 'Halstead'],
            'TX': ['Keller Williams', 'RE/MAX', 'Century 21', 'Berkshire Hathaway', 'Compass'],
            'FL': ['Coldwell Banker', 'RE/MAX', 'Keller Williams', 'Compass', 'EXP Realty'],
        }
        brokerages = brokerages_by_state.get(state, ['RE/MAX', 'Century 21', 'Keller Williams', 'Coldwell Banker'])
        
        # Area codes by state
        area_codes = {
            'CA': ['415', '510', '650', '408', '925', '707'],
            'NY': ['212', '718', '646', '917', '516', '631'],
            'TX': ['512', '713', '214', '817', '210', '361'],
            'FL': ['305', '786', '954', '561', '407', '813'],
        }
        local_area_codes = area_codes.get(state, ['555'])
        
        # Property types
        property_specializations = [
            ['Single Family', 'Condos'],
            ['Luxury Homes', 'Waterfront'],
            ['First-time Buyers', 'Condos'],
            ['Investment Properties', 'Multi-family'],
            ['All Types'],
            ['Senior Living', 'Downsizing'],
            ['New Construction', 'Land'],
            ['Historic Homes', 'Unique Properties']
        ]
        
        # Personality types
        personalities = ['professional', 'friendly', 'analytical', 'enthusiastic', 'patient', 'aggressive']
        
        # Communication styles
        comm_styles = ['frequent', 'balanced', 'minimal', 'digital-first', 'traditional']
        
        for i in range(count):
            # Randomly choose gender
            is_female = random.random() > 0.5
            first_name = random.choice(first_names_female if is_female else first_names_male)
            last_name = random.choice(last_names)
            
            # Generate experience and related metrics
            years_exp = random.choices(
                [random.randint(1, 3), random.randint(4, 7), random.randint(8, 15), random.randint(16, 30)],
                weights=[30, 40, 20, 10]
            )[0]
            
            # Sales based on experience
            if years_exp < 3:
                recent_sales = random.randint(3, 12)
                avg_sale_price = random.randint(200000, 500000)
            elif years_exp < 8:
                recent_sales = random.randint(10, 25)
                avg_sale_price = random.randint(300000, 700000)
            elif years_exp < 15:
                recent_sales = random.randint(15, 40)
                avg_sale_price = random.randint(400000, 900000)
            else:
                recent_sales = random.randint(20, 60)
                avg_sale_price = random.randint(350000, 1200000)
            
            # Tech score based on age implied by experience
            if years_exp < 5:
                tech_score = random.randint(65, 95)
            elif years_exp < 10:
                tech_score = random.randint(50, 85)
            elif years_exp < 20:
                tech_score = random.randint(35, 70)
            else:
                tech_score = random.randint(25, 60)
            
            # Adjust tech score for certain brokerages
            brokerage = random.choice(brokerages)
            if brokerage in ['Compass', 'EXP Realty']:
                tech_score = min(100, tech_score + 15)
            
            # Generate phone
            area_code = random.choice(local_area_codes)
            phone = f"({area_code}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
            
            # Generate email
            email_domain = brokerage.lower().replace(' ', '').replace('\'', '')
            email = f"{first_name.lower()}.{last_name.lower()}@{email_domain}.com"
            
            agent = {
                'id': i + 1,
                'name': f"{first_name} {last_name}",
                'first_name': first_name,
                'last_name': last_name,
                'brokerage': brokerage,
                'years_experience': years_exp,
                'recent_sales': recent_sales,
                'avg_sale_price': avg_sale_price,
                'total_volume': avg_sale_price * recent_sales,
                'rating': round(random.uniform(3.5, 5.0), 1),
                'review_count': random.randint(5, 200),
                'phone': phone,
                'email': email,
                'city': city,
                'state': state,
                'zip_code': zip_code,
                'specializations': random.choice(property_specializations),
                'tech_score': tech_score,
                'personality': random.choice(personalities),
                'communication_style': random.choice(comm_styles),
                'availability': random.choice(['immediate', '1 week', '2 weeks', '1 month']),
                'languages': ['English'] + (random.choice([['Spanish'], ['Mandarin'], ['French'], []]))
            }
            
            agents.append(agent)
        
        return agents

# ================== MAIN APPLICATION ==================
def main():
    st.title("🏡 Brydje - Smart Agent Matching Platform")
    st.markdown("**Find your perfect real estate agent** • **AI-powered matching** • **Swipe to connect**")
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Platform Mode")
        
        mode = st.radio(
            "Choose your role:",
            ["🏠 I'm Selling (Find an Agent)", "🏢 I'm an Agent (Find Clients)"],
            index=0
        )
        
        st.divider()
        
        if mode == "🏠 I'm Selling (Find an Agent)":
            st.info("""
            **For Sellers:**
            1. Complete your profile
            2. Tell us about your property
            3. Swipe through matched agents
            4. Connect with your favorites
            
            **It's like Tinder for real estate!**
            """)
        else:
            st.info("""
            **For Agents:**
            1. Search ZIP codes
            2. Find tech-savvy agents
            3. Build email campaigns
            4. Convert to Brydje platform
            """)
        
        st.divider()
        
        # Stats
        if st.session_state.liked_agents:
            st.success(f"💚 {len(st.session_state.liked_agents)} Liked Agents")
        if st.session_state.rejected_agents:
            st.error(f"❌ {len(st.session_state.rejected_agents)} Passed")
    
    if mode == "🏠 I'm Selling (Find an Agent)":
        # SELLER MODE - The Core Feature!
        
        tabs = st.tabs(["📝 Seller Profile", "💘 Match & Swipe", "⭐ Your Matches", "📊 Analytics"])
        
        # Tab 1: Seller Profile & Questionnaire
        with tabs[0]:
            st.header("📝 Tell Us About You & Your Property")
            st.markdown("The more we know, the better we can match you with the perfect agent!")
            
            with st.form("seller_profile_form"):
                st.markdown('<div class="seller-form-card">', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("About You")
                    
                    seller_name = st.text_input("Your Name", placeholder="John Smith")
                    seller_email = st.text_input("Email", placeholder="john@email.com")
                    seller_phone = st.text_input("Phone", placeholder="(555) 123-4567")
                    
                    first_time = st.selectbox(
                        "Is this your first time selling?",
                        ["Yes, first time", "No, I've sold before"]
                    )
                    
                    timeline = st.selectbox(
                        "When do you want to sell?",
                        ["ASAP", "1-3 months", "3-6 months", "6-12 months", "Just exploring"]
                    )
                    
                    communication = st.selectbox(
                        "Communication preference?",
                        ["Frequent updates", "Balanced", "Only important updates", "Minimal contact"]
                    )
                    
                    personality = st.selectbox(
                        "What style do you prefer?",
                        ["Professional & formal", "Friendly & casual", "Data-driven & analytical", 
                         "Enthusiastic & motivating", "Patient & educational"]
                    )
                
                with col2:
                    st.subheader("About Your Property")
                    
                    zip_code = st.text_input("Property ZIP Code", placeholder="94105")
                    
                    property_type = st.selectbox(
                        "Property Type",
                        ["Single Family Home", "Condo/Townhouse", "Multi-family", 
                         "Luxury Property", "Land/Lot", "Commercial"]
                    )
                    
                    home_value = st.number_input(
                        "Estimated Home Value ($)",
                        min_value=50000,
                        max_value=10000000,
                        value=500000,
                        step=25000
                    )
                    
                    bedrooms = st.selectbox("Bedrooms", ["Studio", "1", "2", "3", "4", "5+"])
                    bathrooms = st.selectbox("Bathrooms", ["1", "1.5", "2", "2.5", "3", "3.5", "4+"])
                    
                    home_condition = st.select_slider(
                        "Property Condition",
                        options=["Needs work", "Fair", "Good", "Excellent", "Newly renovated"]
                    )
                    
                    special_features = st.multiselect(
                        "Special Features",
                        ["Pool", "View", "Waterfront", "Large lot", "Smart home", 
                         "Solar panels", "Guest house", "Historic", "Gated community"]
                    )
                
                st.divider()
                
                st.subheader("Your Priorities")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    priority_1 = st.selectbox(
                        "Most Important",
                        ["Get highest price", "Sell quickly", "Minimal hassle", "Great communication"]
                    )
                
                with col2:
                    priority_2 = st.selectbox(
                        "Second Priority",
                        ["Marketing expertise", "Negotiation skills", "Local knowledge", "Technology use"]
                    )
                
                with col3:
                    prefers_digital = st.checkbox("I prefer digital communication", value=True)
                    wants_open_houses = st.checkbox("I'm open to hosting open houses", value=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                submit_button = st.form_submit_button("🎯 Find My Perfect Agent", use_container_width=True)
                
                if submit_button:
                    # Store seller profile
                    st.session_state.seller_profile = {
                        'name': seller_name,
                        'email': seller_email,
                        'phone': seller_phone,
                        'first_time_seller': first_time == "Yes, first time",
                        'timeline': timeline,
                        'communication_preference': communication.split()[0].lower(),
                        'personality': personality.split()[0].lower(),
                        'zip_code': zip_code,
                        'property_type': property_type.split('/')[0],
                        'home_value': home_value,
                        'bedrooms': bedrooms,
                        'bathrooms': bathrooms,
                        'condition': home_condition,
                        'special_features': special_features,
                        'priority_1': priority_1,
                        'priority_2': priority_2,
                        'prefers_digital': prefers_digital,
                        'wants_open_houses': wants_open_houses
                    }
                    
                    # Get city and state for ZIP
                    zip_info = {
                        '94105': {'city': 'San Francisco', 'state': 'CA'},
                        '10001': {'city': 'New York', 'state': 'NY'},
                        '90210': {'city': 'Beverly Hills', 'state': 'CA'},
                        '78701': {'city': 'Austin', 'state': 'TX'},
                        '33139': {'city': 'Miami Beach', 'state': 'FL'},
                    }
                    
                    location = zip_info.get(zip_code, {'city': 'San Francisco', 'state': 'CA'})
                    st.session_state.seller_profile.update(location)
                    
                    # Generate agent pool
                    with st.spinner("🤖 Using AI to find your perfect agents..."):
                        generator = AgentGenerator()
                        agents = generator.generate_agents_for_location(
                            zip_code,
                            location['city'],
                            location['state'],
                            30
                        )
                        
                        # Apply ML matching
                        engine = MLMatchingEngine()
                        matched_agents = engine.rank_agents(st.session_state.seller_profile, agents)
                        
                        st.session_state.current_matches = matched_agents
                        st.session_state.swipe_index = 0
                        
                        time.sleep(2)  # Dramatic effect
                    
                    st.success(f"🎉 Found {len(matched_agents)} matched agents! Go to 'Match & Swipe' tab!")
                    st.balloons()
        
        # Tab 2: Tinder-Style Swiping
        with tabs[1]:
            st.header("💘 Swipe to Find Your Perfect Agent")
            
            if not st.session_state.current_matches:
                st.warning("👆 Please complete your seller profile first!")
            else:
                # Progress bar
                total = len(st.session_state.current_matches)
                current = st.session_state.swipe_index
                progress = current / total if total > 0 else 0
                
                # Progress indicator
                progress_bar = st.progress(progress)
                st.write(f"**Agent {current + 1} of {total}**")
                
                if current < total:
                    agent = st.session_state.current_matches[current]
                    
                    # Create three columns for layout
                    col1, col2, col3 = st.columns([1, 3, 1])
                    
                    with col2:
                        # Agent Card Container
                        card_container = st.container()
                        
                        with card_container:
                            # Match Score at top
                            st.markdown(f"<h1 style='text-align: center; color: #667eea;'>{agent['match_score']}% Match</h1>", unsafe_allow_html=True)
                            
                            # Agent Photo (Initials in circle)
                            st.markdown(f"""
                            <div style='width: 150px; height: 150px; margin: 20px auto; 
                                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                        border-radius: 50%; display: flex; align-items: center; 
                                        justify-content: center; color: white; font-size: 60px; font-weight: bold;'>
                                {agent['first_name'][0]}{agent['last_name'][0]}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Agent Name and Info
                            st.markdown(f"### {agent['name']}")
                            st.markdown(f"**{agent['brokerage']}** • {agent['years_experience']} years experience")
                            
                            # Location and Stats
                            col_stat1, col_stat2 = st.columns(2)
                            with col_stat1:
                                st.metric("Location", f"{agent['city']}, {agent['state']}")
                                st.metric("Recent Sales", agent['recent_sales'])
                            with col_stat2:
                                st.metric("Rating", f"⭐ {agent['rating']}/5.0")
                                st.metric("Avg Sale", f"${agent['avg_sale_price']:,.0f}")
                            
                            # Specializations
                            st.markdown("#### Specializes in:")
                            specialization_tags = " • ".join(agent['specializations'])
                            st.info(specialization_tags)
                            
                            # Communication and Personality
                            with st.expander("📋 Agent Details", expanded=True):
                                col_detail1, col_detail2 = st.columns(2)
                                with col_detail1:
                                    st.write(f"**Communication:** {agent['communication_style'].title()}")
                                    st.write(f"**Personality:** {agent['personality'].title()}")
                                with col_detail2:
                                    st.write(f"**Tech Score:** {agent['tech_score']}/100")
                                    st.write(f"**Languages:** {', '.join(agent['languages'])}")
                            
                            # Match Explanation
                            with st.expander("💡 Why We Matched You", expanded=True):
                                match_reasons = []
                                if agent['match_breakdown']['location'] > 15:
                                    match_reasons.append("✅ **Location match** - Same area")
                                if agent['match_breakdown']['price_compatibility'] > 15:
                                    match_reasons.append("✅ **Price expertise** - Sells in your range")
                                if agent['match_breakdown']['timeline'] > 10:
                                    match_reasons.append("✅ **Timeline fits** - Available when you need")
                                if agent['match_breakdown']['communication'] > 7:
                                    match_reasons.append("✅ **Communication style** - Matches your preference")
                                if agent['match_breakdown']['experience'] > 7:
                                    match_reasons.append("✅ **Experience level** - Right for your needs")
                                
                                for reason in match_reasons:
                                    st.markdown(reason)
                        
                        # Swipe Buttons
                        st.markdown("---")
                        col_reject, col_super, col_like = st.columns(3)
                        
                        with col_reject:
                            if st.button("❌ Pass", key=f"reject_{current}", use_container_width=True, 
                                       help="Not interested in this agent"):
                                st.session_state.rejected_agents.append(agent)
                                st.session_state.swipe_index += 1
                                st.rerun()
                        
                        with col_super:
                            if st.button("⭐ Super Like", key=f"super_{current}", use_container_width=True,
                                       type="primary", help="This agent is perfect!"):
                                agent['super_liked'] = True
                                st.session_state.liked_agents.insert(0, agent)
                                st.session_state.swipe_index += 1
                                st.balloons()
                                st.success(f"⭐ Super Liked {agent['name']}!")
                                time.sleep(1.5)
                                st.rerun()
                        
                        with col_like:
                            if st.button("💚 Like", key=f"like_{current}", use_container_width=True,
                                       help="Interested in this agent"):
                                st.session_state.liked_agents.append(agent)
                                st.session_state.swipe_index += 1
                                st.success(f"💚 Liked {agent['name']}!")
                                time.sleep(0.5)
                                st.rerun()
                        
                        # Skip to end option
                        if st.button("Skip to Results", key="skip_button"):
                            st.session_state.swipe_index = total
                            st.rerun()
                
                else:
                    # End of swiping
                    st.balloons()
                    st.success("# 🎉 You've reviewed all agents!")
                    st.info("### Check your matches in the 'Your Matches' tab")
                    
                    # Summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Reviewed", total)
                    with col2:
                        st.metric("Liked", len(st.session_state.liked_agents))
                    with col3:
                        st.metric("Passed", len(st.session_state.rejected_agents))
                    
                    if st.button("View My Matches", type="primary", use_container_width=True):
                        st.session_state.selected_tab = 2
                        st.rerun()
        
        # Tab 3: Your Matches
        with tabs[2]:
            st.header("⭐ Your Matched Agents")
            
            if st.session_state.liked_agents:
                st.success(f"You've matched with {len(st.session_state.liked_agents)} agents!")
                
                # Sort by super likes first
                super_liked = [a for a in st.session_state.liked_agents if a.get('super_liked')]
                regular_liked = [a for a in st.session_state.liked_agents if not a.get('super_liked')]
                
                if super_liked:
                    st.markdown("### ⭐ Super Liked Agents")
                    for agent in super_liked:
                        with st.expander(f"⭐ {agent['name']} - {agent['match_score']}% Match"):
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                st.write(f"**{agent['brokerage']}**")
                                st.write(f"📞 {agent['phone']}")
                                st.write(f"✉️ {agent['email']}")
                                st.write(f"📍 {agent['city']}, {agent['state']}")
                                st.write(f"⭐ Rating: {agent['rating']}/5.0 ({agent['review_count']} reviews)")
                            
                            with col2:
                                st.write(f"**Experience:** {agent['years_experience']} years")
                                st.write(f"**Recent Sales:** {agent['recent_sales']}")
                                st.write(f"**Avg Price:** ${agent['avg_sale_price']:,.0f}")
                                st.write(f"**Specialties:** {', '.join(agent['specializations'])}")
                            
                            st.divider()
                            
                            if st.button(f"📞 Contact {agent['name']}", key=f"contact_{agent['id']}"):
                                st.info(f"Call {agent['phone']} or email {agent['email']}")
                            
                            if st.button(f"📅 Schedule Meeting", key=f"schedule_{agent['id']}"):
                                st.info("Meeting scheduler would open here")
                
                if regular_liked:
                    st.markdown("### 💚 Liked Agents")
                    for agent in regular_liked:
                        with st.expander(f"{agent['name']} - {agent['match_score']}% Match"):
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                st.write(f"**{agent['brokerage']}**")
                                st.write(f"📞 {agent['phone']}")
                                st.write(f"✉️ {agent['email']}")
                                st.write(f"📍 {agent['city']}, {agent['state']}")
                            
                            with col2:
                                st.write(f"**Experience:** {agent['years_experience']} years")
                                st.write(f"**Recent Sales:** {agent['recent_sales']}")
                                st.write(f"**Avg Price:** ${agent['avg_sale_price']:,.0f}")
                            
                            if st.button(f"Contact", key=f"contact2_{agent['id']}"):
                                st.info(f"Call {agent['phone']} or email {agent['email']}")
                
                # Export options
                st.divider()
                
                if st.button("📊 Export Matches to CSV"):
                    df = pd.DataFrame(st.session_state.liked_agents)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "Download CSV",
                        csv,
                        f"my_matched_agents_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
            else:
                st.info("No matches yet. Start swiping to find your perfect agent!")
        
        # Tab 4: Analytics
        with tabs[3]:
            st.header("📊 Your Matching Analytics")
            
            if st.session_state.liked_agents or st.session_state.rejected_agents:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Reviewed", len(st.session_state.liked_agents) + len(st.session_state.rejected_agents))
                
                with col2:
                    st.metric("Liked", len(st.session_state.liked_agents))
                
                with col3:
                    st.metric("Super Liked", len([a for a in st.session_state.liked_agents if a.get('super_liked')]))
                
                with col4:
                    like_rate = len(st.session_state.liked_agents) / (len(st.session_state.liked_agents) + len(st.session_state.rejected_agents)) * 100 if (st.session_state.liked_agents or st.session_state.rejected_agents) else 0
                    st.metric("Like Rate", f"{like_rate:.0f}%")
                
                if st.session_state.liked_agents:
                    st.divider()
                    
                    # Analyze matches
                    df = pd.DataFrame(st.session_state.liked_agents)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Match Score Distribution")
                        score_data = df['match_score'].value_counts().sort_index()
                        st.bar_chart(score_data)
                    
                    with col2:
                        st.subheader("Top Brokerages")
                        brokerage_data = df['brokerage'].value_counts().head(5)
                        st.bar_chart(brokerage_data)
                    
                    # Average stats
                    st.subheader("Average Stats of Your Matches")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Avg Match Score", f"{df['match_score'].mean():.0f}%")
                        st.metric("Avg Experience", f"{df['years_experience'].mean():.1f} years")
                    
                    with col2:
                        st.metric("Avg Recent Sales", f"{df['recent_sales'].mean():.0f}")
                        st.metric("Avg Sale Price", f"${df['avg_sale_price'].mean():,.0f}")
                    
                    with col3:
                        st.metric("Avg Rating", f"{df['rating'].mean():.1f}/5.0")
                        st.metric("Avg Tech Score", f"{df['tech_score'].mean():.0f}/100")
            else:
                st.info("No data yet. Start swiping to see your analytics!")
    
    else:
        # AGENT MODE - For Brydje customer acquisition
        st.header("🏢 Agent Mode - Find & Convert Agents to Brydje")
        st.markdown("Find tech-savvy agents in any ZIP code and build conversion campaigns")
        
        tabs = st.tabs(["🔍 ZIP Search", "🎯 Tech-Savvy Filter", "📧 Email Campaign", "📊 Analytics", "📋 Selected Agents"])
        
        # Tab 1: ZIP Code Search
        with tabs[0]:
            st.header("🔍 Search Agents by ZIP Code")
            st.markdown("Enter any ZIP code to find real estate agents in that area")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                agent_zip = st.text_input(
                    "Enter ZIP Code",
                    placeholder="e.g., 94105, 10001, 90210",
                    help="Any valid 5-digit US ZIP code"
                )
            
            with col2:
                min_tech = st.slider(
                    "Min Tech Score",
                    0, 100, 50,
                    help="Filter for tech-savvy agents"
                )
            
            with col3:
                top_n = st.number_input(
                    "Show Top",
                    min_value=10,
                    max_value=100,
                    value=30,
                    step=10
                )
            
            if st.button("🔍 Search for Agents", type="primary"):
                if agent_zip and len(agent_zip) == 5 and agent_zip.isdigit():
                    # Get location info
                    zip_info = {
                        '94105': {'city': 'San Francisco', 'state': 'CA'},
                        '10001': {'city': 'New York', 'state': 'NY'},
                        '90210': {'city': 'Beverly Hills', 'state': 'CA'},
                        '78701': {'city': 'Austin', 'state': 'TX'},
                        '33139': {'city': 'Miami Beach', 'state': 'FL'},
                        '60601': {'city': 'Chicago', 'state': 'IL'},
                        '02108': {'city': 'Boston', 'state': 'MA'},
                    }
                    
                    location = zip_info.get(agent_zip, {'city': 'City', 'state': 'ST'})
                    
                    with st.spinner(f"Searching for agents in {location['city']}, {location['state']} {agent_zip}..."):
                        # Generate agents
                        generator = AgentGenerator()
                        agents = generator.generate_agents_for_location(
                            agent_zip,
                            location['city'],
                            location['state'],
                            top_n
                        )
                        
                        # Store in session
                        st.session_state.agents_pool = agents
                        time.sleep(1)  # Dramatic effect
                    
                    st.success(f"✅ Found {len(agents)} agents in ZIP {agent_zip}!")
                    
                    # Display agents
                    st.divider()
                    
                    # Filter by tech score
                    filtered_agents = [a for a in agents if a['tech_score'] >= min_tech]
                    
                    st.subheader(f"Showing {len(filtered_agents)} agents with Tech Score ≥ {min_tech}")
                    
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Agents", len(filtered_agents))
                    with col2:
                        avg_tech = sum(a['tech_score'] for a in filtered_agents) / len(filtered_agents) if filtered_agents else 0
                        st.metric("Avg Tech Score", f"{avg_tech:.0f}")
                    with col3:
                        high_tech = len([a for a in filtered_agents if a['tech_score'] >= 70])
                        st.metric("High Tech (70+)", high_tech)
                    with col4:
                        super_tech = len([a for a in filtered_agents if a['tech_score'] >= 85])
                        st.metric("Super Tech (85+)", super_tech)
                    
                    st.divider()
                    
                    # Display agents in a table with selection
                    if filtered_agents:
                        # Create DataFrame
                        df_display = pd.DataFrame([{
                            'Select': False,
                            'Name': a['name'],
                            'Brokerage': a['brokerage'],
                            'Tech Score': a['tech_score'],
                            'Recent Sales': a['recent_sales'],
                            'Avg Price': f"${a['avg_sale_price']:,.0f}",
                            'Rating': f"⭐ {a['rating']}",
                            'Experience': f"{a['years_experience']} yrs",
                            'Phone': a['phone'],
                            'Email': a['email'],
                            'Index': i
                        } for i, a in enumerate(filtered_agents)])
                        
                        # Editable dataframe
                        edited_df = st.data_editor(
                            df_display,
                            column_config={
                                "Select": st.column_config.CheckboxColumn(
                                    "Select",
                                    help="Select agents for campaign",
                                    default=False,
                                ),
                                "Tech Score": st.column_config.ProgressColumn(
                                    "Tech Score",
                                    help="Tech savviness score",
                                    format="%d",
                                    min_value=0,
                                    max_value=100,
                                ),
                            },
                            disabled=["Name", "Brokerage", "Recent Sales", "Avg Price", "Rating", "Experience", "Phone", "Email", "Index"],
                            hide_index=True,
                            use_container_width=True
                        )
                        
                        # Process selections
                        selected_indices = edited_df[edited_df['Select']]['Index'].tolist()
                        
                        if selected_indices:
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if st.button("➕ Add to Campaign", type="primary", use_container_width=True):
                                    for idx in selected_indices:
                                        agent = filtered_agents[idx]
                                        if agent not in st.session_state.selected_agents:
                                            st.session_state.selected_agents.append(agent)
                                    st.success(f"Added {len(selected_indices)} agents to campaign!")
                                    st.balloons()
                            
                            with col2:
                                if st.button("📊 Export Selected", use_container_width=True):
                                    selected_agents = [filtered_agents[idx] for idx in selected_indices]
                                    df_export = pd.DataFrame(selected_agents)
                                    csv = df_export.to_csv(index=False)
                                    st.download_button(
                                        "Download CSV",
                                        csv,
                                        f"agents_{agent_zip}_{datetime.now().strftime('%Y%m%d')}.csv",
                                        "text/csv"
                                    )
                            
                            with col3:
                                if st.button("🔍 View Details", use_container_width=True):
                                    for idx in selected_indices[:5]:  # Show max 5
                                        agent = filtered_agents[idx]
                                        with st.expander(f"{agent['name']} - {agent['brokerage']}"):
                                            col_a, col_b = st.columns(2)
                                            with col_a:
                                                st.write(f"**Tech Score:** {agent['tech_score']}/100")
                                                st.write(f"**Experience:** {agent['years_experience']} years")
                                                st.write(f"**Recent Sales:** {agent['recent_sales']}")
                                            with col_b:
                                                st.write(f"**Phone:** {agent['phone']}")
                                                st.write(f"**Email:** {agent['email']}")
                                                st.write(f"**Specialties:** {', '.join(agent['specializations'])}")
                
                else:
                    st.error("Please enter a valid 5-digit ZIP code")
        
        # Tab 2: Tech-Savvy Filter
        with tabs[1]:
            st.header("🎯 Find Tech-Savvy Agents")
            st.markdown("Advanced filtering to find agents most likely to adopt Brydje")
            
            if st.session_state.agents_pool:
                # Filtering options
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    filter_tech = st.select_slider(
                        "Tech Score Range",
                        options=["All", "50-70", "70-85", "85-100"],
                        value="70-85"
                    )
                
                with col2:
                    filter_exp = st.multiselect(
                        "Experience Level",
                        ["1-3 years", "4-7 years", "8-15 years", "16+ years"],
                        default=["4-7 years", "8-15 years"]
                    )
                
                with col3:
                    filter_brokerage = st.multiselect(
                        "Tech-Forward Brokerages",
                        ["Compass", "eXp Realty", "Redfin", "All Others"],
                        default=["Compass", "eXp Realty"]
                    )
                
                # Apply filters
                tech_filtered = st.session_state.agents_pool.copy()
                
                # Tech score filter
                if filter_tech != "All":
                    if filter_tech == "50-70":
                        tech_filtered = [a for a in tech_filtered if 50 <= a['tech_score'] < 70]
                    elif filter_tech == "70-85":
                        tech_filtered = [a for a in tech_filtered if 70 <= a['tech_score'] < 85]
                    elif filter_tech == "85-100":
                        tech_filtered = [a for a in tech_filtered if a['tech_score'] >= 85]
                
                # Experience filter
                if filter_exp:
                    exp_filtered = []
                    for agent in tech_filtered:
                        years = agent['years_experience']
                        if "1-3 years" in filter_exp and 1 <= years <= 3:
                            exp_filtered.append(agent)
                        elif "4-7 years" in filter_exp and 4 <= years <= 7:
                            exp_filtered.append(agent)
                        elif "8-15 years" in filter_exp and 8 <= years <= 15:
                            exp_filtered.append(agent)
                        elif "16+ years" in filter_exp and years >= 16:
                            exp_filtered.append(agent)
                    tech_filtered = exp_filtered
                
                # Brokerage filter
                if filter_brokerage and "All Others" not in filter_brokerage:
                    tech_filtered = [a for a in tech_filtered if a['brokerage'] in filter_brokerage]
                
                st.divider()
                
                # Display filtered results
                st.subheader(f"🎯 {len(tech_filtered)} Tech-Savvy Agents Found")
                
                if tech_filtered:
                    # Sort by tech score
                    tech_filtered.sort(key=lambda x: x['tech_score'], reverse=True)
                    
                    # Display top agents
                    for i, agent in enumerate(tech_filtered[:10]):
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            tech_badge = "🚀" if agent['tech_score'] >= 85 else "💻" if agent['tech_score'] >= 70 else "📱"
                            st.write(f"{tech_badge} **{agent['name']}** - {agent['brokerage']}")
                            st.caption(f"Tech Score: {agent['tech_score']} | {agent['years_experience']} years exp | {agent['recent_sales']} sales")
                        
                        with col2:
                            st.write(f"📞 {agent['phone']}")
                        
                        with col3:
                            pain_points = "Spending $600+/mo on tools" if agent['tech_score'] > 70 else "Need efficiency"
                            st.caption(f"Pain: {pain_points}")
                        
                        with col4:
                            if st.button("Add", key=f"add_tech_{i}", use_container_width=True):
                                if agent not in st.session_state.selected_agents:
                                    st.session_state.selected_agents.append(agent)
                                    st.success("Added!")
                    
                    # Bulk add option
                    st.divider()
                    if st.button("🎯 Add All Tech-Savvy Agents to Campaign", type="primary"):
                        for agent in tech_filtered:
                            if agent not in st.session_state.selected_agents:
                                st.session_state.selected_agents.append(agent)
                        st.success(f"Added {len(tech_filtered)} agents to campaign!")
                        st.balloons()
            else:
                st.info("👆 Search for agents in a ZIP code first")
        
        # Tab 3: Email Campaign
        with tabs[2]:
            st.header("📧 Brydje Conversion Campaign")
            st.markdown("Generate personalized emails to convert agents to Brydje platform")
            
            if st.session_state.selected_agents:
                st.success(f"📧 {len(st.session_state.selected_agents)} agents selected for campaign")
                
                # Campaign settings
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("Campaign Settings")
                    
                    campaign_name = st.text_input("Campaign Name", f"Brydje_Outreach_{datetime.now().strftime('%Y%m%d')}")
                    
                    template = st.selectbox(
                        "Email Template",
                        ["Tech-Savvy Focus", "Cost Savings", "Time Savings", "Feature Focus", "Social Proof"]
                    )
                    
                    subject_lines = {
                        "Tech-Savvy Focus": "You're spending too much time on marketing",
                        "Cost Savings": "Save $500+/month on real estate tools",
                        "Time Savings": "Get 5 hours back every week",
                        "Feature Focus": "30-second listing videos with AI",
                        "Social Proof": "Why top agents in {city} switched to Brydje"
                    }
                    
                    subject = st.text_input("Subject Line", subject_lines[template])
                
                with col2:
                    st.subheader("Personalization Options")
                    
                    use_name = st.checkbox("Use agent's name", value=True)
                    mention_brokerage = st.checkbox("Mention brokerage", value=True)
                    reference_sales = st.checkbox("Reference recent sales", value=True)
                    mention_tech_score = st.checkbox("Acknowledge tech-savviness", value=True)
                
                st.divider()
                
                # Generate sample email
                if st.session_state.selected_agents:
                    sample_agent = st.session_state.selected_agents[0]
                    
                    st.subheader("📧 Email Preview")
                    
                    # Generate email based on template
                    if template == "Tech-Savvy Focus":
                        name_part = sample_agent['name'] if use_name else 'there'
                        brokerage_part = f"I noticed you're at {sample_agent['brokerage']} and " if mention_brokerage else ''
                        sales_part = f"crushing it with {sample_agent['recent_sales']} recent sales!" if reference_sales else 'I found your profile while researching top agents.'
                        tech_part = f"As someone with a tech score of {sample_agent['tech_score']}/100, you clearly understand the value of technology in real estate." if mention_tech_score else ''
                        city_part = sample_agent['city']
                        
                        email_body = f"""
Hi {name_part},

{brokerage_part}{sales_part}

{tech_part}

Quick question - how many hours do you spend each week creating:
- Listing videos
- Property websites  
- Marketing materials
- Social media posts

Brydje uses AI to create all of these in 30 seconds. Literally.

Top agents {'at ' + sample_agent['brokerage'] if mention_brokerage else 'in ' + city_part} are saving 5+ hours every week.

Worth a quick demo? I'll show you how to create a listing video in real-time.

Best,
[Your Name]

P.S. First 20 agents in {city_part} get 50% off for life.
"""
                    elif template == "Cost Savings":
                        name_part = sample_agent['name'] if use_name else 'there'
                        sales_part = f"With {sample_agent['recent_sales']} recent sales" if reference_sales else 'For busy agents'
                        brokerage_part = f"other {sample_agent['brokerage']} agents" if mention_brokerage else 'top agents'
                        
                        email_body = f"""
Hi {name_part},

You're probably spending $600+ per month on:
- Video editing tools ($50/mo)
- Website builders ($100/mo)  
- Virtual tour software ($150/mo)
- Marketing automation ($200/mo)
- Lead generation ($100/mo)

Brydje does ALL of this for $99/month.

{sales_part}, saving $500+/month adds up quickly.

Want to see how {brokerage_part} are cutting costs?

5-minute demo: [calendar link]

Best,
[Your Name]
"""
                    else:
                        name_part = sample_agent['name'] if use_name else 'there'
                        sales_part = f"Congrats on your {sample_agent['recent_sales']} recent sales!" if reference_sales else 'Hope you\'re having a great week!'
                        brokerage_part = f"agents at {sample_agent['brokerage']}" if mention_brokerage else 'top agents'
                        tech_part = 'With your tech-forward approach' if mention_tech_score else 'For modern agents'
                        
                        email_body = f"""
Hi {name_part},

{sales_part}

I'm reaching out because Brydje is helping {brokerage_part} save 5+ hours per week on marketing.

Our AI creates:
✅ Professional listing videos (30 seconds)
✅ Property landing pages (instant)
✅ QR codes for signs (automatic)
✅ Social media content (one click)

{tech_part}, this could be a game-changer.

Free demo this week? [calendar link]

Best,
[Your Name]
"""
                    
                    st.text_area("Email Content", email_body, height=400)
                    
                    # Actions
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📧 Generate All Emails", type="primary", use_container_width=True):
                            st.info(f"Generating {len(st.session_state.selected_agents)} personalized emails...")
                            progress = st.progress(0)
                            for i, agent in enumerate(st.session_state.selected_agents):
                                progress.progress((i + 1) / len(st.session_state.selected_agents))
                                time.sleep(0.1)
                            st.success("All emails generated!")
                    
                    with col2:
                        # Export to CSV
                        export_data = []
                        for agent in st.session_state.selected_agents:
                            export_data.append({
                                'Name': agent['name'],
                                'Email': agent['email'],
                                'Phone': agent['phone'],
                                'Brokerage': agent['brokerage'],
                                'Tech Score': agent['tech_score'],
                                'Subject': subject.format(city=agent['city']),
                                'Email Body': email_body.replace(sample_agent['name'], agent['name'])
                            })
                        
                        df_export = pd.DataFrame(export_data)
                        csv = df_export.to_csv(index=False)
                        
                        st.download_button(
                            "📊 Export Campaign CSV",
                            csv,
                            f"{campaign_name}.csv",
                            "text/csv",
                            use_container_width=True
                        )
                    
                    with col3:
                        if st.button("🗑️ Clear Campaign", use_container_width=True):
                            st.session_state.selected_agents = []
                            st.success("Campaign cleared!")
                            st.rerun()
            else:
                st.info("👆 No agents selected yet. Search for agents and add them to your campaign.")
        
        # Tab 4: Analytics
        with tabs[3]:
            st.header("📊 Agent Analytics")
            
            if st.session_state.agents_pool:
                df_all = pd.DataFrame(st.session_state.agents_pool)
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Agents Found", len(df_all))
                    st.metric("Avg Tech Score", f"{df_all['tech_score'].mean():.0f}")
                
                with col2:
                    high_tech = len(df_all[df_all['tech_score'] >= 70])
                    st.metric("High Tech (70+)", high_tech)
                    st.metric("Conversion Potential", f"{(high_tech/len(df_all)*100):.0f}%")
                
                with col3:
                    st.metric("Avg Experience", f"{df_all['years_experience'].mean():.1f} years")
                    st.metric("Avg Recent Sales", f"{df_all['recent_sales'].mean():.0f}")
                
                with col4:
                    st.metric("Selected for Campaign", len(st.session_state.selected_agents))
                    if st.session_state.selected_agents:
                        selected_df = pd.DataFrame(st.session_state.selected_agents)
                        st.metric("Selected Avg Tech", f"{selected_df['tech_score'].mean():.0f}")
                
                st.divider()
                
                # Visualizations
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Tech Score Distribution")
                    tech_bins = pd.cut(df_all['tech_score'], bins=[0, 50, 70, 85, 100], labels=['Low', 'Medium', 'High', 'Super High'])
                    tech_dist = tech_bins.value_counts()
                    st.bar_chart(tech_dist)
                
                with col2:
                    st.subheader("Top Brokerages")
                    brokerage_counts = df_all['brokerage'].value_counts().head(5)
                    st.bar_chart(brokerage_counts)
                
                # Tech score by brokerage
                st.subheader("Average Tech Score by Brokerage")
                brokerage_tech = df_all.groupby('brokerage')['tech_score'].mean().sort_values(ascending=False).head(10)
                st.bar_chart(brokerage_tech)
                
                # Detailed breakdown
                st.subheader("Detailed Breakdown")
                
                # Group by experience and tech score
                exp_tech = df_all.groupby(pd.cut(df_all['years_experience'], bins=[0, 3, 7, 15, 50], labels=['Junior', 'Mid', 'Senior', 'Veteran']))['tech_score'].mean()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Tech Score by Experience Level**")
                    st.dataframe(exp_tech)
                
                with col2:
                    st.write("**High-Value Targets (Tech 70+, Sales 20+)**")
                    targets = df_all[(df_all['tech_score'] >= 70) & (df_all['recent_sales'] >= 20)]
                    st.metric("Prime Targets", len(targets))
                    if len(targets) > 0:
                        st.write("Top 5:")
                        for _, agent in targets.head(5).iterrows():
                            st.caption(f"• {agent['name']} - {agent['brokerage']} (Tech: {agent['tech_score']})")
            else:
                st.info("No data yet. Search for agents to see analytics.")
        
        # Tab 5: Selected Agents
        with tabs[4]:
            st.header("📋 Selected Agents for Campaign")
            
            if st.session_state.selected_agents:
                st.success(f"**{len(st.session_state.selected_agents)} agents** selected for Brydje outreach")
                
                # Display as table
                df_selected = pd.DataFrame(st.session_state.selected_agents)
                
                # Show key columns
                display_df = df_selected[['name', 'brokerage', 'tech_score', 'recent_sales', 'phone', 'email', 'city', 'state']]
                
                st.dataframe(
                    display_df,
                    column_config={
                        "tech_score": st.column_config.ProgressColumn(
                            "Tech Score",
                            help="Tech savviness",
                            format="%d",
                            min_value=0,
                            max_value=100,
                        ),
                        "recent_sales": st.column_config.NumberColumn(
                            "Recent Sales",
                            help="Sales in last 12 months",
                        ),
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # Summary
                st.divider()
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Average Tech Score", f"{df_selected['tech_score'].mean():.0f}")
                    st.metric("Tech-Savvy (70+)", len(df_selected[df_selected['tech_score'] >= 70]))
                
                with col2:
                    st.metric("Total Recent Sales", df_selected['recent_sales'].sum())
                    st.metric("Avg Sales/Agent", f"{df_selected['recent_sales'].mean():.0f}")
                
                with col3:
                    unique_brokerages = df_selected['brokerage'].nunique()
                    st.metric("Unique Brokerages", unique_brokerages)
                    st.metric("Cities Covered", df_selected['city'].nunique())
                
                # Actions
                st.divider()
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📧 Go to Email Campaign", type="primary", use_container_width=True):
                        st.info("Switch to Email Campaign tab to generate emails")
                
                with col2:
                    csv = df_selected.to_csv(index=False)
                    st.download_button(
                        "📊 Export Selected Agents",
                        csv,
                        f"selected_agents_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv",
                        use_container_width=True
                    )
                
                with col3:
                    if st.button("🗑️ Clear Selection", use_container_width=True):
                        st.session_state.selected_agents = []
                        st.success("Selection cleared!")
                        st.rerun()
            else:
                st.info("No agents selected yet. Search for agents and add them to build your campaign.")

if __name__ == "__main__":
    main()
