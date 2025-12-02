# TeachPlay

## 目标

一套完整、可扩展、可学习、可编辑、可复用 的 “游戏自动化：教学录制 + 学习识别 + 智能决策” 系统方案


## 核心要求：逐条映射你的需求

 1. 教学录制模式(Record Mode): 启动教学 → 用户操作 → 提取点击区域的信息并记录 -> 生成路径配置文件(json)
 2. 自动执行(Play Mode): 执行配置文件(json) -> 智能node or 固定node -> AI根据OCR提取的信息决策 or 固定点击/滑动 执行
 3. 后台管理端：按项目管理录制文件列表、图片资源、执行步骤node编辑, 可将某个node设置为AI节点，AI根据用户设置的prompt + OCR提取的信息决策改选择哪个按钮，当执行到该节点时，需要从全窗口的多媒体流帧中提取有用的信息判断坐标位置

## 详细系统设计

1. 实时图像捕获（DXGI）, 补充MAC端方案？跨平台（Windows / macOS）
2. 录制步骤时：非文本点击区域点击时 → 自动记录周边元素(优先 OCR识别文本 -> 点击坐标自动截图)，录制同时记录点击、滚顶、拖动等事件及坐标
3. 录制步骤记录为json，上传到minio
4. 文件存储方案：docker 部署 minio 
5. OCR可以考虑PaddleOCR，或者轻量的大模型
6. 执行时，如果是只有截图，则用相似度匹配，如果有文字，则按文字去检索坐标。(录制时会记录坐标，可以用于加速检索区域)
7. 执行时，需要兼容异步操作，比如中途调用AI的接口作决策
8. UI界面/管理端：Tauri + React。功能包含：创建项目、项目列表->录制步骤列表(执行、编辑、删除)、开始录制、停止录制。编辑包含，编辑每个录制步骤的节点，比如某个点击，改为"mode": "ai_decision",由AI决策。并设置prompt
9. 开始录制：需要支持选择所有窗口，展示窗口的缩略图并选择，也可选择全屏模式


项目目录结构

TeachPlay/
  README.md  # 介绍+开发+使用说明
  apps/
    management-console/          # Tauri + React 管理界面
      src/
        main/                     # Tauri 主进程
        renderer/                 # React UI
        components/
        pages/
        services/
      public/
      tauri.conf.json
      package.json
    desktop-recorder/            # 桌面录制器壳，复用 recorder SDK
      src/
        main.rs                   # rust tauri/跨端入口，可选
        commands/                 # 调用 recorder-service
      package.json
  services/                      # python FastAPI
    management-api/              # 项目/节点/资源管理后端
      src/
        controllers/
        services/                # 读取
      tests/
    recorder-service/            # 录制流程管理，封装 DXGI/mac 截屏
      src/
        capture/
          windows_dxgi/
          macos_metal/
        input/
        storage/                  # 上传 MinIO
        pipelines/
        api/
      tests/
    executor-service/            # 播放/AI 决策执行
      src/
        playback/
        ai_nodes/
        ocr/
        matcher/
        async_flows/
        api/
      tests/
    workflow-coordinator/        # 可选，调度录制/执行任务
      src/
      tests/
  packages/
    recorder-sdk/                # 录制流程 SDK，供桌面端/服务端使用
      src/
        capture/
        annotation/
        serialization/
      tests/
    playback-sdk/
      src/
        actions/
        strategy/
        scheduler/
      tests/
    ai-decision-core/
      src/
        agents/
        prompts/
        state_encoder/
      tests/
    ocr-adapter/
      src/
        paddleocr/
        lightweight_llm/
        postprocess/
      tests/
    shared/                      # 公共工具
      config/
      logging/
      messaging/
      types/
  infra/
    docker/
      docker-compose.yml         # MinIO、API、服务编排
      management-api.Dockerfile
      recorder-service.Dockerfile
      executor-service.Dockerfile
    helm/
      Chart.yaml
      templates/
    minio/
      tenant-config.yaml
  data/
    sample_recordings/
    fixtures/
  tests/
    integration/
      management_flow.test.json
      playback_flow.test.json
  scripts/
    bootstrap.ps1
    bootstrap.sh
    dev/
      start_all.ps1
      start_all.sh


🎥 录制（Recorder）： 录制 → JSON → 回放 机制设计


通过鼠标/键盘 hook 捕获：

点击/移动/滚动事件

当前屏幕视频帧中所点击的区域

鼠标点位处 OCR 的文本

UI Automation 的元素信息（如按钮 name/text）

录制时间线（方便回放）

示例 JSON：

