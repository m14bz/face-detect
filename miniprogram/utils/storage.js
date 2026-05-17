const config = require('../config/config');

const storage = {
  // 设置Token
  setToken(token) {
    wx.setStorageSync(config.tokenKey, token);
  },
  
  // 获取Token
  getToken() {
    return wx.getStorageSync(config.tokenKey);
  },
  
  // 移除Token
  removeToken() {
    wx.removeStorageSync(config.tokenKey);
  },
  
  // 设置用户信息
  setUserInfo(userInfo) {
    wx.setStorageSync(config.userInfoKey, userInfo);
  },
  
  // 获取用户信息
  getUserInfo() {
    return wx.getStorageSync(config.userInfoKey);
  },
  
  // 移除用户信息
  removeUserInfo() {
    wx.removeStorageSync(config.userInfoKey);
  },
  
  // 设置用户ID
  setUserId(userId) {
    wx.setStorageSync(config.userIdKey, userId);
  },
  
  // 获取用户ID
  getUserId() {
    return wx.getStorageSync(config.userIdKey);
  },
  
  // 移除用户ID
  removeUserId() {
    wx.removeStorageSync(config.userIdKey);
  },
  
  // 清除所有登录信息
  clearLoginInfo() {
    this.removeToken();
    this.removeUserInfo();
    this.removeUserId();
  },
  
  // 检查是否已登录
  isLoggedIn() {
    return !!this.getToken();
  }
};

module.exports = storage;
