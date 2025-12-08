"""
LLM Vision OCR适配器
使用大模型的视觉能力进行OCR
"""

import io
import base64
import json
import re
from typing import Optional
from dataclasses import dataclass
from PIL import Image

from .base import OCRAdapter, TextRegion, Position, BoundingBox


@dataclass
class LLMConfig:
    """LLM配置"""
    provider: str = "openai"  # openai, anthropic
    model: str = "gpt-4o"  # gpt-4o, claude-3-5-sonnet
    api_key: str = ""
    base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.1


class LLMVisionAdapter(OCRAdapter):
    """LLM Vision OCR适配器"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None

    def _get_client(self):
        """获取API客户端"""
        if self._client:
            return self._client

        if self.config.provider == "openai":
            from openai import OpenAI

            self._client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url
            )
        elif self.config.provider == "anthropic":
            from anthropic import Anthropic

            self._client = Anthropic(
                api_key=self.config.api_key
            )
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

        return self._client

    def _image_to_base64(self, image: Image.Image) -> str:
        """将图片转为base64"""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

    def recognize(self, image: Image.Image) -> list[TextRegion]:
        """识别图片中的所有文字"""
        client = self._get_client()
        img_base64 = self._image_to_base64(image)
        width, height = image.size

        prompt = f"""请识别这张图片中的所有文字。
图片尺寸: {width}x{height}像素

请以JSON格式返回识别结果，格式如下：
{{
  "regions": [
    {{
      "text": "识别到的文字",
      "bbox": {{"x": 左上角x, "y": 左上角y, "width": 宽度, "height": 高度}},
      "confidence": 0.95
    }}
  ]
}}

注意：
1. 坐标是相对于图片左上角的像素值
2. 尽量准确估计每个文字区域的边界框
3. confidence表示识别置信度，范围0-1
4. 只返回JSON，不要其他文字"""

        if self.config.provider == "openai":
            response = client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            result_text = response.choices[0].message.content

        elif self.config.provider == "anthropic":
            response = client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": img_base64
                                }
                            },
                            {"type": "text", "text": prompt}
                        ]
                    }
                ]
            )
            result_text = response.content[0].text

        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

        # 解析JSON结果
        return self._parse_result(result_text)

    def _parse_result(self, result_text: str) -> list[TextRegion]:
        """解析LLM返回的结果"""
        regions = []

        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                data = json.loads(json_match.group())

                for item in data.get("regions", []):
                    bbox_data = item.get("bbox", {})
                    regions.append(TextRegion(
                        text=item.get("text", ""),
                        bbox=BoundingBox(
                            x=int(bbox_data.get("x", 0)),
                            y=int(bbox_data.get("y", 0)),
                            width=int(bbox_data.get("width", 0)),
                            height=int(bbox_data.get("height", 0))
                        ),
                        confidence=float(item.get("confidence", 0.8))
                    ))

        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM OCR result: {e}")

        return regions

    def find_text(self, image: Image.Image, text: str) -> Optional[Position]:
        """查找指定文字的位置"""
        client = self._get_client()
        img_base64 = self._image_to_base64(image)
        width, height = image.size

        prompt = f"""在这张图片中找到文字 "{text}" 的位置。
图片尺寸: {width}x{height}像素

如果找到了，请返回该文字中心点的坐标，格式如下：
{{"found": true, "x": 中心点x坐标, "y": 中心点y坐标}}

如果没有找到，请返回：
{{"found": false}}

只返回JSON，不要其他文字。"""

        if self.config.provider == "openai":
            response = client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=256,
                temperature=self.config.temperature
            )
            result_text = response.choices[0].message.content

        elif self.config.provider == "anthropic":
            response = client.messages.create(
                model=self.config.model,
                max_tokens=256,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": img_base64
                                }
                            },
                            {"type": "text", "text": prompt}
                        ]
                    }
                ]
            )
            result_text = response.content[0].text

        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

        # 解析结果
        try:
            json_match = re.search(r'\{[\s\S]*?\}', result_text)
            if json_match:
                data = json.loads(json_match.group())
                if data.get("found"):
                    return Position(
                        x=int(data.get("x", 0)),
                        y=int(data.get("y", 0))
                    )
        except json.JSONDecodeError:
            pass

        return None
