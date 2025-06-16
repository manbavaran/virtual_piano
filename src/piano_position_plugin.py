import cv2
import mediapipe as mp

class PianoPositionPlugin:
    def __init__(self):
        self.hands = mp.solutions.hands.Hands()
        self.position_locked = False
        self.snap_position = (None, None)

    def get_snap_position(self, x, y, frame_width, frame_height):
        cols, rows = 3, 2  # 예: 3x2 그리드
        cell_w, cell_h = frame_width // cols, frame_height // rows
        snap_x = round(x / cell_w) * cell_w
        snap_y = round(y / cell_h) * cell_h
        return snap_x, snap_y

    def on_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        h, w, _ = frame.shape

        if results.multi_hand_landmarks and not self.position_locked:
            hand = results.multi_hand_landmarks[0]
            cx = int(hand.landmark[9].x * w)
            cy = int(hand.landmark[9].y * h)

            snap_x, snap_y = self.get_snap_position(cx, cy, w, h)
            self.snap_position = (snap_x, snap_y)

            # 제스처 인식 예시: 주먹 쥐었을 때 (손가락 길이 기준 등으로 체크)
            # 여기선 예시로 간단히 특정 landmark 간 거리로 대체
            index_tip = hand.landmark[8]
            thumb_tip = hand.landmark[4]
            dist = ((index_tip.x - thumb_tip.x)**2 + (index_tip.y - thumb_tip.y)**2)**0.5

            if dist < 0.05:  # 주먹 제스처 감지
                self.position_locked = True

        # 미리보기 UI (스냅 위치 표시)
        if self.snap_position[0] is not None:
            color = (0, 255, 0) if self.position_locked else (0, 0, 255)
            cv2.rectangle(frame,
                        (self.snap_position[0]-50, self.snap_position[1]-20),
                        (self.snap_position[0]+50, self.snap_position[1]+20),
                        color, 2)

        return frame
