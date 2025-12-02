import cv2
import numpy as np
from PIL import Image
import pytesseract


def pil_to_cv(img):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def extract_button_candidates(pil_frame, min_area=500, approx_ratio=(1.0, 6.0)):
    """Return list of candidates: {bbox: (x,y,w,h), text: str, score: float}

    Uses simple contour detection on a grayscale thresholded image and OCR for text.
    """
    cv = pil_to_cv(pil_frame)
    gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thr = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # find contours
    contours, _ = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        if area < min_area:
            continue
        ratio = max(w/h, h/w)
        if ratio < approx_ratio[0] or ratio > approx_ratio[1]:
            continue
        # crop and OCR
        crop = pil_frame.crop((x, y, x + w, y + h))
        text = pytesseract.image_to_string(crop, lang='chi_sim+eng').strip()
        score = 0.0
        if text:
            score = 0.9
        candidates.append({'bbox': (x, y, w, h), 'text': text, 'score': score})
    # sort by score and area
    candidates.sort(key=lambda c: (c['score'], c['bbox'][2] * c['bbox'][3]), reverse=True)
    return candidates
