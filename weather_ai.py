from typing import Dict, Any
import os
from openai import OpenAI

class WeatherAI:
    def __init__(self, api_key=None):
        """
        Initialize the WeatherSearch AI engine with OpenAI client.
        
        Args:
            api_key (str, optional): OpenAI API key. If not provided, will try to get from environment.
        """
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))

    # Helper Methods for Weather Analysis
    def _get_temp_description(self, feelslike_c):
        """
        Get a description of the temperature comfort level based on feels-like temperature.
        
        Args:
            feelslike_c (float): The feels-like temperature in Celsius
            
        Returns:
            str: A description of the temperature comfort level
        """
        if feelslike_c < -20:
            return "Extremely Cold – Extreme precautions necessary, high frostbite risk"
        elif -20 <= feelslike_c < 0:
            return "Very Cold to Frigid – Frostbite risk, dress in thermal layers"
        elif 0 <= feelslike_c < 15:
            return "Cold – Need warm clothing, exposure could be uncomfortable"
        elif 15 <= feelslike_c < 25:
            return "Cool to Mild – Generally comfortable, light to medium layers needed"
        elif 25 <= feelslike_c < 30:
            return "Warm – Pleasant for most, dress lightly, stay hydrated"
        elif 30 <= feelslike_c < 40:
            return "Hot – Can be uncomfortable, important to stay cool and hydrated"
        elif feelslike_c >= 40:
            return "Extremely Hot – Dangerous heat levels, risk of heat-related illnesses"
        else:
            return "Unknown temperature comfort level"

    def _get_wind_description(self, wind_kph):
        """
        Get description of wind speed.
        
        Args:
            wind_kph (float): Wind speed in kilometers per hour
            
        Returns:
            str: Description of wind conditions
        """
        if wind_kph < 5:
            return "very light breeze"
        elif wind_kph < 12:
            return "gentle breeze"
        elif wind_kph < 20:
            return "moderate wind"
        elif wind_kph < 30:
            return "strong wind"
        else:
            return "very strong wind"

    def _get_aqi_description(self, aqi):
        """
        Get description of air quality based on AQI level.
        
        Args:
            aqi (int): Air Quality Index value
            
        Returns:
            str: Description of air quality conditions
        """
        aqi_levels = {
            1: "Good - Air quality is satisfactory, and air pollution poses little or no risk.",
            2: "Moderate - Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.",
            3: "Unhealthy for Sensitive Groups - Members of sensitive groups may experience health effects. The general public is less likely to be affected.",
            4: "Unhealthy - Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects",
            5: "Very Unhealthy - Health alert: The risk of health effects is increased for everyone.",
            6: "Hazardous - Health warnings of emergency conditions. The entire population is more likely to be affected."
        }
        return aqi_levels.get(aqi, "Unknown")

    def _get_day_night_description(self, is_day):
        """
        Get description of day or night.
        
        Args:
            is_day (bool): True if it's day, False if it's night
            
        Returns:
            str: Description of day or night
        """
        return "day" if is_day == 1 else "night"
    
    # Main Weather Analysis Methods
    def get_weather_summary(self, weather_data: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of the current weather conditions.
        
        Args:
            weather_data (Dict[str, Any]): Weather data dictionary from API
            
        Returns:
            str: A natural language summary of the weather conditions
        """
        try:
            current = weather_data['current']
            temp = current['temp_c']
            feels_like = current['feelslike_c']
            condition = current['condition']['text']
            humidity = current['humidity']
            wind_kph = current['wind_kph']
            is_day = current['is_day']
            
            temp_desc = self._get_temp_description(feels_like).split(' – ')[0]  # Get just the comfort level
            time_of_day = self._get_day_night_description(is_day)
            wind_desc = self._get_wind_description(wind_kph)
            location_name = weather_data['location']['name']
            
            return f"""During the {time_of_day} in {location_name}, residents can expect {temp_desc.lower()} conditions 
            with {condition.lower()} skies. The temperature stands at {temp}°C, but with the wind chill, 
            it feels like {feels_like}°C. Humidity levels are at {humidity}%, and there is a {wind_desc} 
            blowing at {wind_kph} km/h{', which adds to the cold sensation' if feels_like < temp else ''}. 
            {'Remember to layer up' if feels_like < 10 else 'Stay hydrated' if temp > 25 else 'Enjoy the pleasant weather'} 
            if you're heading outdoors."""
            
        except Exception as e:
            return f"Unable to generate weather summary: {str(e)}"

    def analyze_weather(self, weather_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Analyze weather data and provide detailed insights using AI.
        
        Args:
            weather_data (Dict[str, Any]): Dictionary containing weather information
            
        Returns:
            Dict[str, str]: Dictionary containing analysis, recommendations, health advice, and activities
        """
        try:
            # Extract weather metrics
            temp_c = weather_data['current']['temp_c']
            condition = weather_data['current']['condition']['text']
            humidity = weather_data['current']['humidity']
            wind_kph = weather_data['current']['wind_kph']
            aqi = weather_data['current']['air_quality']['us-epa-index']
            feels_like = weather_data['current']['feelslike_c']
            heat_index = weather_data['current']['heatindex_c']
            is_day = weather_data['current']['is_day']

            # Create AI prompt
            prompt = f"""You are WeatherSearch's expert meteorologist. Analyze the following weather data and provide detailed recommendations:

            Current Weather Conditions:
            🌡️ Temperature Metrics:
            - Current: {temp_c}°C
            - Feels Like: {feels_like}°C ({self._get_temp_description(feels_like)})
            - Heat Index: {heat_index}°C
            - Humidity: {humidity}%

            🌪️ Weather Status:
            - Time: {self._get_day_night_description(is_day).capitalize()}time
            - Condition: {condition}
            - Wind Speed: {wind_kph} km/h ({self._get_wind_description(wind_kph)})

            😷 Air Quality:
            - AQI Level: {aqi} ({self._get_aqi_description(aqi)})

            Required Analysis Format:
            Return a JSON object with these keys, providing specific and actionable information:

            1. "analysis": Combine temperature metrics, weather conditions, time of day, and air quality into a comprehensive weather summary.
            Example: "In the {self._get_day_night_description(is_day)}, {weather_data['location']['name']} is experiencing {condition} conditions at {temp_c}°C, {self._get_temp_description(feels_like)}. Air quality is {self._get_aqi_description(aqi)}."

            2. "recommendations": Suggest specific clothing and comfort measures based on:
            - Temperature comfort level: {self._get_temp_description(feels_like)}
            - Weather conditions: {condition}
            - Wind speed and conditions
            - Time of day adaptations
            Example: "In the {self._get_day_night_description(is_day)}, with {self._get_temp_description(feels_like)} conditions, it's advisable to wear appropriate clothing and take necessary precautions."

            3. "health_advice": Provide health precautions based on:
            - Temperature safety: {self._get_temp_description(feels_like)}
            - Air quality considerations: {self._get_aqi_description(aqi)}
            - UV protection needs
            - Wind chill or heat index factors

            4. "activities": Recommend suitable activities considering:
            - Temperature comfort level
            - AQI level restrictions
            - Time-specific considerations
            Example: "In the {self._get_day_night_description(is_day)}, considering the {self._get_temp_description(feels_like)} conditions and current air quality, recommended activities include..."
            
            Format your response exactly like this:
            {{
                "analysis": "Detailed current conditions analysis",
                "recommendations": "Specific clothing and comfort advice",
                "health_advice": "Health precautions based on AQI and weather",
                "activities": "Suitable activity recommendations"
            }}

            Ensure each section is detailed yet concise (2-3 sentences max) and directly relates to the provided weather data."""

            # Get AI response
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are WeatherSearch's expert meteorologist specializing in providing detailed, actionable weather insights with health and activity recommendations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            # Parse and return the response
            try:
                return eval(response.choices[0].message.content.strip())
            except:
                return {
                    'analysis': 'Unable to analyze weather conditions.',
                    'recommendations': 'Recommendations unavailable.',
                    'activities': 'Activity suggestions unavailable.',
                    'health_advice': 'Health advice unavailable.'
                }

        except Exception as e:
            print(f"Error in analyze_weather: {str(e)}")
            return {
                'analysis': 'Unable to analyze weather conditions.',
                'recommendations': 'Recommendations unavailable.',
                'activities': 'Activity suggestions unavailable.',
                'health_advice': 'Health advice unavailable.'
            }
