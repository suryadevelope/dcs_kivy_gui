import dlib
import face_recognition
import os
import cv2
import numpy as np
KNOWN_FACES_DIR =  "../registered_faces" # training data
TOLERANCE = 0.4
FRAME_THICKNESS = 1 # rectangle thickness
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


while True:
    ret, image = video.read() # obtain new image from webcan
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
        if results[matchIndex] and face_dist<=TOLERANCE: # if there is a known face
            match = known_names[matchIndex] # who that person is
            print(f"Match found: {match}")
### DRAW RECTANGLE AND #####################################
            top_left = (face_location[3], face_location[0])
            bottom_right = (face_location[1], face_location[2])
            color = [0, 255, 0] # green 
            cv2.rectangle(image, top_left, bottom_right, color, FRAME_THICKNESS)
            top_left = (face_location[3], face_location[2])
            bottom_right = (face_location[1], face_location[2]+22)
            cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)
            cv2.putText(image, match, (face_location[3]+10, face_location[2]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), FONT_THICKNESS)
            #############################################################
    cv2.imshow("webcam images", image) # make window
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
# Release the capture and close windows
video.release()
cv2.destroyAllWindows()