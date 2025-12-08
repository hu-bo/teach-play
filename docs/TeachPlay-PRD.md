# TeachPlay - 产品需求文档 (PRD)

> 版本: v1.0.0
> 最后更新: 2025-12-08

---

## 1. 项目概述

### 1.1 项目名称
**TeachPlay** - 游戏自动化教学录制与智能回放系统

### 1.2 项目目标
构建一套 **完整、可扩展、可学习、可编辑、可复用** 的游戏自动化系统，实现：
- 教学录制 (Record Mode)
- 学习识别 (OCR + 图像匹配)
- 智能决策 (AI Decision)

### 1.3 核心价值
| 特性 | 说明 |
|------|------|
| 完整性 | 覆盖录制、回放、管理全流程 |
| 可扩展 | 模块化设计，支持多种 OCR/AI 引擎 |
| 可学习 | AI 节点支持自定义 Prompt 决策 |
| 可编辑 | 录制后可视化编辑每个节点 |
| 可复用 | 项目级管理，步骤可跨项目复用 |

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     TeachPlay 系统架构                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    客户端 (Tauri + React)                │    │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────────────┐   │    │
│  │  │ 项目管理   │  │ 录制控制   │  │ 步骤编辑器        │   │    │
│  │  └───────────┘  └───────────┘  └───────────────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   Services (FastAPI)                     │    │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────┐    │    │
│  │  │ 项目服务    │  │ 录制服务    │  │ 回放服务        │    │    │
│  │  └────────────┘  └────────────┘  └────────────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                        SDK 层                            │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │    │
│  │  │recorder-sdk │  │playback-sdk │  │ ocr-adapter    │  │    │
│  │  └─────────────┘  └─────────────┘  └────────────────┘  │    │
│  │                    ┌─────────────────┐                  │    │
│  │                    │ai-decision-core │                  │    │
│  │                    └─────────────────┘                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                     存储层 (MinIO)                       │    │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────┐    │    │
│  │  │ 项目配置    │  │ 步骤JSON   │  │ 截图资源        │    │    │
│  │  └────────────┘  └────────────┘  └────────────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 模块划分

| 模块 | 技术栈 | 职责 |
|------|--------|------|
| **客户端** | Tauri + React | UI 管理界面 |
| **services** | Python FastAPI | 后端 API 服务 |
| **recorder-sdk** | Python | 屏幕捕获、事件监听、步骤记录 |
| **playback-sdk** | Python | 步骤回放、事件模拟 |
| **ocr-adapter** | Python | OCR 统一接口适配层 |
| **ai-decision-core** | Python | AI 决策引擎 |
| **deploy** | Docker Compose | 容器化部署 |
| **storage** | MinIO | 对象存储 |

---

## 3. 核心功能需求

### 3.1 教学录制模式 (Record Mode)

#### 3.1.1 录制流程
```
启动录制 → 选择目标窗口 → 用户操作 → 实时捕获 → 生成步骤JSON → 上传MinIO
```

#### 3.1.2 功能点

| ID | 功能 | 优先级 | 说明 |
|----|------|--------|------|
| R-001 | 窗口选择 | P0 | 列出所有窗口，显示缩略图，支持选择 |
| R-002 | 全屏模式 | P1 | 支持录制全屏操作 |
| R-003 | 鼠标事件捕获 | P0 | 捕获点击、双击、右键事件及坐标 |
| R-004 | 滚动事件捕获 | P0 | 捕获滚轮滚动方向和距离 |
| R-005 | 拖拽事件捕获 | P1 | 捕获拖拽起止坐标 |
| R-006 | 键盘事件捕获 | P0 | 捕获按键输入 |
| R-007 | 区域截图 | P0 | 点击时自动截取点击区域图片 |
| R-008 | OCR 识别 | P0 | 对截图区域进行文字识别 |
| R-009 | 文件路径记录 | P1 | 文件上传操作记录完整路径 |
| R-010 | 实时预览 | P2 | 录制时显示捕获的步骤列表 |

