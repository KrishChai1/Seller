"""
🏡 Brydje Complete Platform - Final Working Version
All features: Seller matching, Agent acquisition, Agent inbox, Speed tools
"""

# Standard library imports
import time as time_module  # Rename to avoid any conflicts
import random
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple

# Third-party imports
import streamlit as st
import pandas as pd
import numpy as np

# For web scraping (though blocked in this environment)
try:
    import requests
    from bs4 import BeautifulSoup
    import json
except ImportError:
    pass

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

# ================== CUSTOM CSS ==================
st.markdown("""
<style>
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }
    
    .metric-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ================== HELPER CLASSES ==================

class MLMatchingEngine:
    """ML-based matching system for seller-agent pairing"""
    
    @staticmethod
    def calculate_match_score(seller: Dict, agent: Dict) -> Tuple[float, Dict]:
        """Calculate match score between seller and agent"""
        score_breakdown = {
            'location': 0,
            'price_compatibility': 0,
            'timeline': 0,
            'experience': 0,
            'tech_savvy': 0
        }
        
        # Location match
        if seller.get('zip_code') == agent.get('zip_code'):
            score_breakdown['location'] = 25
        elif seller.get('city') == agent.get('city'):
            score_breakdown['location'] = 20
        
        # Price range compatibility
        seller_price = seller.get('home_value', 500000)
        agent_avg_price = agent.get('avg_sale_price', 500000)
        price_diff = abs(seller_price - agent_avg_price) / seller_price
        
        if price_diff < 0.2:
            score_breakdown['price_compatibility'] = 20
        elif price_diff < 0.5:
            score_breakdown['price_compatibility'] = 10
        
        # Timeline match
        if seller.get('timeline') == 'ASAP':
            score_breakdown['timeline'] = 15
        else:
            score_breakdown['timeline'] = 10
        
        # Experience match
        if agent.get('years_experience', 5) > 5:
            score_breakdown['experience'] = 10
        
        # Tech preference
        if seller.get('prefers_digital') and agent.get('tech_score', 50) > 70:
            score_breakdown['tech_savvy'] = 10
        
        total_score = sum(score_breakdown.values())
        return min(100, total_score), score_breakdown
    
    @staticmethod
    def rank_agents(seller: Dict, agents: List[Dict]) -> List[Dict]:
        """Rank agents by match score"""
        for agent in agents:
            score, breakdown = MLMatchingEngine.calculate_match_score(seller, agent)
            agent['match_score'] = score
            agent['match_breakdown'] = breakdown
        
        agents.sort(key=lambda x: x['match_score'], reverse=True)
        return agents

class AgentGenerator:
    """Generate realistic agents"""
    
    @staticmethod
    def generate_agents_for_location(zip_code: str, city: str, state: str, count: int = 30) -> List[Dict]:
        """Generate agents for a location"""
        agents = []
        
        first_names = ['John', 'Sarah', 'Michael', 'Jennifer', 'David', 'Jessica', 
                      'Robert', 'Emily', 'James', 'Ashley', 'William', 'Michelle']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
                     'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Chen', 'Anderson']
        
        brokerages = ['RE/MAX', 'Keller Williams', 'Compass', 'Century 21', 'Coldwell Banker']
        
        for i in range(count):
            first = random.choice(first_names)
            last = random.choice(last_names)
            
            agent = {
                'id': i + 1,
                'name': f"{first} {last}",
                'first_name': first,
                'last_name': last,
                'brokerage': random.choice(brokerages),
                'years_experience': random.randint(1, 20),
                'recent_sales': random.randint(5, 40),
                'avg_sale_price': random.randint(200000, 1000000),
                'rating': round(random.uniform(3.5, 5.0), 1),
                'phone': f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
                'email': f"{first.lower()}.{last.lower()}@realestate.com",
                'city': city,
                'state': state,
                'zip_code': zip_code,
                'tech_score': random.randint(40, 95),
                'specializations': ['Single Family', 'Condos'],
                'communication_style': random.choice(['frequent', 'balanced', 'minimal']),
                'personality': random.choice(['professional', 'friendly', 'analytical'])
            }
            agents.append(agent)
        
        return agents

# ================== MAIN APPLICATION ==================

def main():
    st.title("🏡 Brydje - Complete Real Estate Platform")
    st.markdown("**Smart Matching** • **AI Tools** • **Lead Management**")
    
    # Sidebar for mode selection
    with st.sidebar:
        st.header("🎯 Platform Mode")
        
        mode = st.radio(
            "Choose your role:",
            ["🏠 I'm Selling (Find Agent)",
             "🏢 I'm an Agent (Find Clients)",
             "📨 Agent Inbox",
             "🚀 Speed-to-Sell Tools"]
        )
        
        st.divider()
        st.info(f"Current mode: {mode}")
    
    # MODE 1: SELLER FINDING AGENTS
    if mode == "🏠 I'm Selling (Find Agent)":
        st.header("Find Your Perfect Agent")
        
        tabs = st.tabs(["📝 Profile", "💘 Swipe", "⭐ Matches"])
        
        # Tab 1: Seller Profile
        with tabs[0]:
            st.subheader("Tell Us About Your Property")
            
            with st.form("seller_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Your Name")
                    email = st.text_input("Email")
                    phone = st.text_input("Phone")
                    timeline = st.selectbox("Timeline", ["ASAP", "1-3 months", "3-6 months"])
                
                with col2:
                    zip_code = st.text_input("Property ZIP", "94105")
                    property_type = st.selectbox("Type", ["Single Family", "Condo", "Townhouse"])
                    home_value = st.number_input("Est. Value", 100000, 5000000, 500000)
                    prefers_digital = st.checkbox("Prefer digital communication")
                
                if st.form_submit_button("Find Agents", type="primary"):
                    # Save profile
                    st.session_state.seller_profile = {
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'timeline': timeline,
                        'zip_code': zip_code,
                        'property_type': property_type,
                        'home_value': home_value,
                        'prefers_digital': prefers_digital,
                        'city': 'San Francisco',
                        'state': 'CA'
                    }
                    
                    # Generate and match agents
                    generator = AgentGenerator()
                    agents = generator.generate_agents_for_location(zip_code, 'San Francisco', 'CA', 20)
                    
                    # Apply ML matching
                    engine = MLMatchingEngine()
                    matched = engine.rank_agents(st.session_state.seller_profile, agents)
                    
                    st.session_state.current_matches = matched
                    st.session_state.swipe_index = 0
                    
                    st.success(f"Found {len(matched)} agents! Go to Swipe tab.")
        
        # Tab 2: Swipe Interface
        with tabs[1]:
            st.subheader("Swipe to Match")
            
            if st.session_state.current_matches:
                total = len(st.session_state.current_matches)
                current = st.session_state.swipe_index
                
                if current < total:
                    agent = st.session_state.current_matches[current]
                    
                    # Progress
                    progress = st.progress(current / total)
                    st.write(f"Agent {current + 1} of {total}")
                    
                    # Agent Card
                    st.markdown(f"### {agent['name']}")
                    st.markdown(f"**{agent['brokerage']}** • {agent['years_experience']} years")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Match Score", f"{agent['match_score']}%")
                        st.metric("Recent Sales", agent['recent_sales'])
                    with col2:
                        st.metric("Rating", f"⭐ {agent['rating']}")
                        st.metric("Tech Score", f"{agent['tech_score']}/100")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("❌ Pass", use_container_width=True):
                            st.session_state.rejected_agents.append(agent)
                            st.session_state.swipe_index += 1
                            st.rerun()
                    
                    with col2:
                        if st.button("⭐ Super", use_container_width=True, type="primary"):
                            agent['super_liked'] = True
                            st.session_state.liked_agents.append(agent)
                            st.session_state.swipe_index += 1
                            st.balloons()
                            st.rerun()
                    
                    with col3:
                        if st.button("💚 Like", use_container_width=True):
                            st.session_state.liked_agents.append(agent)
                            st.session_state.swipe_index += 1
                            st.rerun()
                else:
                    st.success("Done swiping! Check your matches.")
            else:
                st.info("Complete your profile first!")
        
        # Tab 3: Matches
        with tabs[2]:
            st.subheader("Your Matched Agents")
            
            if st.session_state.liked_agents:
                for agent in st.session_state.liked_agents:
                    with st.expander(f"{agent['name']} - {agent['match_score']}%"):
                        st.write(f"📞 {agent['phone']}")
                        st.write(f"✉️ {agent['email']}")
                        st.write(f"🏢 {agent['brokerage']}")
                        
                        if st.button(f"Contact {agent['name']}", key=f"contact_{agent['id']}"):
                            st.info("Contact info displayed above!")
            else:
                st.info("No matches yet. Start swiping!")
    
    # MODE 2: AGENT CUSTOMER ACQUISITION
    elif mode == "🏢 I'm an Agent (Find Clients)":
        st.header("Find Tech-Savvy Agents")
        
        tabs = st.tabs(["🔍 Search", "📧 Campaign"])
        
        with tabs[0]:
            st.subheader("Search by ZIP")
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                search_zip = st.text_input("ZIP Code", "94105")
            with col2:
                min_tech = st.slider("Min Tech Score", 0, 100, 50)
            with col3:
                count = st.number_input("Results", 10, 50, 20)
            
            if st.button("Search Agents", type="primary"):
                # Generate agents
                generator = AgentGenerator()
                agents = generator.generate_agents_for_location(
                    search_zip, "San Francisco", "CA", count
                )
                
                # Filter by tech score
                filtered = [a for a in agents if a['tech_score'] >= min_tech]
                st.session_state.agents_pool = filtered
                
                st.success(f"Found {len(filtered)} agents!")
                
                # Display results
                for agent in filtered[:10]:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{agent['name']}** - {agent['brokerage']}")
                        st.caption(f"Tech: {agent['tech_score']} | Sales: {agent['recent_sales']}")
                    
                    with col2:
                        st.write(agent['phone'])
                    
                    with col3:
                        if st.button("Add", key=f"add_{agent['id']}"):
                            if agent not in st.session_state.selected_agents:
                                st.session_state.selected_agents.append(agent)
                                st.success("Added!")
        
        with tabs[1]:
            st.subheader("Email Campaign")
            
            if st.session_state.selected_agents:
                st.success(f"{len(st.session_state.selected_agents)} agents selected")
                
                template = st.text_area(
                    "Email Template",
                    value="""Hi [Name],\n\nSave $500/month on real estate tools with Brydje.\n\nBest,\n[Your name]""",
                    height=200
                )
                
                if st.button("Export Campaign CSV"):
                    df = pd.DataFrame(st.session_state.selected_agents)
                    csv = df.to_csv(index=False)
                    st.download_button("Download", csv, "campaign.csv", "text/csv")
            else:
                st.info("No agents selected yet.")
    
    # MODE 3: AGENT INBOX
    elif mode == "📨 Agent Inbox":
        st.header("Review Seller Leads")
        
        if 'seller_leads' not in st.session_state:
            st.session_state.seller_leads = []
        if 'accepted_sellers' not in st.session_state:
            st.session_state.accepted_sellers = []
        
        if st.button("Load Sample Leads"):
            # Generate sample seller leads
            leads = []
            for i in range(10):
                lead = {
                    'id': i,
                    'name': f"Seller {i+1}",
                    'property_value': random.randint(300000, 1500000),
                    'timeline': random.choice(['ASAP', '1-3 months']),
                    'commission': 0
                }
                lead['commission'] = lead['property_value'] * 0.03
                leads.append(lead)
            
            st.session_state.seller_leads = leads
            st.success("Loaded 10 leads!")
        
        if st.session_state.seller_leads:
            for lead in st.session_state.seller_leads[:5]:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{lead['name']}**")
                    st.caption(f"${lead['property_value']:,} • {lead['timeline']}")
                
                with col2:
                    st.metric("Commission", f"${lead['commission']:,.0f}")
                
                with col3:
                    if st.button("Accept", key=f"accept_{lead['id']}"):
                        st.session_state.accepted_sellers.append(lead)
                        st.success("Accepted!")
    
    # MODE 4: SPEED-TO-SELL TOOLS
    elif mode == "🚀 Speed-to-Sell Tools":
        st.header("AI-Powered Selling Tools")
        
        tabs = st.tabs(["💰 Price Optimizer", "🎨 Staging AI", "📅 Timeline"])
        
        with tabs[0]:
            st.subheader("Optimize Your Price")
            
            # Initialize state properly
            if 'price_state' not in st.session_state:
                st.session_state.price_state = {
                    'current': 750000,
                    'optimal': None
                }
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Input current price
                current = st.number_input(
                    "Current Price",
                    100000,
                    5000000,
                    st.session_state.price_state['current']
                )
                st.session_state.price_state['current'] = current
                
                if st.button("Optimize Price", type="primary"):
                    # Calculate optimal price
                    optimal = current * random.uniform(0.95, 1.05)
                    st.session_state.price_state['optimal'] = optimal
                    st.success("Analysis complete!")
            
            with col2:
                if st.session_state.price_state['optimal']:
                    optimal = st.session_state.price_state['optimal']
                    current = st.session_state.price_state['current']
                    
                    st.metric(
                        "Optimal Price",
                        f"${optimal:,.0f}",
                        f"{(optimal/current - 1)*100:+.1f}%"
                    )
                    
                    st.metric("Quick Sale", f"${optimal * 0.95:,.0f}")
                    st.metric("Premium", f"${optimal * 1.05:,.0f}")
        
        with tabs[1]:
            st.subheader("Staging Recommendations")
            
            room = st.selectbox("Room", ["Living Room", "Kitchen", "Bedroom"])
            budget = st.slider("Budget", 500, 5000, 1500)
            
            if st.button("Get Staging Plan"):
                st.success(f"Staging plan for {room}:")
                st.write("• Remove clutter")
                st.write("• Add fresh flowers")
                st.write("• Update lighting")
                st.write(f"• Total cost: ${budget * 0.8:.0f}")
        
        with tabs[2]:
            st.subheader("Selling Timeline")
            
            timeline = st.select_slider(
                "Desired Timeline",
                ["7 days", "14 days", "30 days", "60 days"]
            )
            
            if st.button("Generate Plan"):
                st.success(f"Your {timeline} action plan:")
                
                if "7 days" in timeline:
                    st.write("**Day 1**: Professional photos")
                    st.write("**Day 2**: List on MLS")
                    st.write("**Day 3-4**: Social media blast")
                    st.write("**Day 5-6**: Open houses")
                    st.write("**Day 7**: Review offers")
                else:
                    st.write("**Week 1**: Preparation and staging")
                    st.write("**Week 2**: Marketing launch")
                    st.write("**Week 3+**: Showings and offers")

if __name__ == "__main__":
    main()
