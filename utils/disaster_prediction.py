import requests
import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Mapping of seasons to months in India
SEASONS = {
    "Winter": [1, 2],
    "Summer": [3, 4, 5],
    "Monsoon": [6, 7, 8, 9],
    "Post-Monsoon": [10, 11],
    "Pre-Winter": [12]
}

# Mapping of disaster types to seasons when they're more likely
SEASONAL_DISASTERS = {
    "Flood": ["Monsoon"],
    "Cyclone": ["Monsoon", "Post-Monsoon"],
    "Drought": ["Summer"],
    "Heat Wave": ["Summer"],
    "Cold Wave": ["Winter"],
    "Landslide": ["Monsoon"],
    "Forest Fire": ["Summer"],
    "Urban Flooding": ["Monsoon"]
}

# Regional disaster susceptibility
REGIONAL_DISASTERS = {
    "Mumbai": ["Flood", "Urban Flooding", "Cyclone"],
    "Delhi": ["Heat Wave", "Cold Wave", "Urban Flooding"],
    "Bangalore": ["Drought", "Urban Flooding"],
    "Hyderabad": ["Flood", "Heat Wave"],
    "Chennai": ["Flood", "Cyclone", "Urban Flooding"],
    "Kolkata": ["Flood", "Cyclone"],
    "Pune": ["Landslide", "Flood"],
    "Ahmedabad": ["Heat Wave", "Flood"],
    "Jaipur": ["Heat Wave", "Drought"],
    "Surat": ["Flood", "Cyclone"],
    "Lucknow": ["Flood", "Heat Wave", "Cold Wave"],
    "Kanpur": ["Flood", "Heat Wave", "Cold Wave"],
    "Nagpur": ["Heat Wave", "Drought"],
    "Indore": ["Heat Wave"],
    "Thane": ["Flood", "Landslide"],
    "Bhopal": ["Flood"],
    "Visakhapatnam": ["Cyclone", "Flood"],
    "Patna": ["Flood"],
    "Vadodara": ["Flood"],
    "Ghaziabad": ["Urban Flooding", "Heat Wave", "Cold Wave"]
}

def predict_disasters(city):
    """
    Predict potential disasters for a city based on historical patterns,
    current season, and regional susceptibility
    """
    if city not in REGIONAL_DISASTERS:
        raise ValueError(f"City '{city}' is not supported")
    
    # Get current month to determine season
    current_month = datetime.now().month
    current_season = None
    for season, months in SEASONS.items():
        if current_month in months:
            current_season = season
            break
    
    predictions = []
    
    # Get disasters that the city is susceptible to
    susceptible_disasters = REGIONAL_DISASTERS.get(city, [])
    
    for disaster_type in susceptible_disasters:
        # Check if the disaster is seasonal and more likely in the current season
        is_seasonal = False
        for season in SEASONAL_DISASTERS.get(disaster_type, []):
            if season == current_season:
                is_seasonal = True
                break
        
        # Calculate probability based on seasonality
        if is_seasonal:
            probability = random.uniform(0.6, 0.9)  # Higher probability in appropriate season
            severity = random.randint(3, 5)
        else:
            probability = random.uniform(0.1, 0.4)  # Lower probability out of season
            severity = random.randint(1, 3)
        
        # For demonstration purposes, adjust some probabilities based on known patterns
        # In a real application, this would be based on actual prediction models
        if disaster_type == "Flood" and current_season == "Monsoon":
            probability = random.uniform(0.7, 0.95)
            severity = random.randint(4, 5)
        elif disaster_type == "Heat Wave" and current_season == "Summer":
            probability = random.uniform(0.8, 0.95)
            severity = random.randint(3, 5)
        elif disaster_type == "Cyclone" and current_season in ["Monsoon", "Post-Monsoon"]:
            probability = random.uniform(0.6, 0.85)
            severity = random.randint(3, 5)
        
        # Add prediction if probability is significant
        if probability > 0.3:
            valid_days = random.randint(5, 14)  # Prediction valid for 5-14 days
            predictions.append({
                "disaster_type": disaster_type,
                "location": city,
                "probability": round(probability, 2),
                "severity": severity,
                "prediction_date": datetime.now().strftime("%Y-%m-%d"),
                "valid_until": (datetime.now() + timedelta(days=valid_days)).strftime("%Y-%m-%d"),
                "description": get_disaster_description(disaster_type, severity),
                "precautions": get_disaster_precautions(disaster_type)
            })
    
    return predictions

