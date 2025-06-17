# 파일: piano_position_plugin.py
import cv2

class PianoPositionPlugin:
    def __init__(self):
        self.prev_hand_center = None

    def on_frame(self, frame):
        h, w = frame.shape[:2]

        # 기준선: 피아노 UI가 위치할 영역 시각화 (22% ~ 45%)
        y_top = int(h * 0.55)
        y_bottom = int(h * 0.78)
        cv2.line(frame, (0, y_top), (w, y_top), (0, 255, 0), 1)
        cv2.line(frame, (0, y_bottom), (w, y_bottom), (0, 255, 0), 1)

        # (임시) 손가락 검출 없이 네모 제스처가 있다고 가정하고 표시
        # 추후 hand tracking 기반 제스처 인식으로 확장
        box_width = 300
        box_height = 100
        cx, cy = w // 2, (y_top + y_bottom) // 2

        x1 = max(0, cx - box_width // 2)
        y1 = max(0, cy - box_height // 2)
        x2 = min(w, cx + box_width // 2)
        y2 = min(h, cy + box_height // 2)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)

        return frame
