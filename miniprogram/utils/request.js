const config = require('../config/config');

const REQUEST_TIMEOUT = 15000; // 15秒超时

const request = (url, method = 'GET', data = {}) => {
  return new Promise((resolve, reject) => {
    let isTimeout = false;
    let timer = null;
    
    // 超时处理
    timer = setTimeout(() => {
      isTimeout = true;
      wx.showToast({
        title: '请求超时，请检查网络',
        icon: 'none',
        duration: 2000
      });
      reject({ code: 'TIMEOUT', message: '请求超时' });
    }, REQUEST_TIMEOUT);
    
    wx.request({
      url: `${config.baseUrl}${url}`,
      method: method,
      data: data,
      timeout: REQUEST_TIMEOUT,
      header: {
        'content-type': 'application/json',
        'Authorization': `Bearer ${wx.getStorageSync(config.tokenKey)}`
      },
      success: (res) => {
        if (isTimeout) return;
        clearTimeout(timer);
        
        if (res.statusCode === 200) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
          // Token过期或无效，跳转登录
          wx.removeStorageSync(config.tokenKey);
          wx.removeStorageSync(config.userInfoKey);
          wx.redirectTo({
            url: '/pages/settings/settings'
          });
          reject(res.data);
        } else {
          console.error(`[Request] ${method} ${url} failed:`, res.statusCode, res.data);
          reject(res.data);
        }
      },
      fail: (err) => {
        if (isTimeout) return;
        clearTimeout(timer);
        
        console.error(`[Request] ${method} ${url} error:`, err);
        wx.showToast({
          title: '网络连接失败',
          icon: 'none'
        });
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
