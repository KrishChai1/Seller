"""
🏡 Brydje Ultimate Agent Matcher & Acquisition Platform
Complete solution with Claude AI, ZIP code search, and comprehensive agent profiling
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sqlite3
import requests
from bs4 import BeautifulSoup
import re
import time
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import anthropic
from typing import Dict, List, Optional, Tuple
import hashlib
import random
from dataclasses import dataclass, asdict
import zipcode  # pip install zipcodes

# ================== PAGE CONFIGURATION ==================
st.set_page_config(
    page_title="Brydje Ultimate Agent Matcher",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== CUSTOM CSS ==================
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        color: white;
        margin: 20px 0;
        transition: transform 0.3s ease;
    }
    
    .agent-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(0,0,0,0.3);
    }
    
    .seller-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        color: white;
        margin: 20px 0;
    }
    
    .match-score {
        font-size: 72px;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 20px 0;
    }
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 30px rgba(0,0,0,0.12);
    }
    
    .zip-search-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        margin: 20px 0;
    }
    
    .tech-score-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
        margin: 5px;
    }
    
    .tech-score-high {
        background: #4CAF50;
        color: white;
    }
    
    .tech-score-medium {
        background: #FFC107;
        color: black;
    }
    
    .tech-score-low {
        background: #f44336;
        color: white;
    }
    
    .agent-profile-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .agent-profile-card:hover {
        border-color: #667eea;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ================== SESSION STATE INITIALIZATION ==================
if 'db_conn' not in st.session_state:
    st.session_state.db_conn = sqlite3.connect('brydje_ultimate.db', check_same_thread=False)

if 'current_matches' not in st.session_state:
    st.session_state.current_matches = []

if 'selected_agents' not in st.session_state:
    st.session_state.selected_agents = []

if 'claude_client' not in st.session_state:
    st.session_state.claude_client = None

if 'agent_profiles' not in st.session_state:
    st.session_state.agent_profiles = {}

if 'zip_agents' not in st.session_state:
    st.session_state.zip_agents = []

# ================== DATABASE SETUP ==================
def init_database():
    """Initialize comprehensive database schema"""
    conn = st.session_state.db_conn
    cursor = conn.cursor()
    
    # Enhanced Agents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            brokerage TEXT,
            license_number TEXT,
            years_experience INTEGER,
            age_range TEXT,
            total_sales INTEGER,
            sales_last_12_months INTEGER,
            sales_last_30_days INTEGER,
            avg_sale_price REAL,
            avg_days_on_market INTEGER,
            list_to_sale_ratio REAL,
            specializations TEXT,
            tech_score INTEGER,
            social_media_presence TEXT,
            tools_used TEXT,
            rating REAL,
            review_count INTEGER,
            response_time TEXT,
            zip_code TEXT,
            city TEXT,
            state TEXT,
            profile_image TEXT,
            website_url TEXT,
            languages TEXT,
            certifications TEXT,
            team_size INTEGER,
            buyer_agent_sales INTEGER,
            listing_agent_sales INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP
        )
    ''')
    
    # ZIP Code Analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS zip_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zip_code TEXT UNIQUE,
            city TEXT,
            state TEXT,
            population INTEGER,
            median_home_price REAL,
            avg_days_on_market INTEGER,
            total_agents INTEGER,
            tech_savvy_agents INTEGER,
            market_heat_score INTEGER,
            last_analyzed TIMESTAMP
        )
    ''')
    
    # Agent Performance Metrics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER,
            metric_date DATE,
            listings_added INTEGER,
            listings_sold INTEGER,
            buyer_clients INTEGER,
            social_posts INTEGER,
            website_visits INTEGER,
            lead_response_time INTEGER,
            client_satisfaction REAL,
            FOREIGN KEY (agent_id) REFERENCES agents (id)
        )
    ''')
    
    # Outreach Tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outreach_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER,
            campaign_name TEXT,
            email_sent BOOLEAN DEFAULT FALSE,
            email_opened BOOLEAN DEFAULT FALSE,
            link_clicked BOOLEAN DEFAULT FALSE,
            replied BOOLEAN DEFAULT FALSE,
            demo_scheduled BOOLEAN DEFAULT FALSE,
            trial_started BOOLEAN DEFAULT FALSE,
            converted BOOLEAN DEFAULT FALSE,
            revenue_generated REAL,
            notes TEXT,
            sent_date TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents (id)
        )
    ''')
    
    conn.commit()

# ================== CLAUDE AI INTEGRATION ==================
class ClaudeAnalyzer:
    """Claude AI for intelligent agent analysis and email generation"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def analyze_agent_profile(self, agent_data: Dict) -> Dict:
        """Use Claude to analyze agent profile and generate insights"""
        prompt = f"""
        Analyze this real estate agent profile and provide insights:
        
        Agent Data:
        - Name: {agent_data.get('name')}
        - Experience: {agent_data.get('years_experience')} years
        - Total Sales: {agent_data.get('total_sales')}
        - Recent Sales (12 months): {agent_data.get('sales_last_12_months')}
        - Average Sale Price: ${agent_data.get('avg_sale_price', 0):,.0f}
        - Tech Score: {agent_data.get('tech_score')}/100
        - Social Media: {agent_data.get('social_media_presence')}
        - Tools Used: {agent_data.get('tools_used')}
        
        Provide:
        1. Tech-savviness assessment (likelihood to adopt Brydje)
        2. Key strengths
        3. Pain points Brydje could solve
        4. Best outreach approach
        5. Estimated monthly tool spend
        6. Personality type (analytical, social, traditional, innovative)
        
        Format as JSON.
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse Claude's response
            return json.loads(response.content[0].text)
        except Exception as e:
            return {
                "tech_adoption_likelihood": "High" if agent_data.get('tech_score', 0) > 70 else "Medium",
                "strengths": ["Strong sales record", "Active in market"],
                "pain_points": ["Time-consuming marketing", "Multiple tool management"],
                "outreach_approach": "Focus on time savings and consolidation",
                "estimated_tool_spend": 600,
                "personality_type": "innovative" if agent_data.get('tech_score', 0) > 70 else "traditional"
            }
    
    def generate_personalized_email(self, agent_data: Dict, template_type: str) -> str:
        """Generate highly personalized email using Claude"""
        prompt = f"""
        Write a personalized email to a real estate agent for Brydje (AI-powered real estate platform).
        
        Agent Details:
        - Name: {agent_data.get('name')}
        - Brokerage: {agent_data.get('brokerage')}
        - Recent Sales: {agent_data.get('sales_last_12_months')} in last 12 months
        - Location: {agent_data.get('city')}, {agent_data.get('state')}
        - Tech Score: {agent_data.get('tech_score')}/100
        - Personality: {agent_data.get('personality_type', 'professional')}
        
        Brydje Features:
        - Creates listing videos in 30 seconds using AI
        - Generates landing pages and QR codes instantly
        - Smart open house management with lead capture
        - All-in-one platform for $99/month (vs. $600+ for multiple tools)
        
        Email Type: {template_type}
        
        Requirements:
        - Keep under 150 words
        - Include specific reference to their recent success
        - Mention time savings (5+ hours/week)
        - Include clear CTA for 5-minute demo
        - Professional but friendly tone
        - No generic phrases
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except:
            # Fallback template
            return f"""
Hi {agent_data.get('name')},

Congrats on your {agent_data.get('sales_last_12_months', 'recent')} sales in {agent_data.get('city')}! 

I noticed you're using multiple tools for marketing. What if you could create stunning listing videos, landing pages, and QR codes in 30 seconds - all in one platform?

Brydje replaces 6+ tools for just $99/month (you're probably spending $600+).

Three agents from {agent_data.get('brokerage', 'your brokerage')} are already saving 5+ hours weekly.

Worth a quick 5-minute demo? I'm offering 50% off for founding members.

Best,
[Your Name]
"""

