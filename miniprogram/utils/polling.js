/**
 * HTTP 轮询工具类
 * 用于替代 WebSocket 的实时通知功能
 */

const request = require('./request');
const config = require('../config/config');

let pollingTimer = null;
let isPolling = false;
let lastCheckTime = 0;
let callbacks = {};

/**
 * 开始轮询
 * @param {number} interval - 轮询间隔（毫秒），默认 5000
 */
const startPolling = (interval = 5000) => {
  if (isPolling) {
    console.log('轮询已在运行');
    return;
  }
  
  isPolling = true;
  lastCheckTime = Date.now() / 1000;
  
  console.log(`开始 HTTP 轮询，间隔: ${interval}ms`);
  
  // 立即执行一次
  pollOnce();
  
  // 设置定时器
  pollingTimer = setInterval(() => {
    pollOnce();
  }, interval);
};

/**
 * 执行一次轮询
 */
const pollOnce = async () => {
  try {
    const response = await request.get('/api/poll', {
      last_check: lastCheckTime
    });
    
    if (response && response.status === 'ok') {
      lastCheckTime = response.timestamp;
      
      // 这里可以添加逻辑来处理新数据
      // 暂时只记录日志
      console.log('轮询成功:', response);
    }
  } catch (err) {
    console.error('轮询失败:', err);
  }
};

/**
 * 停止轮询
 */
const stopPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer);
    pollingTimer = null;
  }
  isPolling = false;
  console.log('已停止 HTTP 轮询');
};

/**
 * 注册事件回调
 * @param {string} event - 事件名称
 * @param {function} callback - 回调函数
 */
const on = (event, callback) => {
  callbacks[event] = callback;
};

/**
 * 移除事件回调
 * @param {string} event - 事件名称
 */
const off = (event) => {
  if (callbacks[event]) {
    delete callbacks[event];
  }
};

/**
 * 模拟发送事件（本地测试用）
 * @param {string} event - 事件名称
 * @param {object} data - 事件数据
 */
const emit = (event, data) => {
  if (callbacks[event]) {
    callbacks[event](data);
  }
};

module.exports = {
  startPolling,
  stopPolling,
  pollOnce,
  on,
  off,
  emit,
  isPolling: () => isPolling
};