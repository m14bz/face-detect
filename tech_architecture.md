# 智慧门禁系统 - 前后端技术架构文档

## 1. 系统架构概览

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

## 2. 后端技术架构

### 2.1 技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| Web框架 | Flask 2.0+ | 轻量级，适合边缘设备部署 |
| 数据库 | SQLite 3 | 轻量级，无额外依赖 |
| 实时通信 | Flask-SocketIO | WebSocket支持 |
| 数据验证 | Marshmallow | 请求/响应数据序列化 |
| 日志 | Python logging | 标准日志模块 |
| 跨域 | Flask-CORS | 处理跨域请求 |

### 2.2 项目结构

```
backend/
├── app.py                    # 应用入口
├── config.py                 # 配置文件
├── requirements.txt          # 依赖列表
├── models/                   # 数据模型
│   ├── __init__.py
│   ├── user.py              # 用户模型
│   ├── face.py              # 人脸特征模型
│   ├── stranger.py          # 陌生人记录模型
│   ├── log.py               # 开门日志模型
│   └── device.py            # 设备信息模型
├── routes/                   # API路由
│   ├── __init__.py
│   ├── users.py             # 用户管理接口
│   ├── faces.py             # 人脸特征接口
│   ├── logs.py              # 开门记录接口
│   ├── strangers.py         # 陌生人记录接口
│   ├── devices.py           # 设备管理接口
│   └── auth.py              # 认证接口
├── services/                 # 业务逻辑
│   ├── __init__.py
│   ├── user_service.py      # 用户业务逻辑
│   ├── face_service.py      # 人脸业务逻辑
│   ├── log_service.py       # 日志业务逻辑
│   └── notify_service.py    # 通知业务逻辑
├── utils/                    # 工具函数
│   ├── __init__.py
│   ├── response.py          # 统一响应格式
│   └── validator.py         # 数据验证
├── database/                 # 数据库操作
│   ├── __init__.py
│   ├── db.py                # 数据库连接
│   └── init_db.py           # 数据库初始化
├── websocket/                # WebSocket处理
│   ├── __init__.py
│   └── events.py            # WebSocket事件
└── logs/                     # 日志目录
```

### 2.3 数据库设计

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
    FOREIGN KEY (user_id) REFERENCES users(user_id)
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

#### 开门日志表 (access_logs)

```sql
CREATE TABLE access_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER,  -- user_id或NULL（陌生人）
    person_type VARCHAR(20),  -- known/stranger
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    device_id INTEGER,
    result VARCHAR(20),  -- success/failed/pending
    image_path VARCHAR(255),
    FOREIGN KEY (person_id) REFERENCES users(user_id),
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
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

### 2.4 RESTful API 设计

#### 2.4.1 用户管理 API

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | /api/users | 获取用户列表 | - | 用户数组 |
| GET | /api/users/<id> | 获取单个用户 | - | 用户对象 |
| POST | /api/users | 创建用户 | {name, phone, permission} | 新用户 |
| PUT | /api/users/<id> | 更新用户 | {name, phone, permission} | 更新后用户 |
| DELETE | /api/users/<id> | 删除用户 | - | 删除结果 |

**请求示例：**
```json
// POST /api/users
{
    "name": "张三",
    "phone": "13800138000",
    "permission": "normal"
}

// 响应
{
    "code": 200,
    "message": "success",
    "data": {
        "user_id": 1,
        "name": "张三",
        "phone": "13800138000",
        "permission": "normal",
        "created_at": "2026-05-09T17:00:00"
    }
}
```

#### 2.4.2 人脸特征 API

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | /api/faces | 获取所有人脸记录 | - | 人脸数组 |
| GET | /api/faces/<user_id> | 获取用户人脸 | - | 人脸数组 |
| POST | /api/faces | 注册人脸 | {user_id, feature_vector} | 新记录 |
| DELETE | /api/faces/<face_id> | 删除人脸 | - | 删除结果 |

**请求示例：**
```json
// POST /api/faces
{
    "user_id": 1,
    "feature_vector": [0.12, 0.34, ...]  // 128维浮点数数组
}

