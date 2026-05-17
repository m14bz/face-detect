[ miniprogram/app.json 文件内容错误] miniprogram/app.json: ["usingComponents"]["van-button"]: "@vant/weapp/button/index", component not found in the path: C:/Users/26457/Desktop/摄像头人脸识别/miniprogram/@vant/weapp/button/index
C:/Users/26457/Desktop/摄像头人脸识别/miniprogram/@vant/weapp/button/index/index
C:/Users/26457/Desktop/摄像头人脸识别/miniprogram/miniprogram_npm/@vant/weapp/button/index
C:/Users/26457/Desktop/摄像头人脸识别/miniprogram/miniprogram_npm/@vant/weapp/button/index/index
C:/Users/26457/Desktop/摄像头人脸识别/miniprogram/miniprogram_npm/@vant/weapp/button/index
C:/Users/26457/Desktop/摄像头人脸识别/miniprogram/miniprogram_npm/@vant/weapp/button/index/index(env: Windows,mp,2.01.2510290; lib: 3.16.0)# 智慧门禁系统 - 项目说明文档

## 1. 项目概述

智慧门禁系统是一套基于人脸识别技术的智能门禁管理解决方案，包含后端服务、微信小程序前端和边缘设备端三部分。本项目实现了完整的人脸识别门禁管理功能，包括用户管理、人脸注册、开门记录、陌生人检测与审核、远程开门等核心功能。

---

## 2. 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端层                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  微信小程序   │  │   Web管理台   │  │  边缘设备端   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        通信层                                   │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │  HTTP REST   │  │  WebSocket   │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       后端服务层                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Flask API   │  │   业务逻辑    │  │   日志系统   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据层                                   │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │  SQLite数据库 │  │  本地文件系统 │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 后端服务 (backend/)

### 3.1 技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| Web框架 | Flask 2.3.0 | 轻量级，适合边缘设备部署 |
| 数据库 | SQLite 3 | 轻量级，无额外依赖 |
| 实时通信 | Flask-SocketIO 5.3.0 | WebSocket支持 |
| 数据验证 | Marshmallow 3.20.0 | 请求/响应数据序列化 |
| 日志 | Python logging | 标准日志模块 |
| 跨域 | Flask-CORS 4.0.0 | 处理跨域请求 |
| 认证 | PyJWT 2.8.0 | JWT Token认证 |

### 3.2 项目结构

```
backend/
├── app.py                      # 应用入口（Flask + SocketIO）
├── config.py                   # 配置文件（数据库、JWT、日志等）
├── requirements.txt            # Python依赖列表
├── smart_access.db             # SQLite数据库文件（运行后自动生成）
├── models/                     # 数据模型层
│   ├── __init__.py
│   ├── user.py                # 用户模型（CRUD操作）
│   ├── face.py                # 人脸特征模型（特征向量存储）
│   ├── stranger.py            # 陌生人记录模型
│   ├── log.py                 # 开门日志模型
│   └── device.py              # 设备信息模型
├── routes/                     # API路由层
│   ├── __init__.py
│   ├── users.py               # 用户管理接口
│   ├── faces.py               # 人脸特征接口
│   ├── logs.py                # 开门记录接口
│   ├── strangers.py           # 陌生人记录接口
│   ├── devices.py             # 设备管理接口
│   └── auth.py                # JWT认证接口
├── services/                   # 业务逻辑层
│   ├── __init__.py
│   ├── user_service.py        # 用户业务逻辑
│   ├── face_service.py        # 人脸业务逻辑
│   ├── log_service.py         # 日志业务逻辑
│   └── notify_service.py      # WebSocket通知服务
├── utils/                      # 工具函数
│   ├── __init__.py
│   ├── response.py            # 统一响应格式
│   └── validator.py           # Marshmallow数据验证
├── database/                   # 数据库操作
│   ├── __init__.py
│   ├── db.py                  # SQLite连接管理（线程安全）
│   └── init_db.py             # 数据库初始化（建表）
├── websocket/                  # WebSocket事件处理
│   ├── __init__.py
│   └── events.py              # 连接、开门、报警等事件
└── logs/                       # 日志输出目录
```

