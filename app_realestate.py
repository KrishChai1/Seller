"""
🏡 Brydje Ultimate Agent Matcher - FINAL VERSION
Complete platform with integrated public data scraping
Works with ANY ZIP code - Gets real publicly available data
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
from typing import Dict, List, Optional, Tuple
import hashlib
import random
from dataclasses import dataclass, asdict
from urllib.parse import quote

# ================== PAGE CONFIGURATION ==================
st.set_page_config(
    page_title="Brydje Agent Matcher - Real Data Edition",
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
    
    .data-source-badge {
        display: inline-block;
        background: #4CAF50;
        color: white;
        padding: 5px 15px;
        border-radius: 15px;
        font-size: 12px;
        margin: 5px 0;
    }
    
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .research-link {
        display: inline-block;
        background: #f0f2f6;
        padding: 8px 15px;
        border-radius: 10px;
        margin: 5px;
        text-decoration: none;
        color: #667eea;
        transition: background 0.3s ease;
    }
    
    .research-link:hover {
        background: #e1e4e8;
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
    
    .public-data-warning {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ================== SESSION STATE ==================
if 'db_conn' not in st.session_state:
    st.session_state.db_conn = sqlite3.connect('brydje_real_data.db', check_same_thread=False)

if 'current_agents' not in st.session_state:
    st.session_state.current_agents = []

if 'selected_agents' not in st.session_state:
    st.session_state.selected_agents = []

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

if 'scraped_data_cache' not in st.session_state:
    st.session_state.scraped_data_cache = {}

# ================== DATABASE SETUP ==================
def init_database():
    """Initialize database with tables for real data"""
    conn = st.session_state.db_conn
    cursor = conn.cursor()
    
    # Real agents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS real_agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            brokerage TEXT,
            license_number TEXT,
            rating REAL,
            review_count INTEGER,
            recent_sales TEXT,
            specializations TEXT,
            languages TEXT,
            zip_code TEXT,
            city TEXT,
            state TEXT,
            profile_url TEXT,
            website_url TEXT,
            social_media TEXT,
            tech_score INTEGER,
            data_source TEXT,
            last_verified TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Search history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zip_code TEXT,
            city TEXT,
            state TEXT,
            agents_found INTEGER,
            search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Manual research queue
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS research_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name TEXT,
            zip_code TEXT,
            google_result TEXT,
            research_status TEXT DEFAULT 'pending',
            instagram_checked BOOLEAN DEFAULT FALSE,
            facebook_checked BOOLEAN DEFAULT FALSE,
            website_found TEXT,
            notes TEXT,
            tech_score_estimate INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()

# ================== PUBLIC DATA SCRAPER ==================
class PublicDataScraper:
    """
    Scrapes publicly available real estate agent data
    No API keys required - uses public information only
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_zip_info(self, zip_code: str) -> Dict:
        """Get city and state from ZIP code"""
        try:
            # Using public ZIP code API
            response = self.session.get(f"https://api.zippopotam.us/us/{zip_code}")
            if response.status_code == 200:
                data = response.json()
                return {
                    'zip': zip_code,
                    'city': data.get('places', [{}])[0].get('place name', 'Unknown'),
                    'state': data.get('places', [{}])[0].get('state abbreviation', 'Unknown')
                }
        except:
            pass
        
        return {'zip': zip_code, 'city': 'Unknown', 'state': 'Unknown'}
    
    def search_agents_google(self, zip_code: str, city: str = None) -> List[Dict]:
        """Search Google for real estate agents in ZIP code"""
        agents = []
        
        # Build search query
        location = f"{city} {zip_code}" if city else zip_code
        queries = [
            f"real estate agents {location}",
            f"top realtors {location}",
            f"best real estate agents near {zip_code}"
        ]
        
        for query in queries[:1]:  # Limit to avoid rate limiting
            try:
                # Google search URL
                url = "https://www.google.com/search"
                params = {
                    'q': query,
                    'num': 20
                }
                
                response = self.session.get(url, params=params)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Parse search results
                results = soup.find_all('div', class_=['g', 'Gx5Zad'])
                
                for result in results[:10]:
                    # Try to extract agent information
                    title_elem = result.find(['h3', 'div', 'a'])
                    snippet = result.get_text()
                    
                    # Look for agent names (basic pattern matching)
                    if title_elem and any(word in snippet.lower() for word in ['agent', 'realtor', 'broker', 'real estate']):
                        # Extract potential agent name
                        title = title_elem.get_text() if title_elem else ""
                        
                        # Basic parsing for agent info
                        agent_info = self.parse_agent_from_text(title, snippet, zip_code)
                        if agent_info['name'] and agent_info['name'] != 'Unknown':
                            agents.append(agent_info)
                
                time.sleep(2)  # Be respectful
                
            except Exception as e:
                st.warning(f"Google search limited. Error: {str(e)[:100]}")
        
        return agents
    
    def parse_agent_from_text(self, title: str, snippet: str, zip_code: str) -> Dict:
        """Parse agent information from search result text"""
        
        # Common patterns for agent names
        name = "Unknown"
        brokerage = "Unknown"
        phone = None
        rating = None
        
        # Try to extract name from title
        if '|' in title:
            parts = title.split('|')
            name = parts[0].strip()
        elif '-' in title:
            parts = title.split('-')
            name = parts[0].strip()
        else:
            # Look for capitalized names
            words = title.split()
            if len(words) >= 2:
                potential_name = ' '.join(words[:2])
                if potential_name[0].isupper():
                    name = potential_name
        
        # Look for brokerage names
        brokerages = ['RE/MAX', 'Keller Williams', 'Century 21', 'Coldwell Banker', 
                     'Compass', 'Berkshire Hathaway', 'Sotheby', 'Redfin', 'eXp Realty']
        for b in brokerages:
            if b.lower() in snippet.lower():
                brokerage = b
                break
        
        # Look for phone numbers
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, snippet)
        if phone_match:
            phone = phone_match.group()
        
        # Look for ratings
        rating_pattern = r'(\d+(?:\.\d+)?)\s*(?:star|★|rating)'
        rating_match = re.search(rating_pattern, snippet.lower())
        if rating_match:
            rating = float(rating_match.group(1))
        
        return {
            'name': name,
            'brokerage': brokerage,
            'phone': phone,
            'rating': rating,
            'zip_code': zip_code,
            'data_source': 'Google Search',
            'snippet': snippet[:200]
        }
    
    def search_zillow_public(self, zip_code: str) -> List[Dict]:
        """Search Zillow's public agent directory"""
        agents = []
        
        # Zillow public URL patterns
        urls = [
            f"https://www.zillow.com/professionals/real-estate-agent-reviews/{zip_code}/",
            f"https://www.zillow.com/directory/real-estate-agents/{zip_code}/"
        ]
        
        for url in urls[:1]:
            try:
                response = self.session.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for agent information in various formats
                    # Zillow changes their structure, so we try multiple patterns
                    patterns = [
                        {'class': 'ldb-contact-summary'},
                        {'class': 'agent-card'},
                        {'class': 'professional-card'},
                        {'attrs': {'data-testid': 'agent-card'}}
                    ]
                    
                    for pattern in patterns:
                        if 'attrs' in pattern:
                            cards = soup.find_all('div', attrs=pattern['attrs'])
                        else:
                            cards = soup.find_all('div', class_=pattern['class'])
                        
                        if cards:
                            for card in cards[:20]:
                                agent = self.parse_zillow_card(card, zip_code)
                                if agent['name'] != 'Unknown':
                                    agents.append(agent)
                            break
                    
                time.sleep(3)  # Respect rate limits
                
            except Exception as e:
                st.info(f"Zillow structure may have changed. Trying alternative sources...")
        
        return agents
    
    def parse_zillow_card(self, card, zip_code: str) -> Dict:
        """Parse agent information from Zillow card HTML"""
        
        agent = {
            'name': 'Unknown',
            'brokerage': 'Unknown',
            'phone': None,
            'rating': None,
            'review_count': 0,
            'recent_sales': None,
            'zip_code': zip_code,
            'data_source': 'Zillow Directory'
        }
        
        # Try various selectors
        name_selectors = ['h2', 'h3', '.agent-name', '[data-testid="agent-name"]', 'a']
        for selector in name_selectors:
            name_elem = card.select_one(selector)
            if name_elem:
                agent['name'] = name_elem.get_text().strip()
                break
        
        # Look for ratings
        rating_elem = card.select_one('[class*="rating"]')
        if rating_elem:
            rating_text = rating_elem.get_text()
            rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
            if rating_match:
                agent['rating'] = float(rating_match.group(1))
        
        # Look for review count
        review_elem = card.select_one('[class*="review"]')
        if review_elem:
            review_text = review_elem.get_text()
            review_match = re.search(r'(\d+)', review_text)
            if review_match:
                agent['review_count'] = int(review_match.group(1))
        
        # Look for sales info
        sales_elem = card.select_one('[class*="sale"]')
        if sales_elem:
            agent['recent_sales'] = sales_elem.get_text().strip()
        
        return agent
    
    def search_realtor_public(self, zip_code: str) -> List[Dict]:
        """Search Realtor.com public directory"""
        agents = []
        
        url = f"https://www.realtor.com/realestateagents/{zip_code}"
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for agent cards
                cards = soup.find_all('div', class_=['agent-list-card', 'agent-card'])
                
                for card in cards[:20]:
                    agent = self.parse_realtor_card(card, zip_code)
                    if agent['name'] != 'Unknown':
                        agents.append(agent)
                
                time.sleep(2)
                
        except Exception as e:
            st.info("Realtor.com data limited. Trying other sources...")
        
        return agents
    
    def parse_realtor_card(self, card, zip_code: str) -> Dict:
        """Parse agent information from Realtor.com card"""
        
        agent = {
            'name': 'Unknown',
            'brokerage': 'Unknown',
            'phone': None,
            'zip_code': zip_code,
            'data_source': 'Realtor.com'
        }
        
        # Extract name
        name_elem = card.select_one('.agent-name, h2, h3')
        if name_elem:
            agent['name'] = name_elem.get_text().strip()
        
        # Extract brokerage
        brokerage_elem = card.select_one('.agent-group, .brokerage-name')
        if brokerage_elem:
            agent['brokerage'] = brokerage_elem.get_text().strip()
        
        # Extract phone
        phone_elem = card.select_one('.agent-phone, [href^="tel:"]')
        if phone_elem:
            phone_text = phone_elem.get_text() if phone_elem.get_text() else phone_elem.get('href', '')
            phone_match = re.search(r'\d{3}[-.]?\d{3}[-.]?\d{4}', phone_text)
            if phone_match:
                agent['phone'] = phone_match.group()
        
        return agent
    
    def generate_research_links(self, agent_name: str, zip_code: str) -> Dict:
        """Generate research links for manual verification"""
        
        # Clean agent name for URLs
        clean_name = quote(agent_name)
        
        return {
            'google': f"https://www.google.com/search?q={clean_name}+real+estate+agent+{zip_code}",
            'zillow': f"https://www.zillow.com/professionals/real-estate-agent-reviews/?search={clean_name}",
            'realtor': f"https://www.realtor.com/realestateagents/search?name={clean_name}",
            'linkedin': f"https://www.linkedin.com/search/results/people/?keywords={clean_name}%20real%20estate",
            'facebook': f"https://www.facebook.com/search/people/?q={clean_name}",
            'instagram': f"https://www.instagram.com/explore/search/?q={clean_name.replace('+', '')}",
            'youtube': f"https://www.youtube.com/results?search_query={clean_name}+real+estate"
        }
    
    def estimate_tech_score(self, agent: Dict) -> int:
        """Estimate tech score based on available public data"""
        score = 50  # Base score
        
        # Has rating - indicates online presence
        if agent.get('rating'):
            score += 10
        
        # Has reviews - active online
        if agent.get('review_count', 0) > 10:
            score += 10
        
        # Has phone - contactable
        if agent.get('phone'):
            score += 5
        
        # Known brokerage - established
        major_brokerages = ['RE/MAX', 'Keller Williams', 'Compass', 'eXp Realty']
        if agent.get('brokerage') in major_brokerages:
            score += 10
        
        # Recent sales mentioned
        if agent.get('recent_sales'):
            score += 10
        
        # Multiple data sources
        if agent.get('data_source') and agent['data_source'] != 'Manual':
            score += 5
        
        return min(100, score)
    
    def search_all_sources(self, zip_code: str) -> List[Dict]:
        """Search all available public sources for agents"""
        
        all_agents = []
        seen_names = set()
        
        # Get ZIP info
        zip_info = self.get_zip_info(zip_code)
        city = zip_info.get('city', 'Unknown')
        state = zip_info.get('state', 'Unknown')
        
        with st.spinner(f"Searching public directories for agents in {city}, {state} {zip_code}..."):
            
            # Search Google
            st.info("🔍 Searching Google...")
            google_agents = self.search_agents_google(zip_code, city)
            for agent in google_agents:
                if agent['name'] not in seen_names:
                    agent['city'] = city
                    agent['state'] = state
                    all_agents.append(agent)
                    seen_names.add(agent['name'])
            
            # Search Zillow
            st.info("🏠 Checking Zillow directory...")
            zillow_agents = self.search_zillow_public(zip_code)
            for agent in zillow_agents:
                if agent['name'] not in seen_names:
                    agent['city'] = city
                    agent['state'] = state
                    all_agents.append(agent)
                    seen_names.add(agent['name'])
            
            # Search Realtor.com
            st.info("🏘️ Checking Realtor.com...")
            realtor_agents = self.search_realtor_public(zip_code)
            for agent in realtor_agents:
                if agent['name'] not in seen_names:
                    agent['city'] = city
                    agent['state'] = state
                    all_agents.append(agent)
                    seen_names.add(agent['name'])
        
        # Add tech scores
        for agent in all_agents:
            agent['tech_score'] = self.estimate_tech_score(agent)
            agent['research_links'] = self.generate_research_links(agent['name'], zip_code)
        
        # Sort by tech score
        all_agents.sort(key=lambda x: x.get('tech_score', 0), reverse=True)
        
        return all_agents

