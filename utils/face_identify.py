import threading
import dlib
import face_recognition
import os
import cv2
import numpy as np


class facedetection():

    def __init__(self):
        self.isfaces_loaded="no" #no,notfound,yes
        self.KNOWN_FACES_DIR = "registered_faces"  # training data
        self.TOLERANCE = 0.7
        self.FRAME_THICKNESS = 3  # rectangle thickness
        self.FONT_THICKNESS = 2  # font thickness
        self.MODEL = "cnn"  # convolutional
        self.known_faces = []  # store known faces here
        self.known_names = []  # store names here
        self.matchfound = ""
        self.isyawning = False
        self.isSleepy = False

        # Threshold values for drowsiness
        self.EYE_AR_THRESHOLD = 0.25
        self.MOUTH_AR_THRESHOLD = 0.75
        self.DROWSINESS_FRAMES = 20
        self.COUNTER = 0

        print(dlib.DLIB_USE_CUDA)  # True if CUDA is enabled

        # Load dlib's face detector and facial landmarks predictor
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("assets/shape_predictor_68_face_landmarks.dat")  # download model from dlib
        threading.Thread(target=self.load_registered_faces,daemon=True).start()
    
    def load_registered_faces(self):
        ### TRAIN THE CNN MODEL ON KNOWN FACES #############################
        for name in os.listdir(self.KNOWN_FACES_DIR):
            for filename in os.listdir(f"{self.KNOWN_FACES_DIR}/{name}"):
                image = face_recognition.load_image_file(f"{self.KNOWN_FACES_DIR}/{name}/{filename}")
                encoding = face_recognition.face_encodings(image)[0]
                self.known_faces.append(encoding)
                self.known_names.append(name)
        if(len(self.known_faces)>0):
            self.isfaces_loaded="yes"
        else:
            self.isfaces_loaded="notfound"
        
    def eye_aspect_ratio(self,eye_points):
        # Calculate distances between vertical eye landmarks
        A = np.linalg.norm(eye_points[1] - eye_points[5])
        B = np.linalg.norm(eye_points[2] - eye_points[4])
        # Calculate distance between horizontal eye landmarks
        C = np.linalg.norm(eye_points[0] - eye_points[3])
        # Compute eye aspect ratio
        ear = (A + B) / (2.0 * C)
        return ear

    def mouth_aspect_ratio(self,mouth_points):
        # Calculate distances between vertical mouth landmarks
        A = np.linalg.norm(mouth_points[2] - mouth_points[10])  # 51, 59
        B = np.linalg.norm(mouth_points[4] - mouth_points[8])   # 53, 57
        # Calculate distance between horizontal mouth landmarks
        C = np.linalg.norm(mouth_points[0] - mouth_points[6])   # 49, 55
        # Compute mouth aspect ratio
        mar = (A + B) / (2.0 * C)
        return mar

    def start_detect(self,image):

        if(self.isfaces_loaded=="no"):
            return [{
                "status":"waiting for loding the regestered faces"
                    }]
        elif(self.isfaces_loaded=="notfound"):
            return [{
                "status":"faces not yet "
                    }]
        
        locations = face_recognition.face_locations(image, model=self.MODEL)  # find face
        encodings = face_recognition.face_encodings(image, locations)  # extract face features

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)

        for face_encoding, face_location in zip(encodings, locations):
            results = face_recognition.compare_faces(self.known_faces, face_encoding, self.TOLERANCE)
            match = None
            if True in results:  # if there is a known face
                match = self.known_names[results.index(True)]  # who that person is
                self.matchfound = match
                print(f"Match found: {match}")

                ### DRAW RECTANGLE AROUND THE FACE
                top_left = (face_location[3], face_location[0])
                bottom_right = (face_location[1], face_location[2])
                color = [0, 255, 0]  # green
                cv2.rectangle(image, top_left, bottom_right, color, self.FRAME_THICKNESS)
                top_left = (face_location[3], face_location[2])
                bottom_right = (face_location[1], face_location[2] + 22)
                cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
                cv2.putText(image, match, (face_location[3] + 10, face_location[2] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), self.FONT_THICKNESS)

        # Detect drowsiness based on eyes and mouth
        for face in faces:
            landmarks = self.predictor(gray, face)

            # Extract the coordinates of the eye and mouth landmarks
            left_eye_points = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(36, 42)])
            right_eye_points = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(42, 48)])
            mouth_points = np.array([(landmarks.part(n).x, landmarks.part(n).y) for n in range(48, 60)])

            # Calculate aspect ratios
            left_eye_ear = self.eye_aspect_ratio(left_eye_points)
            right_eye_ear = self.eye_aspect_ratio(right_eye_points)
            mouth_mar = self.mouth_aspect_ratio(mouth_points)

            # Average eye aspect ratio
            ear = (left_eye_ear + right_eye_ear) / 2.0

            # Check for closed eyes (sleeping)
            if ear < self.EYE_AR_THRESHOLD:
                self.COUNTER += 1
                if self.COUNTER >= self.DROWSINESS_FRAMES:
                    self.isSleepy=True
                    cv2.putText(image, "DROWSINESS ALERT!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                self.isSleepy=False
                self.COUNTER = 0

            # Check for yawning
            if mouth_mar > self.MOUTH_AR_THRESHOLD:
                self.isyawning=True
                cv2.putText(image, "YAWNING ALERT!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                self.isyawning=False
        return [{
            "person":self.matchfound,
            "yawn":self.isyawning,
            "sleepy":self.isSleepy,
        },image]



# cap = cv2.VideoCapture(2)
# detect = facedetection()
# while True:
#     _,frame = cap.read()
#     data = detect.start_detect(frame)
#     print(data)
