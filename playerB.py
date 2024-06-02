import cv2
from modules.PoseEstimator import HandPoseEstimator
from modules.GUI import QuoridorGame
import threading
from queue import Queue
import socket
import time

# declare global queue
frame_queue = Queue()
opponent_queue = Queue()

# declare player
PLAYER = "B"
HOST = "192.168.1.191"
PORT = 8080

def runPose(game : QuoridorGame):
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
                if game.turn == PLAYER:
                    curr_pos = game.players["B"]
                    sp1 = game.selected_player
                    frame_queue.put(poses)
                    time.sleep(1)

                    new_pos = game.players["B"]
                    sp2 = game.selected_player

                    if curr_pos != new_pos or (sp1 != sp2 and sp2 != None):
                        opponent_queue.put(poses)

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

def runGUI(game: QuoridorGame):
    game.run()

def runSocket():
    with socket.socket(socket.AF_INET , socket.SOCK_STREAM) as s:
        print(".... Player B online ....")

        def sender():
            while True:
                if not opponent_queue.empty():
                    poses = opponent_queue.get()
                    data = " ".join(map(str, poses))
                    print("\nDATA SENT\n", data)
                    s.sendall(bytes(data, encoding = "utf-8"))
                    time.sleep(1)
                    
        def receiver():
            while True:
                data = s.recv(1024)
                if data:
                    data = data.decode(encoding = "utf-8")
                    pos = list(map(int, data.split(" ")))
                    if len(pos) == 5:
                        frame_queue.put(pos)
                    time.sleep(1)

        # establish connection
        s.connect((HOST, PORT))
        print(f".... Established Connection with player A ....")

        t1 = threading.Thread(target = sender)
        t2 = threading.Thread(target = receiver)

        t1.start()
        t2.start()
        
        t1.join()
        t2.join()
            
        # while True:
        #     data = s.recv(1024)
            
        #     if data:
        #         data = data.decode(encoding="utf-8")
        #         pos = list(map(int, data.split(" ")))
        #         if len(pos) == 5:
        #             frame_queue.put(pos)
        #         time.sleep(1)

def main():
    game = QuoridorGame(you = PLAYER)
    game.frame_queue = frame_queue

    p1 = threading.Thread(target = runPose, args=(game, ))
    p2 = threading.Thread(target = runGUI, args=(game, ))
    p3 = threading.Thread(target = runSocket)
    
    p1.start()
    p2.start()
    p3.start()
    
    p1.join()
    p2.join()
    p3.join()

if __name__ == '__main__':
    main()