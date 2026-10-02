from flask import Flask, request, jsonify, render_template
import joblib
import os
import ollama
app = Flask(__name__)

model_path = os.path.join("Agent","soil_recommendation_model.pkl")
model = joblib.load(model_path)
def landfill_suitability(soil, groundwater):

    if soil == "Arid" and groundwater > 20:
        return "Suitable"

    if soil == "Alluvial" and groundwater < 10:
        return "Not Suitable"

    return "Moderate"

def explain_prediction(soil, temperature, rainfall, humidity, soil_moisture):

    prompt = f"""
    A machine learning model predicted the soil type as {soil}.

    Environmental conditions:
    Temperature: {temperature} °C
    Rainfall: {rainfall} mm
    Humidity: {humidity} %
    Soil moisture: {soil_moisture} %

    Explain briefly why this soil type might occur under these conditions.
    """

    response = ollama.chat(
        model="llama3.2",   # or llama3.2 if you downloaded that
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/prediction")
def prediction_page():
    return render_template("prediction.html")

@app.route("/about")
def about():
    return render_template("aboutus.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")
    
@app.route("/predict", methods=["POST"])

def predict():
    data = request.json
    print("Received data:", data)
    temperature = float(data["temperature"])
    rainfall = float(data["rainfall"])
    humidity = float(data["humidity"])
    soil_moisture = float(data["soil_moisture"])
    latitude = float(data["latitude"])
    longitude = float(data["longitude"])
    distance_coast = float(data["distance_coast"])
    groundwater = float(data["groundwater"])
    print("Temperature received:", temperature)
    if not (-10 <= temperature <= 60):
        return jsonify({"error": "Temperature must be between -10 and 60°C"})

    if not (0 <= humidity <= 100):
        return jsonify({"error": "Humidity must be between 0 and 100%"})

    if not (0 <= soil_moisture <= 100):
        return jsonify({"error": "Soil moisture must be between 0 and 100%"})

    if not (-90 <= latitude <= 90):
        return jsonify({"error": "Latitude must be between -90 and 90"})

    if not (-180 <= longitude <= 180):
        return jsonify({"error": "Longitude must be between -180 and 180"})

    if not (0 <= groundwater <= 200):
        return jsonify({"error": "Groundwater depth must be between 0 and 200 meters"})

    features = [[
        temperature,
        rainfall,
        humidity,
        soil_moisture,
        latitude,
        longitude,
        distance_coast,
        groundwater
    ]]

    prediction = model.predict(features)[0]

    suitability = landfill_suitability(
        prediction,
        groundwater
    )
    explanation = explain_prediction(
    prediction,
    temperature,
    rainfall,
    humidity,
    soil_moisture
    )
    return jsonify({
        "predicted_soil": prediction,
        "landfill_suitability": suitability,
        "explanation": explanation
    })

if __name__ == "__main__":
    app.run(debug=True)