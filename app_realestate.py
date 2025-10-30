"""
🏡 Brydje Ultimate Complete Platform - ALL FEATURES
Includes: Seller matching, Agent acquisition, Agent inbox, Speed-to-sell tools
With: ML matching, Tinder swipes, commission tracking, price optimization, staging AI, buyer psychology
"""

# Standard library imports
import random
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple

# Third-party imports
import streamlit as st
import pandas as pd
import numpy as np

# ================== PAGE CONFIGURATION ==================
st.set_page_config(
    page_title="Brydje - Complete Real Estate Platform",
    page_icon="🏡",
    layout="wide"
)

# ================== SESSION STATE INITIALIZATION ==================
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
if 'seller_leads' not in st.session_state:
    st.session_state.seller_leads = []
if 'accepted_sellers' not in st.session_state:
    st.session_state.accepted_sellers = []
if 'rejected_sellers' not in st.session_state:
    st.session_state.rejected_sellers = []
if 'lead_index' not in st.session_state:
    st.session_state.lead_index = 0

# ================== CUSTOM CSS ==================
st.markdown("""
<style>
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    
    .agent-card {
        background: white;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    
    .match-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    
    .feature-badge {
        background: rgba(102, 126, 234, 0.1);
        color: #667eea;
        padding: 5px 12px;
        border-radius: 15px;
        margin: 5px;
        display: inline-block;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ================== ML MATCHING ENGINE ==================
class MLMatchingEngine:
    """Advanced ML-based matching system for seller-agent pairing"""
    
    @staticmethod
    def calculate_match_score(seller: Dict, agent: Dict) -> Tuple[float, Dict]:
        """Calculate comprehensive match score using ML-style algorithms"""
        
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
        
        price_diff_ratio = abs(seller_price - agent_avg_price) / seller_price if seller_price > 0 else 1
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
        if seller_timeline == 'ASAP':
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
        else:
            score_breakdown['communication'] = 5
        
        # 5. Experience Level Match (10 points)
        if seller.get('first_time_seller'):
            if agent.get('years_experience', 5) > 7:
                score_breakdown['experience'] = 10
            elif agent.get('years_experience', 5) > 3:
                score_breakdown['experience'] = 7
        else:
            score_breakdown['experience'] = 8
        
        # 6. Specialization Match (10 points)
        seller_property_type = seller.get('property_type', 'Single Family')
        agent_specializations = agent.get('specializations', [])
        if seller_property_type in agent_specializations:
            score_breakdown['specialization'] = 10
        else:
            score_breakdown['specialization'] = 4
        
        # 7. Personality Match (5 points)
        if seller.get('personality') == agent.get('personality'):
            score_breakdown['personality'] = 5
        else:
            score_breakdown['personality'] = 3
        
        # 8. Tech Preference Match (5 points)
        if seller.get('prefers_digital'):
            if agent.get('tech_score', 50) > 70:
                score_breakdown['tech_savvy'] = 5
            else:
                score_breakdown['tech_savvy'] = 2
        else:
            score_breakdown['tech_savvy'] = 3
        
        # Calculate total score
        total_score = sum(score_breakdown.values())
        
        # Apply bonuses
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
        first_names_male = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph']
        first_names_female = ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 
                     'Rodriguez', 'Martinez', 'Chen', 'Park', 'Kim', 'Lee', 'Anderson', 'Taylor']
        
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
        
        # Property specializations
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

# ================== EMAIL GENERATOR ==================
def generate_email_for_agent(agent: Dict, template_type: str = "Tech-Savvy Focus") -> str:
    """Generate personalized email for agent outreach"""
    
    name = agent.get('name', 'there')
    city = agent.get('city', 'your area')
    brokerage = agent.get('brokerage', '')
    recent_sales = agent.get('recent_sales', 10)
    tech_score = agent.get('tech_score', 50)
    
    if template_type == "Tech-Savvy Focus":
        email = f"""
Hi {name},

I noticed you're at {brokerage} and crushing it with {recent_sales} recent sales!

As someone with a tech score indicating you value efficiency, I wanted to share how Brydje 
is helping agents save 5+ hours per week on marketing.

Our AI creates:
• Listing videos in 30 seconds
• Property websites instantly
• QR codes for smart open houses
• Automated buyer-matching

Other agents at {brokerage} are saving $500+/month by consolidating their tools.

Worth a quick 5-minute demo? First 20 agents in {city} get 50% off.

Best,
[Your Name]

P.S. Check out this 30-second listing video created with Brydje: [demo link]
"""
    
    elif template_type == "Cost Savings":
        email = f"""
Hi {name},

You're probably spending $600+ per month on:
- Video editing tools ($50/mo)
- Website builders ($100/mo)
- Virtual tour software ($150/mo)
- Marketing automation ($200/mo)
- Lead generation ($100/mo)

Brydje does ALL of this for $99/month.

With {recent_sales} recent sales, saving $500+/month adds up quickly.

Want to see how other {brokerage} agents are cutting costs?

5-minute demo: [calendar link]

Best,
[Your Name]
"""
    
    else:  # Time Savings
        email = f"""
Hi {name},

Congrats on your {recent_sales} recent sales!

Quick question - how many hours do you spend each week on:
- Creating listing videos
- Building property websites
- Managing open house sign-ins
- Following up with leads

Brydje automates all of this, saving agents 5+ hours every week.

Worth exploring? Let's chat: [calendar link]

Best,
[Your Name]
"""
    
    return email

# ================== MAIN APPLICATION ==================
def main():
    st.title("🏡 Brydje - Complete Real Estate Platform")
    st.markdown("**Smart Matching** • **AI-Powered Sales** • **Faster Closings**")
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Platform Mode")
        
        mode = st.radio(
            "Choose your role:",
            ["🏠 I'm Selling (Find an Agent)", 
             "🏢 I'm an Agent (Find Clients)",
             "📨 Agent Inbox (Review Leads)",
             "🚀 Speed-to-Sell Tools"],
            index=0
        )
        
        st.divider()
        
        # Mode-specific info
        if mode == "🏠 I'm Selling (Find an Agent)":
            st.info("""
            **For Sellers:**
            1. Complete your profile
            2. Tell us about your property
            3. Swipe through matched agents
            4. Connect with your favorites
            
            **It's like Tinder for real estate!**
            """)
            
            if st.session_state.liked_agents:
                st.success(f"💚 {len(st.session_state.liked_agents)} Liked Agents")
            if st.session_state.rejected_agents:
                st.error(f"❌ {len(st.session_state.rejected_agents)} Passed")
                
        elif mode == "🏢 I'm an Agent (Find Clients)":
            st.info("""
            **For Agents:**
            1. Search ZIP codes
            2. Find tech-savvy agents
            3. Build email campaigns
            4. Convert to Brydje platform
            """)
            
            if st.session_state.selected_agents:
                st.success(f"📧 {len(st.session_state.selected_agents)} agents selected")
                
        elif mode == "📨 Agent Inbox (Review Leads)":
            st.info("""
            **Agent Lead Management:**
            1. Review seller matches
            2. Accept/Reject leads
            3. Manage your pipeline
            4. Track conversions
            
            **Tinder for agents too!**
            """)
            
            if st.session_state.accepted_sellers:
                st.metric("Accepted Leads", len(st.session_state.accepted_sellers))
            if st.session_state.rejected_sellers:
                st.metric("Rejected Leads", len(st.session_state.rejected_sellers))
                
        else:
            st.info("""
            **Speed-to-Sell Tools:**
            1. AI pricing optimizer
            2. Staging recommendations
            3. Marketing timeline
            4. Buyer psychology insights
            
            **Sell 50% faster!**
            """)
    
    # ============== MODE 1: SELLER FINDING AGENTS ==============
    if mode == "🏠 I'm Selling (Find an Agent)":
        tabs = st.tabs(["📝 Seller Profile", "💘 Match & Swipe", "⭐ Your Matches", "📊 Analytics"])
        
        # Tab 1: Seller Profile & Questionnaire
        with tabs[0]:
            st.header("📝 Tell Us About You & Your Property")
            st.markdown("The more we know, the better we can match you with the perfect agent!")
            
            with st.form("seller_profile_form"):
                st.markdown("### About You")
                
                col1, col2 = st.columns(2)
                
                with col1:
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
                
                with col2:
                    communication = st.selectbox(
                        "Communication preference?",
                        ["Frequent updates", "Balanced", "Only important updates", "Minimal contact"]
                    )
                    
                    personality = st.selectbox(
                        "What style do you prefer?",
                        ["Professional & formal", "Friendly & casual", "Data-driven & analytical", 
                         "Enthusiastic & motivating", "Patient & educational"]
                    )
                    
                    prefers_digital = st.checkbox("I prefer digital communication", value=True)
                    wants_open_houses = st.checkbox("I'm open to hosting open houses", value=True)
                
                st.markdown("### About Your Property")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    zip_code = st.text_input("Property ZIP Code", placeholder="94105")
                    
                    property_type = st.selectbox(
                        "Property Type",
                        ["Single Family Home", "Condo/Townhouse", "Multi-family", 
                         "Luxury Property", "Land/Lot", "Commercial"]
                    )
                    
                    bedrooms = st.selectbox("Bedrooms", ["Studio", "1", "2", "3", "4", "5+"])
                    bathrooms = st.selectbox("Bathrooms", ["1", "1.5", "2", "2.5", "3", "3.5", "4+"])
                
                with col2:
                    home_value = st.number_input(
                        "Estimated Home Value ($)",
                        min_value=50000,
                        max_value=10000000,
                        value=500000,
                        step=25000
                    )
                    
                    home_condition = st.select_slider(
                        "Property Condition",
                        options=["Needs work", "Fair", "Good", "Excellent", "Newly renovated"]
                    )
                    
                    special_features = st.multiselect(
                        "Special Features",
                        ["Pool", "View", "Waterfront", "Large lot", "Smart home", 
                         "Solar panels", "Guest house", "Historic", "Gated community"]
                    )
                
                st.markdown("### Your Priorities")
                
                col1, col2 = st.columns(2)
                
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
                
                # Progress indicator
                progress_bar = st.progress(current / total if total > 0 else 0)
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
                                st.rerun()
                        
                        with col_like:
                            if st.button("💚 Like", key=f"like_{current}", use_container_width=True,
                                       help="Interested in this agent"):
                                st.session_state.liked_agents.append(agent)
                                st.session_state.swipe_index += 1
                                st.success(f"💚 Liked {agent['name']}!")
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
                
                total_reviewed = len(st.session_state.liked_agents) + len(st.session_state.rejected_agents)
                
                with col1:
                    st.metric("Total Reviewed", total_reviewed)
                
                with col2:
                    st.metric("Liked", len(st.session_state.liked_agents))
                
                with col3:
                    st.metric("Super Liked", len([a for a in st.session_state.liked_agents if a.get('super_liked')]))
                
                with col4:
                    like_rate = len(st.session_state.liked_agents) / total_reviewed * 100 if total_reviewed else 0
                    st.metric("Like Rate", f"{like_rate:.0f}%")
                
                if st.session_state.liked_agents:
                    st.divider()
                    
                    # Analyze matches
                    df = pd.DataFrame(st.session_state.liked_agents)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Match Score Distribution")
                        st.bar_chart(df['match_score'])
                    
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
    
    # ============== MODE 2: AGENT CUSTOMER ACQUISITION ==============
    elif mode == "🏢 I'm an Agent (Find Clients)":
        st.header("🏢 Agent Mode - Find & Convert Agents to Brydje")
        st.markdown("Find tech-savvy agents in any ZIP code and build conversion campaigns")
        
        tabs = st.tabs(["🔍 ZIP Search", "🎯 Tech-Savvy Filter", "📧 Email Campaign", "📊 Analytics", "📋 Selected Agents"])
        
        # Tab 1: ZIP Code Search
        with tabs[0]:
            st.header("🔍 Search Agents by ZIP Code")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                agent_zip = st.text_input(
                    "Enter ZIP Code",
                    placeholder="e.g., 94105, 10001, 90210"
                )
            
            with col2:
                min_tech = st.slider("Min Tech Score", 0, 100, 50)
            
            with col3:
                top_n = st.number_input("Show Top", min_value=10, max_value=100, value=30, step=10)
            
            if st.button("🔍 Search for Agents", type="primary"):
                if agent_zip and len(agent_zip) == 5 and agent_zip.isdigit():
                    # Get location info
                    zip_info = {
                        '94105': {'city': 'San Francisco', 'state': 'CA'},
                        '10001': {'city': 'New York', 'state': 'NY'},
                        '90210': {'city': 'Beverly Hills', 'state': 'CA'},
                        '78701': {'city': 'Austin', 'state': 'TX'},
                        '33139': {'city': 'Miami Beach', 'state': 'FL'},
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
                        
                        st.session_state.agents_pool = agents
                    
                    st.success(f"✅ Found {len(agents)} agents in ZIP {agent_zip}!")
                    
                    # Filter by tech score
                    filtered_agents = [a for a in agents if a['tech_score'] >= min_tech]
                    
                    # Display results
                    if filtered_agents:
                        st.subheader(f"Showing {len(filtered_agents)} agents with Tech Score ≥ {min_tech}")
                        
                        # Create DataFrame
                        df_display = pd.DataFrame(filtered_agents)
                        
                        # Show key columns
                        display_columns = ['name', 'brokerage', 'tech_score', 'recent_sales', 'phone', 'email']
                        st.dataframe(df_display[display_columns])
                        
                        # Add to campaign button
                        if st.button("➕ Add All to Campaign", type="primary"):
                            for agent in filtered_agents:
                                if agent not in st.session_state.selected_agents:
                                    st.session_state.selected_agents.append(agent)
                            st.success(f"Added {len(filtered_agents)} agents to campaign!")
                            st.balloons()
                else:
                    st.error("Please enter a valid 5-digit ZIP code")
        
        # Tab 2: Tech-Savvy Filter
        with tabs[1]:
            st.header("🎯 Find Tech-Savvy Agents")
            
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
                        default=["Compass"]
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
                
                st.divider()
                st.subheader(f"🎯 {len(tech_filtered)} Tech-Savvy Agents Found")
                
                if tech_filtered:
                    # Display filtered results
                    for i, agent in enumerate(tech_filtered[:10]):
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            tech_badge = "🚀" if agent['tech_score'] >= 85 else "💻" if agent['tech_score'] >= 70 else "📱"
                            st.write(f"{tech_badge} **{agent['name']}** - {agent['brokerage']}")
                            st.caption(f"Tech Score: {agent['tech_score']} | {agent['years_experience']} years exp | {agent['recent_sales']} sales")
                        
                        with col2:
                            st.write(f"📞 {agent['phone']}")
                        
                        with col3:
                            if st.button("Add", key=f"add_tech_{i}"):
                                if agent not in st.session_state.selected_agents:
                                    st.session_state.selected_agents.append(agent)
                                    st.success("Added!")
            else:
                st.info("👆 Search for agents in a ZIP code first")
        
        # Tab 3: Email Campaign
        with tabs[2]:
            st.header("📧 Brydje Conversion Campaign")
            
            if st.session_state.selected_agents:
                st.success(f"📧 {len(st.session_state.selected_agents)} agents selected for campaign")
                
                # Campaign settings
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    campaign_name = st.text_input("Campaign Name", f"Brydje_Outreach_{datetime.now().strftime('%Y%m%d')}")
                    
                    template = st.selectbox(
                        "Email Template",
                        ["Tech-Savvy Focus", "Cost Savings", "Time Savings", "Feature Focus", "Social Proof"]
                    )
                
                with col2:
                    subject_lines = {
                        "Tech-Savvy Focus": "You're spending too much time on marketing",
                        "Cost Savings": "Save $500+/month on real estate tools",
                        "Time Savings": "Get 5 hours back every week",
                        "Feature Focus": "30-second listing videos with AI",
                        "Social Proof": "Why top agents in {city} switched to Brydje"
                    }
                    
                    subject = st.text_input("Subject Line", subject_lines[template])
                
                st.divider()
                
                # Generate sample email
                if st.session_state.selected_agents:
                    sample_agent = st.session_state.selected_agents[0]
                    
                    st.subheader("📧 Email Preview")
                    
                    email_content = generate_email_for_agent(sample_agent, template)
                    st.text_area("Email Content", email_content, height=400)
                    
                    # Actions
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("📧 Generate All Emails", type="primary", use_container_width=True):
                            st.info(f"Generating {len(st.session_state.selected_agents)} personalized emails...")
                            progress = st.progress(0)
                            for i, agent in enumerate(st.session_state.selected_agents):
                                progress.progress((i + 1) / len(st.session_state.selected_agents))
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
                                'Email Body': generate_email_for_agent(agent, template)
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
                display_df = df_selected[['name', 'brokerage', 'tech_score', 'recent_sales', 'phone', 'email']]
                st.dataframe(display_df)
                
                # Actions
                st.divider()
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = df_selected.to_csv(index=False)
                    st.download_button(
                        "📊 Export Selected Agents",
                        csv,
                        f"selected_agents_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    if st.button("🗑️ Clear Selection", use_container_width=True):
                        st.session_state.selected_agents = []
                        st.success("Selection cleared!")
                        st.rerun()
            else:
                st.info("No agents selected yet. Search for agents and add them to build your campaign.")
    
    # ============== MODE 3: AGENT INBOX ==============
    elif mode == "📨 Agent Inbox (Review Leads)":
        st.header("📨 Agent Inbox - Review Seller Leads")
        st.markdown("**Swipe through seller leads** • **Accept high-value clients** • **Build your pipeline**")
        
        tabs = st.tabs(["📬 New Leads", "✅ Accepted Clients", "📊 Pipeline Analytics", "💰 Commission Calculator"])
        
        # Tab 1: New Leads
        with tabs[0]:
            st.header("📬 Review New Seller Leads")
            
            # Generate sample seller leads if none exist
            if not st.session_state.seller_leads:
                if st.button("🔄 Load New Seller Leads", type="primary"):
                    # Generate realistic seller leads
                    seller_leads = []
                    
                    names = ["John Smith", "Sarah Johnson", "Mike Chen", "Emily Davis", "Robert Wilson",
                            "Jennifer Martinez", "David Brown", "Lisa Anderson", "James Taylor", "Maria Garcia"]
                    
                    for i, name in enumerate(names):
                        lead = {
                            'id': i + 1,
                            'name': name,
                            'property_value': random.randint(200000, 2000000),
                            'property_type': random.choice(['Single Family', 'Condo', 'Townhouse', 'Luxury Home']),
                            'bedrooms': random.choice([2, 3, 4, 5]),
                            'bathrooms': random.choice([1.5, 2, 2.5, 3, 3.5]),
                            'timeline': random.choice(['ASAP', '1-3 months', '3-6 months']),
                            'motivation': random.choice(['Relocating', 'Upgrading', 'Downsizing', 'Investment', 'Divorce']),
                            'prequalified': random.choice([True, False]),
                            'cash_buyer': random.choice([True, False]) if random.random() > 0.7 else False,
                            'first_time': random.choice([True, False]),
                            'lead_score': random.randint(60, 100),
                            'commission_potential': 0,
                            'days_on_market_estimate': random.randint(15, 90),
                            'motivated_seller': random.choice([True, False]),
                            'flexible_price': random.choice([True, False]),
                            'needs_help': random.choice(['Staging', 'Repairs', 'Pricing', 'Marketing', 'None']),
                            'source': random.choice(['Brydje Match', 'Website', 'Referral', 'Open House'])
                        }
                        # Calculate commission
                        lead['commission_potential'] = lead['property_value'] * 0.03
                        
                        seller_leads.append(lead)
                    
                    st.session_state.seller_leads = seller_leads
                    st.session_state.lead_index = 0
                    st.success(f"Loaded {len(seller_leads)} new seller leads!")
                    st.balloons()
            
            if st.session_state.seller_leads:
                # Progress
                total = len(st.session_state.seller_leads)
                current = st.session_state.lead_index
                
                if current < total:
                    lead = st.session_state.seller_leads[current]
                    
                    # Progress bar
                    progress = st.progress(current / total if total > 0 else 0)
                    st.write(f"**Lead {current + 1} of {total}**")
                    
                    # Lead Card
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col2:
                        # Lead Score Badge
                        score_color = "🟢" if lead['lead_score'] >= 80 else "🟡" if lead['lead_score'] >= 60 else "🔴"
                        st.markdown(f"# {score_color} Lead Score: {lead['lead_score']}/100")
                        
                        # Seller Info
                        st.markdown(f"### {lead['name']}")
                        
                        # Property Details
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            st.metric("Property Value", f"${lead['property_value']:,.0f}")
                            st.metric("Commission Potential", f"${lead['commission_potential']:,.0f}")
                            st.metric("Timeline", lead['timeline'])
                        
                        with col_b:
                            st.metric("Type", lead['property_type'])
                            st.metric("Size", f"{lead['bedrooms']}BR / {lead['bathrooms']}BA")
                            st.metric("Est. Days on Market", lead['days_on_market_estimate'])
                        
                        # Seller Insights
                        with st.expander("💡 Seller Insights", expanded=True):
                            insights = []
                            
                            if lead['cash_buyer']:
                                insights.append("💰 **Cash Buyer** - Quick closing possible")
                            if lead['prequalified']:
                                insights.append("✅ **Pre-qualified** - Serious buyer")
                            if lead['first_time']:
                                insights.append("🆕 **First-time seller** - Needs guidance")
                            if lead['motivated_seller']:
                                insights.append("🔥 **Motivated** - Ready to move fast")
                            if lead['flexible_price']:
                                insights.append("💵 **Flexible on price** - Room to negotiate")
                            
                            insights.append(f"📍 **Motivation**: {lead['motivation']}")
                            insights.append(f"🛠️ **Needs help with**: {lead['needs_help']}")
                            insights.append(f"📥 **Lead source**: {lead['source']}")
                            
                            for insight in insights:
                                st.write(insight)
                        
                        # Action Buttons
                        st.divider()
                        
                        col_reject, col_maybe, col_accept = st.columns(3)
                        
                        with col_reject:
                            if st.button("❌ Pass", key=f"reject_lead_{current}", use_container_width=True):
                                lead['status'] = 'rejected'
                                st.session_state.rejected_sellers.append(lead)
                                st.session_state.lead_index += 1
                                st.rerun()
                        
                        with col_maybe:
                            if st.button("🤔 Maybe Later", key=f"maybe_lead_{current}", use_container_width=True):
                                # Move to end of queue
                                st.session_state.seller_leads.append(lead)
                                st.session_state.lead_index += 1
                                st.info("Moved to end of queue")
                                st.rerun()
                        
                        with col_accept:
                            if st.button("✅ Accept", key=f"accept_lead_{current}", use_container_width=True, type="primary"):
                                lead['status'] = 'accepted'
                                lead['accepted_date'] = datetime.now()
                                st.session_state.accepted_sellers.append(lead)
                                st.session_state.lead_index += 1
                                st.success(f"Accepted {lead['name']}! Commission potential: ${lead['commission_potential']:,.0f}")
                                st.balloons()
                                st.rerun()
                else:
                    st.success("You've reviewed all leads!")
                    if st.button("Load More Leads"):
                        st.session_state.seller_leads = []
                        st.session_state.lead_index = 0
                        st.rerun()
        
        # Tab 2: Accepted Clients
        with tabs[1]:
            st.header("✅ Your Accepted Clients")
            
            if st.session_state.accepted_sellers:
                st.success(f"You have {len(st.session_state.accepted_sellers)} accepted clients")
                
                # Sort by commission potential
                accepted_sorted = sorted(st.session_state.accepted_sellers, 
                                        key=lambda x: x['commission_potential'], 
                                        reverse=True)
                
                for client in accepted_sorted:
                    with st.expander(f"{client['name']} - ${client['commission_potential']:,.0f} commission"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**Property**: ${client['property_value']:,.0f}")
                            st.write(f"**Type**: {client['property_type']}")
                            st.write(f"**Size**: {client['bedrooms']}BR/{client['bathrooms']}BA")
                        
                        with col2:
                            st.write(f"**Timeline**: {client['timeline']}")
                            st.write(f"**Motivation**: {client['motivation']}")
                            st.write(f"**Lead Score**: {client['lead_score']}/100")
                        
                        with col3:
                            if st.button(f"📞 Contact", key=f"contact_client_{client['id']}"):
                                st.info("Opening contact manager...")
                            if st.button(f"📝 Add Notes", key=f"notes_client_{client['id']}"):
                                st.info("Notes feature would open here")
            else:
                st.info("No accepted clients yet. Review leads in the 'New Leads' tab.")
        
        # Tab 3: Pipeline Analytics
        with tabs[2]:
            st.header("📊 Your Pipeline Analytics")
            
            total_accepted = len(st.session_state.accepted_sellers)
            total_rejected = len(st.session_state.rejected_sellers)
            total_reviewed = total_accepted + total_rejected
            
            if total_reviewed > 0:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Reviewed", total_reviewed)
                    acceptance_rate = (total_accepted / total_reviewed * 100) if total_reviewed > 0 else 0
                    st.metric("Acceptance Rate", f"{acceptance_rate:.0f}%")
                
                with col2:
                    st.metric("Accepted", total_accepted)
                    if st.session_state.accepted_sellers:
                        avg_commission = sum(c['commission_potential'] for c in st.session_state.accepted_sellers) / len(st.session_state.accepted_sellers)
                        st.metric("Avg Commission", f"${avg_commission:,.0f}")
                
                with col3:
                    st.metric("Rejected", total_rejected)
                    if st.session_state.accepted_sellers:
                        total_pipeline = sum(c['commission_potential'] for c in st.session_state.accepted_sellers)
                        st.metric("Pipeline Value", f"${total_pipeline:,.0f}")
                
                with col4:
                    if st.session_state.accepted_sellers:
                        high_value = len([c for c in st.session_state.accepted_sellers if c['commission_potential'] > 30000])
                        st.metric("High Value (>$30k)", high_value)
                        urgent = len([c for c in st.session_state.accepted_sellers if c['timeline'] == 'ASAP'])
                        st.metric("Urgent (ASAP)", urgent)
            else:
                st.info("No data yet. Start reviewing leads to see analytics.")
        
        # Tab 4: Commission Calculator
        with tabs[3]:
            st.header("💰 Commission Calculator")
            
            if st.session_state.accepted_sellers:
                st.subheader("Your Pipeline")
                
                # Calculate totals
                total_value = sum(c['property_value'] for c in st.session_state.accepted_sellers)
                total_commission = sum(c['commission_potential'] for c in st.session_state.accepted_sellers)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Property Value", f"${total_value:,.0f}")
                
                with col2:
                    st.metric("Total Commission (3%)", f"${total_commission:,.0f}")
                
                with col3:
                    after_split = total_commission * 0.5  # Assuming 50/50 split
                    st.metric("After Brokerage Split (50%)", f"${after_split:,.0f}")
                
                # Detailed breakdown
                st.divider()
                st.subheader("Commission Breakdown by Client")
                
                df_commission = pd.DataFrame(st.session_state.accepted_sellers)[
                    ['name', 'property_value', 'commission_potential', 'timeline']
                ]
                df_commission.columns = ['Client', 'Property Value', 'Commission (3%)', 'Timeline']
                
                st.dataframe(df_commission)
            else:
                st.info("Accept some clients to see commission calculations.")
    
    # ============== MODE 4: SPEED-TO-SELL TOOLS ==============
    elif mode == "🚀 Speed-to-Sell Tools":
        st.header("🚀 Speed-to-Sell Intelligence Suite")
        st.markdown("**AI-powered tools** to sell your property **50% faster** than market average")
        
        tabs = st.tabs(["💰 Price Optimizer", "🎨 Staging AI", "📅 Timeline Planner", "🧠 Buyer Psychology", "📊 Market Timing"])
        
        # Tab 1: Price Optimizer
        with tabs[0]:
            st.header("💰 AI Price Optimizer")
            
            # Initialize state
            if 'price_optimizer_state' not in st.session_state:
                st.session_state.price_optimizer_state = {
                    'current_price': 750000,
                    'optimal_price': None,
                    'quick_sale_price': None,
                    'premium_price': None
                }
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Property Details")
                
                address = st.text_input("Property Address", "123 Main St, San Francisco, CA 94105")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    bedrooms = st.selectbox("Bedrooms", [1, 2, 3, 4, 5, 6])
                    bathrooms = st.selectbox("Bathrooms", [1, 1.5, 2, 2.5, 3, 3.5, 4])
                
                with col_b:
                    sqft = st.number_input("Square Feet", 500, 10000, 2000, 100)
                    lot_size = st.number_input("Lot Size (sqft)", 0, 50000, 5000, 500)
                
                condition = st.select_slider(
                    "Condition",
                    ["Needs Work", "Fair", "Good", "Excellent", "New/Renovated"]
                )
                
                # Update current price in session state
                st.session_state.price_optimizer_state['current_price'] = st.number_input(
                    "Your Asking Price", 
                    100000, 
                    5000000, 
                    st.session_state.price_optimizer_state['current_price'], 
                    10000
                )
                
                if st.button("🤖 Optimize Price", type="primary"):
                    with st.spinner("Analyzing 500+ comparable sales..."):
                        # Get current price from session state
                        current = st.session_state.price_optimizer_state['current_price']
                        
                        # Simulated AI pricing
                        optimal = current * random.uniform(0.92, 1.08)
                        quick = optimal * 0.95
                        premium = optimal * 1.05
                        
                        # Store all results in session state
                        st.session_state.price_optimizer_state['optimal_price'] = optimal
                        st.session_state.price_optimizer_state['quick_sale_price'] = quick
                        st.session_state.price_optimizer_state['premium_price'] = premium
                        
                        st.success("Price Analysis Complete!")
                
            with col2:
                st.subheader("AI Recommendations")
                
                # Get values from session state
                state = st.session_state.price_optimizer_state
                
                if state['optimal_price'] is not None:
                    # Get all values from state
                    optimal_price = state['optimal_price']
                    quick_sale_price = state['quick_sale_price']
                    premium_price = state['premium_price']
                    current_price = state['current_price']
                    
                    # Price recommendations
                    st.metric("Optimal Price", f"${optimal_price:,.0f}", 
                             f"{(optimal_price/current_price - 1)*100:+.1f}% vs asking")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Quick Sale (7 days)", f"${quick_sale_price:,.0f}")
                    with col_b:
                        st.metric("Premium (30+ days)", f"${premium_price:,.0f}")
                    
                    # Market insights
                    st.divider()
                    st.write("**Market Insights:**")
                    
                    insights = [
                        "📈 Properties priced 3-5% below market sell 65% faster",
                        "🏘️ Your neighborhood average: 21 days on market",
                        "💹 Market trending: +2.3% this month",
                        "🎯 Sweet spot for multiple offers",
                        "⚠️ Overpriced risk: 45+ days if too high"
                    ]
                    
                    for insight in insights:
                        st.write(insight)
                else:
                    st.info("👈 Enter property details and click 'Optimize Price' to see recommendations")
        
        # Tab 2: Staging AI
        with tabs[1]:
            st.header("🎨 AI Staging Advisor")
            
            room = st.selectbox(
                "Select Room to Stage",
                ["Living Room", "Kitchen", "Master Bedroom", "Bathroom", "Dining Room", "Entryway"]
            )
            
            target_buyer = st.selectbox(
                "Target Buyer Profile",
                ["Young Professionals", "Growing Family", "Empty Nesters", "Investors", "Luxury Buyers"]
            )
            
            budget = st.slider("Staging Budget", 500, 10000, 2500, 500)
            
            if st.button("🎨 Get Staging Plan", type="primary"):
                st.success(f"Staging Plan for {room}")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("Must-Do Changes")
                    
                    if room == "Living Room":
                        musts = [
                            "🛋️ **Remove 30% of furniture** - Create flow",
                            "💡 **Add warm lighting** - 3000K bulbs",
                            "🖼️ **Neutral artwork** - Remove family photos",
                            "🪴 **Fresh greenery** - 2 large plants"
                        ]
                    elif room == "Kitchen":
                        musts = [
                            "🍴 **Clear countertops** - 90% clear space",
                            "🍎 **Fresh fruit bowl** - Adds life",
                            "☕ **Coffee station** - Shows lifestyle",
                            "💐 **Fresh flowers** - Center island"
                        ]
                    else:
                        musts = [
                            "🧹 **Deep clean everything**",
                            "💡 **Maximize lighting**",
                            "🎨 **Neutral colors**",
                            "📦 **Declutter 50%**"
                        ]
                    
                    for must in musts:
                        st.write(must)
                
                with col2:
                    st.subheader("ROI Impact")
                    
                    st.metric("Estimated Days Saved", f"{random.randint(7, 21)} days")
                    st.metric("Value Add", f"${budget * random.uniform(3, 7):,.0f}")
                    st.metric("Buyer Interest", f"+{random.randint(35, 65)}%")
        
        # Tab 3: Timeline Planner
        with tabs[2]:
            st.header("📅 Speed-to-Sell Timeline")
            
            sale_timeline = st.selectbox(
                "Desired Sale Timeline",
                ["7 Days (Urgent)", "14 Days (Fast)", "30 Days (Standard)", "45 Days (Relaxed)"]
            )
            
            if st.button("📅 Generate Timeline", type="primary"):
                st.success(f"Your {sale_timeline} Action Plan")
                
                if "7 Days" in sale_timeline:
                    timeline_items = [
                        ("Day 1", "🏠 Professional photos + 3D tour", "Critical"),
                        ("Day 2", "📱 List on MLS + Zillow + Social", "Critical"),
                        ("Day 4-5", "🏡 Open house (Fri evening)", "Critical"),
                        ("Day 6", "🏡 Open house (Saturday)", "Critical"),
                        ("Day 7", "📝 Review offers, negotiate", "Critical")
                    ]
                else:
                    timeline_items = [
                        ("Week 1", "🎨 Staging and repairs", "Important"),
                        ("Week 2", "📱 Launch listing", "Critical"),
                        ("Week 3-4", "🏡 Open houses", "Critical")
                    ]
                
                for time_period, action, priority in timeline_items:
                    col1, col2, col3 = st.columns([1, 3, 1])
                    
                    with col1:
                        st.write(f"**{time_period}**")
                    
                    with col2:
                        st.write(action)
                    
                    with col3:
                        if priority == "Critical":
                            st.error(priority)
                        else:
                            st.warning(priority)
        
        # Tab 4: Buyer Psychology
        with tabs[3]:
            st.header("🧠 Buyer Psychology Insights")
            
            property_type = st.selectbox(
                "Your Property Type",
                ["Single Family", "Condo", "Townhouse", "Luxury Home"]
            )
            
            price_range = st.select_slider(
                "Price Range",
                ["Under $500k", "$500k-$750k", "$750k-$1M", "$1M-$2M", "Over $2M"]
            )
            
            if st.button("🧠 Analyze Buyer Mindset", type="primary"):
                st.success("Buyer Psychology Profile Generated")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("🎯 Your Likely Buyers")
                    
                    if "Under $500k" in price_range:
                        personas = [
                            "👫 **First-time buyers** (65%)",
                            "👨‍👩‍👧 **Young families** (25%)",
                            "💼 **Investors** (10%)"
                        ]
                    else:
                        personas = [
                            "📈 **Move-up buyers** (45%)",
                            "🏢 **Executives** (35%)",
                            "🌎 **Relocating professionals** (20%)"
                        ]
                    
                    for persona in personas:
                        st.write(persona)
                    
                    st.divider()
                    st.write("**What They Want:**")
                    wants = [
                        "• Move-in ready condition",
                        "• Low maintenance",
                        "• Good schools nearby",
                        "• Future value potential"
                    ]
                    for want in wants:
                        st.write(want)
                
                with col2:
                    st.subheader("🎨 Emotional Triggers")
                    
                    st.write("**Words That Sell:**")
                    
                    power_words = [
                        "✨ 'Turn-key' - Appeals to convenience",
                        "🏡 'Sanctuary' - Emotional safety",
                        "🎯 'Rare opportunity' - FOMO",
                        "💎 'Pride of ownership' - Status"
                    ]
                    
                    for word in power_words:
                        st.write(word)
        
        # Tab 5: Market Timing
        with tabs[4]:
            st.header("📊 Market Timing Intelligence")
            
            st.subheader("🗓️ Optimal Listing Calendar")
            
            month = st.selectbox(
                "Current Month",
                ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"]
            )
            
            if st.button("📊 Analyze Timing", type="primary"):
                st.success("Market Timing Analysis")
                
                # Seasonal analysis
                seasonal_data = {
                    "March": ("🟢 Excellent", "Spring market begins, high buyer activity"),
                    "April": ("🟢 Excellent", "Peak spring market, maximum exposure"),
                    "May": ("🟢 Excellent", "Families buying before summer"),
                    "June": ("🟡 Good", "Still active but starting to slow"),
                    "September": ("🟢 Excellent", "Fall market surge"),
                    "December": ("🔴 Challenging", "Lowest activity, but serious buyers")
                }
                
                rating, description = seasonal_data.get(month, ("🟡 Good", "Average market conditions"))
                
                st.metric("Market Rating", rating)
                st.write(description)
                
                st.write("**Best Days to List:**")
                best_days = [
                    "📅 **Thursday** - 20% more views",
                    "📅 **Friday** - Weekend shoppers",
                    "❌ **Monday** - Lowest engagement"
                ]
                
                for day in best_days:
                    st.write(day)

if __name__ == "__main__":
    main()
