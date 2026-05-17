Component({
  properties: {
    user: {
      type: Object,
      value: null
    },
    show: {
      type: Boolean,
      value: false
    }
  },
  
  data: {
    form: {
      name: '',
      phone: '',
      permission: 'normal'
    },
    permissionOptions: ['normal', 'admin', 'blacklist']
  },
  
  observers: {
    'user': function(user) {
      if (user) {
        this.setData({
          form: {
            name: user.name,
            phone: user.phone,
            permission: user.permission
          }
        });
      } else {
        this.setData({
          form: {
            name: '',
            phone: '',
            permission: 'normal'
          }
        });
      }
    }
  },
  
  methods: {
    onInputName(e) {
      this.setData({
        'form.name': e.detail
      });
    },
    
    onInputPhone(e) {
      this.setData({
        'form.phone': e.detail
      });
    },
    
    onPermissionChange(e) {
      const index = e.detail.value;
      this.setData({
        'form.permission': this.data.permissionOptions[index]
      });
    },
    
    onSave() {
      const { form } = this.data;
      
      if (!form.name || !form.phone) {
        wx.showToast({
          title: '请填写完整信息',
          icon: 'none'
        });
        return;
      }
      
      this.triggerEvent('save', { form: form });
    },
    
    onClose() {
      this.triggerEvent('close');
    }
  }
});
