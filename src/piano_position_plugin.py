# 파일: virtual_piano/piano_position_plugin.py
import cv2
import mediapipe as mp
from piano_keys_ui import draw_piano_ui
class PianoPositionPlugin:
    def __init__(self):
        self.should_crop = False
        self.piano_area = None  # (x, y, w, h)
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    @staticmethod
    def is_ok_sign(hand_landmarks):
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]

        dx = thumb_tip.x - index_tip.x
        dy = thumb_tip.y - index_tip.y
        distance = (dx**2 + dy**2) ** 0.5

        return distance < 0.05  # OK 판단 임계값
    
    
    def on_frame(self, frame):
        try:
            h, w = frame.shape[:2]
            y1 = int(h * 0.45)
            y2 = int(h * 0.78)

            # 기준선 (0.45, 0.78 위치)
            cv2.line(frame, (0, y1), (w, y1), (0, 255, 0), 2)
            cv2.line(frame, (0, y2), (w, y2), (0, 255, 0), 2)

            # 안내문구 (크롭 전, 기준선 안쪽)
            middle_y = int((y1 + y2) / 2)
            if not self.should_crop:
                # 위쪽 안내
                cv2.putText(frame,
                    "Put your camera above for a top-down view",
                    (25, y1 - 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 120, 255),  # Orange
                    2, cv2.LINE_AA
                )
                # 메인 안내
                cv2.putText(frame, "Put your hand here for piano keys",
                            (20, middle_y - 20), cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (20, 110, 30), 3, cv2.LINE_AA)
                # OK 안내
                cv2.putText(frame, "Show the OK gesture in this zone to start",
                            (60, middle_y + 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.55,
                            (0, 120, 255),
                            2, cv2.LINE_AA
                            )

            # 제스처 인식
            results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            crop_rect = None
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    if self.is_ok_sign(hand_landmarks):
                        cx = int(hand_landmarks.landmark[9].x * w)
                        cy = int(hand_landmarks.landmark[9].y * h)
                        if y1 <= cy <= y2:
                            print("✅ OK 사인 인식 + 기준선 통과")
                            self.should_crop = True
                            break
                        else:
                            print("OK 사인 인식됨. 하지만 기준선 밖입니다.")

            # 크롭 및 피아노 UI
            if self.should_crop:
                crop_rect = (0, y1, w, y2 - y1)
                
                pressed_keys = []
                n_keys = 10  # 혹은 원하는 건반 수
                # 손가락 tip index (MediaPipe 기준: 8-검지, 12-중지, 16-약지, 20-소지)
                finger_indices = [4, 8, 12, 16, 20]
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        for idx in finger_indices:
                            fx = int(hand_landmarks.landmark[idx].x * w)
                            # fy는 피아노 영역 내 판별용
                            fy = int(hand_landmarks.landmark[idx].y * h)
                            # 피아노 영역 내에 있는 손가락만
                            if y1 <= fy <= y2:
                                # key index 추출 함수 (예: key_idx = finger_x_to_key_index(fx, 0, w, n_keys))
                                key_idx = int((fx - 0) / w * n_keys)
                                if 0 <= key_idx < n_keys and key_idx not in pressed_keys:
                                    pressed_keys.append(key_idx)
                                    
                # 피아노 UI 그리기 (pressed_keys 적용)
                frame = draw_piano_ui(frame,
                                    0, y1,
                                    w, y2 - y1,
                                    n_keys=n_keys, pressed_keys=pressed_keys,
                                    glow_color=(0, 255, 255), glow_alpha=0.4
                                    )
                cropped = frame[y1:y2, :]
                return cropped, crop_rect
            else:
                print("크롭 실패")

            return frame, None


        except Exception as e:
            print(f"❌ on_frame 처리 중 예외 발생: {e}")
            return frame, None
