# from scipy.spatial import distance as dist

# def mouth_aspect_ratio(mouth):
#     # compute the euclidean distances between the two sets of
#     # vertical mouth landmarks (x, y)-coordinates
#     A = dist.euclidean(mouth[2], mouth[10])  # 51, 59
#     B = dist.euclidean(mouth[4], mouth[8])  # 53, 57

#     # compute the euclidean distance between the horizontal
#     # mouth landmark (x, y)-coordinates
#     C = dist.euclidean(mouth[0], mouth[6])  # 49, 55

#     # compute the mouth aspect ratio
#     mar = (A + B) / (2.0 * C)

#     # return the mouth aspect ratio
#     return mar


from scipy.spatial import distance as dist

def mouth_aspect_ratio(mouth_landmarks):
    """
    Compute the Mouth Aspect Ratio (MAR) using Mediapipe landmarks.

    Args:
        mouth_landmarks (list of tuples): List of (x, y, z) tuples representing mouth landmarks.

    Returns:
        float: The mouth aspect ratio (MAR).
    """
    # Validate that we have enough landmarks (Mediapipe provides 20 for the mouth region).
    if len(mouth_landmarks) < 11:  # Ensure the required points exist
        print(f"Error: Insufficient landmarks for mouth. Detected points: {len(mouth_landmarks)}")
        return 0.0  # Default value

    # Extract key points using Mediapipe's landmark indices (x, y only)
    # Mediapipe index mapping for mouth:
    # Indices: 0 - 9 correspond to the outer ring, 10 - 19 correspond to the inner ring.
    point_2 = mouth_landmarks[2][:2]  # 3rd outer landmark
    point_10 = mouth_landmarks[10][:2]  # 11th outer landmark
    point_4 = mouth_landmarks[4][:2]  # 5th outer landmark
    point_8 = mouth_landmarks[8][:2]  # 9th outer landmark
    point_0 = mouth_landmarks[0][:2]  # 1st outer landmark
    point_6 = mouth_landmarks[6][:2]  # 7th outer landmark

    # Compute the Euclidean distances for MAR calculation
    A = dist.euclidean(point_2, point_10)
    B = dist.euclidean(point_4, point_8)
    C = dist.euclidean(point_0, point_6)

    # Compute the mouth aspect ratio
    mar = (A + B) / (2.0 * C)

    # Return the mouth aspect ratio
    return mar
