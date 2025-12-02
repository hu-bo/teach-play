import pytesseract
from PIL import Image

def image_to_text(img):
    if isinstance(img, Image.Image):
        return pytesseract.image_to_string(img, lang='chi_sim+eng')
    return ''
