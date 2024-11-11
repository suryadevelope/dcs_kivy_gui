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
           
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        size = gray.shape

        rect = dlib.rectangle(face_location[3], face_location[0], face_location[1], face_location[2])
        
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        # extract the left and right eye coordinates, then use the
        # coordinates to compute the eye aspect ratio for both eyes
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        # average the eye aspect ratio together for both eyes
        ear = (leftEAR + rightEAR) / 2.0

        # compute the convex hull for the left and right eye, then
        # visualize each of the eyes
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(image, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(image, [rightEyeHull], -1, (0, 255, 0), 1)

        # check to see if the eye aspect ratio is below the blink
        # threshold, and if so, increment the blink image counter
        if ear < EYE_AR_THRESH:
            COUNTER += 1
            # if the eyes were closed for a sufficient number of times
            # then show the warning
            if COUNTER >= EYE_AR_CONSEC_imageS:
                cv2.putText(image, "Eyes Closed!", (500, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            # otherwise, the eye aspect ratio is not below the blink
            # threshold, so reset the counter and alarm
        else:
            COUNTER = 0

        mouth = shape[mStart:mEnd]

        mouthMAR = mouth_aspect_ratio(mouth)
        mar = mouthMAR
        # compute the convex hull for the mouth, then
        # visualize the mouth
        mouthHull = cv2.convexHull(mouth)

        cv2.drawContours(image, [mouthHull], -1, (0, 255, 0), 1)
        cv2.putText(image, "MAR: {:.2f}".format(mar), (20, 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Draw text if mouth is open
        if mar > MOUTH_AR_THRESH:
            cv2.putText(image, "Yawning!", (500, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


        # loop over the (x, y)-coordinates for the facial landmarks
        # and draw each of them
        for (i, (x, y)) in enumerate(shape):
            if i == 33:
                # something to our key landmarks
                # save to our new key point list
                # i.e. keypoints = [(i,(x,y))]
                image_points[0] = np.array([x, y], dtype='double')
                # write on image in Green
                cv2.circle(image, (x, y), 1, (0, 255, 0), -1)
                cv2.putText(image, str(i + 1), (x - 10, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
            elif i == 8:
                # something to our key landmarks
                # save to our new key point list
                # i.e. keypoints = [(i,(x,y))]
                image_points[1] = np.array([x, y], dtype='double')
                # write on image in Green
                cv2.circle(image, (x, y), 1, (0, 255, 0), -1)
                cv2.putText(image, str(i + 1), (x - 10, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
            elif i == 36:
                # something to our key landmarks
                # save to our new key point list
                # i.e. keypoints = [(i,(x,y))]
                image_points[2] = np.array([x, y], dtype='double')
                # write on image in Green
                cv2.circle(image, (x, y), 1, (0, 255, 0), -1)
                cv2.putText(image, str(i + 1), (x - 10, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
            elif i == 45:
                # something to our key landmarks
                # save to our new key point list
                # i.e. keypoints = [(i,(x,y))]
                image_points[3] = np.array([x, y], dtype='double')
                # write on image in Green
                cv2.circle(image, (x, y), 1, (0, 255, 0), -1)
                cv2.putText(image, str(i + 1), (x - 10, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
            elif i == 48:
                # something to our key landmarks
                # save to our new key point list
                # i.e. keypoints = [(i,(x,y))]
                image_points[4] = np.array([x, y], dtype='double')
                # write on image in Green
                cv2.circle(image, (x, y), 1, (0, 255, 0), -1)
                cv2.putText(image, str(i + 1), (x - 10, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
            elif i == 54:
                # something to our key landmarks
                # save to our new key point list
                # i.e. keypoints = [(i,(x,y))]
                image_points[5] = np.array([x, y], dtype='double')
                # write on image in Green
                cv2.circle(image, (x, y), 1, (0, 255, 0), -1)
                cv2.putText(image, str(i + 1), (x - 10, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
            else:
                # everything to all other landmarks
                # write on image in Red
                cv2.circle(image, (x, y), 1, (0, 0, 255), -1)
                cv2.putText(image, str(i + 1), (x - 10, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
            # Draw a line connecting to the next point
            if i < len(shape) - 1:
                next_point = shape[i + 1]
                cv2.line(image, (x, y), (next_point[0], next_point[1]), (255, 0, 0), 1)  # Blue line with thickness of 1

        # Optionally, connect the last point back to the first to form a closed shape
        if len(shape) > 1:
            cv2.line(image, (shape[-1][0], shape[-1][1]), (shape[0][0], shape[0][1]), (255, 0, 0), 1)

        #Draw the determinant image points onto the person's face
        for p in image_points:
            cv2.circle(image, (int(p[0]), int(p[1])), 3, (0, 0, 255), -1)

      
        (head_tilt_degree, start_point, end_point, 
            end_point_alt) = getHeadTiltAndCoords(size, image_points, image_height)

        cv2.line(image, start_point, end_point, (255, 0, 0), 2)
        cv2.line(image, start_point, end_point_alt, (0, 0, 255), 2)

        if head_tilt_degree:
            cv2.putText(image, 'Head Tilt Degree: ' + str(head_tilt_degree[0]), (170, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

            #############################################################
    cv2.imshow("webcam images", image) # make window
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
# Release the capture and close windows
video.release()
cv2.destroyAllWindows()