#### 3.1.3 屏幕捕获方案

| 平台 | 方案 | 说明 |
|------|------|------|
| Windows | DXGI (Desktop Duplication API) | 高性能、低延迟 |
| macOS | CGWindowListCreateImage / ScreenCaptureKit | 系统原生 API |

#### 3.1.4 事件记录策略

**点击事件处理流程：**
```
点击事件 → 获取点击坐标 → 截取区域图片(100x100px) → OCR识别
    │
    ├── 有文字 → 记录: { type: "click", text: "xxx", position: {x, y}, screenshot: "url" }
    │
    └── 无文字 → 记录: { type: "click", position: {x, y}, screenshot: "url" }
```

---

### 3.2 自动执行模式 (Play Mode)

#### 3.2.1 回放流程
```
加载步骤JSON → 遍历节点 → 判断节点类型 → 执行/决策 → 下一节点
```

#### 3.2.2 节点类型

| 类型 | mode 值 | 说明 |
|------|---------|------|
| 固定节点 | `fixed` | 按录制坐标直接执行 |
| 智能节点 | `smart` | 通过 OCR/图像匹配定位后执行 |
| AI决策节点 | `ai_decision` | 调用 AI 接口决策后执行 |
| 等待节点 | `wait` | 等待指定条件/时间 |

#### 3.2.3 功能点

| ID | 功能 | 优先级 | 说明 |
|----|------|--------|------|
| P-001 | 固定坐标执行 | P0 | 直接点击录制时的坐标 |
| P-002 | 文字定位执行 | P0 | OCR 识别文字位置后点击 |
| P-003 | 图像匹配执行 | P0 | 模板匹配定位后点击 |
| P-004 | AI 决策执行 | P0 | 调用 AI 分析屏幕并决策 |
| P-005 | 异步操作支持 | P1 | 支持等待 AI 响应 |
| P-006 | 执行日志 | P1 | 记录每步执行结果 |
| P-007 | 错误重试 | P2 | 失败时自动重试 |
| P-008 | 断点续播 | P2 | 从指定步骤开始执行 |

#### 3.2.4 定位策略优先级
```
1. 文字定位 (OCR) → 精确度高，抗偏移
2. 图像匹配 (Template Matching) → 无文字时使用
3. 固定坐标 → 兜底方案
```

#### 3.2.5 区域加速检索
```
录制坐标 (x, y) → 扩展搜索区域 (x±200, y±200) → OCR/匹配 → 精确定位
```

---

### 3.3 后台管理端

#### 3.3.1 功能模块