// 响应
{
    "code": 200,
    "message": "success",
    "data": {
        "face_id": 1,
        "user_id": 1,
        "registered_at": "2026-05-09T17:00:00"
    }
}
```

#### 2.4.3 开门记录 API

| 方法 | 路径 | 说明 | 请求参数 | 响应 |
|------|------|------|----------|------|
| GET | /api/logs | 获取开门记录 | ?page=&limit=&start_date=&end_date=&person_id= | 记录数组 |
| GET | /api/logs/<id> | 获取单条记录 | - | 记录对象 |

**请求示例：**
```
GET /api/logs?page=1&limit=20&start_date=2026-05-01&end_date=2026-05-09
```

**响应示例：**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "records": [
            {
                "log_id": 1,
                "person_id": 1,
                "person_name": "张三",
                "person_type": "known",
                "access_time": "2026-05-09T08:30:00",
                "device_id": 1,
                "result": "success",
                "image_path": "/captures/2026/05/09/001.jpg"
            }
        ],
        "total": 150,
        "page": 1,
        "limit": 20
    }
}
```

#### 2.4.4 陌生人记录 API

| 方法 | 路径 | 说明 | 请求体/参数 | 响应 |
|------|------|------|-------------|------|
| GET | /api/strangers | 获取陌生人列表 | ?page=&limit=&status= | 记录数组 |
| GET | /api/strangers/<id> | 获取单条记录 | - | 记录对象 |
| PUT | /api/strangers/<id> | 处理记录 | {status, processor_id} | 更新后记录 |

**请求示例：**
```json
// PUT /api/strangers/1
{
    "status": "approved",
    "processor_id": 1
}

// 响应
{
    "code": 200,
    "message": "success",
    "data": {
        "record_id": 1,
        "status": "approved",
        "processor_id": 1,
        "processed_at": "2026-05-09T17:00:00"
    }
}
```

#### 2.4.5 设备管理 API

| 方法 | 路径 | 说明 | 请求体 | 响应 |
|------|------|------|--------|------|
| GET | /api/devices | 获取设备列表 | - | 设备数组 |
| GET | /api/devices/<id> | 获取设备详情 | - | 设备对象 |
| POST | /api/devices | 注册设备 | {name, location, ip_address} | 新设备 |
| PUT | /api/devices/<id> | 更新设备 | {name, location, status} | 更新后设备 |
| PUT | /api/devices/<id>/heartbeat | 心跳上报 | {status} | 更新结果 |

### 2.5 WebSocket 事件设计

#### 连接事件

```javascript
// 客户端连接
socket.on('connect', function() {
    console.log('Connected to server');
});

// 加入设备房间（边缘设备使用）
socket.emit('join_device', { device_id: 1 });

// 加入管理房间（小程序/Web使用）
socket.emit('join_admin');
```

#### 陌生人报警事件

```javascript
// 服务端推送
socket.emit('stranger_alert', {
    record_id: 1,
    device_id: 1,
    device_name: "前门",
    image_path": "/captures/2026/05/09/stranger_001.jpg",
    captured_at": "2026-05-09T17:00:00",
    message": "检测到陌生人"
});

// 客户端处理
socket.on('stranger_alert', function(data) {
    showNotification(data);
});
```

#### 开门记录事件

```javascript
// 服务端推送
socket.emit('access_log', {
    log_id": 1,
    person_name": "张三",
    person_type": "known",
    access_time": "2026-05-09T08:30:00",
    result": "success"
});

// 客户端处理
socket.on('access_log', function(data) {
    updateLogList(data);
});
```

#### 远程开门事件

