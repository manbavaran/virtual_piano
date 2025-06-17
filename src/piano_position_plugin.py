# piano_position_plugin.py
import cv2

class PianoPositionPlugin:
    def __init__(self):
        self.crop_active = False
        self.crop_rect = None

    def on_frame(self, frame):
        h, w = frame.shape[:2]

        # 기준선 시각화
        lower = int(h * 0.78)
        upper = int(h * 0.45)
        cv2.line(frame, (0, lower), (w, lower), (0, 255, 0), 2)
        cv2.line(frame, (0, upper), (w, upper), (0, 255, 0), 2)

        # 제스처 인식 로직 (예: 쌍따봉) – 여기선 임시로 활성화 가정
        if not self.crop_active:
            self.crop_active = True
            self.crop_rect = (0, lower, w, upper - lower)

        # 크롭 여부에 따라 결과 리턴
        return frame, self.crop_rect if self.crop_active else None

plugin = PianoPositionPlugin()
def on_frame(frame):
    return plugin.on_frame(frame)
