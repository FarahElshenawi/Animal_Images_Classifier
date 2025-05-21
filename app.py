from flask import Flask, request, render_template, jsonify
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from flask_cors import CORS
from io import BytesIO

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
# Load the trained model
model = load_model('model/model.h5')

class_names = ['dog', 'horse', 'elephant', 'butterfly', 'hen', 'cat', 'cow', 'sheep', 'spider', 'squirrel']
print(f"Class names: {class_names}")

# Image preprocessing function
def preprocess_image_file(file):
    file_stream = BytesIO(file.read())
    img = load_img(file_stream, target_size=(224, 224))
    img_array = img_to_array(img)
    img_array = img_array / 255.0  # Rescale to [0,1]
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

@app.route('/predict', methods=['GET', 'POST'])
def upload_predict():
    print(f"Request method: {request.method}")
    print(f"Request headers: {request.headers}")
    print(f"Request files: {request.files}")

    if request.method == 'POST':
        # Check if an image was uploaded
        if 'image' not in request.files:
            print("No image part in request.files")
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        print(f"Uploaded filename: {file.filename}")
        if file.filename == '':
            print("No image selected (empty filename)")
            return jsonify({'error': 'No image selected'}), 400
        
        if file:
            try:
                # Use in-memory file for prediction
                img_array = preprocess_image_file(file)
                predictions = model.predict(img_array)[0]
                predicted_class_idx = np.argmax(predictions)
                predicted_class = class_names[predicted_class_idx]
                confidence = float(predictions[predicted_class_idx]) * 100

                # Format predictions for display
                prediction_results = [
                    {'class': class_names[i], 'confidence': float(predictions[i]) * 100}
                    for i in range(len(class_names))
                ]
                prediction_results.sort(key=lambda x: x['confidence'], reverse=True)

                print(f"Prediction: {predicted_class}, Confidence: {confidence:.2f}%")
                return jsonify({
                   'prediction': predicted_class,
                    'confidence': f"{confidence:.2f}%",
                    'all_predictions': prediction_results
                })
            except Exception as e:
                print(f"Exception during prediction: {e}")
                return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    # Handle GET or any other method
    return jsonify({'message': 'Please use POST to submit an image.'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
