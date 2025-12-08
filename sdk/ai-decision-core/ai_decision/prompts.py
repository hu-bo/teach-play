"""
AI决策Prompt模板
"""

DECISION_PROMPT_TEMPLATE = """你是一个游戏自动化助手，需要根据屏幕截图和用户的决策需求，选择最合适的选项。

## 用户需求
{user_prompt}

## 可选项
{options_description}

## 输出要求
请分析屏幕截图，理解当前游戏状态，然后根据用户需求选择最合适的选项。

请以JSON格式返回你的决策：
{{
    "selected": "选项标签",
    "confidence": 0.95,
    "reasoning": "选择理由"
}}

注意：
1. selected 必须是可选项中的一个标签
2. confidence 是你对这个决策的置信度，范围0-1
3. reasoning 简要说明你的决策理由
4. 只返回JSON，不要其他文字
"""

ANALYSIS_PROMPT_TEMPLATE = """你是一个游戏自动化助手，需要分析屏幕截图中的内容。

## 分析需求
{user_prompt}

## 输出要求
请详细分析屏幕截图，识别其中的重要元素、文字、按钮等。

请以JSON格式返回分析结果：
{{
    "description": "屏幕整体描述",
    "elements": [
        {{
            "type": "元素类型(button/text/image/etc)",
            "content": "元素内容或文字",
            "position": {{"x": 100, "y": 200, "width": 50, "height": 30}},
            "importance": "high/medium/low"
        }}
    ],
    "suggestions": ["建议的操作1", "建议的操作2"]
}}

注意：
1. 尽可能详细地描述屏幕内容
2. 识别所有可交互的元素
3. position 是元素的边界框，坐标相对于图片左上角
4. 只返回JSON，不要其他文字
"""

LOCATE_PROMPT_TEMPLATE = """你是一个游戏自动化助手，需要在屏幕截图中定位特定元素。

## 定位需求
{user_prompt}

## 图片尺寸
宽度: {width}px
高度: {height}px

## 输出要求
请在屏幕截图中找到目标元素的位置。

请以JSON格式返回定位结果：
{{
    "found": true/false,
    "position": {{"x": 中心点x, "y": 中心点y}},
    "confidence": 0.95,
    "description": "找到的元素描述"
}}

注意：
1. position 是元素中心点的坐标，单位是像素
2. 如果找不到目标元素，found 设为 false
3. confidence 是定位的置信度
4. 只返回JSON，不要其他文字
"""


def build_decision_prompt(user_prompt: str, options: list) -> str:
    """构建决策Prompt"""
    options_desc = []
    for i, opt in enumerate(options, 1):
        desc = f"{i}. 标签: {opt.get('label', '')}"
        if opt.get('description'):
            desc += f" - {opt['description']}"
        region = opt.get('region', {})
        if region:
            desc += f" (位置: x={region.get('x', 0)}, y={region.get('y', 0)}, " \
                   f"宽={region.get('width', 0)}, 高={region.get('height', 0)})"
        options_desc.append(desc)

    return DECISION_PROMPT_TEMPLATE.format(
        user_prompt=user_prompt,
        options_description="\n".join(options_desc)
    )


def build_analysis_prompt(user_prompt: str) -> str:
    """构建分析Prompt"""
    return ANALYSIS_PROMPT_TEMPLATE.format(user_prompt=user_prompt)


def build_locate_prompt(user_prompt: str, width: int, height: int) -> str:
    """构建定位Prompt"""
    return LOCATE_PROMPT_TEMPLATE.format(
        user_prompt=user_prompt,
        width=width,
        height=height
    )
