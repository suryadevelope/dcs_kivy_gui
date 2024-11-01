import cv2
import face_recognition


known_face_encodings = []
known_face_names = []

known_face1 = face_recognition.load_image_file("./images/team-2.jpg")

known_face1_encoding = face_recognition.face_encodings(known_face1)[0]

known_face_encodings.append(known_face1_encoding)

known_face_names.append("face1")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    # Read the frame from the cam
    _, frame = cap.read()

    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        
    cv2.imshow("frame", frame)

    if cv2.waitKey(0):
            break

cap.release()
cv2.destroyAllWindows()