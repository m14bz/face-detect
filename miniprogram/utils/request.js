const config = require('../config/config');

const REQUEST_TIMEOUT = 30000; // 30秒超时

const request = (url, method = 'GET', data = {}) => {
  const fullUrl = `${config.baseUrl}${url}`;
  console.log(`[Request] ${method} ${fullUrl}`, data);
  
  return new Promise((resolve, reject) => {
    wx.request({
      url: fullUrl,
      method: method,
      data: data,
      timeout: REQUEST_TIMEOUT,
      header: {
        'content-type': 'application/json',
        'Authorization': `Bearer ${wx.getStorageSync(config.tokenKey)}`
      },
      success: (res) => {
        console.log(`[Request] ${method} ${url} 响应:`, res.statusCode, res.data);
        
        if (res.statusCode === 200) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
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
        console.error(`[Request] ${method} ${url} 失败:`, err);
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
