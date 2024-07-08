import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import Label, filedialog
from PIL import Image, ImageTk

# Function to calculate frames per second
def calculate_fps(start_time, end_time, num_frames):
    elapsed_time = end_time - start_time
    fps = num_frames / elapsed_time
    return fps

# Function to update the video frame
def update_frame():
    global frame_count, start_time, fps
    
    ret, frame = cap.read()
    if not ret:
        return

    # Apply background subtraction
    fgmask = fgbg.apply(frame)

    # Apply additional morphological operations to remove noise
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    # Find contours in the foreground mask
    contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Iterate through contours
    for contour in contours:
        # Set a threshold area to consider as motion
        if cv2.contourArea(contour) > 1000:
            # Draw bounding box around the object in motion
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    frame_count += 1
    if frame_count == 30:  # Calculate FPS every 30 frames
        end_time = time.time()
        fps = calculate_fps(start_time, end_time, frame_count)
        frame_count = 0
        start_time = time.time()

    # Display FPS in the corner of the video
    fps_text = f"FPS: {fps:.2f}"
    cv2.putText(frame, fps_text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Convert frame to ImageTk format
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)

    # Update the image on the canvas
    lbl_video.imgtk = imgtk
    lbl_video.configure(image=imgtk)
    
    # Schedule the next frame update
    lbl_video.after(10, update_frame)

# Function to select a video file
def select_video_file():
    global cap
    video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
    if video_path:
        cap = cv2.VideoCapture(video_path)
        update_frame()

# Initialize background subtractor
fgbg = cv2.createBackgroundSubtractorMOG2()

# Variables for FPS calculation
frame_count = 0
start_time = time.time()
fps = 0  # Initialize fps variable

# Setup Tkinter window
root = tk.Tk()
root.title("Motion Detection")

# Create a label to hold the video frame
lbl_video = Label(root)
lbl_video.pack()

# Add a button to select the video file
btn_select_video = tk.Button(root, text="Select Video File", command=select_video_file)
btn_select_video.pack()

# Start the Tkinter main loop
root.mainloop()

# Release video capture when the Tkinter window is closed
cap.release()