```
┌─────────────────────────────────────────────────────────────┐
│                       管理端功能结构                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   项目管理   │    │   录制管理   │    │   资源管理   │     │
│  ├─────────────┤    ├─────────────┤    ├─────────────┤     │
│  │ • 创建项目   │    │ • 开始录制   │    │ • 图片列表   │     │
│  │ • 项目列表   │    │ • 停止录制   │    │ • 上传图片   │     │
│  │ • 删除项目   │    │ • 录制列表   │    │ • 删除资源   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    步骤编辑器                         │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ • 查看步骤列表                                        │   │
│  │ • 编辑节点属性 (type, mode, position, text, prompt)  │   │
│  │ • 设置 AI 决策节点                                    │   │
│  │ • 添加等待节点                                        │   │
│  │ • 调整步骤顺序                                        │   │
│  │ • 删除步骤                                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    执行控制                           │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │ • 选择录制执行                                        │   │
│  │ • 执行进度显示                                        │   │
│  │ • 暂停/继续/停止                                      │   │
│  │ • 执行日志查看                                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 3.3.2 功能点

| ID | 功能 | 优先级 | 说明 |
|----|------|--------|------|
| M-001 | 创建项目 | P0 | 新建项目，设置名称、描述 |
| M-002 | 项目列表 | P0 | 展示所有项目 |
| M-003 | 录制列表 | P0 | 展示项目下的录制文件 |
| M-004 | 开始录制 | P0 | 启动录制，选择窗口 |
| M-005 | 停止录制 | P0 | 结束录制，保存步骤 |
| M-006 | 步骤编辑 | P0 | 可视化编辑步骤属性 |
| M-007 | 设置AI节点 | P0 | 将节点 mode 改为 ai_decision |
| M-008 | 配置Prompt | P0 | 为 AI 节点设置决策 Prompt |
| M-009 | 添加等待节点 | P1 | 手动插入等待节点 |
| M-010 | 执行录制 | P0 | 运行选中的录制 |
| M-011 | 执行日志 | P1 | 查看执行过程日志 |
| M-012 | 窗口缩略图 | P1 | 录制时显示窗口预览 |

---

## 4. 数据结构设计

### 4.1 项目配置 (project.json)

```json
{
  "id": "proj_001",
  "name": "微信小游戏自动化",
  "description": "向僵尸开炮游戏自动化脚本",
  "created_at": "2025-12-08T10:00:00Z",
  "updated_at": "2025-12-08T10:00:00Z",
  "recordings": [
    "rec_001",
    "rec_002"
  ]
}
```

### 4.2 录制步骤 (recording.json)

```json
{
  "id": "rec_001",
  "project_id": "proj_001",
  "name": "完整游戏流程",
  "created_at": "2025-12-08T10:00:00Z",
  "target_window": {
    "title": "微信",
    "process_name": "WeChat.exe",
    "rect": { "x": 0, "y": 0, "width": 1920, "height": 1080 }
  },
  "steps": [
    {
      "id": "step_001",
      "index": 0,
      "type": "click",
      "mode": "smart",
      "position": { "x": 500, "y": 300 },
      "text": "向僵尸开炮",
      "screenshot": "minio://screenshots/step_001.png",
      "timestamp": 1733648000000,
      "description": "点击搜索结果"
    },
    {
      "id": "step_002",
      "index": 1,
      "type": "click",
      "mode": "smart",
      "position": { "x": 600, "y": 400 },
      "text": "开始游戏",
      "screenshot": "minio://screenshots/step_002.png",
      "timestamp": 1733648005000,
      "description": "点击开始游戏按钮"
    },
    {
      "id": "step_003",
      "index": 2,
      "type": "click",
      "mode": "ai_decision",
      "position": { "x": 400, "y": 500 },
      "screenshot": "minio://screenshots/step_003.png",
      "timestamp": 1733648010000,
      "description": "选择卡片",
      "ai_config": {
        "prompt": "屏幕上有三张卡片，请根据卡片上的文字描述，选择攻击力最高的卡片，返回该卡片的位置编号(1/2/3)",
        "options": [
          { "label": "1", "region": { "x": 200, "y": 400, "width": 150, "height": 200 } },
          { "label": "2", "region": { "x": 400, "y": 400, "width": 150, "height": 200 } },
          { "label": "3", "region": { "x": 600, "y": 400, "width": 150, "height": 200 } }
        ]
      }
    },
    {
      "id": "step_004",
      "index": 3,
      "type": "wait",
      "mode": "condition",
      "condition": {
        "type": "image_match",
        "template": "minio://templates/game_over.png",
        "threshold": 0.8
      },
      "timeout": 300000,
      "description": "等待游戏结束画面"
    }
  ]
}
```

### 4.3 步骤类型定义

#### 4.3.1 click (点击)
```json
{
  "type": "click",
  "mode": "fixed | smart | ai_decision",
  "position": { "x": 100, "y": 200 },
  "text": "按钮文字(可选)",
  "screenshot": "截图URL(可选)",
  "button": "left | right | middle"
}
```

#### 4.3.2 scroll (滚动)
```json
{
  "type": "scroll",
  "mode": "fixed",
  "position": { "x": 100, "y": 200 },
  "direction": "up | down | left | right",
  "amount": 300
}
```

#### 4.3.3 drag (拖拽)
```json
{
  "type": "drag",
  "mode": "fixed | smart",
  "from": { "x": 100, "y": 200 },
  "to": { "x": 300, "y": 400 }
}
```

#### 4.3.4 input (输入)
```json
{
  "type": "input",
  "mode": "fixed",
  "text": "要输入的文字",
  "position": { "x": 100, "y": 200 }
}
```

#### 4.3.5 key (按键)
```json
{
  "type": "key",
  "mode": "fixed",
  "key": "enter | tab | escape | ctrl+c | ..."
}
```

#### 4.3.6 wait (等待)
```json
{
  "type": "wait",
  "mode": "time | condition",
  "duration": 3000,
  "condition": {
    "type": "text_appear | text_disappear | image_match",
    "value": "匹配值",
    "region": { "x": 0, "y": 0, "width": 100, "height": 100 }
  },
  "timeout": 30000
}
```

#### 4.3.7 file_select (文件选择)
```json
{
  "type": "file_select",
  "mode": "fixed",
  "file_path": "/Users/xxx/Documents/test.pdf"
}
```

---

## 5. API 接口设计

### 5.1 项目管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/projects` | 获取项目列表 |
| POST | `/api/projects` | 创建项目 |
| GET | `/api/projects/{id}` | 获取项目详情 |
| PUT | `/api/projects/{id}` | 更新项目 |
| DELETE | `/api/projects/{id}` | 删除项目 |

