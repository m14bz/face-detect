const config = require('../config/config');

let socketTask = null;
let isConnected = false;
let reconnectTimer = null;

const connect = () => {
  if (isConnected) {
    console.log('WebSocket已连接');
    return;
  }
  
  socketTask = wx.connectSocket({
    url: config.wsUrl,
    success: () => {
      console.log('WebSocket连接请求已发送');
    }
  });
  
  socketTask.onOpen(() => {
    console.log('WebSocket已打开');
    isConnected = true;
    
    // 加入管理房间
    send('join_admin', {});
  });
  
  socketTask.onMessage((res) => {
    try {
      const data = JSON.parse(res.data);
      handleMessage(data);
    } catch (e) {
      console.error('解析WebSocket消息失败', e);
    }
  });
  
  socketTask.onClose(() => {
    console.log('WebSocket已关闭');
    isConnected = false;
    
    // 自动重连
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
    }
    reconnectTimer = setTimeout(() => {
      connect();
    }, 3000);
  });
  
  socketTask.onError((err) => {
    console.error('WebSocket连接错误', err);
    isConnected = false;
  });
};

const send = (event, data) => {
  if (socketTask && isConnected) {
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

const off = (event) => {
  if (wx.$socketCallbacks && wx.$socketCallbacks[event]) {
    delete wx.$socketCallbacks[event];
  }
};

const handleMessage = (message) => {
  const { event, data } = message;
  if (wx.$socketCallbacks && wx.$socketCallbacks[event]) {
    wx.$socketCallbacks[event](data);
  }
};

const close = () => {
  if (socketTask) {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
    }
    socketTask.close();
    socketTask = null;
    isConnected = false;
  }
};

module.exports = {
  connect,
  send,
  on,
  off,
  close,
  isConnected: () => isConnected
};