# ================== ENHANCED FEATURES ==================
class AgentEnricher:
    """Enrich agent data with additional insights"""
    
    @staticmethod
    def analyze_agent_potential(agent: Dict) -> Dict:
        """Analyze agent's potential as Brydje customer"""
        
        analysis = {
            'brydje_fit_score': 0,
            'pain_points': [],
            'selling_points': [],
            'outreach_priority': 'low'
        }
        
        score = 0
        
        # Tech score factor
        tech_score = agent.get('tech_score', 0)
        if tech_score > 70:
            score += 30
            analysis['selling_points'].append("Tech-savvy - quick adopter")
            analysis['outreach_priority'] = 'high'
        elif tech_score > 50:
            score += 20
            analysis['selling_points'].append("Open to technology")
            analysis['outreach_priority'] = 'medium'
        else:
            score += 10
            analysis['pain_points'].append("May need education on tech benefits")
        
        # Activity level
        if agent.get('recent_sales'):
            score += 20
            analysis['pain_points'].append("Busy agent - needs time-saving tools")
            analysis['selling_points'].append("High volume = high value customer")
        
        # Online presence
        if agent.get('rating'):
            score += 15
            analysis['selling_points'].append("Values online reputation")
        
        if agent.get('review_count', 0) > 20:
            score += 15
            analysis['pain_points'].append("Managing many client relationships")
        
        # Brokerage type
        if agent.get('brokerage') in ['eXp Realty', 'Compass']:
            score += 10
            analysis['selling_points'].append("Works for tech-forward brokerage")
        
        # Common pain points for all agents
        analysis['pain_points'].extend([
            "Spending hours on listing materials",
            "Managing multiple marketing tools",
            "Competing with tech-savvy agents"
        ])
        
        analysis['brydje_fit_score'] = min(100, score)
        
        return analysis
    
    @staticmethod
    def generate_email_template(agent: Dict) -> str:
        """Generate personalized email template for agent"""
        
        name = agent.get('name', 'there')
        city = agent.get('city', 'your area')
        brokerage = agent.get('brokerage', '')
        
        # Personalization based on available data
        if agent.get('rating') and agent['rating'] > 4:
            opener = f"I saw your excellent {agent['rating']} star rating - impressive!"
        elif agent.get('recent_sales'):
            opener = f"Congrats on your recent sales success!"
        else:
            opener = f"I found your profile while researching top agents in {city}."
        
        template = f"""
Hi {name},

{opener}

I'm reaching out because I built Brydje specifically for successful agents{f' at {brokerage}' if brokerage and brokerage != 'Unknown' else ''} who value their time.

Quick question - how long does it take you to create listing videos and marketing materials for each property?

Brydje uses AI to create professional listing videos, landing pages, and QR codes in literally 30 seconds. 

Agents in {city} are saving 5+ hours per week and closing deals faster.

Worth a quick 5-minute demo? I'm offering 50% off for the first 20 agents in {city}.

Best,
[Your Name]

P.S. Here's a 30-second listing video created with Brydje: [link]
"""
        return template