### 5.2 录制管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/projects/{id}/recordings` | 获取录制列表 |
| POST | `/api/recordings` | 创建录制 |
| GET | `/api/recordings/{id}` | 获取录制详情 |
| PUT | `/api/recordings/{id}` | 更新录制 |
| DELETE | `/api/recordings/{id}` | 删除录制 |

### 5.3 录制控制

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/windows` | 获取窗口列表(含缩略图) |
| POST | `/api/record/start` | 开始录制 |
| POST | `/api/record/stop` | 停止录制 |
| GET | `/api/record/status` | 获取录制状态 |

### 5.4 回放控制

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/playback/start` | 开始执行 |
| POST | `/api/playback/pause` | 暂停执行 |
| POST | `/api/playback/resume` | 继续执行 |
| POST | `/api/playback/stop` | 停止执行 |
| GET | `/api/playback/status` | 获取执行状态 |
| GET | `/api/playback/logs` | 获取执行日志 |

### 5.5 步骤编辑

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/recordings/{id}/steps` | 获取步骤列表 |
| PUT | `/api/recordings/{id}/steps/{stepId}` | 更新步骤 |
| POST | `/api/recordings/{id}/steps` | 插入步骤 |
| DELETE | `/api/recordings/{id}/steps/{stepId}` | 删除步骤 |
| PUT | `/api/recordings/{id}/steps/reorder` | 调整步骤顺序 |

### 5.6 资源管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/upload` | 上传文件到 MinIO |
| GET | `/api/files/{path}` | 获取文件 |
| DELETE | `/api/files/{path}` | 删除文件 |

---

## 6. SDK 设计

### 6.1 recorder-sdk

**职责**: 屏幕捕获、事件监听、步骤记录

```python
# 核心类
class Recorder:
    def __init__(self, config: RecorderConfig):
        """初始化录制器"""

    def list_windows(self) -> List[WindowInfo]:
        """获取窗口列表"""

    def start(self, window_id: str) -> None:
        """开始录制"""

    def stop(self) -> Recording:
        """停止录制，返回录制结果"""

    def on_event(self, callback: Callable[[Event], None]) -> None:
        """注册事件回调"""

# 屏幕捕获
class ScreenCapture:
    def capture_window(self, window_id: str) -> Image:
        """捕获指定窗口"""

    def capture_region(self, x: int, y: int, width: int, height: int) -> Image:
        """捕获指定区域"""

# 事件监听
class EventListener:
    def start(self) -> None:
        """开始监听"""

    def stop(self) -> None:
        """停止监听"""
```

