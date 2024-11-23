import cv2
from ultralytics import YOLO

# Load the YOLO model
model = YOLO("./yolo11x.pt")
# model = YOLO("./traffic_sign_detector.pt")

# Initialize the webcam
cap = cv2.VideoCapture(0)  # Use 0 for the default webcam; change for external cameras
# cap = cv2.VideoCapture("./assets/video1.mp4")  # Use 0 for the default webcam; change for external cameras

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    # Capture frame from the webcam
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Perform object detection
    results = model(frame, verbose=False)  # Pass the frame to the YOLO model


    print(results)

    # Visualize the results directly on the frame
    annotated_frame = results[0].plot()  # Add detection annotations to the frame

    # Display the frame with detections
    cv2.imshow("YOLO Real-Time Object Detection", annotated_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
