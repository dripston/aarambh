import requests
import logging
import json
import os
import base64
from io import BytesIO
import traceback

logger = logging.getLogger(__name__)

# Hugging Face API token from environment variable
HUGGINGFACE_API_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN", "")

# Image classification model for disaster detection
DISASTER_MODEL_URL = "https://api-inference.huggingface.co/models/davanstrien/disaster_types"

# General image captioning model as fallback
CAPTION_MODEL_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base"

def analyze_image(image_data):
    """
    Analyze an uploaded image to identify potential disasters
    
    Args:
        image_data: Binary image data
        
    Returns:
        dict: Analysis results including disaster type, description, etc.
    """
    try:
        # First try disaster-specific classifier
        disaster_results = classify_disaster(image_data)
        
        # If classification confidence is low, use general image captioning as fallback
        if disaster_results.get("confidence", 0) < 0.5:
            caption_results = generate_image_caption(image_data)
            
            # Try to infer disaster type from caption
            disaster_type = infer_disaster_from_caption(caption_results.get("caption", ""))
            
            return {
                "disaster_type": disaster_type,
                "description": caption_results.get("caption", ""),
                "confidence": 0.4,  # Lower confidence for inferred results
                "analysis_method": "caption_inference"
            }
        
        return disaster_results
    
    except Exception as e:
        logger.error(f"Error in image analysis: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return a fallback response
        return {
            "disaster_type": "Unknown",
            "description": "Could not analyze the image. Please try again with a clearer image.",
            "confidence": 0.0,
            "error": str(e)
        }

def classify_disaster(image_data):
    """
    Classify an image using the disaster detection model
    """
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"
    }
    
    try:
        response = requests.post(
            DISASTER_MODEL_URL,
            headers=headers,
            data=image_data
        )
        response.raise_for_status()
        
        # Parse results
        results = response.json()
        
        if isinstance(results, list) and len(results) > 0:
            # Find the prediction with highest confidence
            sorted_results = sorted(results, key=lambda x: x.get("score", 0), reverse=True)
            top_result = sorted_results[0]
            
            disaster_type_map = {
                "fire": "Forest Fire",
                "flood": "Flood",
                "earthquake": "Earthquake",
                "cyclone": "Cyclone",
                "landslide": "Landslide",
                "non_disaster": "No Disaster"
            }
            
            disaster_type = disaster_type_map.get(top_result.get("label", "").lower(), "Unknown")
            
            return {
                "disaster_type": disaster_type,
                "confidence": top_result.get("score", 0),
                "description": f"The image shows signs of a {disaster_type.lower()}.",
                "analysis_method": "classification"
            }
        
        # If results are empty or not in expected format
        return {
            "disaster_type": "Unknown",
            "confidence": 0.0,
            "description": "Could not classify the image.",
            "analysis_method": "classification_failed"
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in disaster classification API call: {str(e)}")
        raise Exception(f"Failed to classify image: {str(e)}")

def generate_image_caption(image_data):
    """
    Generate a caption for the image using a general image captioning model
    """
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"
    }
    
    try:
        response = requests.post(
            CAPTION_MODEL_URL,
            headers=headers,
            data=image_data
        )
        response.raise_for_status()
        
        # Parse results
        results = response.json()
        
        if isinstance(results, list) and len(results) > 0:
            caption = results[0].get("generated_text", "")
            
            return {
                "caption": caption,
                "success": True
            }
        
        # If results are empty or not in expected format
        return {
            "caption": "Could not generate a caption for this image.",
            "success": False
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in image captioning API call: {str(e)}")
        raise Exception(f"Failed to generate image caption: {str(e)}")

def infer_disaster_from_caption(caption):
    """
    Attempt to infer disaster type from image caption
    """
    caption = caption.lower()
    
    disaster_keywords = {
        "flood": ["flood", "flooded", "flooding", "water level", "submerged", "inundated"],
        "fire": ["fire", "burning", "flames", "smoke", "wildfire", "forest fire"],
        "earthquake": ["earthquake", "quake", "tremor", "collapsed", "rubble", "destruction"],
        "cyclone": ["cyclone", "hurricane", "typhoon", "storm", "wind", "tornadic"],
        "landslide": ["landslide", "mudslide", "rockfall", "collapsed hill", "debris flow"],
        "drought": ["drought", "dry", "arid", "parched", "cracked earth"],
        "tsunami": ["tsunami", "tidal wave", "giant wave"],
        "heat wave": ["heat wave", "extreme heat", "scorching"]
    }
    
    # Check for disaster keywords in caption
    for disaster, keywords in disaster_keywords.items():
        for keyword in keywords:
            if keyword in caption:
                disaster_type_map = {
                    "flood": "Flood",
                    "fire": "Forest Fire",
                    "earthquake": "Earthquake",
                    "cyclone": "Cyclone",
                    "landslide": "Landslide",
                    "drought": "Drought",
                    "tsunami": "Tsunami",
                    "heat wave": "Heat Wave"
                }
                return disaster_type_map.get(disaster)
    
    return "Unknown"