### 6.2 playback-sdk

**职责**: 步骤回放、事件模拟

```python
# 核心类
class Player:
    def __init__(self, config: PlayerConfig):
        """初始化播放器"""

    def load(self, recording: Recording) -> None:
        """加载录制"""

    def play(self) -> None:
        """开始执行"""

    def pause(self) -> None:
        """暂停执行"""

    def resume(self) -> None:
        """继续执行"""

    def stop(self) -> None:
        """停止执行"""

    def on_step(self, callback: Callable[[Step, StepResult], None]) -> None:
        """注册步骤回调"""

# 事件模拟
class EventSimulator:
    def click(self, x: int, y: int, button: str = "left") -> None:
        """模拟点击"""

    def scroll(self, x: int, y: int, amount: int, direction: str) -> None:
        """模拟滚动"""

    def drag(self, from_x: int, from_y: int, to_x: int, to_y: int) -> None:
        """模拟拖拽"""

    def type_text(self, text: str) -> None:
        """模拟输入"""

    def press_key(self, key: str) -> None:
        """模拟按键"""
```

### 6.3 ocr-adapter

**职责**: OCR 统一接口适配

```python
# 抽象接口
class OCRAdapter(ABC):
    @abstractmethod
    def recognize(self, image: Image) -> List[TextRegion]:
        """识别图片中的文字"""

    @abstractmethod
    def find_text(self, image: Image, text: str) -> Optional[Position]:
        """查找指定文字的位置"""

# PaddleOCR 实现
class PaddleOCRAdapter(OCRAdapter):
    def __init__(self, config: PaddleConfig):
        """初始化 PaddleOCR"""

# LLM Vision 实现 (备选)
class LLMVisionAdapter(OCRAdapter):
    def __init__(self, config: LLMConfig):
        """初始化 LLM Vision"""
```

### 6.4 ai-decision-core

**职责**: AI 决策引擎

```python
# 核心类
class AIDecisionEngine:
    def __init__(self, config: AIConfig):
        """初始化 AI 引擎"""

    async def decide(
        self,
        screenshot: Image,
        prompt: str,
        options: List[Option]
    ) -> Decision:
        """
        AI 决策

        Args:
            screenshot: 当前屏幕截图
            prompt: 用户配置的决策提示词
            options: 可选项列表

        Returns:
            Decision: 决策结果，包含选中的选项和置信度
        """

    async def analyze_screen(self, screenshot: Image, prompt: str) -> AnalysisResult:
        """
        分析屏幕内容

        Args:
            screenshot: 屏幕截图
            prompt: 分析提示词

        Returns:
            AnalysisResult: 分析结果
        """
```

---

## 7. 部署架构

### 7.1 Docker Compose 配置

```yaml
version: '3.8'

services:
  # FastAPI 后端服务
  api:
    build: ./services
    ports:
      - "8000:8000"
    environment:
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY}
      - AI_API_KEY=${AI_API_KEY}
    depends_on:
      - minio
    volumes:
      - ./sdk:/app/sdk

  # MinIO 对象存储
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_ACCESS_KEY}
      - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY}
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"

  # PaddleOCR 服务 (可选，也可内嵌到 api 中)
  ocr:
    build: ./sdk/ocr-adapter
    ports:
      - "8001:8001"

volumes:
  minio_data:
```

### 7.2 MinIO Bucket 结构

```
teachplay/
├── projects/
│   └── {project_id}/
│       └── project.json
├── recordings/
│   └── {recording_id}/
│       └── recording.json
├── screenshots/
│   └── {recording_id}/
│       ├── step_001.png
│       ├── step_002.png
│       └── ...
└── templates/
    └── {project_id}/
        └── *.png
```

