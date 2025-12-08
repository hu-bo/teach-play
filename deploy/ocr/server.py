"""
PaddleOCR HTTP 服务
"""

import io
import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image
from paddleocr import PaddleOCR

app = FastAPI(title="TeachPlay OCR Service")

# 初始化OCR
ocr = PaddleOCR(use_gpu=False, lang="ch", show_log=False)


class OCRRequest(BaseModel):
    """OCR请求"""
    image: str  # base64编码的图片


class TextRegion(BaseModel):
    """文字区域"""
    text: str
    bbox: dict
    confidence: float


class OCRResponse(BaseModel):
    """OCR响应"""
    regions: list[TextRegion]


@app.post("/ocr", response_model=OCRResponse)
async def recognize(request: OCRRequest):
    """识别图片中的文字"""
    try:
        # 解码图片
        image_data = base64.b64decode(request.image)
        image = Image.open(io.BytesIO(image_data))

        # 转换为numpy数组
        import numpy as np
        img_array = np.array(image)

        # OCR识别
        result = ocr.ocr(img_array, cls=False)

        regions = []
        if result and result[0]:
            for line in result[0]:
                if len(line) >= 2:
                    bbox_points = line[0]
                    text_info = line[1]

                    if len(text_info) >= 2:
                        x_coords = [p[0] for p in bbox_points]
                        y_coords = [p[1] for p in bbox_points]

                        regions.append(TextRegion(
                            text=text_info[0],
                            bbox={
                                "x": int(min(x_coords)),
                                "y": int(min(y_coords)),
                                "width": int(max(x_coords) - min(x_coords)),
                                "height": int(max(y_coords) - min(y_coords)),
                            },
                            confidence=float(text_info[1])
                        ))

        return OCRResponse(regions=regions)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
