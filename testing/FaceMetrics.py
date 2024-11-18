import numpy as np
from scipy.spatial import distance as dist

class FaceMetrics:
    def __init__(self, face_landmarks, image_width, image_height):
        """
        Initialize the FaceMetrics object.

        Args:
            face_landmarks (list): Mediapipe face landmarks as normalized (x, y, z).
            image_width (int): Width of the image.
            image_height (int): Height of the image.
        """
        self.positions = self.get_landmark_positions(face_landmarks, image_width, image_height)
    
    def get_landmark_positions(self, face_landmarks, image_width, image_height):
        """
        Extract specific facial features from Mediapipe landmarks.

        Args:
            face_landmarks (list): Mediapipe face landmarks.
            image_width (int): Image width.
            image_height (int): Image height.

        Returns:
            dict: A dictionary with positions for left eye, right eye, mouth, nose, and ears.
        """
        def scale_landmark(landmark):
            return (int(landmark.x * image_width), int(landmark.y * image_height))

        positions = {
            "left_eye": [scale_landmark(face_landmarks[idx]) for idx in [33, 160, 158, 133, 153, 144]],  # Mediapipe indices
            "right_eye": [scale_landmark(face_landmarks[idx]) for idx in [362, 385, 387, 263, 373, 380]],
            "mouth": [scale_landmark(face_landmarks[idx]) for idx in [61, 291, 185, 40, 39, 37, 0, 267, 269, 270, 409]],
            "nose": scale_landmark(face_landmarks[1]),
            "ears": [scale_landmark(face_landmarks[idx]) for idx in [234, 454]]
        }
        return positions

    def eye_aspect_ratio(self, eye):
        """
        Calculate Eye Aspect Ratio (EAR) for detecting blinks.

        Args:
            eye (list): List of (x, y) tuples for the eye.

        Returns:
            float: Eye aspect ratio (EAR).
        """
        A = dist.euclidean(eye[1], eye[5])  # Vertical distance
        B = dist.euclidean(eye[2], eye[4])  # Vertical distance
        C = dist.euclidean(eye[0], eye[3])  # Horizontal distance
        ear = (A + B) / (2.0 * C)
        return ear

    def mouth_aspect_ratio(self):
        """
        Calculate Mouth Aspect Ratio (MAR).

        Returns:
            float: Mouth aspect ratio (MAR).
        """
        mouth = np.array(self.positions["mouth"])
        if len(mouth) < 11:
            return 0.0  # Insufficient landmarks

        # Calculate distances for MAR
        A = dist.euclidean(mouth[2], mouth[10])
        B = dist.euclidean(mouth[4], mouth[8])
        C = dist.euclidean(mouth[0], mouth[6])
        mar = (A + B) / (2.0 * C)
        return mar

    def head_direction(self):
        """
        Determine the horizontal direction of the head based on nose and ears.

        Returns:
            str: "Left", "Right", or "Center" indicating the head direction.
        """
        nose = self.positions["nose"]
        left_ear = self.positions["ears"][0]
        right_ear = self.positions["ears"][1]

        # Determine the horizontal position of the nose relative to the ears
        if nose[0] < left_ear[0]:
            return "Left"
        elif nose[0] > right_ear[0]:
            return "Right"
        else:
            return "Center"

    def analyze(self):
        left_ear = self.eye_aspect_ratio(self.positions["left_eye"])
        right_ear = self.eye_aspect_ratio(self.positions["right_eye"])
        common_ear = (left_ear + right_ear) / 2  # Calculate common EAR
        mar = self.mouth_aspect_ratio()
        direction = self.head_direction()
        return {
            "common_ear": common_ear,
            "mouth_aspect_ratio": mar,
            "head_direction": direction
        }