---

## 8. 用例场景

### 8.1 案例1: Web 自动化

**场景**: 自动化 Chrome 浏览器操作

**录制步骤**:
1. 新建录制
2. 选择 Chrome 窗口
3. 输入网址 → 记录 `{ type: "input", text: "https://..." }`
4. 输入文字 → 记录 `{ type: "input", text: "搜索内容" }`
5. 滚动页面 → 记录 `{ type: "scroll", direction: "down", amount: 500 }`
6. 点击上传按钮 → 记录 `{ type: "click", text: "上传文件" }`
7. 选择文件 → 记录 `{ type: "file_select", file_path: "/path/to/file.pdf" }`
8. 停止录制

### 8.2 案例2: 微信小游戏自动化

**场景**: "向僵尸开炮" 游戏自动化

**录制步骤**:
```
步骤1: 打开微信
  → { type: "click", mode: "smart", text: "微信" }

步骤2: 搜索游戏
  → { type: "input", text: "向僵尸开炮" }

步骤3: 点击搜索结果
  → { type: "click", mode: "smart", text: "向僵尸开炮", screenshot: "step_003.png" }

步骤4: 点击开始游戏
  → { type: "click", mode: "smart", text: "开始游戏", screenshot: "step_004.png" }

步骤5: 选择卡片 (AI决策)
  → {
      type: "click",
      mode: "ai_decision",
      ai_config: {
        prompt: "分析三张卡片，选择攻击力最高的一张",
        options: [...]
      }
    }

步骤6: 等待游戏结束
  → {
      type: "wait",
      mode: "condition",
      condition: {
        type: "image_match",
        template: "game_over.png"
      }
    }
```

**后期编辑**:
- 将步骤5改为 AI 决策节点
- 设置 Prompt: "屏幕上有三张卡片，请分析每张卡片的文字描述，选择攻击力最高或效果最好的卡片"
- 添加步骤6等待节点，上传游戏结束画面作为匹配模板

---

## 9. 技术选型

### 9.1 客户端

| 技术 | 版本 | 说明 |
|------|------|------|
| Tauri | 2.x | 跨平台桌面应用框架 |
| React | 18.x | UI 框架 |
| TypeScript | 5.x | 类型安全 |
| TailwindCSS | 3.x | 样式框架 |
| React Query | 5.x | 数据请求管理 |

### 9.2 后端

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | 后端语言 |
| FastAPI | 0.100+ | Web 框架 |
| Pydantic | 2.x | 数据校验 |
| MinIO SDK | 7.x | 对象存储客户端 |
| PaddleOCR | 2.7+ | OCR 引擎 |

### 9.3 SDK 依赖

| 库 | 用途 | 平台 |
|------|------|------|
| pynput | 键鼠事件监听/模拟 | 跨平台 |
| mss | 屏幕截图 | 跨平台 |
| pywin32 | Windows API | Windows |
| pyobjc | macOS API | macOS |
| opencv-python | 图像处理/模板匹配 | 跨平台 |
| pillow | 图像处理 | 跨平台 |

### 9.4 AI 服务

| 服务 | 用途 | 说明 |
|------|------|------|
| OpenAI GPT-4V | 图像理解+决策 | 主选方案 |
| Claude 3.5 | 图像理解+决策 | 备选方案 |
| 本地 LLM | 离线决策 | 可选扩展 |

---

## 10. 开发路线图

### Phase 1: 基础框架 (MVP)
- [ ] 项目结构搭建
- [ ] MinIO 部署与集成
- [ ] FastAPI 基础服务
- [ ] Tauri + React 客户端框架
- [ ] 基础录制功能 (鼠标点击 + 截图)
- [ ] 基础回放功能 (固定坐标)

### Phase 2: 智能识别
- [ ] PaddleOCR 集成
- [ ] 文字定位回放
- [ ] 图像模板匹配
- [ ] 区域加速检索

