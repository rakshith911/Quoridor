import cv2
import mediapipe as mp
import numpy as np

class HandPoseEstimator:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False,
                                         max_num_hands=2,
                                         min_detection_confidence=0.5,
                                         min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

    def get_hand_landmarks(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        hand_landmarks = []


        if results.multi_hand_landmarks:
            for hand_landmark, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                landmarks = []
                for lm in hand_landmark.landmark:
                    landmarks.append((lm.x, lm.y, lm.z))
                
                hand_label = handedness.classification[0].label
                hand_landmarks.append([hand_label, landmarks])
        return hand_landmarks

    def draw_hand_landmarks(self, frame, hand_landmarks):
        for hand_landmark in hand_landmarks:
            self.mp_drawing.draw_landmarks(frame, hand_landmark, self.mp_hands.HAND_CONNECTIONS)
        return frame

    def detect_pose(self, hand_label, landmarks):
        poses = [0, 0, 0, 0, 0]

        # thumb
        c1 = hand_label == "Left" and landmarks[4][0] > landmarks[3][0]
        c2 = hand_label == "Right" and landmarks[4][0] < landmarks[3][0]
        if c1 or c2:
            poses[0] = 1

        # Index Finger
        if landmarks[8][1] < landmarks[6][1]:
            poses[1] = 1

        # Middle Finger
        if landmarks[12][1] < landmarks[10][1]:
            poses[2] = 1

        # Ring Finger
        if landmarks[16][1] < landmarks[14][1]:
            poses[3] = 1

        # Little Finger
        if landmarks[20][1] < landmarks[18][1]:
            poses[4] = 1

        return poses
