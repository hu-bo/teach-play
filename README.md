# TeachPlay

游戏自动化教学录制与智能回放系统

## 功能特性

- **教学录制 (Record Mode)**: 录制鼠标、键盘操作，自动截图并OCR识别
- **智能回放 (Play Mode)**: 支持固定坐标、OCR文字定位、图像模板匹配
- **AI决策**: 支持将步骤设置为AI决策节点，由AI分析屏幕内容做出选择
- **可视化编辑**: 可视化编辑录制步骤，调整执行模式和参数
- **跨平台**: 支持 Windows 和 macOS

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     TeachPlay 系统架构                           │
├─────────────────────────────────────────────────────────────────┤
│  客户端 (Tauri + React)                                          │
│  └── 项目管理 / 录制控制 / 步骤编辑器                              │
├─────────────────────────────────────────────────────────────────┤
│  Services (FastAPI)                                              │
│  └── 项目服务 / 录制服务 / 回放服务                                │
├─────────────────────────────────────────────────────────────────┤
│  SDK 层                                                          │
│  └── recorder-sdk / playback-sdk / ocr-adapter / ai-decision    │
├─────────────────────────────────────────────────────────────────┤
│  存储层 (MinIO)                                                   │
│  └── 项目配置 / 步骤JSON / 截图资源                                │
└─────────────────────────────────────────────────────────────────┘
```

## 目录结构

```
teach-play/
├── client/                 # Tauri + React 客户端
├── services/               # FastAPI 后端服务
├── sdk/                    # SDK 模块
│   ├── recorder-sdk/       # 录制 SDK
│   ├── playback-sdk/       # 回放 SDK
│   ├── ocr-adapter/        # OCR 适配器
│   └── ai-decision-core/   # AI 决策引擎
├── deploy/                 # 部署配置
└── docs/                   # 文档
```

## 快速开始

### 1. 启动后端服务

```bash
# 进入部署目录
cd deploy

# 复制环境变量配置
cp .env.example .env

# 编辑 .env 文件，配置 AI API Key 等

# 启动服务
docker-compose up -d
```

### 2. 启动客户端开发服务器

```bash
# 进入客户端目录
cd client

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 3. 访问应用

- 客户端: http://localhost:1420
- API 文档: http://localhost:8000/api/docs
- MinIO 控制台: http://localhost:9001

## SDK 使用

### recorder-sdk

```python
from recorder import Recorder, RecorderConfig

# 创建录制器
recorder = Recorder(RecorderConfig())

# 获取窗口列表
windows = recorder.list_windows()

# 开始录制
recorder.start(window_id="xxx", project_id="proj_001")

# 停止录制
recording = recorder.stop()

# 保存到文件
recorder.save_to_file(recording, "recording.json")
```

### playback-sdk

```python
from playback import Player, PlayerConfig

# 创建播放器
player = Player(PlayerConfig())

# 加载录制
player.load(recording_dict)

# 开始执行
player.play()

# 暂停/继续/停止
player.pause()
player.resume()
player.stop()
```

### ocr-adapter

```python
from ocr_adapter import PaddleOCRAdapter

# 创建OCR适配器
ocr = PaddleOCRAdapter()

# 识别图片
regions = ocr.recognize(image)

# 查找文字位置
position = ocr.find_text(image, "开始游戏")
```

### ai-decision-core

```python
from ai_decision import AIDecisionEngine, AIConfig

# 创建AI引擎
engine = AIDecisionEngine(AIConfig(
    provider="openai",
    model="gpt-4o",
    api_key="your_api_key"
))

# AI决策
decision = await engine.decide(
    screenshot=image,
    prompt="选择攻击力最高的卡片",
    options=[...]
)
```

## API 接口

### 项目管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/projects` | 获取项目列表 |
| POST | `/api/projects` | 创建项目 |
| GET | `/api/projects/{id}` | 获取项目详情 |
| PUT | `/api/projects/{id}` | 更新项目 |
| DELETE | `/api/projects/{id}` | 删除项目 |

### 录制管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/recordings` | 获取录制列表 |
| POST | `/api/recordings` | 创建录制 |
| GET | `/api/recordings/{id}` | 获取录制详情 |
| PUT | `/api/recordings/{id}` | 更新录制 |
| DELETE | `/api/recordings/{id}` | 删除录制 |

### 录制控制

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/record/windows` | 获取窗口列表 |
| POST | `/api/record/start` | 开始录制 |
| POST | `/api/record/stop` | 停止录制 |
| GET | `/api/record/status` | 获取录制状态 |

### 回放控制

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/playback/start` | 开始执行 |
| POST | `/api/playback/pause` | 暂停执行 |
| POST | `/api/playback/resume` | 继续执行 |
| POST | `/api/playback/stop` | 停止执行 |
| GET | `/api/playback/status` | 获取执行状态 |

## 环境要求

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose

## 开发指南

### 使用 Conda 创建 Python 3.11 环境

推荐先创建独立的 Conda 虚拟环境，并确保 Python 版本为 3.11，例如：

```bash
conda create -n teachplay python=3.11
conda activate teachplay
```


### 安装 SDK 开发依赖

```bash
# recorder-sdk
cd sdk/recorder-sdk
pip install -e ".[dev]" -i https://mirrors.aliyun.com/pypi/simple

# playback-sdk
cd sdk/playback-sdk
pip install -e ".[dev]" -i https://mirrors.aliyun.com/pypi/simple

# ocr-adapter
cd sdk/ocr-adapter
pip install -e ".[all,dev]" -i https://mirrors.aliyun.com/pypi/simple

# ai-decision-core
cd sdk/ai-decision-core
pip install -e ".[all,dev]" -i https://mirrors.aliyun.com/pypi/simple
```

### 运行后端服务（开发模式）

```bash
cd services
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
python -m uvicorn app.main:app --reload
```

### 构建客户端

```bash
cd client
npm run build
npm run tauri build
```

## License

MIT