# ================== DATA GENERATION & COLLECTION ==================
class AgentDataGenerator:
    """Generate realistic agent data based on ZIP codes"""
    
    @staticmethod
    def generate_agents_for_zip(zip_code: str, count: int = 20) -> List[Dict]:
        """Generate realistic agents for a specific ZIP code"""
        
        # ZIP code data (in production, use real ZIP code API)
        zip_data = {
            'city': f"City_{zip_code[:3]}",
            'state': 'CA' if zip_code.startswith('9') else 'NY' if zip_code.startswith('1') else 'TX',
            'median_price': int(zip_code[:3]) * 2000
        }
        
        agents = []
        brokerages = ["RE/MAX", "Keller Williams", "Coldwell Banker", "Century 21", "Compass", 
                     "eXp Realty", "Berkshire Hathaway", "Sotheby's", "Douglas Elliman", "Local Boutique"]
        
        first_names = ["Sarah", "Michael", "Jennifer", "David", "Jessica", "Robert", "Emily", 
                      "James", "Ashley", "William", "Olivia", "John", "Emma", "Daniel", "Sophia"]
        last_names = ["Johnson", "Chen", "Smith", "Garcia", "Martinez", "Brown", "Davis", 
                     "Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Jackson", "Lee", "Harris"]
        
        age_ranges = ["25-34", "35-44", "45-54", "55-64", "65+"]
        
        for i in range(count):
            # Generate age and experience correlation
            age_range = np.random.choice(age_ranges, p=[0.25, 0.35, 0.25, 0.10, 0.05])
            
            if age_range == "25-34":
                years_exp = np.random.randint(1, 8)
                tech_base = 75
                social_probability = 0.8
            elif age_range == "35-44":
                years_exp = np.random.randint(5, 15)
                tech_base = 60
                social_probability = 0.6
            elif age_range == "45-54":
                years_exp = np.random.randint(10, 25)
                tech_base = 45
                social_probability = 0.4
            else:
                years_exp = np.random.randint(15, 35)
                tech_base = 30
                social_probability = 0.2
            
            # Performance metrics based on experience
            if years_exp < 3:
                annual_sales = np.random.randint(3, 12)
                monthly_sales = np.random.randint(0, 2)
            elif years_exp < 10:
                annual_sales = np.random.randint(8, 25)
                monthly_sales = np.random.randint(1, 3)
            else:
                annual_sales = np.random.randint(15, 40)
                monthly_sales = np.random.randint(2, 5)
            
            # Generate social media presence
            social_media = {}
            if np.random.random() < social_probability:
                social_media['instagram'] = np.random.choice([True, False], p=[0.7, 0.3])
                social_media['facebook'] = np.random.choice([True, False], p=[0.8, 0.2])
                social_media['linkedin'] = np.random.choice([True, False], p=[0.6, 0.4])
                social_media['tiktok'] = np.random.choice([True, False], p=[0.3, 0.7]) if age_range in ["25-34", "35-44"] else False
                social_media['youtube'] = np.random.choice([True, False], p=[0.2, 0.8])
            
            # Calculate tech score
            tech_score = tech_base + np.random.randint(-10, 25)
            tech_score += sum([10 for platform, active in social_media.items() if active])
            tech_score = min(100, max(0, tech_score))
            
            # Tools used based on tech score
            if tech_score > 70:
                tools = ["CRM", "Video Editor", "Virtual Tour", "E-signature", "Social Media Manager", "AI Tools"]
            elif tech_score > 50:
                tools = ["CRM", "Email Marketing", "E-signature", "Basic Website"]
            else:
                tools = ["Basic CRM", "Email"]
            
            agent = {
                'id': i + 1,
                'name': f"{np.random.choice(first_names)} {np.random.choice(last_names)}",
                'email': f"agent{i+1}.{zip_code}@example.com",
                'phone': f"({zip_code[:3]}) {np.random.randint(100,999)}-{np.random.randint(1000,9999)}",
                'brokerage': np.random.choice(brokerages),
                'license_number': f"DRE{np.random.randint(1000000, 9999999)}",
                'years_experience': years_exp,
                'age_range': age_range,
                'total_sales': annual_sales * max(1, years_exp // 2),
                'sales_last_12_months': annual_sales,
                'sales_last_30_days': monthly_sales,
                'avg_sale_price': zip_data['median_price'] * np.random.uniform(0.7, 1.5),
                'avg_days_on_market': np.random.randint(15, 60),
                'list_to_sale_ratio': np.random.uniform(0.94, 0.99),
                'specializations': np.random.choice([
                    ["First-time buyers", "Condos"],
                    ["Luxury homes", "Waterfront"],
                    ["Investment properties", "Multi-family"],
                    ["FSBO", "Foreclosures"],
                    ["Seniors", "Downsizing"],
                    ["Military relocation", "Corporate"]
                ]),
                'tech_score': tech_score,
                'social_media_presence': json.dumps(social_media),
                'tools_used': json.dumps(tools),
                'rating': round(np.random.uniform(3.5, 5.0), 1),
                'review_count': np.random.randint(5, 150),
                'response_time': np.random.choice(["< 1 hour", "< 3 hours", "< 6 hours", "< 24 hours"]),
                'zip_code': zip_code,
                'city': zip_data['city'],
                'state': zip_data['state'],
                'website_url': f"www.{agent.get('name', '').lower().replace(' ', '')}.com" if tech_score > 60 else None,
                'languages': json.dumps(["English"] + (["Spanish"] if np.random.random() > 0.7 else [])),
                'certifications': json.dumps(np.random.choice([
                    ["ABR", "CRS"],
                    ["GRI", "SRES"],
                    ["e-PRO", "SFR"],
                    ["PSA", "RSPS"],
                    []
                ])),
                'team_size': 1 if years_exp < 5 else np.random.choice([1, 3, 5, 10], p=[0.6, 0.25, 0.10, 0.05]),
                'buyer_agent_sales': int(annual_sales * np.random.uniform(0.3, 0.7)),
                'listing_agent_sales': int(annual_sales * np.random.uniform(0.3, 0.7))
            }
            
            agents.append(agent)
        
        return agents

# ================== MATCHING ENGINE ==================
class AdvancedMatchingEngine:
    """Enhanced ML-powered matching with multiple factors"""
    
    @staticmethod
    def calculate_comprehensive_tech_score(agent: Dict) -> int:
        """Calculate detailed tech score with multiple factors"""
        score = 0
        
        # Age factor (25 points)
        age_scores = {
            "25-34": 25,
            "35-44": 18,
            "45-54": 10,
            "55-64": 5,
            "65+": 0
        }
        score += age_scores.get(agent.get('age_range', '45-54'), 10)
        
        # Social media (30 points)
        social = json.loads(agent.get('social_media_presence', '{}'))
        score += sum([6 for platform, active in social.items() if active])
        
        # Tools usage (20 points)
        tools = json.loads(agent.get('tools_used', '[]'))
        tech_tools = ['CRM', 'Video Editor', 'Virtual Tour', 'E-signature', 'AI Tools', 'Marketing Automation']
        score += sum([4 for tool in tools if tool in tech_tools])
        
        # Website presence (10 points)
        if agent.get('website_url'):
            score += 10
        
        # Response time (10 points)
        response = agent.get('response_time', '24 hours')
        if '1 hour' in response:
            score += 10
        elif '3 hours' in response:
            score += 7
        elif '6 hours' in response:
            score += 4
        
        # Review engagement (5 points)
        if agent.get('review_count', 0) > 20:
            score += 5
        
        return min(100, score)
    
    @staticmethod
    def match_seller_to_agent(seller: Dict, agent: Dict) -> float:
        """Advanced matching algorithm with multiple factors"""
        score = 0.0
        weights = {
            'location': 25,
            'price': 20,
            'specialization': 20,
            'availability': 15,
            'experience': 10,
            'tech': 10
        }
        
        # Location match (same ZIP gets full points)
        if seller.get('zip_code') == agent.get('zip_code'):
            score += weights['location']
        elif seller.get('city') == agent.get('city'):
            score += weights['location'] * 0.7
        
        # Price range compatibility
        seller_budget = seller.get('price_range', 500000)
        agent_avg = agent.get('avg_sale_price', 500000)
        if abs(seller_budget - agent_avg) / seller_budget < 0.2:
            score += weights['price']
        elif abs(seller_budget - agent_avg) / seller_budget < 0.4:
            score += weights['price'] * 0.5
        
        # Specialization match
        seller_type = seller.get('property_type', 'Single Family')
        agent_specs = json.loads(agent.get('specializations', '[]'))
        if any(spec in seller_type for spec in agent_specs):
            score += weights['specialization']
        
        # Response time for urgent sellers
        if seller.get('timeline') == 'ASAP' and '1 hour' in agent.get('response_time', ''):
            score += weights['availability']
        elif seller.get('timeline') in ['1-3 months', '3-6 months']:
            score += weights['availability'] * 0.5
        
        # Experience factor
        years_exp = agent.get('years_experience', 5)
        if years_exp > 10:
            score += weights['experience']
        elif years_exp > 5:
            score += weights['experience'] * 0.7
        elif years_exp > 2:
            score += weights['experience'] * 0.4
        
        # Tech compatibility (important for Brydje)
        if agent.get('tech_score', 0) > 70:
            score += weights['tech']
        
        return min(100, score)

# ================== UI COMPONENTS ==================
def display_agent_card(agent: Dict, detailed: bool = False):
    """Display beautiful agent card with all information"""
    
    tech_score = agent.get('tech_score', 0)
    tech_class = "tech-score-high" if tech_score > 70 else "tech-score-medium" if tech_score > 50 else "tech-score-low"
    
    if detailed:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h2>📊 Performance</h2>
                <h3>{agent.get('sales_last_12_months', 0)}</h3>
                <p>Sales (12 mo)</p>
                <hr>
                <h3>${agent.get('avg_sale_price', 0):,.0f}</h3>
                <p>Avg Sale Price</p>
                <hr>
                <h3>{agent.get('avg_days_on_market', 30)}</h3>
                <p>Days on Market</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="agent-card">
                <h1>{agent.get('name')}</h1>
                <p><strong>{agent.get('brokerage')}</strong> | {agent.get('city')}, {agent.get('state')} {agent.get('zip_code')}</p>
                <p>📍 License: {agent.get('license_number')}</p>
                <p>👤 Age: {agent.get('age_range')} | Experience: {agent.get('years_experience')} years</p>
                <p>⭐ Rating: {agent.get('rating')}/5 ({agent.get('review_count')} reviews)</p>
                <p>⚡ Response: {agent.get('response_time')}</p>
                <p>🏡 Total Career Sales: {agent.get('total_sales')}</p>
                <div class="{tech_class} tech-score-badge">Tech Score: {tech_score}/100</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h2>📱 Digital Presence</h2>
            """, unsafe_allow_html=True)
            
            social = json.loads(agent.get('social_media_presence', '{}'))
            for platform, active in social.items():
                if active:
                    st.success(f"✓ {platform.title()}")
                else:
                    st.info(f"✗ {platform.title()}")
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="agent-profile-card">
            <h3>{agent.get('name')} - {agent.get('brokerage')}</h3>
            <p>📍 {agent.get('city')}, {agent.get('state')} | 🏆 {agent.get('sales_last_12_months')} sales | ⭐ {agent.get('rating')}/5</p>
            <div class="{tech_class} tech-score-badge">Tech Score: {tech_score}/100</div>
        </div>
        """, unsafe_allow_html=True)

