from flask import Flask, request, render_template
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import os

app = Flask(__name__)

# Load the trained model
model = load_model('model/model.h5')

class_names= ['cane', 'cavallo', 'elefante', 'farfalla', 'gallina', 'gatto', 'mucca', 'pecora', 'ragno', 'scoiattolo']
print(f"Class names: {class_names}")

# Image preprocessing function
def preprocess_image(image_path):
    img = load_img(image_path, target_size=(224, 224))
    img_array = img_to_array(img)
    img_array = img_array / 255.0  # Rescale to [0,1]
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

@app.route('/', methods=['GET', 'POST'])
def upload_predict():
    if request.method == 'POST':
        # Check if an image was uploaded
        if 'image' not in request.files:
            return render_template('index.html', error='No image uploaded')
        
        file = request.files['image']
        if file.filename == '':
            return render_template('index.html', error='No image selected')
        
        if file:
            # Save the uploaded image temporarily
            upload_folder = 'uploads'
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, file.filename)
            file.save(file_path)
            
            # Preprocess and predict
            img_array = preprocess_image(file_path)
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
            
            # Clean up the uploaded file
            os.remove(file_path)
            
            return render_template(
                'index.html',
                prediction=predicted_class,
                confidence=f"{confidence:.2f}%",
                all_predictions=prediction_results
            )
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)