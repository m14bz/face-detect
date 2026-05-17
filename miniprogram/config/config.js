// config/config.js
const config = {
  // API基础地址
  // 注意:小程序不能使用 localhost,必须使用真实的 IP 地址
  // 确保手机和电脑在同一个局域网内
  baseUrl: 'http://192.168.1.163:5000',
  
  // WebSocket地址
  wsUrl: 'ws://192.168.1.163:5000',
  
  // Token存储键
  tokenKey: 'token',
  
  // 用户信息存储键
  userInfoKey: 'userInfo',
  
  // 用户ID存储键
  userIdKey: 'userId'
};

module.exports = config;
