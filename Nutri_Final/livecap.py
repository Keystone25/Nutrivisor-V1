from flask import Flask, render_template, Response, request, flash
import cv2
import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from keras.utils import img_to_array

app = Flask(__name__)
app.config['SECRET_KEY'] = "random string"

# Globals
camera = cv2.VideoCapture(0)
captured_frame = None
food_label = ''

# Load model
km = load_model(
    r'C:/Users/mail4/OneDrive/Desktop/Nutrivisor/Nutrivisor-V1/Nutri_Final/food_detect_model.hdf5',
    compile=False
)

df = pd.read_csv(
    r'C:/Users/mail4/OneDrive/Desktop/Nutrivisor/Nutrivisor-V1/Nutri_Final/calorie_data.csv'
)
labels = list(df['categories'].values)


# 🎥 Live Camera Feed
def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            continue

        ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# 📸 Captured Image Feed
def cap_snap():
    global captured_frame

    if captured_frame is None:
        blank = np.zeros((300, 300, 3), dtype=np.uint8)
        ret, buffer = cv2.imencode('.jpg', blank)
    else:
        ret, buffer = cv2.imencode('.jpg', cv2.flip(captured_frame, 1))

    frame_bytes = buffer.tobytes()

    yield (b'--frame\r\n'
           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# 🧠 Classification
def classify(frame):
    if frame is None:
        return "No image"

    roi = cv2.resize(frame, (299, 299))
    roi = img_to_array(roi)
    roi = np.expand_dims(roi, axis=0)
    roi = roi / 255.0

    pred = km.predict(roi)
    ind = pred.argmax()

    return labels[ind]


# 🌐 Routes
@app.route('/')
def index():
    return render_template('index1.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/capture_snap')
def capture_snap():
    return Response(cap_snap(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/requests', methods=['POST', 'GET'])
def tasks():
    global captured_frame, food_label

    if request.method == 'POST':

        # 📸 Capture + Analyse
        if request.form.get('click') == 'Capture':
            success, frame = camera.read()

            if success:
                captured_frame = frame.copy()
                food_label = classify(captured_frame)

                flash(f"Detected Food: {food_label}")
            else:
                flash("Camera error!")

        # 🧹 Clear
        elif request.form.get('click') == 'Clear':
            captured_frame = None
            food_label = ''
            flash("Cleared")

    return render_template('index1.html')


# 🚀 Run app
if __name__ == '__main__':
    app.run(port=5400, debug=True)