// app.js
const websocket = require('./utils/websocket');

App({
  onLaunch() {
    // 检查登录状态
    const token = wx.getStorageSync('token');
    if (token) {
      // 尝试连接WebSocket
      websocket.connect();
    }
  },

  globalData: {
    userInfo: null,
    token: null,
    baseUrl: 'http://192.168.1.163:5000'
  }
});
