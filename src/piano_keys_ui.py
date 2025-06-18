import cv2
import numpy as np

def finger_x_to_key_index(finger_x, x, w, n_keys):
    """
    finger_x: 손가락 x좌표 (이미지 좌표계)
    x, w: 피아노 UI 좌상단 x, 전체 폭
    n_keys: 건반 개수
    """
    if finger_x < x or finger_x >= x + w:
        return None
    rel_x = finger_x - x
    key_width = w / n_keys
    idx = int(rel_x // key_width)
    return idx if 0 <= idx < n_keys else None

def overlay_transparent(dst, overlay, x, y, alpha=0.5):
    """overlay 이미지를 dst 위에 투명하게 합성"""
    h, w = overlay.shape[:2]
    if overlay.shape[2] == 3:
        overlay = cv2.cvtColor(overlay, cv2.COLOR_BGR2BGRA)
    if dst.shape[2] == 3:
        dst = cv2.cvtColor(dst, cv2.COLOR_BGR2BGRA)

    roi = dst[y:y+h, x:x+w].copy()

    overlay_img = overlay[..., :3]
    mask = overlay[..., 3:] / 255.0 * alpha

    bg = roi[..., :3] * (1.0 - mask)
    fg = overlay_img * mask
    out = bg + fg

    dst[y:y+h, x:x+w, :3] = out
    dst[y:y+h, x:x+w, 3] = 255  # 완전 불투명
    return cv2.cvtColor(dst, cv2.COLOR_BGRA2BGR)

def draw_piano_ui(
    frame, x, y, w, h, n_keys=10, pressed_keys=None, glow_color=(0, 255, 255), glow_alpha=0.4
):
    """
    frame: OpenCV 이미지
    x, y, w, h: 피아노 위치, 크기
    n_keys: 건반 개수
    pressed_keys: 누른 건반 인덱스 리스트 (예: [2,4,6])
    glow_color: 불빛 색 (BGR)
    glow_alpha: 불빛 투명도 (0~1)
    """
    if pressed_keys is None:
        pressed_keys = []
    key_width = int(w / n_keys)
    key_height = h

    # 피아노 전체 그릴 버퍼 (불빛 오버레이용)
    piano_img = frame.copy()

    # 흰 건반 + 누른 건반 하이라이트
    for i in range(n_keys):
        x0 = x + i * key_width
        x1 = x + (i + 1) * key_width

        # 흰건반 & 외곽선
        cv2.rectangle(piano_img, (x0, y), (x1, y + key_height), (255, 255, 255), -1)
        cv2.rectangle(piano_img, (x0, y), (x1, y + key_height), (0, 0, 0), 2)
        note = chr(67 + (i % 7))
        cv2.putText(
            piano_img, note, (x0 + key_width // 2 - 8, y + key_height - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 30, 30), 2, cv2.LINE_AA
        )

        # 누른 건반이면 불빛 오버레이
        if i in pressed_keys:
            overlay = np.zeros((key_height, key_width, 4), dtype=np.uint8)
            overlay[..., :3] = glow_color  # BGR
            overlay[..., 3] = int(255 * glow_alpha)
            piano_img = overlay_transparent(piano_img, overlay, x0, y, alpha=1.0)  # alpha는 위에서 조정

    # 검은 건반
    black_key_indices = [1, 2, 4, 5, 6]  # 임시 예시
    black_key_width = int(key_width * 0.7)
    black_key_height = int(h * 0.55)
    for i in black_key_indices:
        bx = x + i * key_width - black_key_width // 2
        by = y
        cv2.rectangle(
            piano_img, (bx, by), (bx + black_key_width, by + black_key_height), (20, 20, 20), -1
        )

    # 완성된 피아노를 원본 frame에 붙임
    frame[y:y+h, x:x+w] = piano_img[y:y+h, x:x+w]
    return frame
