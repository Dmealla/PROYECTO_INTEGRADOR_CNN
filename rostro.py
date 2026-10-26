import cv2
import mediapipe as mp

_FD = mp.solutions.face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)


def detectar_rostro(frame):
    h, w = frame.shape[:2]
    res = _FD.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    if not res.detections:
        return None
    mejor, area = None, 0
    for d in res.detections:
        b = d.location_data.relative_bounding_box
        x, y = int(b.xmin * w), int(b.ymin * h)
        bw, bh = int(b.width * w), int(b.height * h)
        if bw * bh > area:
            area, mejor = bw * bh, (x, y, bw, bh)
    x, y, bw, bh = mejor
    x, y = max(0, x), max(0, y)
    bw, bh = min(bw, w - x), min(bh, h - y)
    if bw <= 0 or bh <= 0:
        return None
    return (x, y, bw, bh)
