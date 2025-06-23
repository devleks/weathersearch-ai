import pytest
from unittest.mock import patch, MagicMock
# Add app.py to sys.path to allow direct import, or adjust PYTHONPATH
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app

# Sample successful API response
mock_weather_data_success = {
    "location": {"name": "London", "country": "UK"},
    "current": {"temp_c": 15}
}

# Sample API response for city not found (400 error)
mock_city_not_found_response = {
    "error": {
        "code": 1006,
        "message": "No matching location found."
    }
}

@patch('app.requests.get')
def test_get_current_weather_success(mock_get):
    # Configure the mock for a successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_weather_data_success
    mock_get.return_value = mock_response

    # Call the function
    result = app.get_current_weather("London")

    # Assertions
    mock_get.assert_called_once() # Verify that requests.get was called
    assert result == mock_weather_data_success

@patch('app.requests.get')
@patch('app.st') # Mock streamlit
def test_get_current_weather_city_not_found(mock_st, mock_get):
    # Configure the mock for a 400 error response
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = mock_city_not_found_response
    # Create an HTTPError instance that http_error.response.status_code can be checked against
    http_error = app.requests.exceptions.HTTPError("400 Client Error")
    http_error.response = mock_response # Attach the mock_response to the error object
    mock_response.raise_for_status.side_effect = http_error
    mock_get.return_value = mock_response

    # Call the function
    result = app.get_current_weather("UnknownCity")

    # Assertions
    mock_get.assert_called_once()
    mock_st.error.assert_called_with("🔍 City 'UnknownCity' not found. Please check the spelling and try again.")
    assert result is None

@patch('app.requests.get')
@patch('app.st') # Mock streamlit
def test_get_current_weather_api_error(mock_st, mock_get):
    # Configure the mock for a generic API error (e.g., 500)
    mock_response = MagicMock()
    mock_response.status_code = 500
    http_error = app.requests.exceptions.HTTPError("500 Server Error")
    http_error.response = mock_response # Attach response to error for status_code check in get_current_weather
    mock_response.raise_for_status.side_effect = http_error
    mock_get.return_value = mock_response

    # Call the function
    result = app.get_current_weather("TestCity")

    # Assertions
    mock_get.assert_called_once()
    mock_st.error.assert_called_with("⚠️ API Error: 500 Server Error")
    assert result is None

@patch('app.requests.get')
@patch('app.st') # Mock streamlit
def test_get_current_weather_network_error(mock_st, mock_get):
    # Configure the mock for a network error
    mock_get.side_effect = app.requests.exceptions.RequestException("Network Error")

    # Call the function
    result = app.get_current_weather("TestCity")

    # Assertions
    mock_get.assert_called_once()
    mock_st.error.assert_called_with("⚠️ Network Error: Unable to fetch weather data. Please check your internet connection.")
    assert result is None

def test_get_current_weather_no_city():
    # Test with no city provided
    result = app.get_current_weather("")
    assert result is None

# Sample data for display_weather_info
sample_display_data = {
    'location': {'name': 'Testville', 'country': 'Testland', 'lat': 0, 'lon': 0}, # Added lat/lon for expander
    'current': {
        'temp_c': 22.0,
        'feelslike_c': 23.0,
        'condition': {'text': 'Sunny', 'icon': 'http://example.com/icon.png'},
        'air_quality': {'us-epa-index': 1},
        'is_day': 1,
        'humidity': 60,
        'wind_kph': 5.0,
        'wind_dir': 'N',
        'last_updated': '2023-01-01 12:00'
    }
}

# Mock WeatherAI class
class MockWeatherAI:
    def __init__(self, api_key=None): # Add api_key param to match original
        pass
    def get_weather_summary(self, data):
        return "Mock AI Summary"
    def analyze_weather(self, data):
        return {
            'analysis': 'Mock Analysis',
            'recommendations': 'Mock Recommendations',
            'activities': 'Mock Activities',
            'health_advice': 'Mock Health Advice'
        }

@patch('app.st')
@patch('app.WeatherAI', new_callable=lambda: MockWeatherAI)
def test_display_weather_info_all_data_ai_enabled(mock_weather_ai_class, mock_st):
    app.ai_enabled = True
    # Crucially, app.weather_ai needs to be an *instance* of the mock class
    app.weather_ai = mock_weather_ai_class()

    mock_st.columns.side_effect = [
        (MagicMock(), MagicMock(), MagicMock()),  # For col_icon
        (MagicMock(), MagicMock(), MagicMock()),  # For col1, col2, col3 (metrics)
        (MagicMock(), MagicMock()),               # For AI insights col3, col4
        (MagicMock(), MagicMock())                # For col5, col6 in expander
    ]

    app.display_weather_info(sample_display_data)

    mock_st.subheader.assert_any_call("Testville, Testland")
    mock_st.write.assert_any_call("☁️ Sunny")
    mock_st.image.assert_any_call("http://example.com/icon.png", use_container_width=True)
    mock_st.metric.assert_any_call("Temperature", "22.0°C")
    mock_st.metric.assert_any_call("Feels Like", "23.0°C")
    mock_st.metric.assert_any_call("Humidity", "60%")
    mock_st.metric.assert_any_call("Wind Speed", "5.0 km/h")
    mock_st.metric.assert_any_call("Air Quality Index", 1)
    mock_st.metric.assert_any_call("Time of Day", "Day")

    mock_st.info.assert_any_call("🤖 **AI Summary:**  Mock AI Summary")

    # Check that AI insights markdown was called
    ai_insights_markdown_called = False
    for call_args in mock_st.markdown.call_args_list:
        if call_args[0][0] == "### 🧠 AI Insights":
            ai_insights_markdown_called = True
            break
    assert ai_insights_markdown_called, "AI Insights markdown should have been called"

    # Check that st.write was called with AI content (simplified)
    # This relies on st.write being called for each piece of AI insight
    mock_st.write.assert_any_call('Mock Analysis')
    mock_st.write.assert_any_call('Mock Recommendations')
    mock_st.write.assert_any_call('Mock Activities')
    mock_st.write.assert_any_call('Mock Health Advice')

    mock_st.expander.assert_any_call("📝 Detailed Weather Information")
    # Check some calls within expander (order might vary due to columns)
    mock_st.write.assert_any_call("💨 Wind: 5.0 km/h N")
    mock_st.write.assert_any_call("💧 Humidity: 60%")
    mock_st.write.assert_any_call("📍 Position: 0, 0")
    mock_st.write.assert_any_call("🕒 Last updated: 2023-01-01 12:00")


