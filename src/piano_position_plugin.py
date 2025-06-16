import cv2
import mediapipe as mp

class PianoPositionPlugin:
    def __init__(self):
        self.hands = mp.solutions.hands.Hands()
        self.snap_position = (None, None)
        self.position_locked = False

    def get_snap_position(self, x, y, width, height):
        cols, rows = 3, 2
        cell_w = width // cols
        cell_h = height // rows
        snap_x = round(x / cell_w) * cell_w
        snap_y = round(y / cell_h) * cell_h
        return snap_x, snap_y

    def on_frame(self, frame):
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        print(f"📷 Frame size: {w}x{h}")

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        print(f"🤚 손 검출됨? → {bool(results.multi_hand_landmarks)}")

        if results.multi_hand_landmarks and not self.position_locked:
            hand = results.multi_hand_landmarks[0]
            cx = int(hand.landmark[9].x * w)
            cy = int(hand.landmark[9].y * h)
            self.snap_position = self.get_snap_position(cx, cy, w, h)
            print(f"📦 Snap 위치: {self.snap_position}")

            thumb = hand.landmark[4]
            index = hand.landmark[8]
            dist = ((thumb.x - index.x)**2 + (thumb.y - index.y)**2)**0.5
            if dist < 0.05:
                print("✅ 위치 확정됨!")
                self.position_locked = True

        if self.snap_position[0] is not None:
            color = (0, 255, 255) if not self.position_locked else (0, 255, 0)
            cv2.rectangle(
                frame,
                (self.snap_position[0] - 60, self.snap_position[1] - 30),
                (self.snap_position[0] + 60, self.snap_position[1] + 30),
                color, 2
            )

        return frame
