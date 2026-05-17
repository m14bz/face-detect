const request = require('../../utils/request');

Page({
  data: {
    users: [],
    loading: false,
    showForm: false,
    isEdit: false,
    currentUser: null,
    form: {
      name: '',
      phone: '',
      permission: 'normal'
    },
    permissionOptions: ['normal', 'admin', 'blacklist']
  },

  onLoad() {
    this.loadUsers();
  },

  // 加载用户列表
  async loadUsers() {
    this.setData({ loading: true });
    
    try {
      const res = await request.get('/api/users');
      console.log('[loadUsers] 响应:', res);
      
      // 兼容不同的响应格式
      const users = (res && res.data) ? res.data : (Array.isArray(res) ? res : []);
      this.setData({
        users: users
      });
    } catch (err) {
      console.error('[loadUsers] 错误:', err);
      
      let errMsg = '加载失败';
      if (err && err.code === 'TIMEOUT') {
        errMsg = '请求超时，请检查网络';
      } else if (err && err.message) {
        errMsg = err.message;
      }
      
      wx.showToast({
        title: errMsg,
        icon: 'none'
      });
    }
    
    this.setData({ loading: false });
  },

  // 刷新数据
  onPullDownRefresh() {
    this.loadUsers();
    wx.stopPullDownRefresh();
  },

  // 显示添加表单
  showAddForm() {
    this.setData({
      showForm: true,
      isEdit: false,
      currentUser: null,
      form: {
        name: '',
        phone: '',
        permission: 'normal'
      }
    });
  },

  // 显示编辑表单
  showEditForm(e) {
    const { user } = e.currentTarget.dataset;
    this.setData({
      showForm: true,
      isEdit: true,
      currentUser: user,
      form: {
        name: user.name,
        phone: user.phone,
        permission: user.permission
      }
    });
  },

  // 隐藏表单
  hideForm() {
    this.setData({
      showForm: false,
      currentUser: null
    });
  },

  // 表单输入
  onInputName(e) {
    this.setData({
      'form.name': e.detail.value || e.detail
    });
  },

  onInputPhone(e) {
    this.setData({
      'form.phone': e.detail.value || e.detail
    });
  },

  onPermissionChange(e) {
    const index = e.detail.value;
    this.setData({
      'form.permission': this.data.permissionOptions[index]
    });
  },

  // 保存用户
  async saveUser() {
    const { form, isEdit, currentUser } = this.data;
    
    if (!form.name || !form.phone) {
      wx.showToast({
        title: '请填写完整信息',
        icon: 'none'
      });
      return;
    }
    
    try {
      if (isEdit) {
        // 更新
        await request.put(`/api/users/${currentUser.user_id}`, form);
        wx.showToast({
          title: '更新成功'
        });
      } else {
        // 新增
        await request.post('/api/users', form);
        wx.showToast({
          title: '添加成功'
        });
      }
      
      this.hideForm();
      this.loadUsers();
    } catch (err) {
      wx.showToast({
        title: '操作失败',
        icon: 'error'
      });
    }
  },

  // 删除用户
  deleteUser(e) {
    const { id } = e.currentTarget.dataset;
    
    wx.showModal({
      title: '确认',
      content: '确定删除该用户吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await request.delete(`/api/users/${id}`);
            wx.showToast({
              title: '删除成功'
            });
            this.loadUsers();
          } catch (err) {
            wx.showToast({
              title: '删除失败',
              icon: 'error'
            });
          }
        }
      }
    });
  }
});
