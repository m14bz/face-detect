const request = require('../../utils/request');
const socket = require('../../utils/websocket');

Page({
  data: {
    logs: [],
    loading: false,
    page: 1,
    hasMore: true,
    dateRange: '',
    startDate: '',
    endDate: ''
  },

  onLoad() {
    this.loadLogs();
    this.setupWebSocket();
  },

  // 加载开门记录
  async loadLogs() {
    if (this.data.loading || !this.data.hasMore) return;
    
    this.setData({ loading: true });
    
    try {
      const params = {
        page: this.data.page,
        limit: 20
      };
      
      if (this.data.startDate) {
        params.start_date = this.data.startDate;
      }
      if (this.data.endDate) {
        params.end_date = this.data.endDate;
      }
      
      const res = await request.get('/api/logs', params);
      
      this.setData({
        logs: [...this.data.logs, ...res.data.records],
        page: this.data.page + 1,
        hasMore: res.data.records.length === 20
      });
    } catch (err) {
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      });
    }
    
    this.setData({ loading: false });
  },

  // 设置WebSocket监听
  setupWebSocket() {
    socket.on('access_log', (data) => {
      // 新记录添加到顶部
      this.setData({
        logs: [data, ...this.data.logs]
      });
    });
  },

  // 刷新数据
  onPullDownRefresh() {
    this.setData({
      logs: [],
      page: 1,
      hasMore: true
    });
    this.loadLogs();
    wx.stopPullDownRefresh();
  },

  // 加载更多
  onReachBottom() {
    this.loadLogs();
  },

  // 日期选择
  onDateChange(e) {
    const { type } = e.currentTarget.dataset;
    const value = e.detail.value;
    
    this.setData({
      [type === 'start' ? 'startDate' : 'endDate']: value
    });
    
    // 重新加载数据
    this.setData({
      logs: [],
      page: 1,
      hasMore: true
    });
    this.loadLogs();
  },

  // 清除日期筛选
  clearDateFilter() {
    this.setData({
      startDate: '',
      endDate: ''
    });
    
    this.setData({
      logs: [],
      page: 1,
      hasMore: true
    });
    this.loadLogs();
  }
});