### 3.3 数据库设计

#### 用户信息表 (users)
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    permission VARCHAR(20) DEFAULT 'normal',  -- normal/admin/blacklist
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 人脸特征表 (faces)
```sql
CREATE TABLE faces (
    face_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    feature_vector BLOB NOT NULL,  -- 128维特征向量，序列化存储
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

#### 陌生人记录表 (strangers)
```sql
CREATE TABLE strangers (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image_path VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending/approved/rejected
    processed_at TIMESTAMP,
    processor_id INTEGER,
    FOREIGN KEY (processor_id) REFERENCES users(user_id)
);
```

#### 设备信息表 (devices)
```sql
CREATE TABLE devices (
    device_id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    status VARCHAR(20) DEFAULT 'online',  -- online/offline/maintenance
    ip_address VARCHAR(50),
    last_heartbeat TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 开门日志表 (access_logs)
```sql
CREATE TABLE access_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER,
    person_type VARCHAR(20),  -- known/stranger
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    device_id INTEGER,
    result VARCHAR(20),  -- success/failed/pending
    image_path VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES users(user_id),
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);
```

### 3.4 API接口文档

#### 认证接口
| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| POST | /api/auth/login | 登录 | {phone} | {token, user} |
| GET | /api/auth/verify | 验证Token | - | Token信息 |

#### 用户管理接口
| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | /api/users | 获取用户列表 | - | 用户数组 |
| GET | /api/users/<id> | 获取单个用户 | - | 用户对象 |
| POST | /api/users | 创建用户 | {name, phone, permission} | 新用户 |
| PUT | /api/users/<id> | 更新用户 | {name, phone, permission} | 更新后用户 |
| DELETE | /api/users/<id> | 删除用户 | - | 删除结果 |

#### 人脸特征接口
| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | /api/faces | 获取所有人脸记录 | - | 人脸数组 |
| GET | /api/faces/<user_id> | 获取用户人脸 | - | 人脸数组 |
| POST | /api/faces | 注册人脸 | {user_id, feature_vector} | 新记录 |
| DELETE | /api/faces/<face_id> | 删除人脸 | - | 删除结果 |

#### 开门记录接口
| 方法 | 路径 | 说明 | 请求参数 | 响应 |
|------|------|------|----------|------|
| GET | /api/logs | 获取开门记录 | ?page=&limit=&start_date=&end_date=&person_id= | 记录数组 |
| GET | /api/logs/<id> | 获取单条记录 | - | 记录对象 |

#### 陌生人记录接口
| 方法 | 路径 | 说明 | 请求体/参数 | 响应 |
|------|------|------|-------------|------|
| GET | /api/strangers | 获取陌生人列表 | ?page=&limit=&status= | 记录数组 |
| GET | /api/strangers/<id> | 获取单条记录 | - | 记录对象 |
| PUT | /api/strangers/<id> | 处理记录 | {status, processor_id} | 更新后记录 |

#### 设备管理接口
| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | /api/devices | 获取设备列表 | - | 设备数组 |
| GET | /api/devices/<id> | 获取设备详情 | - | 设备对象 |
| POST | /api/devices | 注册设备 | {device_name, location, ip_address} | 新设备 |
| PUT | /api/devices/<id> | 更新设备 | {device_name, location, status} | 更新后设备 |
| PUT | /api/devices/<id>/heartbeat | 心跳上报 | {status} | 更新结果 |

### 3.5 WebSocket事件

| 事件 | 方向 | 说明 | 数据格式 |
|------|------|------|----------|
| join_device | 客户端→服务端 | 设备加入房间 | {device_id} |
| join_admin | 客户端→服务端 | 管理端加入房间 | - |
| remote_open | 客户端→服务端 | 远程开门请求 | {device_id, user_id} |
| open_door | 服务端→设备 | 开门指令 | {device_id, user_id, user_name} |
| door_result | 设备→服务端 | 开门结果 | {device_id, success, image_path} |
| stranger_alert | 服务端→管理端 | 陌生人报警 | {record_id, device_id, image_path, ...} |
| access_log | 服务端→管理端 | 开门记录 | {log_id, person_name, result, ...} |
| stranger_detected | 设备→服务端 | 陌生人检测 | {device_id, image_path} |

### 3.6 启动方式

```bash
# 1. 进入后端目录
cd backend

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python app.py

# 服务启动后访问：http://localhost:5000
```

### 3.7 配置说明

配置文件 `config.py` 包含以下配置项：

- `SECRET_KEY`: Flask密钥
- `DATABASE`: 数据库文件名
- `JWT_SECRET_KEY`: JWT密钥
- `JWT_ACCESS_TOKEN_EXPIRES`: Token有效期（默认24小时）
- `LOG_CONFIG`: 日志配置（文件轮转、格式等）

---

## 4. 微信小程序前端 (miniprogram/)

### 4.1 技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 框架 | 微信小程序原生 | 官方框架，兼容性好 |
| UI组件 | Vant Weapp | 轻量、可靠 |
| 状态管理 | globalData | 小程序内置全局状态 |
| 网络请求 | wx.request | 封装HTTP请求 |
| WebSocket | wx.connectSocket | 实时通信 |
| 本地存储 | wx.setStorageSync | 缓存数据 |

### 4.2 项目结构

```
miniprogram/
├── app.js                      # 应用入口
├── app.json                    # 全局配置
├── app.wxss                    # 全局样式
├── config/
│   └── config.js               # 配置文件（API地址等）
├── utils/
│   ├── request.js              # HTTP请求封装
│   ├── websocket.js            # WebSocket封装
│   └── storage.js              # 本地存储封装
├── pages/
│   ├── index/                  # 首页
│   │   ├── index.js           # 首页逻辑
│   │   ├── index.json         # 页面配置
│   │   ├── index.wxml         # 页面模板
│   │   └── index.wxss         # 页面样式
│   ├── logs/                   # 开门记录
│   ├── strangers/              # 陌生人审核
│   ├── users/                  # 用户管理
│   └── settings/               # 设置
├── components/
│   ├── log-item/               # 日志条目组件
│   ├── stranger-card/          # 陌生人卡片组件
│   └── user-form/              # 用户表单组件
└── images/                     # 图片资源
```

### 4.3 页面功能

#### 首页 (pages/index/)
- 用户信息展示
- 设备列表展示（在线状态）
- 远程开门功能
- 最近开门记录

#### 开门记录 (pages/logs/)
- 分页加载记录
- 日期范围筛选
- 实时更新（WebSocket）
- 下拉刷新、上拉加载更多

#### 陌生人审核 (pages/strangers/)
- 标签切换（待审核/已授权/已拒绝）
- 陌生人图片预览
- 授权/拒绝操作
- 实时提醒（WebSocket）

#### 用户管理 (pages/users/)
- 用户列表展示
- 添加用户
- 编辑用户信息
- 删除用户
- 权限设置（普通用户/管理员/黑名单）

#### 设置 (pages/settings/)
- 手机号登录
- 退出登录
- 系统信息展示

### 4.4 工具函数

#### HTTP请求封装 (utils/request.js)
```javascript
// 自动携带Token
// 统一错误处理
// 401自动跳转登录
const request = {
  get(url, data),    // GET请求
  post(url, data),   // POST请求
  put(url, data),    // PUT请求
  delete(url, data)  // DELETE请求
};
```

#### WebSocket封装 (utils/websocket.js)
```javascript
// 自动重连
// 事件监听
const websocket = {
  connect(),     // 连接WebSocket
  send(event, data),  // 发送消息
  on(event, callback),  // 监听事件
  off(event),    // 取消监听
  close()        // 关闭连接
};
```

#### 本地存储封装 (utils/storage.js)
```javascript
// Token管理
// 用户信息管理
const storage = {
  setToken(token),
  getToken(),
  setUserInfo(userInfo),
  getUserInfo(),
  clearLoginInfo(),
  isLoggedIn()
};
```

### 4.5 使用说明

1. 使用微信开发者工具打开 `miniprogram` 目录
2. 在 `config/config.js` 中配置后端API地址
3. 安装 Vant Weapp 组件库：
   ```bash
   # 在 miniprogram 目录下
   npm init
   npm install @vant/weapp -S
   ```
4. 在微信开发者工具中构建 npm
5. 在 `images/` 目录中添加 tabBar 图标（home.png, log.png, check.png, user.png）

### 4.6 注意事项

- 开发环境使用 `http`，生产环境必须使用 `https`
- 开发环境使用 `ws`，生产环境必须使用 `wss`
- tabBar 图标需要自行准备（建议尺寸 81x81 像素）
- 需要先启动后端服务才能正常使用

---

## 5. 边缘设备端接口

### 5.1 上报数据接口

边缘设备需要调用以下接口上报数据：

```javascript
// 1. 上报识别结果
POST /api/access/recognize
{
    "device_id": 1,
    "user_id": 1,
    "confidence": 0.95,
    "image_path": "/captures/xxx.jpg"
}

// 2. 上报陌生人
POST /api/access/stranger
{
    "device_id": 1,
    "image_path": "/captures/stranger_xxx.jpg"
}

// 3. 心跳上报
PUT /api/devices/{id}/heartbeat
{
    "status": "online",
    "cpu_usage": 45.2,
    "gpu_usage": 60.5,
    "temperature": 42.0
}
```

### 5.2 接收指令接口

边缘设备通过WebSocket接收指令：

```javascript
// 连接WebSocket后加入设备房间
socket.emit('join_device', { device_id: 1 });

// 接收开门指令
socket.on('open_door', (data) => {
    if (data.device_id === MY_DEVICE_ID) {
        // 执行开门
        openDoor();
        // 上报结果
        socket.emit('door_result', {
            device_id: MY_DEVICE_ID,
            success: true
        });
    }
});
```

---

## 6. 安全设计

### 6.1 接口认证
- 使用JWT Token进行身份验证
- Token有效期：24小时
- 边缘设备使用设备密钥认证

### 6.2 数据安全
- 人脸特征向量加密存储
- 敏感信息（手机号等）脱敏显示
- 图片文件访问权限控制

### 6.3 通信安全
- 生产环境使用HTTPS
- WebSocket使用WSS
- 关键操作日志审计

---

## 7. 开发环境要求

### 后端
- Python 3.8+
- pip

### 前端
- 微信开发者工具
- Node.js 14+

---

## 8. 常见问题

### Q1: 后端启动失败？
A: 检查Python版本是否为3.8+，依赖是否安装完整：
```bash
pip install -r requirements.txt
```

### Q2: 小程序无法连接后端？
A: 检查：
1. 后端服务是否启动
2. `config/config.js` 中的API地址是否正确
3. 是否在微信开发者工具中勾选了"不校验合法域名"

### Q3: WebSocket连接失败？
A: 检查：
1. WebSocket地址是否正确
2. 生产环境是否使用了wss
3. 服务器是否支持WebSocket

### Q4: 如何部署到生产环境？
A: 
1. 后端：使用Gunicorn + Nginx部署
2. 前端：在微信公众平台提交审核
3. 配置HTTPS和WSS
4. 配置服务器域名白名单

---

## 9. 版本历史

### v1.0.0 (2026-05-09)
- 初始版本
- 实现核心功能：用户管理、人脸注册、开门记录、陌生人审核、远程开门
- 支持WebSocket实时通信
- 完整的API接口文档
