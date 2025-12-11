# CSC173 Deep Computer Vision Project Proposal
**Student:** Angelyn Jimeno
**Date:** December 11, 2025

## 1. Project Title
**Deep Monocular Parallax: Headset-less VR & Immersive Perspectives**

## 2. Problem Statement
**The Problem:** Traditional Virtual Reality (VR) relies on bulky headsets that isolate users and are impractical for casual use. Standard screens, however, are static—no matter how you move your head, the image remains flat 2D, breaking the immersion.

**Motivation:** This project creates a "Headset-less VR" experience. By tracking the user's head in real-time, the system updates the on-screen camera perspective dynamically. The result is a "Window Effect": as the user looks around, the digital world shifts and rotates to match their viewing angle, creating a convincing illusion of depth and 3D space without any wearable hardware.

## 3. Objectives
* **Face Tracking:** Implement **MediaPipe Face Mesh** to detect the user's head position and rotation (6-DoF) from a standard webcam feed.
* **Off-Axis Projection Logic:** Develop an algorithm that translates physical head movements into virtual camera coordinates to create the "Window Effect."
* **Visual Synthesis:** Use **TouchDesigner** to render a reactive "Retro-wave" 3D environment (infinite grid, mountains, sun) that responds instantly to the user's perspective.
* **Integration:** Establish a high-speed OSC (Open Sound Control) bridge to send tracking data from Python to TouchDesigner with minimal latency.

## 4. Dataset Plan
* **Primary Source:** I will utilize the pre-trained **Google MediaPipe Face Mesh model**, capable of inferring 468 3D facial landmarks from a single camera input.
* **Validation:** I will test the system in a controlled study environment, recording performance metrics (latency and jitter) under different lighting conditions to ensure the "Off-Axis Projection" effect remains smooth and nausea-free.

## 5. Technical Approach
* **Input:** Webcam Stream (720p).
* **Processing (Python):** MediaPipe infers the head's $x, y, z$ position and rotation (yaw, pitch, roll).
* **Communication:** `python-osc` library sends coordinate packets to `localhost:5000`.
* **Rendering (TouchDesigner):** A 3D Scene (Grid + Geometry) is viewed through a camera that is controlled by the incoming OSC data.
* **Outcome:** When the user leans left, the camera pans left; when they lean forward, the camera zooms in.

## 6. Expected Challenges
* **Jitter:** Small tremors in detection can cause the screen to shake. *Solution:* Implement a OneEuroFilter to smooth the data.
* **Lag:** Delay destroys the illusion. *Solution:* Use lightweight wireframe graphics to maintain high FPS.