```javascript
// 客户端发送
socket.emit('remote_open', {
    device_id": 1,
    user_id": 1
});

// 服务端响应
socket.on('remote_open_result', function(data) {
    if (data.success) {
        showToast('开门成功');
    } else {
        showToast('开门失败：' + data.message);
    }
});
```

### 2.6 统一响应格式

```json
{
    "code": 200,        // 状态码：200成功，400参数错误，401未授权，500服务器错误
    "message": "success", // 状态信息
    "data": {}          // 业务数据
}
```

### 2.7 日志系统配置

```python
# config.py
LOG_CONFIG = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 1024 * 1024,  # 1MB
            'backupCount': 10,
            'formatter': 'default'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        }
    },
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['file', 'console']
    }
}

LOG_LEVELS = {
    'DEBUG': 0,
    'INFO': 1,
    'WARNING': 2,
    'ERROR': 3
}
```

### 2.8 主要依赖

```
# requirements.txt
Flask==2.3.0
Flask-SocketIO==5.3.0
Flask-CORS==4.0.0
marshmallow==3.20.0
numpy==1.24.0
python-dotenv==1.0.0
```

---

## 3. 前端技术架构

### 3.1 微信小程序技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 框架 | 微信小程序原生 | 官方框架，兼容性好 |
| UI组件 | Vant Weapp | 轻量、可靠 |
| 状态管理 | globalData | 小程序内置全局状态 |
| 网络请求 | wx.request | 封装HTTP请求 |
| WebSocket | wx.connectSocket | 实时通信 |
| 本地存储 | wx.setStorageSync | 缓存数据 |

### 3.2 小程序项目结构

```
miniprogram/
├── app.js                    # 应用入口
├── app.json                  # 全局配置
├── app.wxss                  # 全局样式
├── config/
│   └── config.js             # 配置文件（API地址等）
├── utils/
│   ├── request.js            # HTTP请求封装
│   ├── websocket.js          # WebSocket封装
│   └── storage.js            # 本地存储封装
├── pages/
│   ├── index/                # 首页
│   │   ├── index.js
│   │   ├── index.json
│   │   ├── index.wxml
│   │   └── index.wxss
│   ├── logs/                 # 开门记录
│   │   ├── logs.js
│   │   ├── logs.json
│   │   ├── logs.wxml
│   │   └── logs.wxss
│   ├── strangers/            # 陌生人审核
│   │   ├── strangers.js
│   │   ├── strangers.json
│   │   ├── strangers.wxml
│   │   └── strangers.wxss
│   ├── users/                # 用户管理
│   │   ├── users.js
│   │   ├── users.json
│   │   ├── users.wxml
│   │   └── users.wxss
│   └── settings/             # 设置
│       ├── settings.js
│       ├── settings.json
│       ├── settings.wxml
│       └── settings.wxss
├── components/               # 公共组件
│   ├── log-item/             # 日志条目组件
│   ├── stranger-card/        # 陌生人卡片组件
│   └── user-form/            # 用户表单组件
└── images/                   # 图片资源
```

### 3.3 核心功能实现

#### 3.3.1 HTTP请求封装 (utils/request.js)

```javascript
const config = require('../config/config');

const request = (url, method = 'GET', data = {}) => {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${config.baseUrl}${url}`,
      method: method,
      data: data,
      header: {
        'content-type': 'application/json',
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data);
        } else {
          reject(res.data);
        }
      },
      fail: (err) => {
        reject(err);
      }
    });
  });
};

module.exports = {
  get: (url, data) => request(url, 'GET', data),
  post: (url, data) => request(url, 'POST', data),
  put: (url, data) => request(url, 'PUT', data),
  delete: (url, data) => request(url, 'DELETE', data)
};
```

#### 3.3.2 WebSocket封装 (utils/websocket.js)

```javascript
const config = require('../config/config');
let socketTask = null;

