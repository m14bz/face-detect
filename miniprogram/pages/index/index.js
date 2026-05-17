const request = require('../../utils/request');
const socket = require('../../utils/websocket');
const storage = require('../../utils/storage');

Page({
  data: {
    isLoggedIn: false,
    userInfo: null,
    devices: [],
    recentLogs: [],
    strangerCount: 0,
    loading: false
  },

  onLoad() {
    this.checkLoginStatus();
  },

  onShow() {
    if (this.data.isLoggedIn) {
      this.loadData();
    }
  },

  // 检查登录状态
  checkLoginStatus() {
    const isLoggedIn = storage.isLoggedIn();
    const userInfo = storage.getUserInfo();
    
    this.setData({
      isLoggedIn: isLoggedIn,
      userInfo: userInfo
    });
    
    if (isLoggedIn) {
      this.setupWebSocket();
    }
  },

  // 加载数据
  async loadData() {
    this.setData({ loading: true });
    
    try {
      // 并行加载设备列表和最近记录
      const [devicesRes, logsRes, strangersRes] = await Promise.all([
        request.get('/api/devices'),
        request.get('/api/logs', { page: 1, limit: 5 }),
        request.get('/api/strangers', { page: 1, limit: 1, status: 'pending' })
      ]);
      
      this.setData({
        devices: devicesRes.data || [],
        recentLogs: logsRes.data.records || [],
        strangerCount: strangersRes.data.total || 0
      });
    } catch (err) {
      console.error('加载数据失败', err);
    }
    
    this.setData({ loading: false });
  },

  // 设置WebSocket监听
  setupWebSocket() {
    socket.on('stranger_alert', (data) => {
      wx.showToast({
        title: '检测到陌生人',
        icon: 'none'
      });
      // 更新陌生人计数
      this.setData({
        strangerCount: this.data.strangerCount + 1
      });
    });
    
    socket.on('access_log', (data) => {
      // 更新最近记录
      const recentLogs = [data, ...this.data.recentLogs].slice(0, 5);
      this.setData({
        recentLogs: recentLogs
      });
    });
  },

  // 跳转到登录页
  goToLogin() {
    wx.navigateTo({
      url: '/pages/settings/settings'
    });
  },

  // 刷新数据
  onPullDownRefresh() {
    this.loadData();
    wx.stopPullDownRefresh();
  },

  // 远程开门
  async openDoor(e) {
    const deviceId = e.currentTarget.dataset.id;
    
    wx.showModal({
      title: '确认',
      content: '确定要远程开门吗？',
      success: async (res) => {
        if (res.confirm) {
          const userId = storage.getUserId();
          
          socket.send('remote_open', {
            device_id: deviceId,
            user_id: userId
          });
          
          wx.showToast({
            title: '开门指令已发送',
            icon: 'none'
          });
        }
      }
    });
  }
});
