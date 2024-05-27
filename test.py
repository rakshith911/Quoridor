import cv2
from modules.PoseEstimator import HandPoseEstimator
# from SpeechToText import SpeechToText
    
def main():
    # Initialize the hand pose estimator
    hand_pose_estimator = HandPoseEstimator()

    # Open the video capture
    cap = cv2.VideoCapture(0)

    # enable text to speech
    # speech_to_text = SpeechToText(device = 1)
    # speech_to_text.start_recognition()

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Get hand landmarks
        hand_landmarks = hand_pose_estimator.get_hand_landmarks(frame)

        # Get speech-to-text
        # text = speech_to_text.recognized_text
        # if text:
        #     cv2.putText(frame, text, (10, 30*2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Draw hand landmarks
        if hand_landmarks:
            for hand_label, landmarks in hand_landmarks:
                for point in landmarks:
                    x, y = int(point[0] * frame.shape[1]), int(point[1] * frame.shape[0])
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

                # Detect poses
                poses = hand_pose_estimator.detect_pose(hand_label, landmarks)

                # Display moves based on detected poses
                # move = mmap[len(poses)] if 1 <= len(poses) <= 5 else "No Move"
                move = " ".join(map(str, poses))
                    
                # Display move text on the frame
                cv2.putText(frame, move, (10, 30 + 30*0), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Display the frame
        cv2.imshow('Hand Pose Estimation and Speech Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    # speech_to_text.stop_recognition()

if __name__ == '__main__':
    main()