# ================== MAIN APPLICATION ==================
def main():
    st.title("🏡 Brydje Agent Matcher - Real Data Edition")
    st.markdown("**Search any ZIP code** • **Get real agent data** • **Public sources** • **No API keys required**")
    
    # Initialize database
    init_database()
    
    # Initialize scraper
    scraper = PublicDataScraper()
    enricher = AgentEnricher()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings & Info")
        
        st.info("""
        **Data Sources:**
        • Google Search Results
        • Zillow Public Directory
        • Realtor.com Directory
        • Public Web Data
        
        **Note:** This uses publicly available data only. For complete data, manual verification recommended.
        """)
        
        st.divider()
        
        # Search History
        st.header("📝 Recent Searches")
        conn = st.session_state.db_conn
        recent = pd.read_sql_query(
            "SELECT * FROM search_history ORDER BY search_date DESC LIMIT 5",
            conn
        )
        if not recent.empty:
            for _, row in recent.iterrows():
                st.write(f"**{row['zip_code']}** - {row['city']}, {row['state']}")
                st.caption(f"{row['agents_found']} agents • {pd.to_datetime(row['search_date']).strftime('%m/%d %I:%M%p')}")
        else:
            st.caption("No recent searches")
        
        st.divider()
        
        # Stats
        st.header("📊 Statistics")
        total_agents = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM real_agents",
            conn
        )['count'][0]
        st.metric("Total Agents in Database", total_agents)
        
        selected_count = len(st.session_state.selected_agents)
        st.metric("Selected for Campaign", selected_count)
    
    # Main Content
    tabs = st.tabs([
        "🔍 ZIP Search",
        "👥 Agent Directory",
        "📧 Email Campaign",
        "🎯 Tech Analysis",
        "📊 Market Insights",
        "🔬 Manual Research"
    ])
    
    # Tab 1: ZIP Search
    with tabs[0]:
        st.header("🔍 Search Real Estate Agents by ZIP Code")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            zip_code = st.text_input(
                "Enter ZIP Code",
                placeholder="e.g., 94105, 10001, 90210",
                help="Any valid US ZIP code"
            )
        
        with col2:
            min_tech_score = st.slider(
                "Min Tech Score",
                0, 100, 30,
                help="Estimated based on public data"
            )
        
        with col3:
            auto_research = st.checkbox(
                "Generate Research Links",
                value=True,
                help="Create links for manual verification"
            )
        
        if st.button("🔍 Search for Agents", type="primary") and zip_code:
            # Check if ZIP is valid
            if len(zip_code) != 5 or not zip_code.isdigit():
                st.error("Please enter a valid 5-digit ZIP code")
            else:
                # Check cache first
                if zip_code in st.session_state.scraped_data_cache:
                    st.info("Using cached data. Click 'Force Refresh' to search again.")
                    agents = st.session_state.scraped_data_cache[zip_code]
                else:
                    # Search for agents
                    agents = scraper.search_all_sources(zip_code)
                    
                    # Cache the results
                    st.session_state.scraped_data_cache[zip_code] = agents
                    
                    # Save to database
                    conn = st.session_state.db_conn
                    cursor = conn.cursor()
                    
                    # Get ZIP info
                    zip_info = scraper.get_zip_info(zip_code)
                    
                    # Save search history
                    cursor.execute('''
                        INSERT INTO search_history (zip_code, city, state, agents_found)
                        VALUES (?, ?, ?, ?)
                    ''', (zip_code, zip_info['city'], zip_info['state'], len(agents)))
                    
                    # Save agents to database
                    for agent in agents:
                        cursor.execute('''
                            INSERT OR REPLACE INTO real_agents 
                            (name, phone, brokerage, rating, review_count, recent_sales,
                             zip_code, city, state, tech_score, data_source, last_verified)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            agent.get('name'),
                            agent.get('phone'),
                            agent.get('brokerage'),
                            agent.get('rating'),
                            agent.get('review_count'),
                            agent.get('recent_sales'),
                            zip_code,
                            zip_info['city'],
                            zip_info['state'],
                            agent.get('tech_score'),
                            agent.get('data_source'),
                            datetime.now()
                        ))
                    
                    conn.commit()
                
                # Store in session
                st.session_state.current_agents = agents
                
                # Display results
                st.success(f"Found {len(agents)} agents in ZIP {zip_code}")
                
                if agents:
                    # Filter by tech score
                    filtered_agents = [a for a in agents if a.get('tech_score', 0) >= min_tech_score]
                    
                    st.markdown(f"### Showing {len(filtered_agents)} agents with tech score ≥ {min_tech_score}")
                    
                    # Display warning about public data
                    st.markdown("""
                    <div class="public-data-warning">
                    ⚠️ <strong>Note:</strong> This data is from public sources. Some information may be incomplete. 
                    Use the research links to verify and enrich agent profiles manually.
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create dataframe for display
                    display_data = []
                    for i, agent in enumerate(filtered_agents):
                        display_data.append({
                            'Select': False,
                            'Name': agent.get('name', 'Unknown'),
                            'Brokerage': agent.get('brokerage', 'Unknown'),
                            'Phone': agent.get('phone', 'Not found'),
                            'Rating': agent.get('rating', 'N/A'),
                            'Reviews': agent.get('review_count', 0),
                            'Tech Score': agent.get('tech_score', 0),
                            'Source': agent.get('data_source', 'Unknown'),
                            'Index': i
                        })
                    
                    df = pd.DataFrame(display_data)
                    
                    # Editable dataframe with selection
                    edited_df = st.data_editor(
                        df,
                        hide_index=True,
                        column_config={
                            "Select": st.column_config.CheckboxColumn(
                                "Select",
                                help="Select agents for campaign"
                            ),
                            "Tech Score": st.column_config.ProgressColumn(
                                "Tech Score",
                                min_value=0,
                                max_value=100
                            ),
                            "Rating": st.column_config.NumberColumn(
                                "Rating",
                                format="⭐ %.1f"
                            )
                        }
                    )
                    
                    # Process selections
                    selected_indices = edited_df[edited_df['Select']]['Index'].tolist()
                    
                    if selected_indices:
                        st.info(f"Selected {len(selected_indices)} agents")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("📧 Add to Campaign"):
                                for idx in selected_indices:
                                    if idx < len(filtered_agents):
                                        st.session_state.selected_agents.append(filtered_agents[idx])
                                st.success(f"Added {len(selected_indices)} agents to campaign")
                        
                        with col2:
                            if st.button("🔬 View Research Links"):
                                for idx in selected_indices[:5]:  # Limit to 5
                                    agent = filtered_agents[idx]
                                    st.write(f"**{agent['name']}**")
                                    links = agent.get('research_links', {})
                                    cols = st.columns(len(links))
                                    for i, (platform, url) in enumerate(links.items()):
                                        with cols[i]:
                                            st.markdown(f"[{platform.title()}]({url})")
                        
                        with col3:
                            # Export to CSV
                            csv_data = pd.DataFrame(filtered_agents).to_csv(index=False)
                            st.download_button(
                                "📊 Export CSV",
                                csv_data,
                                f"agents_{zip_code}_{datetime.now().strftime('%Y%m%d')}.csv",
                                "text/csv"
                            )
                    
                    # Display detailed cards for top agents
                    st.divider()
                    st.subheader("🏆 Top Tech-Savvy Agents")
                    
                    for agent in filtered_agents[:5]:
                        with st.expander(f"{agent['name']} - Tech Score: {agent['tech_score']}"):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write(f"**Brokerage:** {agent.get('brokerage', 'Unknown')}")
                                st.write(f"**Phone:** {agent.get('phone', 'Not found')}")
                                st.write(f"**Rating:** {agent.get('rating', 'N/A')}")
                                st.write(f"**Reviews:** {agent.get('review_count', 0)}")
                                st.write(f"**Data Source:** {agent.get('data_source', 'Unknown')}")
                                
                                # Brydje fit analysis
                                analysis = enricher.analyze_agent_potential(agent)
                                st.write(f"**Brydje Fit Score:** {analysis['brydje_fit_score']}/100")
                                st.write(f"**Priority:** {analysis['outreach_priority'].upper()}")
                            
                            with col2:
                                st.write("**Research Links:**")
                                links = agent.get('research_links', {})
                                for platform, url in links.items():
                                    st.markdown(f"• [{platform.title()}]({url})")
                            
                            # Email template
                            if st.button(f"Generate Email", key=f"email_{agent['name']}"):
                                email = enricher.generate_email_template(agent)
                                st.text_area("Email Template", email, height=300, key=f"template_{agent['name']}")
                
                else:
                    st.warning("No agents found. Try a different ZIP code or expand search criteria.")
        
        # Force refresh button
        if zip_code in st.session_state.scraped_data_cache:
            if st.button("🔄 Force Refresh (Search Again)"):
                del st.session_state.scraped_data_cache[zip_code]
                st.info("Cache cleared. Click 'Search for Agents' to refresh data.")
    
    # Tab 2: Agent Directory
    with tabs[1]:
        st.header("👥 Agent Directory")
        
        # Load all agents from database
        conn = st.session_state.db_conn
        all_agents_df = pd.read_sql_query(
            "SELECT * FROM real_agents ORDER BY tech_score DESC",
            conn
        )
        
        if not all_agents_df.empty:
            # Filters
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                filter_zip = st.selectbox(
                    "Filter by ZIP",
                    ["All"] + list(all_agents_df['zip_code'].unique())
                )
            
            with col2:
                filter_city = st.selectbox(
                    "Filter by City",
                    ["All"] + list(all_agents_df['city'].unique())
                )
            
            with col3:
                filter_brokerage = st.selectbox(
                    "Filter by Brokerage",
                    ["All"] + list(all_agents_df['brokerage'].dropna().unique())
                )
            
            with col4:
                filter_tech = st.slider("Min Tech Score", 0, 100, 50)
            
            # Apply filters
            filtered_df = all_agents_df.copy()
            
            if filter_zip != "All":
                filtered_df = filtered_df[filtered_df['zip_code'] == filter_zip]
            
            if filter_city != "All":
                filtered_df = filtered_df[filtered_df['city'] == filter_city]
            
            if filter_brokerage != "All":
                filtered_df = filtered_df[filtered_df['brokerage'] == filter_brokerage]
            
            filtered_df = filtered_df[filtered_df['tech_score'] >= filter_tech]
            
            # Display
            st.write(f"Showing {len(filtered_df)} agents")
            
            # Add selection column
            filtered_df['Select'] = False
            
            # Display editable dataframe
            edited = st.data_editor(
                filtered_df[['Select', 'name', 'city', 'state', 'zip_code', 'brokerage', 
                           'rating', 'tech_score', 'data_source', 'last_verified']],
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
            
            # Bulk actions
            selected = edited[edited['Select']]
            if len(selected) > 0:
                st.info(f"Selected {len(selected)} agents")
                
                if st.button("📧 Add All to Campaign"):
                    for _, agent in selected.iterrows():
                        st.session_state.selected_agents.append(agent.to_dict())
                    st.success(f"Added {len(selected)} agents to campaign")
        
        else:
            st.info("No agents in database yet. Search for a ZIP code to get started.")
    
    # Tab 3: Email Campaign
    with tabs[2]:
        st.header("📧 Email Campaign Generator")
        
        if st.session_state.selected_agents:
            st.write(f"**Campaign Recipients:** {len(st.session_state.selected_agents)} agents")
            
            # Display selected agents
            selected_df = pd.DataFrame(st.session_state.selected_agents)
            st.dataframe(
                selected_df[['name', 'city', 'state', 'tech_score']].head(10),
                hide_index=True
            )
            
            st.divider()
            
            # Email template options
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("Campaign Settings")
                
                campaign_name = st.text_input("Campaign Name", f"Campaign_{datetime.now().strftime('%Y%m%d')}")
                
                template_type = st.selectbox(
                    "Template Type",
                    ["Tech-Savvy Focus", "Time Savings", "Cost Savings", "FSBO Helper", "Custom"]
                )
                
                subject_lines = [
                    "Save 5 hours/week on your listings",
                    "You're spending too much on real estate tools",
                    f"3 agents in {st.session_state.selected_agents[0].get('city', 'your area')} just switched",
                    "30-second listing videos? (Yes, really)",
                    "Quick question about your marketing"
                ]
                
                selected_subject = st.selectbox("Subject Line", subject_lines)
                
                personalize = st.checkbox("Personalize with agent name", value=True)
                mention_location = st.checkbox("Mention agent's city", value=True)
                include_rating = st.checkbox("Reference their rating (if available)", value=True)
            
            with col2:
                st.subheader("Email Preview")
                
                # Preview with first agent
                if st.session_state.selected_agents:
                    preview_agent = st.session_state.selected_agents[0]
                    
                    # Generate email
                    email = enricher.generate_email_template(preview_agent)
                    
                    # Display
                    st.text_area("Email Content", email, height=400)
                    
                    # Copy button
                    st.button("📋 Copy to Clipboard")
            
            # Export options
            st.divider()
            st.subheader("Export Campaign")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Export emails as CSV
                if st.button("📊 Export as CSV"):
                    export_data = []
                    for agent in st.session_state.selected_agents:
                        export_data.append({
                            'Name': agent.get('name'),
                            'Email': agent.get('email', ''),
                            'Phone': agent.get('phone', ''),
                            'City': agent.get('city'),
                            'State': agent.get('state'),
                            'Subject': selected_subject,
                            'Email_Body': enricher.generate_email_template(agent)
                        })
                    
                    export_df = pd.DataFrame(export_data)
                    csv = export_df.to_csv(index=False)
                    
                    st.download_button(
                        "Download Campaign CSV",
                        csv,
                        f"email_campaign_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
            
            with col2:
                # Generate all emails
                if st.button("📧 Generate All Emails"):
                    with st.spinner("Generating personalized emails..."):
                        emails = []
                        for agent in st.session_state.selected_agents:
                            emails.append({
                                'agent': agent['name'],
                                'email': enricher.generate_email_template(agent)
                            })
                        
                        st.success(f"Generated {len(emails)} personalized emails!")
                        
                        # Display first few
                        for email in emails[:3]:
                            with st.expander(f"Email for {email['agent']}"):
                                st.text(email['email'])
            
            with col3:
                # Clear campaign
                if st.button("🗑️ Clear Campaign"):
                    st.session_state.selected_agents = []
                    st.success("Campaign cleared")
                    st.rerun()
        
        else:
            st.info("No agents selected for campaign. Search for agents and add them to your campaign.")
    
    # Tab 4: Tech Analysis
    with tabs[3]:
        st.header("🎯 Tech-Savvy Agent Analysis")
        
        # Load agents from database
        conn = st.session_state.db_conn
        agents_df = pd.read_sql_query(
            "SELECT * FROM real_agents WHERE tech_score IS NOT NULL",
            conn
        )
        
        if not agents_df.empty:
            # Tech score distribution
            fig_hist = px.histogram(
                agents_df,
                x='tech_score',
                nbins=20,
                title='Tech Score Distribution',
                labels={'tech_score': 'Tech Score', 'count': 'Number of Agents'}
            )
            fig_hist.add_vline(x=70, line_dash="dash", line_color="green",
                              annotation_text="Brydje Target (70+)")
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # Tech score by city
            city_tech = agents_df.groupby('city')['tech_score'].agg(['mean', 'count']).reset_index()
            city_tech = city_tech[city_tech['count'] >= 3]  # Cities with at least 3 agents
            
            if not city_tech.empty:
                fig_city = px.bar(
                    city_tech.sort_values('mean', ascending=False).head(10),
                    x='city',
                    y='mean',
                    title='Average Tech Score by City',
                    labels={'mean': 'Avg Tech Score', 'city': 'City'}
                )
                st.plotly_chart(fig_city, use_container_width=True)
            
            # Brokerage analysis
            brokerage_tech = agents_df.groupby('brokerage')['tech_score'].agg(['mean', 'count']).reset_index()
            brokerage_tech = brokerage_tech[brokerage_tech['count'] >= 2]
            
            if not brokerage_tech.empty:
                fig_brokerage = px.scatter(
                    brokerage_tech,
                    x='count',
                    y='mean',
                    text='brokerage',
                    title='Brokerages: Agent Count vs Tech Score',
                    labels={'count': 'Number of Agents', 'mean': 'Avg Tech Score'}
                )
                st.plotly_chart(fig_brokerage, use_container_width=True)
            
            # Top tech-savvy agents
            st.subheader("🏆 Top 10 Tech-Savvy Agents")
            top_agents = agents_df.nlargest(10, 'tech_score')[['name', 'city', 'state', 'brokerage', 'tech_score', 'rating']]
            st.dataframe(top_agents, hide_index=True)
        
        else:
            st.info("No agent data available yet. Search for some ZIP codes first!")
    
    # Tab 5: Market Insights
    with tabs[4]:
        st.header("📊 Market Insights")
        
        conn = st.session_state.db_conn
        
        # Search history insights
        search_history = pd.read_sql_query(
            "SELECT * FROM search_history ORDER BY search_date DESC",
            conn
        )
        
        if not search_history.empty:
            # Most searched areas
            st.subheader("🔍 Most Searched Areas")
            
            area_stats = search_history.groupby(['city', 'state'])['agents_found'].agg(['sum', 'count']).reset_index()
            area_stats.columns = ['City', 'State', 'Total Agents', 'Searches']
            area_stats = area_stats.sort_values('Total Agents', ascending=False).head(10)
            
            st.dataframe(area_stats, hide_index=True)
            
            # Time series of searches
            search_history['search_date'] = pd.to_datetime(search_history['search_date'])
            daily_searches = search_history.set_index('search_date').resample('D')['agents_found'].sum().reset_index()
            
            fig_timeline = px.line(
                daily_searches,
                x='search_date',
                y='agents_found',
                title='Agents Discovered Over Time',
                labels={'agents_found': 'Agents Found', 'search_date': 'Date'}
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Overall stats
        total_searches = len(search_history)
        total_agents = pd.read_sql_query("SELECT COUNT(*) as count FROM real_agents", conn)['count'][0]
        avg_tech_score = pd.read_sql_query("SELECT AVG(tech_score) as avg FROM real_agents", conn)['avg'][0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total ZIP Codes Searched", total_searches)
        
        with col2:
            st.metric("Total Agents Found", total_agents)
        
        with col3:
            st.metric("Average Tech Score", f"{avg_tech_score:.0f}" if avg_tech_score else "N/A")
    
    # Tab 6: Manual Research
    with tabs[5]:
        st.header("🔬 Manual Research Queue")
        
        st.info("""
        This section helps you track manual research for agents. 
        Use the research links to verify agent information and add notes.
        """)
        
        # Add agent to research queue
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Add to Research Queue")
            
            agent_name = st.text_input("Agent Name")
            agent_zip = st.text_input("ZIP Code", "")
            
            if st.button("Add to Queue") and agent_name:
                conn = st.session_state.db_conn
                cursor = conn.cursor()
                
                # Generate research links
                links = scraper.generate_research_links(agent_name, agent_zip)
                
                cursor.execute('''
                    INSERT INTO research_queue (agent_name, zip_code, google_result)
                    VALUES (?, ?, ?)
                ''', (agent_name, agent_zip, links.get('google', '')))
                
                conn.commit()
                st.success(f"Added {agent_name} to research queue")
        
        with col2:
            st.subheader("Quick Add from Search")
            
            if st.session_state.current_agents:
                quick_add = st.selectbox(
                    "Select agent from recent search",
                    [a['name'] for a in st.session_state.current_agents[:10]]
                )
                
                if st.button("Quick Add to Queue"):
                    selected = next((a for a in st.session_state.current_agents if a['name'] == quick_add), None)
                    if selected:
                        conn = st.session_state.db_conn
                        cursor = conn.cursor()
                        
                        cursor.execute('''
                            INSERT INTO research_queue (agent_name, zip_code, google_result)
                            VALUES (?, ?, ?)
                        ''', (selected['name'], selected.get('zip_code', ''), ''))
                        
                        conn.commit()
                        st.success(f"Added {selected['name']} to research queue")
        
        st.divider()
        
        # Display research queue
        st.subheader("Research Queue")
        
        conn = st.session_state.db_conn
        queue = pd.read_sql_query(
            "SELECT * FROM research_queue WHERE research_status = 'pending' ORDER BY created_at DESC",
            conn
        )
        
        if not queue.empty:
            for _, agent in queue.iterrows():
                with st.expander(f"{agent['agent_name']} - {agent['zip_code']}"):
                    # Research links
                    st.write("**Research Links:**")
                    links = scraper.generate_research_links(agent['agent_name'], agent['zip_code'])
                    
                    cols = st.columns(4)
                    for i, (platform, url) in enumerate(list(links.items())[:4]):
                        with cols[i]:
                            st.markdown(f"[{platform.title()}]({url})")
                    
                    # Research form
                    st.write("**Research Notes:**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        has_instagram = st.checkbox("Has Instagram", key=f"ig_{agent['id']}")
                        has_facebook = st.checkbox("Has Facebook", key=f"fb_{agent['id']}")
                        website = st.text_input("Website URL", key=f"web_{agent['id']}")
                    
                    with col2:
                        tech_estimate = st.slider("Tech Score Estimate", 0, 100, 50, key=f"tech_{agent['id']}")
                        notes = st.text_area("Notes", key=f"notes_{agent['id']}")
                    
                    if st.button("Save Research", key=f"save_{agent['id']}"):
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE research_queue
                            SET instagram_checked = ?, facebook_checked = ?, 
                                website_found = ?, tech_score_estimate = ?,
                                notes = ?, research_status = 'completed'
                            WHERE id = ?
                        ''', (has_instagram, has_facebook, website, tech_estimate, notes, agent['id']))
                        conn.commit()
                        st.success("Research saved!")
                        st.rerun()
        else:
            st.info("No agents in research queue. Add agents from your searches.")

# ================== RUN APPLICATION ==================
if __name__ == "__main__":
    main()
