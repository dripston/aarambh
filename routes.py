import os
from flask import render_template, request, jsonify, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import logging
from app import app, db
from models import WeatherData, DisasterRecord, DisasterPrediction, ImageAnalysis
from utils.weather_api import get_weather_data, get_forecast_data
from utils.disaster_prediction import predict_disasters, get_historical_disasters
from utils.image_analysis import analyze_image
from utils.govt_strategies import get_disaster_strategies

logger = logging.getLogger(__name__)

# List of major Indian cities
INDIAN_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", 
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Surat",
    "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane", 
    "Bhopal", "Visakhapatnam", "Patna", "Vadodara", "Ghaziabad"
]

DISASTER_TYPES = [
    "Flood", "Cyclone", "Drought", "Earthquake", "Landslide",
    "Tsunami", "Heat Wave", "Cold Wave", "Urban Flooding", "Forest Fire"
]

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Get the selected city (default: Mumbai)
    selected_city = request.args.get('city', 'Mumbai')
    
    # Get weather data for the selected city
    try:
        weather_data = get_weather_data(selected_city)
        forecast_data = get_forecast_data(selected_city)
    except Exception as e:
        logger.error(f"Error fetching weather data: {str(e)}")
        weather_data = None
        forecast_data = None
        flash(f"Could not fetch weather data: {str(e)}", "danger")
    
    # Get disaster predictions for the selected city
    try:
        disaster_predictions = predict_disasters(selected_city)
    except Exception as e:
        logger.error(f"Error fetching disaster predictions: {str(e)}")
        disaster_predictions = []
        flash(f"Could not fetch disaster predictions: {str(e)}", "danger")
    
    return render_template(
        'dashboard.html',
        cities=INDIAN_CITIES,
        selected_city=selected_city,
        weather_data=weather_data,
        forecast_data=forecast_data,
        disaster_predictions=disaster_predictions
    )

@app.route('/prediction')
def prediction():
    # Get historical disaster data for India
    try:
        historical_disasters = get_historical_disasters()
    except Exception as e:
        logger.error(f"Error fetching historical disaster data: {str(e)}")
        historical_disasters = []
        flash(f"Could not fetch historical disaster data: {str(e)}", "danger")
    
    # Get current disaster predictions for all cities
    try:
        all_predictions = []
        for city in INDIAN_CITIES:
            city_predictions = predict_disasters(city)
            all_predictions.extend(city_predictions)
    except Exception as e:
        logger.error(f"Error fetching disaster predictions: {str(e)}")
        all_predictions = []
        flash(f"Could not fetch disaster predictions: {str(e)}", "danger")
    
    return render_template(
        'prediction.html',
        cities=INDIAN_CITIES,
        disaster_types=DISASTER_TYPES,
        historical_disasters=historical_disasters,
        predictions=all_predictions
    )

@app.route('/image_analysis', methods=['GET', 'POST'])
def image_analysis():
    analysis_result = None
    
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        location = request.form.get('location', '')
        
        # If user does not select file, browser also
        # submits an empty part without filename
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Process the uploaded image
                filename = secure_filename(file.filename)
                
                # Get the file content
                file_content = file.read()
                
                # Analyze the image
                analysis_result = analyze_image(file_content)
                
                # Save analysis result to database
                new_analysis = ImageAnalysis(
                    filename=filename,
                    location=location,
                    analysis_result=analysis_result.get('description', ''),
                    disaster_type=analysis_result.get('disaster_type', ''),
                    confidence_score=analysis_result.get('confidence', 0.0)
                )
                db.session.add(new_analysis)
                db.session.commit()
                
                flash('Image analyzed successfully!', 'success')
                
            except Exception as e:
                logger.error(f"Error analyzing image: {str(e)}")
                flash(f'Error analyzing image: {str(e)}', 'danger')
        else:
            flash('File type not allowed. Please upload JPG, JPEG or PNG files only.', 'danger')
    
    # Get recent analyses from database
    recent_analyses = ImageAnalysis.query.order_by(ImageAnalysis.upload_date.desc()).limit(5).all()
    
    return render_template(
        'image_analysis.html',
        cities=INDIAN_CITIES,
        disaster_types=DISASTER_TYPES,
        analysis_result=analysis_result,
        recent_analyses=recent_analyses
    )

@app.route('/strategies')
def strategies():
    # Get disaster type from query parameters (default: Flood)
    disaster_type = request.args.get('type', 'Flood')
    
    try:
        # Get government strategies for the selected disaster type
        strategies = get_disaster_strategies(disaster_type)
    except Exception as e:
        logger.error(f"Error fetching government strategies: {str(e)}")
        strategies = []
        flash(f"Could not fetch government strategies: {str(e)}", "danger")
    
    return render_template(
        'strategies.html',
        disaster_types=DISASTER_TYPES,
        selected_type=disaster_type,
        strategies=strategies
    )

@app.route('/api/weather/<city>')
def api_weather(city):
    try:
        weather_data = get_weather_data(city)
        return jsonify(weather_data)
    except Exception as e:
        logger.error(f"API Error fetching weather data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/forecast/<city>')
def api_forecast(city):
    try:
        forecast_data = get_forecast_data(city)
        return jsonify(forecast_data)
    except Exception as e:
        logger.error(f"API Error fetching forecast data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/disasters/predictions/<city>')
def api_disaster_predictions(city):
    try:
        predictions = predict_disasters(city)
        return jsonify(predictions)
    except Exception as e:
        logger.error(f"API Error fetching disaster predictions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/disasters/historical')
def api_historical_disasters():
    try:
        historical_disasters = get_historical_disasters()
        return jsonify(historical_disasters)
    except Exception as e:
        logger.error(f"API Error fetching historical disaster data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/strategies/<disaster_type>')
def api_strategies(disaster_type):
    try:
        strategies = get_disaster_strategies(disaster_type)
        return jsonify(strategies)
    except Exception as e:
        logger.error(f"API Error fetching government strategies: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500