const connect = () => {
  socketTask = wx.connectSocket({
    url: config.wsUrl,
    success: () => {
      console.log('WebSocket连接成功');
    }
  });

  socketTask.onOpen(() => {
    console.log('WebSocket已打开');
    // 加入管理房间
    send('join_admin', {});
  });

  socketTask.onMessage((res) => {
    const data = JSON.parse(res.data);
    handleMessage(data);
  });

  socketTask.onClose(() => {
    console.log('WebSocket已关闭');
    // 自动重连
    setTimeout(connect, 3000);
  });

  socketTask.onError((err) => {
    console.error('WebSocket错误', err);
  });
};

const send = (event, data) => {
  if (socketTask) {
    socketTask.send({
      data: JSON.stringify({ event, data })
    });
  }
};

const on = (event, callback) => {
  // 注册事件监听
  wx.$socketCallbacks = wx.$socketCallbacks || {};
  wx.$socketCallbacks[event] = callback;
};

const handleMessage = (message) => {
  const { event, data } = message;
  if (wx.$socketCallbacks && wx.$socketCallbacks[event]) {
    wx.$socketCallbacks[event](data);
  }
};

module.exports = { connect, send, on };
```

#### 3.3.3 页面功能实现

**陌生人审核页面 (pages/strangers/strangers.js)**

```javascript
const request = require('../../utils/request');
const socket = require('../../utils/websocket');

Page({
  data: {
    strangers: [],
    loading: false,
    page: 1,
    hasMore: true
  },

  onLoad() {
    this.loadStrangers();
    this.setupWebSocket();
  },

  // 加载陌生人列表
  async loadStrangers() {
    if (this.data.loading || !this.data.hasMore) return;
    
    this.setData({ loading: true });
    try {
      const res = await request.get('/api/strangers', {
        page: this.data.page,
        limit: 10,
        status: 'pending'
      });
      this.setData({
        strangers: [...this.data.strangers, ...res.data.records],
        page: this.data.page + 1,
        hasMore: res.data.records.length === 10
      });
    } catch (err) {
      wx.showToast({ title: '加载失败', icon: 'error' });
    }
    this.setData({ loading: false });
  },

  // 设置WebSocket监听
  setupWebSocket() {
    socket.on('stranger_alert', (data) => {
      // 新陌生人提醒
      wx.showToast({ title: '有新陌生人', icon: 'none' });
      // 刷新列表
      this.setData({ strangers: [], page: 1, hasMore: true });
      this.loadStrangers();
    });
  },

  // 授权开门
  async approveStranger(e) {
    const { id } = e.currentTarget.dataset;
    try {
      await request.put(`/api/strangers/${id}`, {
        status: 'approved',
        processor_id: wx.getStorageSync('userId')
      });
      wx.showToast({ title: '已授权' });
      this.removeStranger(id);
    } catch (err) {
      wx.showToast({ title: '操作失败', icon: 'error' });
    }
  },

  // 加入黑名单
  async rejectStranger(e) {
    const { id } = e.currentTarget.dataset;
    wx.showModal({
      title: '确认',
      content: '确定将该人员加入黑名单吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await request.put(`/api/strangers/${id}`, {
              status: 'rejected',
              processor_id: wx.getStorageSync('userId')
            });
            wx.showToast({ title: '已加入黑名单' });
            this.removeStranger(id);
          } catch (err) {
            wx.showToast({ title: '操作失败', icon: 'error' });
          }
        }
      }
    });
  },

  // 从列表移除已处理记录
  removeStranger(id) {
    this.setData({
      strangers: this.data.strangers.filter(s => s.record_id !== id)
    });
  }
});
```

**用户管理页面 (pages/users/users.js)**

```javascript
const request = require('../../utils/request');

