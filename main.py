import cv2
import mediapipe as mp
import json
from pythonosc import udp_client
import math

# --- 1. SETUP & LOAD WEIGHTS ---
client = udp_client.SimpleUDPClient("127.0.0.1", 5000)

try:
    with open('filter_weights.json', 'r') as f:
        data = json.load(f)
        BETA = data['parameters']['beta']
        print(f"✅ Loaded Trained Weights: Beta = {BETA}")
except:
    BETA = 0.1
    print("⚠️ Weights not found, using default.")

class OneEuroFilter:
    def __init__(self, beta):
        self.min_cutoff = 1.0
        self.beta = beta
        self.x_prev = 0
    def exponential_smoothing(self, a, x, x_prev):
        return a * x + (1 - a) * x_prev
    def filter(self, x):
        x_filtered = self.exponential_smoothing(self.beta, x, self.x_prev)
        self.x_prev = x_filtered
        return x_filtered

filter_x = OneEuroFilter(BETA)
filter_y = OneEuroFilter(BETA)
filter_z = OneEuroFilter(BETA)

# --- 2. START CAMERA ---
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
cap = cv2.VideoCapture(0)

print("🚀 VR Tracker Running. Press 'q' to quit.")

while cap.isOpened():
    success, image = cap.read()
    if not success: break

    image = cv2.flip(image, 1)
    results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if results.multi_face_landmarks:
        for landmarks in results.multi_face_landmarks:
            nose = landmarks.landmark[1]
            
            raw_x = (nose.x - 0.5) * 5
            raw_y = (nose.y - 0.5) * 5
            raw_z = nose.z * -20

            smooth_x = filter_x.filter(raw_x)
            smooth_y = filter_y.filter(raw_y)
            smooth_z = filter_z.filter(raw_z)

            client.send_message("/head/pos", [smooth_x, smooth_y, smooth_z])

            h, w, _ = image.shape
            cv2.circle(image, (int(nose.x*w), int(nose.y*h)), 5, (0,255,0), -1)

    cv2.imshow('Tracker View', image)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()