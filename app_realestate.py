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
                
                st.markdown(f"""
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress * 100}%"></div>
                </div>
                """, unsafe_allow_html=True)
                
                st.write(f"Agent {current + 1} of {total}")
                
                if current < total:
                    agent = st.session_state.current_matches[current]
                    
                    # Agent Card (Tinder-style)
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col2:
                        st.markdown(f"""
                        <div class="tinder-card">
                            <div class="match-score-badge">{agent['match_score']}%</div>
                            
                            <div class="agent-photo">
                                {agent['first_name'][0]}{agent['last_name'][0]}
                            </div>
                            
                            <h2 style="text-align: center;">{agent['name']}, {agent['years_experience']} years</h2>
                            <h4 style="text-align: center; color: #667eea;">{agent['brokerage']}</h4>
                            
                            <hr>
                            
                            <div style="text-align: center; margin: 20px 0;">
                                <span class="feature-badge">📍 {agent['city']}, {agent['state']}</span>
                                <span class="feature-badge">🏆 {agent['recent_sales']} recent sales</span>
                                <span class="feature-badge">⭐ {agent['rating']}/5.0</span>
                                <span class="feature-badge">💰 ${agent['avg_sale_price']:,.0f} avg</span>
                            </div>
                            
                            <div style="margin: 20px 0;">
                                <strong>Specializes in:</strong><br>
                                {', '.join(agent['specializations'])}
                            </div>
                            
                            <div style="margin: 20px 0;">
                                <strong>Communication:</strong> {agent['communication_style'].title()}<br>
                                <strong>Personality:</strong> {agent['personality'].title()}<br>
                                <strong>Tech Score:</strong> {agent['tech_score']}/100<br>
                                <strong>Languages:</strong> {', '.join(agent['languages'])}
                            </div>
                            
                            <div style="margin: 20px 0; background: #f8f9fa; padding: 15px; border-radius: 10px;">
                                <strong>Why we matched you:</strong><br>
                                {'✅ Location match' if agent['match_breakdown']['location'] > 15 else ''}
                                {'✅ Price range expertise' if agent['match_breakdown']['price_compatibility'] > 15 else ''}
                                {'✅ Timeline fits' if agent['match_breakdown']['timeline'] > 10 else ''}
                                {'✅ Communication style match' if agent['match_breakdown']['communication'] > 7 else ''}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Swipe Buttons
                        col_reject, col_super, col_like = st.columns(3)
                        
                        with col_reject:
                            if st.button("❌", key=f"reject_{current}", help="Pass", use_container_width=True):
                                st.session_state.rejected_agents.append(agent)
                                st.session_state.swipe_index += 1
                                st.rerun()
                        
                        with col_super:
                            if st.button("⭐", key=f"super_{current}", help="Super Like!", use_container_width=True):
                                agent['super_liked'] = True
                                st.session_state.liked_agents.insert(0, agent)
                                st.session_state.swipe_index += 1
                                st.success(f"⭐ Super Liked {agent['name']}!")
                                time.sleep(1)
                                st.rerun()
                        
                        with col_like:
                            if st.button("💚", key=f"like_{current}", help="Like", use_container_width=True):
                                st.session_state.liked_agents.append(agent)
                                st.session_state.swipe_index += 1
                                st.success(f"💚 Liked {agent['name']}!")
                                time.sleep(0.5)
                                st.rerun()
                
                else:
                    # End of swiping
                    st.markdown("""
                    <div class="perfect-match">
                        <h1>🎉 You've reviewed all agents!</h1>
                        <h3>Check your matches in the next tab</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("View My Matches"):
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
        st.header("🏢 Agent Customer Acquisition Mode")
        st.info("Search for agents to convert to Brydje platform")
        
        # This would include the agent search functionality from before
        # but I'm focusing on the seller-agent matching as that's the core feature you wanted

if __name__ == "__main__":
    main()