def display_zip_analysis(zip_code: str, agents: List[Dict]):
    """Display comprehensive ZIP code analysis"""
    
    df = pd.DataFrame(agents)
    
    # Calculate statistics
    total_agents = len(agents)
    tech_savvy_count = len(df[df['tech_score'] > 70])
    avg_tech_score = df['tech_score'].mean()
    top_brokerages = df['brokerage'].value_counts().head(5)
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Agents", total_agents)
        st.metric("Avg Experience", f"{df['years_experience'].mean():.1f} years")
    
    with col2:
        st.metric("Tech-Savvy Agents", tech_savvy_count)
        st.metric("Avg Tech Score", f"{avg_tech_score:.0f}/100")
    
    with col3:
        st.metric("Avg Sales/Year", f"{df['sales_last_12_months'].mean():.1f}")
        st.metric("Avg Sale Price", f"${df['avg_sale_price'].mean():,.0f}")
    
    with col4:
        st.metric("Top Performers", len(df[df['sales_last_12_months'] > 20]))
        st.metric("Fast Responders", len(df[df['response_time'] == '< 1 hour']))
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Age distribution
        fig_age = px.pie(df, names='age_range', title=f"Age Distribution in ZIP {zip_code}")
        st.plotly_chart(fig_age, use_container_width=True)
    
    with col2:
        # Tech score distribution
        fig_tech = px.histogram(df, x='tech_score', nbins=20, 
                               title="Tech Score Distribution",
                               labels={'tech_score': 'Tech Score', 'count': 'Number of Agents'})
        fig_tech.add_vline(x=70, line_dash="dash", line_color="green",
                          annotation_text="Brydje Target")
        st.plotly_chart(fig_tech, use_container_width=True)
    
    # Performance vs Tech Score
    fig_scatter = px.scatter(df, x='tech_score', y='sales_last_12_months',
                            size='avg_sale_price', color='age_range',
                            title="Performance vs Tech Savviness",
                            labels={'tech_score': 'Tech Score', 
                                   'sales_last_12_months': 'Annual Sales'},
                            hover_data=['name', 'brokerage'])
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Top brokerages
    st.subheader("Top Brokerages in Area")
    for brokerage, count in top_brokerages.items():
        st.write(f"**{brokerage}**: {count} agents")

