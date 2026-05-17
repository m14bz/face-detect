const request = require('../../utils/request');
const websocket = require('../../utils/websocket');
const storage = require('../../utils/storage');

Page({
  data: {
    isLoggedIn: false,
    userInfo: null,
    phone: '',
    loading: false
  },

  onLoad() {
    this.checkLoginStatus();
  },

  onShow() {
    this.checkLoginStatus();
  },

  // 检查登录状态
  checkLoginStatus() {
    const isLoggedIn = storage.isLoggedIn();
    const userInfo = storage.getUserInfo();
    
    this.setData({
      isLoggedIn: isLoggedIn,
      userInfo: userInfo
    });
  },

  // 手机号输入
  onInputPhone(e) {
    this.setData({
      phone: e.detail.value || e.detail
    });
  },

  // 登录
  async login() {
    const { phone } = this.data;
    
    if (!phone) {
      wx.showToast({
        title: '请输入手机号',
        icon: 'none'
      });
      return;
    }
    
    this.setData({ loading: true });
    
    try {
      const res = await request.post('/api/auth/login', {
        phone: phone
      });
      
      if (res.code === 200) {
        // 保存登录信息
        storage.setToken(res.data.token);
        storage.setUserInfo(res.data.user);
        storage.setUserId(res.data.user.user_id);
        
        // 连接WebSocket
        websocket.connect();
        
        this.setData({
          isLoggedIn: true,
          userInfo: res.data.user,
          phone: ''
        });
        
        wx.showToast({
          title: '登录成功'
        });
      } else {
        wx.showToast({
          title: res.message || '登录失败',
          icon: 'error'
        });
      }
    } catch (err) {
      wx.showToast({
        title: '登录失败',
        icon: 'error'
      });
    }
    
    this.setData({ loading: false });
  },

  // 退出登录
  logout() {
    wx.showModal({
      title: '确认',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 清除登录信息
          storage.clearLoginInfo();
          
          // 断开WebSocket
          websocket.close();
          
          this.setData({
            isLoggedIn: false,
            userInfo: null
          });
          
          wx.showToast({
            title: '已退出登录'
          });
        }
      }
    });
  }
});
