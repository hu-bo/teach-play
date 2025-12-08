"""
AI决策引擎
"""

import io
import base64
import json
import re
import asyncio
from typing import Optional
from PIL import Image

from .models import AIConfig, Decision, Option, AnalysisResult, Position, Region
from .prompts import build_decision_prompt, build_analysis_prompt, build_locate_prompt


class AIDecisionEngine:
    """AI决策引擎"""

    def __init__(self, config: AIConfig):
        self.config = config
        self._client = None

    def _get_client(self):
        """获取API客户端"""
        if self._client:
            return self._client

        if self.config.provider == "openai":
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=self.config.timeout
            )
        elif self.config.provider == "anthropic":
            from anthropic import AsyncAnthropic

            self._client = AsyncAnthropic(
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")

        return self._client

    def _image_to_base64(self, image: Image.Image) -> str:
        """将图片转为base64"""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()

    async def decide(
        self,
        screenshot: Image.Image,
        prompt: str,
        options: list[dict]
    ) -> Decision:
        """
        AI决策

        Args:
            screenshot: 当前屏幕截图
            prompt: 用户配置的决策提示词
            options: 可选项列表

        Returns:
            Decision: 决策结果
        """
        client = self._get_client()
        img_base64 = self._image_to_base64(screenshot)

        # 构建决策Prompt
        decision_prompt = build_decision_prompt(prompt, options)

        try:
            if self.config.provider == "openai":
                response = await client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": decision_prompt},
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
                response = await client.messages.create(
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
                                {"type": "text", "text": decision_prompt}
                            ]
                        }
                    ]
                )
                result_text = response.content[0].text

            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")

            # 解析决策结果
            return self._parse_decision(result_text, options)

        except Exception as e:
            return Decision(
                confidence=0.0,
                reasoning=f"AI decision error: {str(e)}",
                raw_response=""
            )

    def _parse_decision(self, result_text: str, options: list[dict]) -> Decision:
        """解析决策结果"""
        try:
            # 尝试提取JSON
            json_match = re.search(r'\{[\s\S]*?\}', result_text)
            if json_match:
                data = json.loads(json_match.group())

                selected = data.get("selected", "")
                confidence = float(data.get("confidence", 0.0))
                reasoning = data.get("reasoning", "")

                # 查找选中选项的位置
                position = None
                for opt in options:
                    if opt.get("label") == selected:
                        region = opt.get("region", {})
                        if region:
                            # 计算中心点
                            position = Position(
                                x=region.get("x", 0) + region.get("width", 0) // 2,
                                y=region.get("y", 0) + region.get("height", 0) // 2
                            )
                        break

                return Decision(
                    selected_option=selected,
                    position=position,
                    confidence=confidence,
                    reasoning=reasoning,
                    raw_response=result_text
                )

        except json.JSONDecodeError:
            pass

        return Decision(
            confidence=0.0,
            reasoning="Failed to parse AI response",
            raw_response=result_text
        )

    async def analyze_screen(
        self,
        screenshot: Image.Image,
        prompt: str
    ) -> AnalysisResult:
        """
        分析屏幕内容

        Args:
            screenshot: 屏幕截图
            prompt: 分析提示词

        Returns:
            AnalysisResult: 分析结果
        """
        client = self._get_client()
        img_base64 = self._image_to_base64(screenshot)

        analysis_prompt = build_analysis_prompt(prompt)

        try:
            if self.config.provider == "openai":
                response = await client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": analysis_prompt},
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
                response = await client.messages.create(
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
                                {"type": "text", "text": analysis_prompt}
                            ]
                        }
                    ]
                )
                result_text = response.content[0].text

            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")

            return self._parse_analysis(result_text)

        except Exception as e:
            return AnalysisResult(
                description=f"Analysis error: {str(e)}",
                raw_response=""
            )

    def _parse_analysis(self, result_text: str) -> AnalysisResult:
        """解析分析结果"""
        try:
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                data = json.loads(json_match.group())

                return AnalysisResult(
                    description=data.get("description", ""),
                    elements=data.get("elements", []),
                    suggestions=data.get("suggestions", []),
                    raw_response=result_text
                )

        except json.JSONDecodeError:
            pass

        return AnalysisResult(
            description="Failed to parse analysis result",
            raw_response=result_text
        )

    async def locate_element(
        self,
        screenshot: Image.Image,
        prompt: str
    ) -> Optional[Position]:
        """
        定位屏幕元素

        Args:
            screenshot: 屏幕截图
            prompt: 定位描述

        Returns:
            Position: 元素位置，未找到返回None
        """
        client = self._get_client()
        img_base64 = self._image_to_base64(screenshot)
        width, height = screenshot.size

        locate_prompt = build_locate_prompt(prompt, width, height)

        try:
            if self.config.provider == "openai":
                response = await client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": locate_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{img_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=512,
                    temperature=self.config.temperature
                )
                result_text = response.choices[0].message.content

            elif self.config.provider == "anthropic":
                response = await client.messages.create(
                    model=self.config.model,
                    max_tokens=512,
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
                                {"type": "text", "text": locate_prompt}
                            ]
                        }
                    ]
                )
                result_text = response.content[0].text

            else:
                raise ValueError(f"Unsupported provider: {self.config.provider}")

            # 解析定位结果
            json_match = re.search(r'\{[\s\S]*?\}', result_text)
            if json_match:
                data = json.loads(json_match.group())
                if data.get("found"):
                    pos = data.get("position", {})
                    return Position(
                        x=int(pos.get("x", 0)),
                        y=int(pos.get("y", 0))
                    )

        except Exception as e:
            print(f"Locate element error: {e}")

        return None

    def decide_sync(
        self,
        screenshot: Image.Image,
        prompt: str,
        options: list[dict]
    ) -> Decision:
        """同步版本的决策方法"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.decide(screenshot, prompt, options))
        finally:
            loop.close()

    def analyze_screen_sync(
        self,
        screenshot: Image.Image,
        prompt: str
    ) -> AnalysisResult:
        """同步版本的分析方法"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.analyze_screen(screenshot, prompt))
        finally:
            loop.close()
