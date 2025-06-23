import pytest
from weather_ai import WeatherAI

# Initialize WeatherAI (no API key needed for these helper tests)
ai = WeatherAI()

def test_get_temp_description():
    assert "Extremely Cold" in ai._get_temp_description(-25)
    assert "Very Cold to Frigid" in ai._get_temp_description(-10)
    assert "Cold" in ai._get_temp_description(5)
    assert "Cool to Mild" in ai._get_temp_description(20)
    assert "Warm" in ai._get_temp_description(28)
    assert "Hot" in ai._get_temp_description(35)
    assert "Extremely Hot" in ai._get_temp_description(45)
    assert "Unknown" in ai._get_temp_description(1000) # Test edge case

def test_get_wind_description():
    assert "very light breeze" in ai._get_wind_description(3)
    assert "gentle breeze" in ai._get_wind_description(8)
    assert "moderate wind" in ai._get_wind_description(15)
    assert "strong wind" in ai._get_wind_description(25)
    assert "very strong wind" in ai._get_wind_description(35)

def test_get_aqi_description():
    assert "Good" in ai._get_aqi_description(1)
    assert "Moderate" in ai._get_aqi_description(2)
    assert "Unhealthy for Sensitive Groups" in ai._get_aqi_description(3)
    assert "Unhealthy" in ai._get_aqi_description(4)
    assert "Very Unhealthy" in ai._get_aqi_description(5)
    assert "Hazardous" in ai._get_aqi_description(6)
    assert "Unknown" in ai._get_aqi_description(0) # Test edge case
    assert "Unknown" in ai._get_aqi_description(7) # Test edge case

def test_get_day_night_description():
    assert "day" in ai._get_day_night_description(1)
    assert "night" in ai._get_day_night_description(0)

# Sample weather data for testing
sample_weather_data = {
    'location': {
        'name': 'London',
        'country': 'United Kingdom',
        'lat': 51.52,
        'lon': -0.11,
    },
    'current': {
        'temp_c': 15.0,
        'feelslike_c': 14.0,
        'condition': {'text': 'Partly cloudy', 'icon': '//cdn.weatherapi.com/weather/64x64/day/116.png'},
        'humidity': 77,
        'wind_kph': 10.0,
        'wind_dir': 'SW',
        'is_day': 1,
        'air_quality': {'us-epa-index': 1},
        'heatindex_c': 15.0,
        'last_updated': '2023-10-27 10:00'
    }
}

# Mock response for OpenAI API call
class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)

class MockMessage:
    def __init__(self, content):
        self.content = content

class MockCompletion:
    def __init__(self, content):
        self.choices = [MockChoice(content)]

def test_get_weather_summary_success(mocker):
    ai_instance = WeatherAI(api_key="fake_key") # Initialize with a dummy key to instantiate self.client
    # No need to mock self.client.chat.completions.create as get_weather_summary doesn't use it directly

    summary = ai_instance.get_weather_summary(sample_weather_data)
    assert "London" in summary
    assert "15.0°C" in summary
    assert "feels like 14.0°C" in summary
    assert "partly cloudy" in summary.lower() # Ensure case-insensitivity for condition
    assert "humidity levels are at 77%" in summary.lower()
    assert "10.0 km/h" in summary

def test_get_weather_summary_api_error(mocker):
    ai_instance = WeatherAI(api_key="fake_key")
    # Test case where weather_data might be incomplete or malformed
    malformed_data = {"location": {"name": "TestCity"}} # Missing 'current' key
    summary = ai_instance.get_weather_summary(malformed_data)
    assert "Unable to generate weather summary" in summary

def test_analyze_weather_success(mocker):
    ai_instance = WeatherAI(api_key="fake_key")
    mock_response_content = {
        "analysis": "Detailed analysis for London.",
        "recommendations": "Wear layers.",
        "health_advice": "Stay hydrated.",
        "activities": "Go for a walk."
    }
    # Convert dict to string representation of dict for eval
    mock_response_str = str(mock_response_content)

    mocker.patch.object(ai_instance.client.chat.completions, 'create', return_value=MockCompletion(mock_response_str))

    insights = ai_instance.analyze_weather(sample_weather_data)

    assert insights['analysis'] == "Detailed analysis for London."
    assert insights['recommendations'] == "Wear layers."
    assert insights['health_advice'] == "Stay hydrated."
    assert insights['activities'] == "Go for a walk."
    ai_instance.client.chat.completions.create.assert_called_once()

def test_analyze_weather_api_failure(mocker):
    ai_instance = WeatherAI(api_key="fake_key")
    mocker.patch.object(ai_instance.client.chat.completions, 'create', side_effect=Exception("API Error"))

    insights = ai_instance.analyze_weather(sample_weather_data)

    assert insights['analysis'] == 'Unable to analyze weather conditions.'
    assert insights['recommendations'] == 'Recommendations unavailable.'
    assert insights['activities'] == 'Activity suggestions unavailable.'
    assert insights['health_advice'] == 'Health advice unavailable.'
    ai_instance.client.chat.completions.create.assert_called_once()

def test_analyze_weather_parsing_failure(mocker):
    ai_instance = WeatherAI(api_key="fake_key")
    # Simulate an API response that is not a valid dict string for eval
    malformed_response_str = "This is not a dictionary"
    mocker.patch.object(ai_instance.client.chat.completions, 'create', return_value=MockCompletion(malformed_response_str))

    insights = ai_instance.analyze_weather(sample_weather_data)

    assert insights['analysis'] == 'Unable to analyze weather conditions.'
    assert insights['recommendations'] == 'Recommendations unavailable.'
    # ... and so on for other keys
    ai_instance.client.chat.completions.create.assert_called_once()
