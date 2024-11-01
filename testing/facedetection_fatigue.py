import dlib
import face_recognition
import os
import cv2
import numpy as np

KNOWN_FACES_DIR = "../registered_faces"  # training data
TOLERANCE = 0.7
FRAME_THICKNESS = 3  # rectangle thickness
FONT_THICKNESS = 2  # font thickness
MODEL = "cnn"  # convolutional
video = cv2.VideoCapture(0)  # use webcam as input (source of test images)
print("Loading known faces")

known_faces = []  # store known faces here
known_names = []  # store names here
print(dlib.DLIB_USE_CUDA)  # True if CUDA is enabled

# Load dlib's face detector and facial landmarks predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("./shape_predictor_68_face_landmarks.dat")  # download model from dlib

### TRAIN THE CNN MODEL ON KNOWN FACES #############################
for name in os.listdir(KNOWN_FACES_DIR):
    for filename in os.listdir(f"{KNOWN_FACES_DIR}/{name}"):
        image = face_recognition.load_image_file(f"{KNOWN_FACES_DIR}/{name}/{filename}")
        encoding = face_recognition.face_encodings(image)[0]
        known_faces.append(encoding)
        known_names.append(name)
####################################################################

def eye_aspect_ratio(eye_points):
    # Calculate distances between vertical eye landmarks
    A = np.linalg.norm(eye_points[1] - eye_points[5])
    B = np.linalg.norm(eye_points[2] - eye_points[4])
    # Calculate distance between horizontal eye landmarks
    C = np.linalg.norm(eye_points[0] - eye_points[3])
    # Compute eye aspect ratio
    ear = (A + B) / (2.0 * C)
    return ear

def mouth_aspect_ratio(mouth_points):
    # Calculate distances between vertical mouth landmarks
    A = np.linalg.norm(mouth_points[2] - mouth_points[10])  # 51, 59
    B = np.linalg.norm(mouth_points[4] - mouth_points[8])   # 53, 57
    # Calculate distance between horizontal mouth landmarks
    C = np.linalg.norm(mouth_points[0] - mouth_points[6])   # 49, 55
    # Compute mouth aspect ratio
    mar = (A + B) / (2.0 * C)
    return mar

# Threshold values for drowsiness
EYE_AR_THRESHOLD = 0.25
MOUTH_AR_THRESHOLD = 0.75
DROWSINESS_FRAMES = 20
COUNTER = 0

while True:
    ret, image = video.read()  # obtain new image from webcam
    locations = face_recognition.face_locations(image, model=MODEL)  # find face
    encodings = face_recognition.face_encodings(image, locations)  # extract face features

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face_encoding, face_location in zip(encodings, locations):
        results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)
        match = None
        if True in results:  # if there is a known face
            match = known_names[results.index(True)]  # who that person is
            print(f"Match found: {match}")

            ### DRAW RECTANGLE AROUND THE FACE
            top_left = (face_location[3], face_location[0])
            bottom_right = (face_location[1], face_location[2])
            color = [0, 255, 0]  # green
            cv2.rectangle(image, top_left, bottom_right, color, FRAME_THICKNESS)
            top_left = (face_location[3], face_location[2])
            bottom_right = (face_location[1], face_location[2] + 22)
            cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
            cv2.putText(image, match, (face_location[3] + 10, face_location[2] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), FONT_THICKNESS)

    # Detect drowsiness based on eyes and mouth
    for face in faces:
        landmarks = predictor(gray, face)

        # Extract the coordinates of the eye and mouth landmarks
        left_eye_points = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(36, 42)])
        right_eye_points = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(42, 48)])
        mouth_points = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(48, 60)])

        # Calculate aspect ratios
        left_eye_ear = eye_aspect_ratio(left_eye_points)
        right_eye_ear = eye_aspect_ratio(right_eye_points)
        mouth_mar = mouth_aspect_ratio(mouth_points)

        # Average eye aspect ratio
        ear = (left_eye_ear + right_eye_ear) / 2.0

        # Check for closed eyes (sleeping)
        if ear < EYE_AR_THRESHOLD:
            COUNTER += 1
            if COUNTER >= DROWSINESS_FRAMES:
                cv2.putText(image, "DROWSINESS ALERT!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            COUNTER = 0

        # Check for yawning
        if mouth_mar > MOUTH_AR_THRESHOLD:
            cv2.putText(image, "YAWNING ALERT!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Webcam Images", image)  # display window
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the capture and close windows
video.release()
cv2.destroyAllWindows()