[
  {
    "type": "click",
    "timestamp": 1712300000.10,
    "text": "网络和 Internet",
    "position": { "x": 312, "y": 450 },
    "mode": "ui_tree",
    "context": {
      "ocr_candidates": ["网络", "Internet"],
      "ui_tree_text": "Button: 网络和 Internet",
      "window": {
        "process": "SystemSettings.exe",
        "title": "设置",
        "url": null
      }
    }
  },

  {
    "type": "click",
    "timestamp": 1712300001.15,
    "text": "登录",
    "position": { "x": 482, "y": 621 },
    "mode": "ocr_text",
    "context": {
      "ocr_candidates": ["登录", "登入"],
      "ui_tree_text": null,
      "window": {
        "process": "chrome.exe",
        "title": "登录 - Google 账号",
        "url": "https://accounts.google.com/signin"
      }
    }
  },

  {
    "type": "scroll",
    "timestamp": 1712300002.20,
    "delta": -300,
    "mode": "absolute_position",
    "context": {
      "ocr_candidates": [],
      "ui_tree_text": null,
      "window": {
        "process": "chrome.exe",
        "title": "ChatGPT",
        "url": "https://chatgpt.com/c/6912a7a3-656c-8327-a134-34a2386405ca"
      }
    }
  },

  {
    "type": "click",
    "timestamp": 1712300003.50,
    "text": "发送",
    "position": { "x": 720, "y": 780 },
    "mode": "ocr_text",
    "context": {
      "ocr_candidates": ["发送"],
      "ui_tree_text": null,
      "window": {
        "process": "WeChat.exe",
        "title": "微信",
        "url": null
      }
    }
  },

  {
    "type": "click",
    "timestamp": 1712300004.60,
    "text": "OK",
    "position": { "x": 532, "y": 412 },
    "mode": "image_template",
    "template_path": "templates/ok_button.png",
    "context": {
      "ocr_candidates": ["OK", "确认"],
      "ui_tree_text": null,
      "window": {
        "process": "my_app.exe",
        "title": "自定义应用",
        "url": null
      }
    }
  },

  {
    "type": "click",
    "timestamp": 1712300005.72,
    "text": "start_game",
    "position": { "x": 330, "y": 860 },
    "mode": "canvas_pattern",
    "canvas_pattern": {
      "pattern_name": "start_btn",
      "color_threshold": 20,
      "shape": "circle"
    },
    "context": {
      "ocr_candidates": [],
      "ui_tree_text": null,
      "window": {
        "process": "WeChat.exe",
        "title": "微信小程序 - 跳一跳",
        "url": null
      }
    }
  },

  {
    "type": "click",
    "timestamp": 1712300006.88,
    "text": "确定",
    "position": { "x": 510, "y": 630 },
    "mode": "ui_tree",
    "context": {
      "ocr_candidates": ["确定"],
      "ui_tree_text": "Button: 确定",
      "window": {
        "process": "explorer.exe",
        "title": "删除文件",
        "url": null
      }
    }
  },

  {
    "type": "click",
    "timestamp": 1712300008.01,
    "text": "下一步",
    "position": { "x": 510, "y": 690 },
    "mode": "ai_decision",
    "ai_hint": "引导用户点击最明显的蓝色按钮",
    "context": {
      "ocr_candidates": ["下一步"],
      "ui_tree_text": null,
      "window": {
        "process": "installer.exe",
        "title": "安装向导",
        "url": null
      }
    }
  }
]




▶️ 回放（Playback Executor）

每步动作并非直接使用录制中的坐标，而是：

文本 → 定位 → 点击

定位顺序优先级：

UI Accessibility Tree 精确匹配 text/name/role

OCR 在桌面 Stream 中查找

模板图匹配

最后才使用录制时的坐标 fallback

做到适配不同分辨率、网页布局变化。



AI 插件体系（可异步）

AI Agent 接口（示例）：

class Agent:
    def next_action(self, state) -> dict:
        """
        state = {
            "stream_frame": ...,
            "ui_tree": ...,
            "history": ...
        }
        return {
            "action": "click",
            "target": "确定"
        }
        """


实现可选择：

LLM（OpenAI / DeepSeek / local Llama）

规则决策（简单脚本）

自定义 plugin

执行流程：

Frame / UI Tree → StateEncoder → Agent.next_action → ActionResolver → PyAutoGUI 执行



TODO 列表（从 MVP 到高级）
✔️ 第一阶段：基础 MVP（能录、能放）

 初始化项目结构

 基础 PyAutoGUI 封装（click, move, drag, scroll）

 跨平台鼠标/键盘 Hook（pynput）

 事件录制保存 JSON

 基础 OCR 模块（PaddleOCR）

 简单回放执行器（直接走坐标）

✔️ 第二阶段：视觉增强

 桌面视频流捕获（Windows: DXGI，macOS: AVFoundation）

 OCR 文本定位器（文本 → 坐标）

 模板匹配定位器

 UIAutomation（Windows）解析树结构

 优先级定位策略（Tree → OCR → Template → Coord）

✔️ 第三阶段：AI 插件系统

 Agent 标准接口定义

 rule_agent（用于测试）

 llm_agent（调用大模型进行下一步决策）

 状态编码（Stream + Tree → text）

✔️ 第四阶段：增强录制系统

 录制时根据鼠标位置自动抓取 OCR 文本

 捕获 UIAutomation 信息

 自动生成可回放的 JSON（带容错）

✔️ 第五阶段：任务系统（流水线）

 支持多个 JSON 串联执行

 支持“等待元素出现”

 支持 “如果失败 → 重试 / 执行备选动作”

 断点恢复