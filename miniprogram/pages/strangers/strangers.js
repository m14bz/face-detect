const request = require('../../utils/request');
const socket = require('../../utils/websocket');
const storage = require('../../utils/storage');

Page({
  data: {
    strangers: [],
    loading: false,
    page: 1,
    hasMore: true,
    activeTab: 'pending',
    tabs: [
      { key: 'pending', title: '待审核' },
      { key: 'approved', title: '已授权' },
      { key: 'rejected', title: '已拒绝' }
    ]
  },

  onLoad() {
    this.loadStrangers();
    this.setupWebSocket();
  },

  // 加载陌生人列表
  async loadStrangers() {
    if (this.data.loading || !this.data.hasMore) return;
    
    this.setData({ loading: true });
    
    try {
      const res = await request.get('/api/strangers', {
        page: this.data.page,
        limit: 10,
        status: this.data.activeTab
      });
      
      this.setData({
        strangers: [...this.data.strangers, ...res.data.records],
        page: this.data.page + 1,
        hasMore: res.data.records.length === 10
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
    socket.on('stranger_alert', (data) => {
      // 新陌生人提醒
      wx.showToast({
        title: '有新陌生人',
        icon: 'none'
      });
      
      // 如果当前是待审核标签，刷新列表
      if (this.data.activeTab === 'pending') {
        this.refreshList();
      }
    });
  },

  // 切换标签
  onTabChange(e) {
    const tab = e.currentTarget.dataset.tab;
    this.setData({
      activeTab: tab,
      strangers: [],
      page: 1,
      hasMore: true
    });
    this.loadStrangers();
  },

  // 刷新列表
  refreshList() {
    this.setData({
      strangers: [],
      page: 1,
      hasMore: true
    });
    this.loadStrangers();
  },

  // 刷新数据
  onPullDownRefresh() {
    this.refreshList();
    wx.stopPullDownRefresh();
  },

  // 加载更多
  onReachBottom() {
    this.loadStrangers();
  },

  // 授权开门
  async approveStranger(e) {
    const { id } = e.currentTarget.dataset;
    
    wx.showModal({
      title: '确认',
      content: '确定授权该人员开门吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await request.put(`/api/strangers/${id}`, {
              status: 'approved',
              processor_id: storage.getUserId()
            });
            
            wx.showToast({
              title: '已授权'
            });
            
            this.removeStranger(id);
          } catch (err) {
            wx.showToast({
              title: '操作失败',
              icon: 'error'
            });
          }
        }
      }
    });
  },

  // 加入黑名单
  async rejectStranger(e) {
    const { id } = e.currentTarget.dataset;
    
    wx.showModal({
      title: '确认',
      content: '确定将该人员加入黑名单吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await request.put(`/api/strangers/${id}`, {
              status: 'rejected',
              processor_id: storage.getUserId()
            });
            
            wx.showToast({
              title: '已加入黑名单'
            });
            
            this.removeStranger(id);
          } catch (err) {
            wx.showToast({
              title: '操作失败',
              icon: 'error'
            });
          }
        }
      }
    });
  },

  // 从列表移除已处理记录
  removeStranger(id) {
    this.setData({
      strangers: this.data.strangers.filter(s => s.record_id !== id)
    });
  }
});
