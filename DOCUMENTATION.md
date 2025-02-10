# Weather Forecast App - Technical Documentation

## Code Structure and Functionality

This document provides a detailed explanation of the Weather Forecast App's implementation.

### File Structure

```
weather_forecast_app/
├── app.py              # Main application file
├── .env               # Environment variables configuration
├── requirements.txt   # Project dependencies
└── README.md         # Project overview and setup instructions
```

### Code Documentation

#### Import Statements
```python
#!/usr/bin/env python3
import os
import streamlit as st
import requests
from dotenv import load_dotenv
```
- `#!/usr/bin/env python3`: Shebang line that specifies the Python interpreter
- `os`: Used for environment variable handling
- `streamlit`: Main framework for building the web interface
- `requests`: HTTP library for making API calls
- `dotenv`: Package for loading environment variables from .env file

#### Configuration Setup
```python
load_dotenv()

API_KEY = os.getenv('WEATHER_API_KEY')
BASE_URL = "http://api.weatherapi.com/v1/current.json"
```
- `load_dotenv()`: Loads environment variables from .env file
- `API_KEY`: Retrieves the WeatherAPI key from environment variables
- `BASE_URL`: Defines the endpoint URL for the WeatherAPI service

#### Page Configuration
```python
st.set_page_config(
    page_title="Weather Forecast App",
    page_icon="🌤️",
    layout="centered"
)
```
- Sets up the Streamlit page configuration:
  - `page_title`: Browser tab title
  - `page_icon`: Browser tab icon (weather emoji)
  - `layout`: Centers the content on the page

#### Weather Data Retrieval Function
```python
def get_current_weather(city, aqi='yes'):
    """
    Retrieve current weather data for a given city.
    
    Args:
        city (str): Name of the city
        aqi (str): Whether to include air quality data ('yes' or 'no')
    
    Returns:
        dict: Weather data if successful, None otherwise
    """
    if not city:
        return None
        
    url = f"{BASE_URL}?key={API_KEY}&q={city}&aqi={aqi}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None
```
- Function to fetch weather data from the API
- Parameters:
  - `city`: Target city name
  - `aqi`: Air Quality Index inclusion flag
- Includes error handling for API requests
- Returns JSON response or None if request fails

#### Weather Information Display Function
```python
def display_weather_info(data):
    """
    Display weather information in a structured format.
    
    Args:
        data (dict): Weather data from API
    """
    if not data:
        return

    # Data Extraction
    location = data['location']
    current = data['current']
    
    city = location['name']
    country = location['country']
    latitude = location['lat']
    longitude = location['lon']
    last_update = current['last_updated']
    temp = current['temp_c']
    feels_like = current['feelslike_c']
    condition = current['condition']['text']
    icon = f"http:{current['condition']['icon']}"
    wind_kph = current['wind_kph']
    humidity = current['humidity']
    wind_direction = current['wind_dir']

    # Layout Creation
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(icon, width=100)
        
    with col2:
        st.subheader(f"{city}, {country}")
        st.write(f"🌡️ {temp}°C (Feels like: {feels_like}°C)")
        st.write(f"☁️ {condition}")

    with st.container():
        st.write("---")
        col3, col4 = st.columns(2)
        
        with col3:
            st.write(f"💨 Wind: {wind_kph} km/h {wind_direction}")
            st.write(f"💧 Humidity: {humidity}%")
            
        with col4:
            st.write(f"📍 Position: {latitude}, {longitude}")
            st.write(f"🕒 Last updated: {last_update}")
```
- Function to display weather data in the UI
- Organizes data into a user-friendly layout using Streamlit components
- Uses columns and containers for structured layout
- Incorporates emojis for better visual representation

#### Main Application Function
```python
def main():
    """Main application function"""
    st.title('🌤️ Weather Forecast App')
    
    city = st.text_input(
        "Enter a city name",
        placeholder="e.g., London, Tokyo, New York"
    )

    if city:
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
```
- Main function that orchestrates the application flow
- Creates the title and input field for city name
- Calls weather data retrieval and display functions
- Includes WeatherAPI attribution as required by the service

#### Application Entry Point
```python
if __name__ == "__main__":
    main()
```
- Standard Python idiom to run the main function when the script is executed directly

## UI Components

The application uses several Streamlit components to create an intuitive user interface:

1. **Text Input**: For city name entry
2. **Columns**: For organized layout of weather information
3. **Container**: For grouping related information
4. **Markdown**: For formatted text and HTML content
5. **Image**: For weather condition icons

## Error Handling

The application includes error handling for:
- Empty city input
- Failed API requests
- Invalid API responses

## Environment Variables

The application uses a `.env` file to manage sensitive configuration:
```
WEATHER_API_KEY=your_api_key_here
```

## API Integration

The application integrates with WeatherAPI.com's REST API:
- Endpoint: `http://api.weatherapi.com/v1/current.json`
- Parameters:
  - `key`: API authentication key
  - `q`: City name query
  - `aqi`: Air quality data flag

## Best Practices Implemented

1. **Security**:
   - API key stored in environment variables
   - No sensitive data in code

2. **Code Organization**:
   - Modular functions with single responsibilities
   - Clear function documentation
   - Consistent error handling

3. **User Experience**:
   - Intuitive layout
   - Visual feedback with icons and emojis
   - Clear error messages
   - Responsive design

4. **Performance**:
   - Efficient API calls
   - Minimal state management
   - Optimized imports
