import cv2
import numpy as np
from ultralytics import YOLO
from vidgear.gears import CamGear
import cvzone
from PolyManager import PolylineManager

# Initialize video stream from YouTube
stream = CamGear(source='https://www.youtube.com/watch?v=_TusTf0iZQU', stream_mode=True, logging=True).start()

# Load class names for COCO dataset
with open("coco.txt", "r") as file:
    class_labels = file.read().splitlines()

# Load the YOLOv8 model for detection and tracking
yolo_model = YOLO("yolo11s.pt")

# Create a PolylineManager instance for managing polylines
polyline_manager = PolylineManager()

# Set up the OpenCV window
cv2.namedWindow('VideoStream')

# Mouse callback function for drawing polylines
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        polyline_manager.add_point((x, y))

# Assign the callback to the OpenCV window
cv2.setMouseCallback('VideoStream', mouse_callback)

tracked_up = {}  # Tracks objects moving up
tracked_down = {}  # Tracks objects moving down
unique_up = []  # List of unique objects moving up
unique_down = []  # List of unique objects moving down

while True:
    # Capture a frame from the video stream
    frame = stream.read()
    frame = cv2.resize(frame, (1020, 500))

    # Run YOLO model on the frame
    results = yolo_model.track(frame, persist=True, classes=[2])

    # Process detection results
    if results[0].boxes is not None and results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.int().cpu().tolist()  # Bounding boxes
        class_ids = results[0].boxes.cls.int().cpu().tolist()  # Class IDs
        track_ids = results[0].boxes.id.int().cpu().tolist()  # Track IDs
        confidences = results[0].boxes.conf.cpu().tolist()  # Confidence scores

        for box, class_id, track_id, conf in zip(boxes, class_ids, track_ids, confidences):
            class_label = class_labels[class_id]
            x1, y1, x2, y2 = box
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            # Check if the object is moving up
            if polyline_manager.is_point_in_polyline((center_x, center_y), 'area1'):
                tracked_up[track_id] = (center_x, center_y)
            if track_id in tracked_up:
               if polyline_manager.is_point_in_polyline((center_x, center_y), 'area2'): 
                  cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                  cvzone.putTextRect(frame, f'{track_id}', (x1, y2), 1, 1)
                  cvzone.putTextRect(frame, f'{class_label}', (x1, y1), 1, 1)
                  if unique_up.count(track_id)==0:
                     unique_up.append(track_id)

            # Check if the object is moving down
            if polyline_manager.is_point_in_polyline((center_x, center_y), 'area2'):
                tracked_down[track_id] = (center_x, center_y)
            if track_id in tracked_down:
               if polyline_manager.is_point_in_polyline((center_x, center_y), 'area1'): 
                  cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
                  cvzone.putTextRect(frame, f'{track_id}', (x1, y2), 1, 1)
                  cvzone.putTextRect(frame, f'{class_label}', (x1, y1), 1, 1)
                  if unique_down.count(track_id)==0:
                     unique_down.append(track_id)

    # Display count of objects moving up and down
    count_down = len(unique_down)       
    count_up = len(unique_up)
    cvzone.putTextRect(frame, f'Moving Down: {count_down}', (50, 60), 2, 2)
    cvzone.putTextRect(frame, f'Moving Up: {count_up}', (50, 160), 2, 2)

    # Draw polylines and points on the frame
    frame = polyline_manager.draw_polylines(frame)

    # Display the frame
    cv2.imshow("VideoStream", frame)

    # Handle polyline management through key events
    if not polyline_manager.handle_key_events():
        break

# Release the video stream and close all windows
stream.stop()
cv2.destroyAllWindows()
