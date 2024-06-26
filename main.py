import cv2
from modules.PoseEstimator import HandPoseEstimator
from modules.GUI import QuoridorGame
import threading
from queue import Queue

# declare global queue
frame_queue = Queue()

def runPose():
    # Initialize the hand pose estimator
    hand_pose_estimator = HandPoseEstimator()

    # Open the video capture
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Get hand landmarks
        hand_landmarks = hand_pose_estimator.get_hand_landmarks(frame)

        # Draw hand landmarks
        if hand_landmarks:
            for hand_label, landmarks in hand_landmarks:
                for point in landmarks:
                    x, y = int(point[0] * frame.shape[1]), int(point[1] * frame.shape[0])
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

                # Detect poses
                poses = hand_pose_estimator.detect_pose(hand_label, landmarks)

                # add data to queue
                frame_queue.put(poses)

                # Display moves based on detected poses
                move = " ".join(map(str, poses))
                    
                # Display move text on the frame
                cv2.putText(frame, move, (10, 30 + 30*0), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Display the frame
        cv2.imshow('Hand Pose Estimation', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def runGUI():
    game = QuoridorGame()
    game.frame_queue = frame_queue
    game.run()

def main():
    p1 = threading.Thread(target = runPose)
    p2 = threading.Thread(target = runGUI)
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
    

if __name__ == '__main__':
    main()