# Tim Deployment, Kelompok 4, Kelas AURAIS, Orbit FA, 2023.
# Maaf jika kodingannya terlihat tidak rapi atau mungkin ada yang kurang dalam pengodiannya, karena kami masih pemula.
# Terima kasih kepada semua yang sudah bekerja sama dalam pembuatan proyek ini.
# Terima kasih juga untuk para coaches yang telah membimbing kami.

import base64
from datetime import datetime
import io
import json
from flask import Flask, jsonify, render_template, request, send_file
import numpy as np
from keras.preprocessing import image
from keras.models import load_model
from PIL import Image, ImageOps 
import pandas as pd
import os

app = Flask(__name__)
model = load_model('casting_product_detection.hdf5')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('aboutus.html')

@app.route('/baca')
def read():
    return render_template('baca.html')

@app.route('/camera')
def camera():
    return render_template('kamera.html')

@app.route('/stats')
def stats():
    return render_template('statistik.html')

@app.route('/upload')
def home():
    return render_template('upload.html')


COUNTER_FILE = 'counter.txt'

def get_current_count():
    try:
        with open(COUNTER_FILE, 'r') as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 0

def increment_count():
    count = get_current_count() + 1
    with open(COUNTER_FILE, 'w') as file:
        file.write(str(count))
    return count

def reset_count():
    with open(COUNTER_FILE, 'w') as file:
        file.write('0')


webcam_image_count = 0  # Global variable to keep track of the webcam image count

@app.route('/webcam_predict', methods=['POST'])
def webcam_predict():
    global webcam_image_count
    webcam_image_count += 1
    image_name = f"image_{increment_count()}.jpg"  # Add file extension
    data = request.get_json()
    image_data = data['image']
    # Convert base64 image to PIL Image
    image_data = base64.b64decode(image_data.split(',')[1])
    img = Image.open(io.BytesIO(image_data))

    # Save the image to the UPLOAD_FOLDER
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
    img.save(save_path)

    # Image preprocessing like in '/predict' route
    img = ImageOps.grayscale(img)
    img = img.resize((300, 300))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0

    prediction = model.predict(img_array)
    is_defective = prediction[0][0] > 0.5
    prediction_result = 'oke' if is_defective else 'cacat'
    result = {'filename': image_name, 'prediction': prediction_result}

    # Save this prediction
    save_prediction(image_name, prediction_result, 'webcam')

    return jsonify({'filename': image_name, 'prediction': prediction_result})


UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

PREDICTIONS_FILE = 'predictions.json'

def save_prediction(filename, prediction, source):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_entry = {'time': current_time, 'filename': filename, 'prediction': prediction, 'source': source}


    try:
        with open(PREDICTIONS_FILE, 'r+') as file:
            data = json.load(file)
            data.append(new_entry)
            file.seek(0)
            json.dump(data, file)
    except FileNotFoundError:
        with open(PREDICTIONS_FILE, 'w') as file:
            json.dump([new_entry], file)

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return render_template('upload.html', error='No file part')

    files = request.files.getlist('file')
    results = {'good': 0, 'defective': 0, 'predictions': []}

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    for file in files:
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

            img = Image.open(filename).convert('L')
            img = ImageOps.grayscale(img)
            img = img.resize((300, 300))
            
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array /= 255.0

            prediction = model.predict(img_array)
            is_defective = prediction[0][0] > 0.5
            prediction_result = 'oke' if is_defective else 'cacat'
            results['predictions'].append({'filename': file.filename, 'prediction': prediction_result})

            if is_defective:
                results['defective'] += 1
            else:
                results['good'] += 1

            # Save this prediction
            save_prediction(file.filename, prediction_result, 'upload')


    return render_template('upload.html', results=results)

@app.route('/get_statistics')
def get_statistics():
    try:
        with open(PREDICTIONS_FILE, 'r') as file:
            data = json.load(file)
            return jsonify(data)
    except FileNotFoundError:
        return jsonify([])
    
@app.route('/delete_entry/<int:index>/<source>', methods=['DELETE'])
def delete_entry(index, source):
    try:
        with open(PREDICTIONS_FILE, 'r+') as file:
            data = json.load(file)
            filtered_data = [d for d in data if d['source'] == source]
            if 0 <= index < len(filtered_data):
                data.remove(filtered_data[index])
                file.seek(0)
                file.truncate()
                json.dump(data, file)

                if not data:
                    reset_count()
                    
                return jsonify({"success": True})
            else:
                return jsonify({"error": "Index out of range"}), 400
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

    
@app.route('/delete_all/<source>', methods=['DELETE'])
def delete_all(source):
    try:
        with open(PREDICTIONS_FILE, 'r+') as file:
            data = json.load(file)
            filtered_data = [d for d in data if d['source'] != source]
            file.seek(0)
            file.truncate()
            json.dump(filtered_data, file)

            if source == 'webcam' and not filtered_data:
                reset_count()

        return jsonify({"success": True, "webcam_empty": source == 'webcam' and not filtered_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/get_current_count', methods=['GET'])
def get_current_counter():
    return jsonify({'count': get_current_count() + 1})

@app.route('/reset_count', methods=['GET'])
def reset_count_endpoint():
    reset_count()
    return jsonify({'success': True})

@app.route('/export_excel')
def export_excel():
    try:
        with open(PREDICTIONS_FILE, 'r') as file:
            data = json.load(file)
            df = pd.DataFrame(data)
            excel_file = 'predictions.xlsx'
            df.to_excel(excel_file, index=False)
            return send_file(excel_file, as_attachment=True)
    except FileNotFoundError:
        return "No data available", 404
    
@app.route('/export_csv')
def export_csv():
    try:
        with open(PREDICTIONS_FILE, 'r') as file:
            data = json.load(file)
            df = pd.DataFrame(data)
            csv_file = 'predictions.csv'
            df.to_csv(csv_file, index=False)
            return send_file(csv_file, as_attachment=True)
    except FileNotFoundError:
        return "No data available", 404
    
@app.route('/export_json')
def export_json():
    try:
        with open(PREDICTIONS_FILE, 'r') as file:
            return send_file(PREDICTIONS_FILE, as_attachment=True, mimetype='application/json')
    except FileNotFoundError:
        return "No data available", 404



if __name__ == '__main__':
    app.run(debug=True)