def get_historical_disasters():
    """
    Fetch historical disaster data from ReliefWeb API
    Focusing on India's past disasters
    """
    url = "https://api.reliefweb.int/v1/disasters"
    params = {
        "appname": "climate-disaster-app",
        "profile": "list",
        "preset": "latest",
        "slim": 1,
        "query[value]": "primary_country.name:India",
        "limit": 20
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        disasters = []
        for item in data.get("data", []):
            fields = item.get("fields", {})
            
            disaster = {
                "id": fields.get("id"),
                "name": fields.get("name"),
                "description": fields.get("description", ""),
                "status": fields.get("status"),
                "date": fields.get("date", {}).get("event"),
                "type": fields.get("type", [{}])[0].get("name") if fields.get("type") else None,
                "country": "India",
                "url": fields.get("url")
            }
            
            disasters.append(disaster)
        
        return disasters
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching historical disaster data: {str(e)}")
        raise Exception(f"Failed to fetch historical disaster data: {str(e)}")

def get_disaster_description(disaster_type, severity):
    """
    Get a description of the predicted disaster based on type and severity
    """
    descriptions = {
        "Flood": [
            "Minor flooding possible in low-lying areas",
            "Moderate flooding expected in vulnerable areas",
            "Significant flooding likely, affecting residential areas",
            "Major flooding expected, potential for evacuations",
            "Severe flooding predicted, high risk to life and property"
        ],
        "Cyclone": [
            "Mild cyclonic conditions possible",
            "Moderate cyclonic activity expected",
            "Strong cyclone likely, prepare for heavy rain and winds",
            "Severe cyclone expected, significant damage possible",
            "Catastrophic cyclone predicted, extreme danger to life and property"
        ],
        "Drought": [
            "Mild water scarcity possible",
            "Moderate drought conditions expected",
            "Significant drought likely, affecting agriculture",
            "Severe drought expected, water rationing possible",
            "Extreme drought predicted, widespread crop failure likely"
        ],
        "Earthquake": [
            "Minor tremors possible",
            "Moderate seismic activity expected",
            "Significant earthquake likely, prepare for aftershocks",
            "Major earthquake expected, significant damage possible",
            "Catastrophic earthquake predicted, extreme damage likely"
        ],
        "Landslide": [
            "Minor soil movement possible in hilly areas",
            "Moderate landslide risk in vulnerable areas",
            "Significant landslides likely in multiple locations",
            "Major landslides expected, evacuations may be necessary",
            "Catastrophic landslides predicted, extreme danger in hilly regions"
        ],
        "Heat Wave": [
            "Slightly above average temperatures expected",
            "Moderate heat wave conditions likely",
            "Significant heat wave expected, take precautions",
            "Severe heat wave predicted, high risk to vulnerable populations",
            "Extreme heat wave, life-threatening conditions likely"
        ],
        "Cold Wave": [
            "Slightly below average temperatures expected",
            "Moderate cold wave conditions likely",
            "Significant cold wave expected, take precautions",
            "Severe cold wave predicted, high risk to vulnerable populations",
            "Extreme cold wave, life-threatening conditions likely"
        ],
        "Urban Flooding": [
            "Minor urban flooding possible in low-lying areas",
            "Moderate urban flooding expected, traffic disruptions likely",
            "Significant urban flooding likely, affecting residential areas",
            "Major urban flooding expected, potential for evacuations",
            "Severe urban flooding predicted, high risk in metropolitan areas"
        ],
        "Forest Fire": [
            "Low risk of isolated forest fires",
            "Moderate forest fire conditions developing",
            "Significant forest fire risk, multiple outbreaks possible",
            "High forest fire danger, large-scale fires possible",
            "Extreme forest fire conditions, catastrophic spread likely"
        ]
    }
    
    # Adjust severity to 0-4 index for the descriptions list
    severity_index = min(severity - 1, 4)
    
    return descriptions.get(disaster_type, ["Unknown disaster type"])[severity_index]

def get_disaster_precautions(disaster_type):
    """
    Get precautionary measures for different disaster types
    """
    precautions = {
        "Flood": [
            "Move to higher ground immediately if instructed",
            "Avoid walking or driving through flood waters",
            "Prepare an emergency kit with essential items",
            "Follow evacuation orders from local authorities",
            "Turn off utilities at the main switches before evacuating"
        ],
        "Cyclone": [
            "Secure loose items around your home",
            "Stay indoors during the cyclone",
            "Keep emergency supplies ready",
            "Listen to radio or TV for updates",
            "Evacuate if instructed by authorities"
        ],
        "Drought": [
            "Conserve water at home and work",
            "Follow water usage restrictions",
            "Use drought-resistant plants in landscaping",
            "Harvest rainwater if possible",
            "Report water leaks to authorities"
        ],
        "Earthquake": [
            "Drop, cover, and hold on during shaking",
            "Stay away from windows and exterior walls",
            "If outdoors, move to an open area away from buildings",
            "Be prepared for aftershocks",
            "Check for injuries and damage after the earthquake"
        ],
        "Landslide": [
            "Be alert for unusual sounds that might indicate moving debris",
            "Evacuate if instructed by authorities",
            "Avoid areas prone to landslides",
            "Watch for flooding which may accompany landslides",
            "Contact local officials if you notice land movement"
        ],
        "Heat Wave": [
            "Stay in air-conditioned areas when possible",
            "Drink plenty of fluids, especially water",
            "Avoid strenuous activities during peak heat",
            "Wear lightweight, light-colored clothing",
            "Check on elderly neighbors and relatives"
        ],
        "Cold Wave": [
            "Stay indoors during extreme cold",
            "Layer clothing to stay warm",
            "Keep emergency heating equipment and supplies",
            "Protect pipes from freezing",
            "Check on elderly neighbors and relatives"
        ],
        "Urban Flooding": [
            "Move to higher floors in buildings",
            "Avoid driving or walking through flooded streets",
            "Be cautious around electrical equipment in flooded areas",
            "Follow evacuation orders",
            "Be aware of contaminated water"
        ],
        "Forest Fire": [
            "Evacuate immediately if instructed",
            "Create defensible space around your home",
            "Have an emergency kit ready",
            "Monitor local news for updates",
            "Keep windows and doors closed to prevent smoke inhalation"
        ]
    }
    
    return precautions.get(disaster_type, ["Follow general safety instructions"])