Page({
  data: {
    users: [],
    loading: false,
    showForm: false,
    currentUser: null
  },

  onLoad() {
    this.loadUsers();
  },

  // 加载用户列表
  async loadUsers() {
    this.setData({ loading: true });
    try {
      const res = await request.get('/api/users');
      this.setData({ users: res.data });
    } catch (err) {
      wx.showToast({ title: '加载失败', icon: 'error' });
    }
    this.setData({ loading: false });
  },

  // 显示添加/编辑表单
  showAddForm() {
    this.setData({
      showForm: true,
      currentUser: null
    });
  },

  showEditForm(e) {
    const { user } = e.currentTarget.dataset;
    this.setData({
      showForm: true,
      currentUser: user
    });
  },

  // 保存用户
  async saveUser(e) {
    const { name, phone, permission } = e.detail.value;
    const { currentUser } = this.data;

    try {
      if (currentUser) {
        // 更新
        await request.put(`/api/users/${currentUser.user_id}`, {
          name, phone, permission
        });
        wx.showToast({ title: '更新成功' });
      } else {
        // 新增
        await request.post('/api/users', { name, phone, permission });
        wx.showToast({ title: '添加成功' });
      }
      this.setData({ showForm: false });
      this.loadUsers();
    } catch (err) {
      wx.showToast({ title: '操作失败', icon: 'error' });
    }
  },

  // 删除用户
  deleteUser(e) {
    const { id } = e.currentTarget.dataset;
    wx.showModal({
      title: '确认',
      content: '确定删除该用户吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await request.delete(`/api/users/${id}`);
            wx.showToast({ title: '删除成功' });
            this.loadUsers();
          } catch (err) {
            wx.showToast({ title: '删除失败', icon: 'error' });
          }
        }
      }
    });
  }
});
```

#### 3.3.4 小程序配置 (app.json)

```json
{
  "pages": [
    "pages/index/index",
    "pages/logs/logs",
    "pages/strangers/strangers",
    "pages/users/users",
    "pages/settings/settings"
  ],
  "window": {
    "backgroundTextStyle": "light",
    "navigationBarBackgroundColor": "#1890ff",
    "navigationBarTitleText": "智慧门禁系统",
    "navigationBarTextStyle": "white"
  },
  "tabBar": {
    "color": "#999",
    "selectedColor": "#1890ff",
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "首页",
        "iconPath": "images/home.png",
        "selectedIconPath": "images/home-active.png"
      },
      {
        "pagePath": "pages/logs/logs",
        "text": "记录",
        "iconPath": "images/log.png",
        "selectedIconPath": "images/log-active.png"
      },
      {
        "pagePath": "pages/strangers/strangers",
        "text": "审核",
        "iconPath": "images/check.png",
        "selectedIconPath": "images/check-active.png"
      },
      {
        "pagePath": "pages/users/users",
        "text": "用户",
        "iconPath": "images/user.png",
        "selectedIconPath": "images/user-active.png"
      }
    ]
  }
}
```

### 3.4 Web管理后台技术栈（可选）

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 框架 | Vue 3 + Vite | 现代前端框架 |
| UI库 | Element Plus | 企业级UI组件 |
| 状态管理 | Pinia | 轻量级状态管理 |
| 网络请求 | Axios | HTTP客户端 |
| WebSocket | Socket.io-client | 实时通信 |

---

## 4. 边缘设备端接口规范

### 4.1 上报数据接口

边缘设备需要调用以下接口上报数据：

```javascript
// 1. 上报识别结果
POST /api/access/recognize
{
    "device_id": 1,
    "user_id": 1,           // 已知人员
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

### 4.2 接收指令接口

边缘设备通过WebSocket接收指令：

```javascript
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

## 5. 安全设计

### 5.1 接口认证

- 使用JWT Token进行身份验证
- Token有效期：24小时
- 边缘设备使用设备密钥认证

### 5.2 数据安全

- 人脸特征向量加密存储
- 敏感信息（手机号等）脱敏显示
- 图片文件访问权限控制

### 5.3 通信安全

- 生产环境使用HTTPS
- WebSocket使用WSS
- 关键操作日志审计
