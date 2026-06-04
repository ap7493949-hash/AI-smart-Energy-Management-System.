import cv2
import requests
import time
from collections import deque

# CONFIG
ROOMS = ['Room_39', 'Room_38', 'Room_37']
SERVER_PORT = 5000
PHONE_IP = "192.168.1.100:8080"
MOTION_THRESHOLD = 3000

class MotionDetector:
    def __init__(self):
        print("📱 Trying phone camera...")
        try:
            self.cap = cv2.VideoCapture(f"http://{PHONE_IP}/video")
            ret, test = self.cap.read()
            if ret:
                print("✅ Phone camera connected!")
            else:
                print("⚠️ Using laptop camera")
                self.cap = cv2.VideoCapture(0)
        except:
            print("⚠️ Using laptop camera")
            self.cap = cv2.VideoCapture(0)
        
        self.prev_frame = None
        self.occupancy_history = deque(maxlen=10)
        self.current_room = ROOMS[0]
        self.room_index = 0
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        print("✅ Motion Detector Ready!")
        print("Press 'q' to quit | 's' to switch room\n")
    
    def detect_motion(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.prev_frame is None:
            self.prev_frame = gray
            return False
        
        frame_delta = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        motion_pixels = cv2.countNonZero(thresh)
        
        self.prev_frame = gray
        return motion_pixels > MOTION_THRESHOLD
    
    def detect_people(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
        return len(faces), faces
    
    def send_data(self, occupancy, motion):
        try:
            url = f"http://localhost:{SERVER_PORT}/api/update/{self.current_room}"
            requests.post(url, json={'occupancy': occupancy, 'motion': motion}, timeout=1)
        except:
            pass
    
    def run(self):
        last_update = 0
        print("🎥 Camera detection started!\n")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Camera error!")
                    break
                
                frame = cv2.resize(frame, (640, 480))
                has_motion = self.detect_motion(frame)
                people_count, faces = self.detect_people(frame)
                
                if people_count > 0:
                    occupancy = people_count
                elif has_motion:
                    occupancy = max(self.occupancy_history) if self.occupancy_history else 1
                else:
                    occupancy = 0
                
                self.occupancy_history.append(occupancy)
                avg_occupancy = int(sum(self.occupancy_history) / len(self.occupancy_history))
                
                current_time = time.time()
                if current_time - last_update > 1:
                    self.send_data(avg_occupancy, has_motion)
                    print(f"✅ {self.current_room}: People={people_count} | Motion={has_motion}")
                    last_update = current_time
                
                cv2.putText(frame, f"Room: {self.current_room}", (10, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(frame, f"People: {people_count}", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Motion: {has_motion}", (10, 140),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if has_motion else (0, 0, 255), 2)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                cv2.putText(frame, "Press 's' next | 'q' quit", (10, 450),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                
                cv2.imshow('Motion Detection', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n👋 Closing...")
                    break
                elif key == ord('s'):
                    self.room_index = (self.room_index + 1) % len(ROOMS)
                    self.current_room = ROOMS[self.room_index]
                    print(f"\n✅ Switched to {self.current_room}\n")
        
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted!")
        
        finally:
            print("🔒 Cleaning up...")
            self.cap.release()
            cv2.destroyAllWindows()
            print("✅ Closed!")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎥 MOTION DETECTION")
    print("="*60 + "\n")
    detector = MotionDetector()
    detector.run()