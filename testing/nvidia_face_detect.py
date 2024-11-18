import dlib
import face_recognition
import os
import cv2
import numpy as np
import imutils
from imutils import face_utils
from EAR import eye_aspect_ratio
from MAR import mouth_aspect_ratio
from HeadPose import getHeadTiltAndCoords
from facedetection_mediapipe import FaceMeshDetector


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(
    '/home/dcs/Desktop/dcs_kivy_gui/testing/Driver-Drowsiness-Detection/dlib_shape_predictor/shape_predictor_68_face_landmarks.dat')


KNOWN_FACES_DIR =  "../registered_faces" # training data
TOLERANCE = 0.4
image_THICKNESS = 1 # rectangle thickness
FONT_THICKNESS = 2 # font thickness
MODEL = "cnn" # convolutional
video = cv2.VideoCapture(0) # use webcan as input (source of test images)
print("loading known faces")
known_faces = [] # store known faces here
known_names = [] # store name of them here
print(dlib.DLIB_USE_CUDA) # ture, if cuda is enabled.
### TRAIN THE CNN MODEL ON KNOWN FACES #############################
for name in os.listdir(KNOWN_FACES_DIR):
    for filename in os.listdir(f"{KNOWN_FACES_DIR}/{name}"):
        image = face_recognition.load_image_file(f"{KNOWN_FACES_DIR}/{name}/{filename}")
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_faces.append(encodings[0])
            known_names.append(name)
####################################################################


# loop over the images from the video stream
# 2D image points. If you change the image, you need to change vector
image_points = np.array([
    (359, 391),     # Nose tip 34
    (399, 561),     # Chin 9
    (337, 297),     # Left eye left corner 37
    (513, 301),     # Right eye right corne 46
    (345, 465),     # Left Mouth corner 49
    (453, 469)      # Right mouth corner 55
], dtype="double")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

EYE_AR_THRESH = 0.25
MOUTH_AR_THRESH = 0.77
EYE_AR_CONSEC_imageS = 3
COUNTER = 0

# grab the indexes of the facial landmarks for the mouth
(mStart, mEnd) = (49, 68)

detector = FaceMeshDetector()


while True:
    ret, image = video.read() # obtain new image from webcan
    image_height = image.shape[0]
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    locations = face_recognition.face_locations(image,model=MODEL) # find face
    encodings = face_recognition.face_encodings(image, locations) # extrac face features
    for face_encoding, face_location in zip(encodings, locations):
        if len(face_encoding) == 0:
            continue  # Skip if encoding not found

        results = face_recognition.compare_faces(known_faces, face_encoding)
        face_dist = face_recognition.face_distance(known_faces, face_encoding)
        print(f"Face distances: {face_dist}")

        matchIndex = np.argmin(face_dist)
        match = "Unknown"
        if results[matchIndex] and face_dist[matchIndex]<=TOLERANCE: # if there is a known face
            match = known_names[matchIndex] # who that person is
            print(f"Match found: {match}")
            ### DRAW RECTANGLE AND #####################################
            top_left = (face_location[3], face_location[0])
            bottom_right = (face_location[1], face_location[2])
            color = [0, 255, 0] # green 
            cv2.rectangle(image, top_left, bottom_right, color, image_THICKNESS)
            top_left = (face_location[3], face_location[2])
            bottom_right = (face_location[1], face_location[2]+22)
            cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
            cv2.putText(image, match, (face_location[3]+10, face_location[2]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), FONT_THICKNESS)
        
        

        image_height, image_width, _ = image.shape
        results = detector.detect_face_landmarks(image)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                detector.draw_landmarks(image, face_landmarks)
                positions = detector.get_landmark_positions(face_landmarks, image_width, image_height)
                print("Left Eye:", positions["left_eye"])
                print("Right Eye:", positions["right_eye"])
                print("Nose:", positions["nose"])
                print("Mouth:", positions["mouth"])
                left_eye = np.array(positions["left_eye"], dtype="int")
                right_eye = np.array(positions["right_eye"], dtype="int")
                mouth = np.array(positions["mouth"], dtype="int")
                nose = np.array(positions["nose"], dtype="int")
                ears = np.array(positions["ears"], dtype="int")

                # EAR Calculation
                leftEAR = eye_aspect_ratio(left_eye)
                rightEAR = eye_aspect_ratio(right_eye)
                ear = (leftEAR + rightEAR) / 2.0

                # Draw eyes and check EAR threshold
                cv2.drawContours(image, [cv2.convexHull(left_eye)], -1, (0, 255, 0), 1)
                cv2.drawContours(image, [cv2.convexHull(right_eye)], -1, (0, 255, 0), 1)

                if ear < EYE_AR_THRESH:
                    COUNTER += 1
                    if COUNTER >= EYE_AR_CONSEC_imageS:
                        cv2.putText(image, "Eyes Closed!", (500, 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    COUNTER = 0

                # MAR Calculation
                mar = mouth_aspect_ratio(mouth)
                cv2.drawContours(image, [cv2.convexHull(mouth)], -1, (0, 255, 0), 1)
                cv2.putText(image, "MAR: {:.2f}".format(mar), (20, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                if mar > MOUTH_AR_THRESH:
                    cv2.putText(image, "Yawning!", (500, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Draw ears and nose
                for (x, y) in ears:
                    cv2.circle(image, (x, y), 3, (255, 0, 0), -1)
                for (x, y) in nose:
                    cv2.circle(image, (x, y), 3, (0, 255, 255), -1)


            #############################################################
   
    cv2.imshow("webcam images", image) # make window
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
# Release the capture and close windows
video.release()
cv2.destroyAllWindows()