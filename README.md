# AI Weather Assistant

An intelligent weather application that combines real-time weather data with AI-powered insights and recommendations.

## Features

- Real-time weather data retrieval
- AI-powered weather analysis and insights
- Personalized recommendations for clothing and activities
- Health advice based on weather conditions
- Natural language weather summaries
- Modern, responsive UI with interactive elements

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root and add your API keys:
   ```
   WEATHER_API_KEY=your_weatherapi_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## AI Features

- **Weather Analysis**: Get AI-powered analysis of current weather conditions
- **Smart Recommendations**: Receive personalized suggestions for clothing and activities
- **Health Insights**: Get relevant health advice based on weather conditions
- **Natural Language**: Weather information presented in natural, easy-to-understand language

## Dependencies

- Python 3.7+
- Streamlit
- OpenAI API
- WeatherAPI
- Requests
- python-dotenv
- tenacity

## API Credits

This application uses:
- [WeatherAPI](https://www.weatherapi.com/) for weather data
- [OpenAI API](https://openai.com/) for AI-powered insights

## License

MIT License
