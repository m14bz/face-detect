// config/config.js
const config = {
  // API基础地址
  // 注意:模拟器中使用127.0.0.1，真机中使用电脑的局域网IP
  // 开发阶段使用127.0.0.1，发布前改为真实IP
  baseUrl: 'http://127.0.0.1:5000',
  
  // WebSocket地址
  wsUrl: 'ws://127.0.0.1:5000',
  
  // Token存储键
  tokenKey: 'token',
  
  // 用户信息存储键
  userInfoKey: 'userInfo',
  
  // 用户ID存储键
  userIdKey: 'userId'
};

module.exports = config;