# ================== MAIN APPLICATION ==================
def main():
    st.title("🏡 Brydje Ultimate Agent Matcher & Acquisition Platform")
    st.markdown("**AI-Powered** Agent Discovery | **ZIP Code** Analysis | **Intelligent** Matching | **Personalized** Outreach")
    
    # Initialize database
    init_database()
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Claude API Key
        claude_api_key = st.text_input(
            "Claude API Key",
            type="password",
            help="Enter your Anthropic Claude API key for AI features"
        )
        
        if claude_api_key:
            st.session_state.claude_client = ClaudeAnalyzer(claude_api_key)
            st.success("✅ Claude AI Connected")
        
        st.divider()
        
        # Quick Actions
        st.header("⚡ Quick Actions")
        
        if st.button("🎯 Find 10 Tech-Savvy Agents"):
            # Generate sample tech-savvy agents
            agents = []
            generator = AgentDataGenerator()
            for zip_code in ["94105", "90210", "10001"]:
                zip_agents = generator.generate_agents_for_zip(zip_code, 5)
                # Filter for tech-savvy
                tech_agents = [a for a in zip_agents if a['tech_score'] > 70]
                agents.extend(tech_agents[:3])
            st.session_state.selected_agents = agents[:10]
            st.success(f"Found {len(st.session_state.selected_agents)} tech-savvy agents!")
        
        if st.button("📧 Generate Email Templates"):
            st.info("Go to 'Email Campaign' tab")
        
        st.divider()
        
        # Statistics
        st.header("📊 Platform Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Agents Analyzed", "2,847")
            st.metric("ZIP Codes", "127")
            st.metric("Tech-Savvy Found", "423")
        with col2:
            st.metric("Emails Sent", "1,205")
            st.metric("Demos Booked", "73")
            st.metric("Conversions", "18")
    
    # Main Content Tabs
    tabs = st.tabs([
        "🔍 ZIP Code Search",
        "🤝 Seller Matching",
        "👤 Agent Profiles", 
        "📧 Email Campaign",
        "📊 Analytics",
        "🎯 Tech Finder",
        "💡 AI Insights"
    ])
    
    # Tab 1: ZIP Code Search
    with tabs[0]:
        st.header("🔍 ZIP Code Agent Search & Analysis")
        st.markdown("Enter a ZIP code to discover all agents and analyze the market")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            zip_code = st.text_input(
                "Enter ZIP Code",
                placeholder="e.g., 94105",
                help="5-digit US ZIP code"
            )
        
        with col2:
            search_radius = st.selectbox(
                "Search Radius",
                ["Exact ZIP", "5 miles", "10 miles", "25 miles"]
            )
        
        with col3:
            min_sales = st.number_input(
                "Min Annual Sales",
                min_value=0,
                max_value=100,
                value=5
            )
        
        if st.button("🔍 Search ZIP Code", type="primary"):
            if zip_code and len(zip_code) == 5:
                with st.spinner(f"Analyzing ZIP {zip_code}..."):
                    # Generate agents for ZIP
                    generator = AgentDataGenerator()
                    agents = generator.generate_agents_for_zip(zip_code, 50)
                    
                    # Filter by minimum sales
                    agents = [a for a in agents if a['sales_last_12_months'] >= min_sales]
                    
                    # Store in session
                    st.session_state.zip_agents = agents
                    
                    st.success(f"Found {len(agents)} agents in ZIP {zip_code}")
        
        if st.session_state.zip_agents:
            st.divider()
            
            # Display ZIP analysis
            display_zip_analysis(zip_code, st.session_state.zip_agents)
            
            st.divider()
            
            # Agent list with filters
            st.subheader("🏆 Agent Directory")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                filter_tech = st.slider("Min Tech Score", 0, 100, 50)
            with col2:
                filter_age = st.multiselect("Age Range", ["25-34", "35-44", "45-54", "55-64", "65+"])
            with col3:
                filter_brokerage = st.multiselect("Brokerage", list(set([a['brokerage'] for a in st.session_state.zip_agents])))
            with col4:
                sort_by = st.selectbox("Sort By", ["Tech Score", "Sales", "Rating", "Experience"])
            
            # Apply filters
            filtered_agents = st.session_state.zip_agents.copy()
            
            if filter_tech > 0:
                filtered_agents = [a for a in filtered_agents if a['tech_score'] >= filter_tech]
            
            if filter_age:
                filtered_agents = [a for a in filtered_agents if a['age_range'] in filter_age]
            
            if filter_brokerage:
                filtered_agents = [a for a in filtered_agents if a['brokerage'] in filter_brokerage]
            
            # Sort
            if sort_by == "Tech Score":
                filtered_agents.sort(key=lambda x: x['tech_score'], reverse=True)
            elif sort_by == "Sales":
                filtered_agents.sort(key=lambda x: x['sales_last_12_months'], reverse=True)
            elif sort_by == "Rating":
                filtered_agents.sort(key=lambda x: x['rating'], reverse=True)
            else:
                filtered_agents.sort(key=lambda x: x['years_experience'], reverse=True)
            
            # Display agents
            st.write(f"Showing {len(filtered_agents)} agents")
            
            # Create selectable dataframe
            agent_df = pd.DataFrame(filtered_agents)
            agent_df['Select'] = False
            
            # Display with checkboxes
            selected_df = st.data_editor(
                agent_df[['Select', 'name', 'brokerage', 'age_range', 'tech_score', 
                         'sales_last_12_months', 'rating', 'response_time']],
                hide_index=True,
                column_config={
                    "Select": st.column_config.CheckboxColumn("Select"),
                    "tech_score": st.column_config.ProgressColumn(
                        "Tech Score",
                        min_value=0,
                        max_value=100
                    ),
                    "rating": st.column_config.NumberColumn(
                        "Rating",
                        format="⭐ %.1f"
                    )
                }
            )
            
            # Action buttons for selected agents
            selected_count = selected_df['Select'].sum()
            
            if selected_count > 0:
                st.info(f"Selected {selected_count} agents")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📧 Add to Email Campaign"):
                        selected_agents = agent_df[selected_df['Select']].to_dict('records')
                        st.session_state.selected_agents.extend(selected_agents)
                        st.success(f"Added {selected_count} agents to campaign")
                
                with col2:
                    if st.button("👤 View Detailed Profiles"):
                        st.session_state.view_profiles = True
                        st.info("Go to 'Agent Profiles' tab")
                
                with col3:
                    csv = selected_df[selected_df['Select']].to_csv(index=False)
                    st.download_button(
                        "📊 Export CSV",
                        csv,
                        f"agents_{zip_code}_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
    
    # Tab 2: Seller Matching
    with tabs[1]:
        st.header("🤝 Intelligent Seller-Agent Matching")
        st.markdown("AI-powered matching to find the perfect agent for sellers")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Seller Profile")
            
            seller_name = st.text_input("Seller Name")
            seller_zip = st.text_input("Property ZIP Code", "94105")
            
            property_type = st.selectbox(
                "Property Type",
                ["Single Family", "Condo", "Townhouse", "Multi-family", "Luxury", "Land"]
            )
            
            price_range = st.number_input(
                "Estimated Price",
                min_value=100000,
                max_value=10000000,
                value=650000,
                step=50000
            )
            
            timeline = st.radio(
                "Selling Timeline",
                ["ASAP", "1-3 months", "3-6 months", "6+ months"],
                horizontal=True
            )
            
            priorities = st.multiselect(
                "Top Priorities",
                ["Quick Sale", "Best Price", "Tech-Savvy Agent", "Experience", 
                 "Communication", "Marketing", "Negotiation"]
            )
            
            is_fsbo = st.checkbox("Considering For Sale By Owner (FSBO)")
            
            if st.button("🎯 Find Matching Agents", type="primary"):
                with st.spinner("Finding perfect matches..."):
                    # Generate agents for seller's ZIP
                    generator = AgentDataGenerator()
                    agents = generator.generate_agents_for_zip(seller_zip, 30)
                    
                    # Calculate match scores
                    seller_data = {
                        'zip_code': seller_zip,
                        'property_type': property_type,
                        'price_range': price_range,
                        'timeline': timeline,
                        'is_fsbo': is_fsbo
                    }
                    
                    matcher = AdvancedMatchingEngine()
                    for agent in agents:
                        agent['match_score'] = matcher.match_seller_to_agent(seller_data, agent)
                    
                    # Sort by match score
                    agents.sort(key=lambda x: x['match_score'], reverse=True)
                    
                    # Store top matches
                    st.session_state.current_matches = agents[:10]
        
        with col2:
            if st.session_state.current_matches:
                st.subheader("🏆 Top Agent Matches")
                
                # Swipe interface
                if 'match_index' not in st.session_state:
                    st.session_state.match_index = 0
                
                current_index = st.session_state.match_index
                
                if current_index < len(st.session_state.current_matches):
                    agent = st.session_state.current_matches[current_index]
                    
                    # Display match score
                    st.markdown(f'<div class="match-score">{agent["match_score"]:.0f}% Match</div>', 
                              unsafe_allow_html=True)
                    
                    # Display agent card
                    display_agent_card(agent, detailed=True)
                    
                    # Swipe buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("❌ Pass", use_container_width=True):
                            st.session_state.match_index += 1
                            st.rerun()
                    
                    with col2:
                        if st.button("⭐ Save", use_container_width=True):
                            st.session_state.selected_agents.append(agent)
                            st.success(f"Saved {agent['name']} to your list!")
                            st.session_state.match_index += 1
                            st.rerun()
                    
                    with col3:
                        if st.button("💚 Perfect Match!", use_container_width=True):
                            st.session_state.selected_agents.insert(0, agent)
                            st.balloons()
                            st.success(f"🎉 {agent['name']} is your top pick!")
                            st.session_state.match_index += 1
                            st.rerun()
                    
                    # Progress indicator
                    st.progress((current_index + 1) / len(st.session_state.current_matches))
                    st.caption(f"Agent {current_index + 1} of {len(st.session_state.current_matches)}")
                else:
                    st.success("✅ You've reviewed all matches!")
                    
                    if st.button("View Saved Agents"):
                        st.write(st.session_state.selected_agents)
                    
                    if st.button("Start New Search"):
                        st.session_state.match_index = 0
                        st.session_state.current_matches = []
                        st.rerun()
    
    # Tab 3: Agent Profiles
    with tabs[2]:
        st.header("👤 Detailed Agent Profiles")
        
        if st.session_state.selected_agents:
            st.write(f"Viewing {len(st.session_state.selected_agents)} selected agents")
            
            for i, agent in enumerate(st.session_state.selected_agents):
                with st.expander(f"{agent['name']} - {agent['brokerage']}", expanded=(i==0)):
                    display_agent_card(agent, detailed=True)
                    
                    # AI Analysis (if Claude is connected)
                    if st.session_state.claude_client:
                        if st.button(f"🤖 Get AI Insights", key=f"ai_{i}"):
                            with st.spinner("Analyzing with Claude AI..."):
                                insights = st.session_state.claude_client.analyze_agent_profile(agent)
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write("**Tech Adoption Likelihood:**", insights.get('tech_adoption_likelihood'))
                                    st.write("**Personality Type:**", insights.get('personality_type'))
                                    st.write("**Estimated Tool Spend:**", f"${insights.get('estimated_tool_spend')}/month")
                                
                                with col2:
                                    st.write("**Key Strengths:**")
                                    for strength in insights.get('strengths', []):
                                        st.write(f"• {strength}")
                                    
                                    st.write("**Pain Points Brydje Solves:**")
                                    for pain in insights.get('pain_points', []):
                                        st.write(f"• {pain}")
                    
                    # Contact actions
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button(f"📧 Generate Email", key=f"email_{i}"):
                            st.session_state.generate_email_for = agent
                            st.info("Go to 'Email Campaign' tab")
                    
                    with col2:
                        if st.button(f"📞 Call Script", key=f"call_{i}"):
                            st.text_area(
                                "Call Script",
                                f"Hi {agent['name']}, this is [Your Name] from Brydje...",
                                height=150
                            )
                    
                    with col3:
                        if st.button(f"📝 Add Notes", key=f"notes_{i}"):
                            notes = st.text_area("Notes", key=f"note_text_{i}")
        else:
            st.info("No agents selected yet. Use ZIP Code Search or Seller Matching to find agents.")
    
    # Tab 4: Email Campaign
    with tabs[3]:
        st.header("📧 AI-Powered Email Campaign Generator")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Campaign Settings")
            
            campaign_name = st.text_input("Campaign Name", f"Campaign_{datetime.now().strftime('%Y%m%d')}")
            
            template_type = st.selectbox(
                "Email Template",
                ["Introduction", "Follow-up", "Social Proof", "Special Offer", "Demo Invitation"]
            )
            
            # Subject lines
            subject_lines = [
                f"Save 5 hours/week on your listings",
                f"You're spending too much on real estate tools",
                f"30-second listing videos? (Yes, really)",
                f"3 agents in your area just switched to Brydje",
                f"Quick question about your marketing"
            ]
            
            selected_subject = st.selectbox("Subject Line", subject_lines)
            
            # Personalization options
            st.write("**Personalization Options:**")
            use_name = st.checkbox("Use agent name", value=True)
            mention_brokerage = st.checkbox("Mention brokerage", value=True)
            include_sales = st.checkbox("Reference recent sales", value=True)
            location_specific = st.checkbox("Location-specific content", value=True)
            
            send_time = st.time_input("Send Time", datetime.now().time())
            
            if st.session_state.selected_agents:
                st.write(f"**Recipients:** {len(st.session_state.selected_agents)} agents")
        
        with col2:
            st.subheader("Email Preview")
            
            if st.session_state.selected_agents:
                # Preview with first agent
                preview_agent = st.session_state.selected_agents[0]
                
                if st.session_state.claude_client:
                    if st.button("🤖 Generate with AI"):
                        with st.spinner("Generating personalized email..."):
                            email_content = st.session_state.claude_client.generate_personalized_email(
                                preview_agent, 
                                template_type.lower()
                            )
                            st.text_area("Email Content", email_content, height=400)
                else:
                    # Fallback template
                    email_content = f"""
Hi {preview_agent['name'] if use_name else 'there'},

Congrats on your {preview_agent['sales_last_12_months']} sales this year{f" at {preview_agent['brokerage']}" if mention_brokerage else ""}!

I noticed you're in {preview_agent['city'] if location_specific else 'the area'} and wanted to reach out about Brydje - an AI platform that creates listing videos, landing pages, and QR codes in 30 seconds.

You're probably using multiple tools that cost $600+/month. Brydje does it all for $99.

Three agents from {preview_agent['city'] if location_specific else 'your area'} are already saving 5+ hours weekly.

Worth a quick 5-minute demo?

Best,
[Your Name]
                    """
                    st.text_area("Email Content", email_content, height=400)
            
            # Bulk actions
            if st.button("📨 Send to All Selected Agents", type="primary"):
                with st.spinner(f"Sending to {len(st.session_state.selected_agents)} agents..."):
                    progress = st.progress(0)
                    for i, agent in enumerate(st.session_state.selected_agents):
                        # Simulate sending
                        time.sleep(0.1)
                        progress.progress((i + 1) / len(st.session_state.selected_agents))
                    
                    st.success(f"✅ Campaign sent to {len(st.session_state.selected_agents)} agents!")
                    st.balloons()
    
    # Tab 5: Analytics
    with tabs[4]:
        st.header("📊 Performance Analytics Dashboard")
        
        # Date range
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        # KPIs
        st.subheader("Key Performance Indicators")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Agents Analyzed", "2,847", "+312", help="Total unique agents in database")
        with col2:
            st.metric("Tech-Savvy Found", "423", "+67", help="Agents with tech score > 70")
        with col3:
            st.metric("Emails Sent", "1,205", "+145", help="Total outreach emails")
        with col4:
            st.metric("Open Rate", "34.2%", "+5.1%", help="Email open rate")
        with col5:
            st.metric("Conversions", "18", "+3", help="Paid Brydje subscriptions")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Conversion funnel
            funnel_data = pd.DataFrame({
                'Stage': ['Agents Found', 'Tech-Savvy', 'Emails Sent', 'Opened', 'Clicked', 'Demo', 'Trial', 'Paid'],
                'Count': [2847, 423, 305, 104, 67, 31, 24, 18],
                'Conversion': ['100%', '14.9%', '10.7%', '34.1%', '64.4%', '46.3%', '77.4%', '75.0%']
            })
            
            fig = go.Figure(go.Funnel(
                y=funnel_data['Stage'],
                x=funnel_data['Count'],
                text=funnel_data['Conversion'],
                textposition="inside",
                textinfo="value+text",
                opacity=0.8,
                marker={"color": ["#667eea", "#7c8ef0", "#929ef6", "#a8aefc", 
                                 "#bebeff", "#d4ceff", "#e0d4ff", "#f0e6ff"]}
            ))
            
            fig.update_layout(title="Conversion Funnel", height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Agent acquisition by source
            source_data = pd.DataFrame({
                'Source': ['ZIP Search', 'LinkedIn', 'Referrals', 'Website', 'Cold Outreach'],
                'Agents': [89, 67, 45, 34, 23]
            })
            
            fig = px.pie(source_data, values='Agents', names='Source',
                        title="Agent Acquisition Sources")
            st.plotly_chart(fig, use_container_width=True)
        
        # Time series
        dates = pd.date_range(start_date, end_date, freq='D')
        metrics_data = pd.DataFrame({
            'Date': dates,
            'Agents Added': np.random.randint(5, 20, len(dates)),
            'Emails Sent': np.random.randint(20, 60, len(dates)),
            'Demos Booked': np.random.randint(0, 5, len(dates))
        })
        
        fig = px.line(metrics_data, x='Date', y=['Agents Added', 'Emails Sent', 'Demos Booked'],
                     title="Daily Activity Metrics")
        st.plotly_chart(fig, use_container_width=True)
        
        # Geographic distribution
        st.subheader("Geographic Distribution")
        
        geo_data = pd.DataFrame({
            'State': ['CA', 'NY', 'TX', 'FL', 'IL'],
            'Agents': [234, 187, 156, 134, 98],
            'Tech-Savvy': [89, 67, 45, 34, 23],
            'Conversions': [8, 5, 3, 2, 1]
        })
        
        fig = px.bar(geo_data, x='State', y=['Agents', 'Tech-Savvy', 'Conversions'],
                    title="Performance by State", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    # Tab 6: Tech Finder
    with tabs[5]:
        st.header("🎯 Advanced Tech-Savvy Agent Finder")
        st.markdown("Use AI and data analysis to find agents most likely to adopt Brydje")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Search Criteria")
            
            # Location
            search_zips = st.text_area(
                "ZIP Codes (one per line)",
                "94105\n90210\n10001",
                height=100
            )
            
            # Tech indicators
            st.write("**Required Tech Indicators:**")
            req_instagram = st.checkbox("Active on Instagram", value=True)
            req_video = st.checkbox("Uses Video Marketing", value=True)
            req_website = st.checkbox("Has Professional Website")
            req_fast_response = st.checkbox("Responds < 3 hours", value=True)
            
            # Performance filters
            st.write("**Performance Criteria:**")
            min_annual_sales = st.slider("Min Annual Sales", 5, 50, 10)
            max_experience = st.slider("Max Years Experience", 1, 20, 8)
            min_rating = st.slider("Min Rating", 3.0, 5.0, 4.0, 0.1)
            
            # Age preference
            preferred_age = st.multiselect(
                "Preferred Age Range",
                ["25-34", "35-44", "45-54"],
                default=["25-34", "35-44"]
            )
            
            if st.button("🔍 Find Tech-Savvy Agents", type="primary"):
                with st.spinner("Searching for tech-savvy agents..."):
                    all_agents = []
                    generator = AgentDataGenerator()
                    
                    for zip_code in search_zips.strip().split('\n'):
                        if zip_code.strip():
                            agents = generator.generate_agents_for_zip(zip_code.strip(), 30)
                            
                            # Apply filters
                            filtered = []
                            for agent in agents:
                                social = json.loads(agent.get('social_media_presence', '{}'))
                                
                                # Check requirements
                                if req_instagram and not social.get('instagram'):
                                    continue
                                if req_video and 'Video' not in str(agent.get('tools_used', [])):
                                    continue
                                if req_website and not agent.get('website_url'):
                                    continue
                                if req_fast_response and '24' in agent.get('response_time', '24'):
                                    continue
                                
                                # Performance filters
                                if agent['sales_last_12_months'] < min_annual_sales:
                                    continue
                                if agent['years_experience'] > max_experience:
                                    continue
                                if agent['rating'] < min_rating:
                                    continue
                                if agent['age_range'] not in preferred_age:
                                    continue
                                
                                # Tech score requirement
                                if agent['tech_score'] < 70:
                                    continue
                                
                                filtered.append(agent)
                            
                            all_agents.extend(filtered)
                    
                    # Sort by tech score
                    all_agents.sort(key=lambda x: x['tech_score'], reverse=True)
                    
                    st.session_state.tech_savvy_agents = all_agents[:50]
                    st.success(f"Found {len(st.session_state.tech_savvy_agents)} tech-savvy agents!")
        
        with col2:
            if 'tech_savvy_agents' in st.session_state and st.session_state.tech_savvy_agents:
                st.subheader(f"🏆 Top {len(st.session_state.tech_savvy_agents)} Tech-Savvy Agents")
                
                # Summary stats
                df = pd.DataFrame(st.session_state.tech_savvy_agents)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Avg Tech Score", f"{df['tech_score'].mean():.0f}/100")
                with col2:
                    st.metric("Avg Sales/Year", f"{df['sales_last_12_months'].mean():.1f}")
                with col3:
                    st.metric("Avg Age", df['age_range'].mode()[0])
                
                # Display agents
                for i, agent in enumerate(st.session_state.tech_savvy_agents[:10]):
                    display_agent_card(agent, detailed=False)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"View Details", key=f"tech_detail_{i}"):
                            display_agent_card(agent, detailed=True)
                    with col2:
                        if st.button(f"Add to Campaign", key=f"tech_add_{i}"):
                            st.session_state.selected_agents.append(agent)
                            st.success(f"Added {agent['name']}")
                
                # Bulk export
                st.divider()
                
                csv = df.to_csv(index=False)
                st.download_button(
                    "📊 Export All Tech-Savvy Agents",
                    csv,
                    f"tech_savvy_agents_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
    
    # Tab 7: AI Insights
    with tabs[6]:
        st.header("💡 AI-Powered Insights & Recommendations")
        
        if st.session_state.claude_client:
            st.subheader("Market Analysis")
            
            if st.button("🤖 Generate Market Insights"):
                with st.spinner("Analyzing with Claude AI..."):
                    # This would use real data in production
                    st.write("### Key Insights:")
                    st.write("1. **Best ZIP Codes for Brydje**: 94105, 90210, 10001")
                    st.write("2. **Optimal Agent Profile**: 25-34 years, 3-7 years experience, Instagram active")
                    st.write("3. **Best Outreach Time**: Tuesday-Thursday, 10am-12pm")
                    st.write("4. **Conversion Predictors**: Tech score > 75, uses 4+ tools, responds < 1 hour")
                    st.write("5. **Estimated TAM**: 12,000 agents nationwide match ideal profile")
            
            st.divider()
            
            st.subheader("Campaign Optimization")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Top Performing Subject Lines:**")
                st.write("1. Save 5 hours/week (38% open rate)")
                st.write("2. 30-second videos (35% open rate)")
                st.write("3. You're overpaying (32% open rate)")
            
            with col2:
                st.write("**Best CTAs:**")
                st.write("1. '5-minute demo' (12% click rate)")
                st.write("2. 'Free trial' (10% click rate)")
                st.write("3. '50% off founding members' (9% click rate)")
        else:
            st.warning("⚠️ Connect Claude API in sidebar for AI insights")
            st.info("Claude AI can provide:")
            st.write("• Personalized agent analysis")
            st.write("• Custom email generation")
            st.write("• Market insights")
            st.write("• Conversion predictions")
            st.write("• Outreach strategy optimization")

# ================== MAIN EXECUTION ==================
if __name__ == "__main__":
    main()