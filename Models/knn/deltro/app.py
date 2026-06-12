from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# Load the model once
model = joblib.load('kn_model.pkl')



@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        x = data["input"]

        # Manual encoding
        gender_map = {"Female": 0, "Male": 1}
        cough_map = {"Mild": 0, "Strong": 1}
        city_map = {
            "Bangalore": 0,
            "Delhi": 1,
            "Kolkata": 2,
            "Mumbai": 3
        }

        input_data = np.array([
            x[0],                    # age
            gender_map[x[1]],        # gender
            x[2],                    # fever
            cough_map[x[3]],         # cough
            city_map[x[4]]           # city
        ]).reshape(1, -1)

        prediction = model.predict(input_data)

        return jsonify({
            "prediction": "Yes" if prediction[0] == 1 else "No"
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
