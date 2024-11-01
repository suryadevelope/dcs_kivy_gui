import os
import cv2
from deepface import DeepFace

# Define a directory to store registered faces
database_path = "registered_faces"
if not os.path.exists(database_path):
    os.makedirs(database_path)

def register_face(name):
    """Capture an image from the webcam to register a new face."""
    cap = cv2.VideoCapture(0)
    print(f"Press 's' to capture and save the face for {name}")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image.")
            break
        cv2.imshow("Register Face", frame)

        # Wait for 's' key to save the image
        if cv2.waitKey(1) & 0xFF == ord('s'):
            save_path = os.path.join(database_path, f"{name}.jpg")
            cv2.imwrite(save_path, frame)
            print(f"Face registered and saved as {save_path}")
            break
    cap.release()
    cv2.destroyAllWindows()

def detect_face():
    """Capture video frames, detect faces, and verify them using registered images."""
    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    print("Starting real-time face detection. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame.")
            break

        # Convert frame to grayscale for face detection
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the frame using OpenCV
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        found_match = False
        for (x, y, w, h) in faces:
            # Draw a bounding box around the detected face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Extract the face region for verification
            face_crop = frame[y:y+h, x:x+w]

            # Loop through registered faces and check if any match
            for file_name in os.listdir(database_path):
                registered_face_path = os.path.join(database_path, file_name)
                try:
                    result = DeepFace.verify(img1_path=face_crop, img2_path=registered_face_path, model_name="VGG-Face", enforce_detection=False, detector_backend='opencv')
                    if result["verified"]:
                        name = file_name.split(".")[0]  # Extract name from filename
                        cv2.putText(frame, f"Detected: {name}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        found_match = True
                        break
                except Exception as e:
                    print(f"Error verifying face: {e}")

            if not found_match:
                cv2.putText(frame, "No Match Found", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # Display the resulting frame
        cv2.imshow("Face Detection", frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    print("Options:\n1. Register Face\n2. Detect Face\n3. Exit")
    while True:
        choice = input("Enter your choice: ")
        if choice == "1":
            name = input("Enter name to register: ")
            register_face(name)
        elif choice == "2":
            detect_face()
        elif choice == "3":
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
