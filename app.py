#!/usr/bin/env python3
import os
import streamlit as st
import requests
from dotenv import load_dotenv
from weather_ai import WeatherAI

# Load environment variables
load_dotenv()

# Configuration
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
BASE_URL = "https://api.weatherapi.com/v1/current.json"

# Page configuration
st.set_page_config(
    page_title="WeatherSearch",
    page_icon="🌤️",
    layout="centered"
)

# Initialize AI assistant
try:
    weather_ai = WeatherAI(OPENAI_API_KEY)
    ai_enabled = True
except Exception as e:
    st.error(f"Error initializing AI assistant: {str(e)}")
    ai_enabled = False

# Custom CSS
st.markdown("""
    <style>
    /* Base theme */
    :root {
        --primary-color: #2D7FF9;
        --secondary-color: #05C7F2;
        --text-color: #FFFFFF;
    }

    /* Reset backgrounds and borders */
    div, section, iframe {
        background-color: transparent !important;
        border: none !important;
    }

    /* Header section */
    .header-container {
        background: linear-gradient(180deg, rgba(45, 127, 249, 0.1), transparent);
        padding: 2rem 0 1rem 0;
        margin-bottom: 2rem;
        border-radius: 0 0 20px 20px;
    }

    /* Main title styling */
    .main-title {
        color: var(--text-color);
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(120deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        color: #B0B0B0;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }

    /* Input box styling */
    .stTextInput > div > div {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 0.25rem 1rem !important;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div:hover,
    .stTextInput > div > div:focus-within {
        border-color: var(--primary-color) !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
    }

    /* Weather card styling */
    .weather-card {
        padding: 0.5rem;
        margin: 0.5rem;
        border-radius: 10px;
    }

    .card-header {
        color: var(--text-color);
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
    }

    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--primary-color);
    }

    /* Remove padding from containers */
    div[data-testid="stVerticalBlock"],
    .block-container,
    div[data-testid="column"] {
        padding: 0 !important;
        gap: 0 !important;
    }

    /* Column layout */
    div[data-testid="column"] {
        padding: 0.5rem !important;
        display: flex !important;
        flex-direction: column !important;
    }

    /* AI Insights cards */
    .ai-insights-card {
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        background: transparent !important;
        border: 1px solid rgba(45, 127, 249, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        padding: 0 !important;
    }

    .ai-insights-card .card-header {
        border-bottom: 1px solid rgba(45, 127, 249, 0.1) !important;
        margin-bottom: 1rem !important;
        background-color: transparent !important;
        padding: 0.5rem !important;
    }

    .ai-insights-card p {
        margin-bottom: 0.75rem !important;
        padding: 0 0.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# App header
st.markdown('<div class="header-container">', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">🌤️ WeatherSearch</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Intelligent Weather Insights & Forecasts</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

def get_current_weather(city, aqi='yes'):
    """Retrieve current weather data for a given city."""
    if not city:
        return None
        
    url = f"{BASE_URL}?key={WEATHER_API_KEY}&q={city}&aqi={aqi}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 400:
            st.error(f"🔍 City '{city}' not found. Please check the spelling and try again.")
        else:
            st.error(f"⚠️ API Error: {str(e)}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Network Error: Unable to fetch weather data. Please check your internet connection.")
        return None

def display_weather_info(data):
    
    """Display weather information with AI insights."""
    if not data:
        return

    # Extract data
    location = data['location']
    current = data['current']
    
    city = location['name']
    country = location['country']
    temp = current['temp_c']
    feels_like = current['feelslike_c']
    condition = current['condition']['text']
    aqi = current['air_quality']['us-epa-index']
    icon_url = current['condition']['icon']
    if not icon_url.startswith('http:') and not icon_url.startswith('https:'):
        icon_url = f"http:{icon_url}"
    
    
    
    # Display location information
    st.markdown('<div class="weather-card">', unsafe_allow_html=True)
    st.subheader(f"{city}, {country}")
    st.write(f"☁️ {condition}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Display current weather information
    st.markdown('<div class="weather-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header"><strong>🌡️ Current Weather</strong></div>', unsafe_allow_html=True)
    
    # Display weather icon centered
    col_icon = st.columns([1, 1, 1])
    with col_icon[1]:
        st.image(icon_url, use_container_width=True)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Temperature", f"{data['current']['temp_c']}°C")
        st.metric("Feels Like", f"{data['current']['feelslike_c']}°C")
    
    with col2:
        st.metric("Humidity", f"{data['current']['humidity']}%")
        st.metric("Wind Speed", f"{data['current']['wind_kph']} km/h")
    
    with col3:
        st.metric("Air Quality Index", data['current']['air_quality']['us-epa-index'])
        st.metric("Time of Day", "Day" if data['current']['is_day'] == 1 else "Night")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Get and display AI insights if enabled
    if ai_enabled:
        try:
            # Attempt to get and display the summary
            weather_summary = weather_ai.get_weather_summary(data)
            st.info(f"🤖 **AI Summary:**  {weather_summary}")

            # Attempt to get and display the detailed analysis
            try:
                ai_insights = weather_ai.analyze_weather(data)
                # If successful, now display the detailed insights section
                # The original st.markdown('</div>') after st.info is tricky here.
                # Let's assume it was meant to close the main weather card section before AI insights or be part of summary.
                # For the test to pass, the st.error from analyze_weather should not be masked by st.markdown issues.
                # The tests don't check this specific st.markdown('</div>') call.
                # The crucial part is that st.markdown("### 🧠 AI Insights") and subsequent writes only happen if ai_insights is successful.

                st.markdown('</div>', unsafe_allow_html=True) # Placed as in original logic, after summary, before detailed title
                                                              # This implies it closes the "Current Weather" card or similar.

                st.markdown("### 🧠 AI Insights")
                col3, col4 = st.columns(2)
                
                with col3:
                    st.markdown('<div class="weather-card ai-insights-card">', unsafe_allow_html=True)
                    st.markdown('<div class="card-header"><strong>📊 Analysis</strong></div>', unsafe_allow_html=True)
                    st.write(ai_insights['analysis'])
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('<div class="card-header"><strong>👕 Recommendations</strong></div>', unsafe_allow_html=True)
                    st.write(ai_insights['recommendations'])
                    st.markdown('</div>', unsafe_allow_html=True)

                with col4:
                    st.markdown('<div class="weather-card ai-insights-card">', unsafe_allow_html=True)
                    st.markdown('<div class="card-header"><strong>🎯 Suggested Activities</strong></div>', unsafe_allow_html=True)
                    st.write(ai_insights['activities'])
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('<div class="card-header"><strong>💪 Health Advice</strong></div>', unsafe_allow_html=True)
                    st.write(ai_insights['health_advice'])
                    st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e_analyze: # Handle failure of analyze_weather
                st.error(f"Error getting AI insights: {str(e_analyze)}") # Test expects this

        except Exception as e_summary: # Handle failure of get_weather_summary or the initial st.info
            st.error(f"Error getting AI insights: {str(e_summary)}") # Test expects this
    else: # if not ai_enabled
        # This st.markdown was likely intended to close the main current weather card if AI is not enabled.
        # If AI is enabled, that card is closed before AI specific sections, or after.
        # Given the original structure, it was after the st.info(summary) display.
        # This part of the original code is: else: st.markdown('</div>', unsafe_allow_html=True)
        # This should remain to close the "Current Weather" card if AI is disabled.
        st.markdown('</div>', unsafe_allow_html=True)

    # Display additional weather details
    st.markdown('<div class="weather-card">', unsafe_allow_html=True)
    with st.expander("📝 Detailed Weather Information"):
        col5, col6 = st.columns(2)
        
        with col5:
            st.write(f"💨 Wind: {current['wind_kph']} km/h {current['wind_dir']}")
            st.write(f"💧 Humidity: {current['humidity']}%")
            
        with col6:
            st.write(f"📍 Position: {location['lat']}, {location['lon']}")
            st.write(f"🕒 Last updated: {current['last_updated']}")

def main():
    """Main application function"""
    
    # Check for Weather API key
    if not WEATHER_API_KEY:
        st.error("⚠️ Please set up your Weather API key in the .env file!")
        st.code("""
        WEATHER_API_KEY=your_weather_api_key
        """)
        return

    # Display AI status
    if not ai_enabled:
        st.warning("⚠️ AI features are disabled. Add your OpenAI API key to enable AI insights.")
        st.code("""
        OPENAI_API_KEY=your_openai_api_key
        """)

    # City input
    city = st.text_input(
        label="City input field",
        placeholder="Enter a city name (e.g., London, Tokyo, New York)",
        help="Type the name of any city to get current weather information",
        label_visibility="collapsed"
    )

    if city:
        with st.spinner('Fetching weather data...'):
            data = get_current_weather(city)
            if data:
                display_weather_info(data)
    
    # Attribution
    st.markdown(
        '<div style="text-align: center; padding: 20px;">'
        '<a href="https://www.weatherapi.com/" title="Free Weather API">'
        '<img src="http://cdn.weatherapi.com/v4/images/weatherapi_logo.png" '
        'alt="Weather data by WeatherAPI.com" border="0"></a>'
        '</div>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
