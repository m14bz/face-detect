Component({
  properties: {
    stranger: {
      type: Object,
      value: {}
    },
    showActions: {
      type: Boolean,
      value: true
    }
  },
  
  data: {},
  
  methods: {
    onApprove() {
      this.triggerEvent('approve', { id: this.data.stranger.record_id });
    },
    
    onReject() {
      this.triggerEvent('reject', { id: this.data.stranger.record_id });
    }
  }
});
