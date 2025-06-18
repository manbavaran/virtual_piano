# 파일: virtual_piano/piano_position_plugin.py
import cv2
import mediapipe as mp

class PianoPositionPlugin:
    def __init__(self):
        self.should_crop = False
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

            # 기준선
            cv2.line(frame, (0, y1), (w, y1), (0, 255, 0), 2)
            cv2.line(frame, (0, y2), (w, y2), (0, 255, 0), 2)

            # 안내문구
            middle_y = int((y1 + y2) / 2)
            if not self.should_crop:
                cv2.putText(frame,
                    "Put your camera above for a top-down view",
                    (25, y1 - 40),     # 초록 영역 위쪽에 위치 (위치 조정 가능)
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,                    # 조금 작게
                    (0, 120, 255),          # 주황색 (BGR, 시인성 높음)
                    2,
                    cv2.LINE_AA
                )
                
                # 메인 안내문구 (진녹색, 굵게, 영역 중앙 위)
                cv2.putText(frame, "Put your hand here for piano keys",
                            (20, middle_y - 20), cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (20, 110, 30), 3, cv2.LINE_AA)
                
                # OK 사인 안내문구 (검정, 작게, 영역 중앙)
                cv2.putText(frame, "Show the OK gesture in this zone to start",
                            (60, middle_y + 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.55,       # 더 작게
                            (0, 120, 255),  # 검정
                            2,
                            cv2.LINE_AA
                            )

            # 제스처 인식
            results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            crop_rect = None
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    if self.is_ok_sign(hand_landmarks):
                        # ✋ 손의 중심 좌표 계산
                        cx = int(hand_landmarks.landmark[9].x * w)
                        cy = int(hand_landmarks.landmark[9].y * h)
                        
                        if y1 <= cy <= y2:  # 💡 기준선 안쪽에 있을 때만 유효
                            print("✅ OK 사인 인식 + 기준선 통과")
                            self.should_crop = True
                            print("✅ OK 제스처 인식됨! 크롭 활성화됨.")
                            break
                        else:
                            print("OK 사인 인식됨. 하지만 기준선 밖입니다.")

            # 크롭 여부
            if self.should_crop:
                crop_rect = (0, y1, w, y2 - y1)
                cropped = frame[y1:y2, :]
                return cropped, crop_rect
            else:
                print("크롭 실패")

            return frame, None

        except Exception as e:
            print(f"❌ on_frame 처리 중 예외 발생: {e}")
            return frame, None