### Phase 3: AI 决策
- [ ] AI Decision Core 实现
- [ ] AI 节点编辑功能
- [ ] Prompt 配置界面
- [ ] 决策日志记录

### Phase 4: 完善功能
- [ ] 完整事件类型支持 (滚动、拖拽、键盘)
- [ ] 等待节点
- [ ] 条件判断节点
- [ ] 执行日志可视化
- [ ] 错误重试机制

### Phase 5: 优化体验
- [ ] 窗口缩略图预览
- [ ] 实时录制预览
- [ ] 断点续播
- [ ] 多项目并行
- [ ] 性能优化

---

## 11. 目录结构

```
teach-play/
├── docs/                          # 文档目录
│   └── TeachPlay-PRD.md          # 本文档
├── client/                        # Tauri + React 客户端
│   ├── src/
│   │   ├── components/           # React 组件
│   │   ├── pages/                # 页面
│   │   ├── hooks/                # 自定义 Hooks
│   │   ├── services/             # API 服务
│   │   ├── stores/               # 状态管理
│   │   └── types/                # TypeScript 类型
│   ├── src-tauri/                # Tauri 后端
│   ├── package.json
│   └── tauri.conf.json
├── services/                      # FastAPI 后端服务
│   ├── app/
│   │   ├── api/                  # API 路由
│   │   ├── core/                 # 核心配置
│   │   ├── models/               # 数据模型
│   │   ├── services/             # 业务逻辑
│   │   └── main.py               # 入口文件
│   ├── requirements.txt
│   └── Dockerfile
├── sdk/                           # SDK 模块
│   ├── recorder-sdk/             # 录制 SDK
│   │   ├── recorder/
│   │   │   ├── __init__.py
│   │   │   ├── capture.py        # 屏幕捕获
│   │   │   ├── listener.py       # 事件监听
│   │   │   └── recorder.py       # 录制器
│   │   └── setup.py
│   ├── playback-sdk/             # 回放 SDK
│   │   ├── playback/
│   │   │   ├── __init__.py
│   │   │   ├── simulator.py      # 事件模拟
│   │   │   ├── locator.py        # 元素定位
│   │   │   └── player.py         # 播放器
│   │   └── setup.py
│   ├── ocr-adapter/              # OCR 适配器
│   │   ├── ocr_adapter/
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # 抽象接口
│   │   │   ├── paddle.py         # PaddleOCR
│   │   │   └── llm.py            # LLM Vision
│   │   └── setup.py
│   └── ai-decision-core/         # AI 决策核心
│       ├── ai_decision/
│       │   ├── __init__.py
│       │   ├── engine.py         # 决策引擎
│       │   └── prompts.py        # Prompt 模板
│       └── setup.py
├── deploy/                        # 部署配置
│   ├── docker-compose.yml
│   ├── .env.example
│   └── nginx.conf
└── README.md                        # 项目介绍、使用说明、部署说明
```

---

## 附录 A: 术语表

| 术语 | 说明 |
|------|------|
| Recording | 一次完整的录制记录 |
| Step | 录制中的单个操作步骤 |
| Node | 同 Step，步骤节点 |
| Mode | 步骤执行模式 (fixed/smart/ai_decision) |
| Fixed Mode | 固定坐标执行模式 |
| Smart Mode | 智能定位执行模式 |
| AI Decision Mode | AI 决策执行模式 |
| Template Matching | 图像模板匹配 |
| OCR | 光学字符识别 |

---

## 附录 B: 参考资料

- [Tauri 官方文档](https://tauri.app/)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [MinIO 官方文档](https://min.io/docs/minio/linux/index.html)
- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [pynput 文档](https://pynput.readthedocs.io/)
- [OpenCV Template Matching](https://docs.opencv.org/4.x/d4/dc6/tutorial_py_template_matching.html)
