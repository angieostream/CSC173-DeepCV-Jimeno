import cv2
import mediapipe as mp
import time
import math
import json
from pythonosc import udp_client

IP = "127.0.0.1"
PORT = 5000
SCALE_X = 40.0   
SCALE_Y = -40.0
SCALE_Z = -15.0 

class OneEuroFilter:
    def __init__(self, min_cutoff=1.0, beta=0.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.x_prev = 0
        self.dx_prev = 0
        self.t_prev = 0

    def smoothing_factor(self, t_e, cutoff):
        r = 2 * math.pi * cutoff * t_e
        return r / (r + 1)

    def exponential_smoothing(self, a, x, x_prev):
        return a * x + (1 - a) * x_prev

    def filter(self, t, x):
        t_e = t - self.t_prev
        if self.t_prev == 0: t_e = 0.033 
        
        self.dx = (x - self.x_prev) / t_e if t_e > 0 else 0
        cutoff = self.min_cutoff + self.beta * abs(self.dx)
        a = self.smoothing_factor(t_e, cutoff)
        x_filtered = self.exponential_smoothing(a, x, self.x_prev)
        
        self.x_prev = x_filtered
        self.dx_prev = self.dx
        self.t_prev = t
        return x_filtered

try:
    with open('filter_weights.json', 'r') as f:
        data = json.load(f)
        best_beta = data["parameters"]["beta"]
        best_cutoff = data["parameters"]["min_cutoff"]
        print(f"✅ SUCCESS: Loaded Optimized Parameters -> Beta: {best_beta}")
except:
    print("WARNING: Weight file not found. Using defaults.")
    best_beta = 0.05
    best_cutoff = 1.0

client = udp_client.SimpleUDPClient(IP, PORT)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)
cap = cv2.VideoCapture(0)

fx = OneEuroFilter(min_cutoff=best_cutoff, beta=best_beta)
fy = OneEuroFilter(min_cutoff=best_cutoff, beta=best_beta)
fz = OneEuroFilter(min_cutoff=best_cutoff, beta=best_beta)

print(f"TRACKER RUNNING. Sending to {IP}:{PORT}...")

while cap.isOpened():
    success, image = cap.read()
    if not success: break

    image = cv2.flip(image, 1)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_image)
    
    current_time = time.time()

    if results.multi_face_landmarks:
        nose = results.multi_face_landmarks[0].landmark[1]
        
        raw_x = (nose.x - 0.5) * SCALE_X
        raw_y = (nose.y - 0.5) * SCALE_Y
        raw_z = nose.z * SCALE_Z

        smooth_x = fx.filter(current_time, raw_x)
        smooth_y = fy.filter(current_time, raw_y)
        smooth_z = fz.filter(current_time, raw_z)

        client.send_message("/head/pos", [smooth_x, smooth_y, smooth_z])

        h, w, _ = image.shape
        cx, cy = int(nose.x * w), int(nose.y * h)
        
        cv2.circle(image, (cx, cy), 8, (0, 255, 0), -1)
        cv2.circle(image, (cx, cy), 12, (0, 255, 0), 2)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, f"TRACKING: ACTIVE", (20, 40), font, 0.7, (0, 255, 0), 2)
        cv2.putText(image, f"X: {smooth_x:.2f}", (20, 80), font, 0.6, (200, 255, 200), 1)
        cv2.putText(image, f"Y: {smooth_y:.2f}", (20, 110), font, 0.6, (200, 255, 200), 1)
        cv2.putText(image, f"Z: {smooth_z:.2f}", (20, 140), font, 0.6, (200, 255, 200), 1)
        
        cv2.putText(image, f"FILTER BETA: {best_beta}", (20, h - 30), font, 0.6, (0, 255, 255), 1)

    cv2.imshow('Deep Monocular Parallax (Input)', image)
    if cv2.waitKey(5) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()