@patch('app.st')
def test_display_weather_info_no_data(mock_st):
    app.display_weather_info(None)
    mock_st.subheader.assert_not_called()
    mock_st.metric.assert_not_called()

@patch('app.st')
@patch('app.WeatherAI', new_callable=lambda: MockWeatherAI)
def test_display_weather_info_ai_disabled(mock_weather_ai_class, mock_st):
    app.ai_enabled = False
    app.weather_ai = mock_weather_ai_class()

    mock_st.columns.side_effect = [
        (MagicMock(), MagicMock(), MagicMock()),  # For col_icon
        (MagicMock(), MagicMock(), MagicMock()),  # For col1, col2, col3
        (MagicMock(), MagicMock())               # For col5, col6 in expander
    ]

    app.display_weather_info(sample_display_data)

    mock_st.subheader.assert_any_call("Testville, Testland")
    mock_st.metric.assert_any_call("Temperature", "22.0°C")

    mock_st.info.assert_not_called()

    ai_insights_markdown_called = False
    for call_args in mock_st.markdown.call_args_list:
        if call_args[0][0] == "### 🧠 AI Insights":
            ai_insights_markdown_called = True
            break
    assert not ai_insights_markdown_called, "AI Insights markdown should NOT have been called"

@patch('app.st')
@patch('app.WeatherAI')
def test_display_weather_info_ai_error(mock_weather_ai_class, mock_st):
    app.ai_enabled = True
    mock_ai_instance = mock_weather_ai_class.return_value
    # Ensure the instance is correctly assigned to app.weather_ai for the function to use
    app.weather_ai = mock_ai_instance

    # Simulate error only for get_weather_summary for this specific test
    # analyze_weather might also be called, so let it return default mock values or mock it too
    mock_ai_instance.get_weather_summary.side_effect = Exception("AI Summary Error")
    mock_ai_instance.analyze_weather.return_value = { # ensure analyze_weather doesn't also error
            'analysis': 'Mock Analysis', 'recommendations': 'Mock Recs',
            'activities': 'Mock Acts', 'health_advice': 'Mock Health'
    }

    mock_st.columns.side_effect = [
        (MagicMock(), MagicMock(), MagicMock()),  # For col_icon
        (MagicMock(), MagicMock(), MagicMock()),  # For col1, col2, col3 (metrics)
        (MagicMock(), MagicMock()),               # For AI insights col3, col4
        (MagicMock(), MagicMock())                # For col5, col6 in expander
    ]

    app.display_weather_info(sample_display_data)

    mock_st.subheader.assert_any_call("Testville, Testland")
    mock_st.metric.assert_any_call("Temperature", "22.0°C")
    # The error message in app.py is "Error getting AI insights: {str(e)}"
    # The first part of the AI insights is weather_summary.
    mock_st.error.assert_any_call("Error getting AI insights: AI Summary Error")

@patch('app.st')
@patch('app.WeatherAI')
def test_display_weather_info_ai_error_in_analyze(mock_weather_ai_class, mock_st):
    app.ai_enabled = True
    mock_ai_instance = mock_weather_ai_class.return_value
    app.weather_ai = mock_ai_instance

    # Simulate error for analyze_weather
    mock_ai_instance.get_weather_summary.return_value = "Mock AI Summary" # summary is fine
    mock_ai_instance.analyze_weather.side_effect = Exception("AI Analyze Error")

    mock_st.columns.side_effect = [
        (MagicMock(), MagicMock(), MagicMock()),  # For col_icon
        (MagicMock(), MagicMock(), MagicMock()),  # For col1, col2, col3 (metrics)
        (MagicMock(), MagicMock()),               # For AI insights col3, col4
        (MagicMock(), MagicMock())                # For col5, col6 in expander
    ]

    app.display_weather_info(sample_display_data)

    mock_st.subheader.assert_any_call("Testville, Testland")
    mock_st.metric.assert_any_call("Temperature", "22.0°C")
    mock_st.info.assert_any_call("🤖 **AI Summary:**  Mock AI Summary") # Summary should still display
    mock_st.error.assert_any_call("Error getting AI insights: AI Analyze Error")
