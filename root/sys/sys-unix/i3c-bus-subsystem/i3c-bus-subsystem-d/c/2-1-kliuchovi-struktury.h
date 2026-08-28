struct i3c_master_controller_ops {
	int (*bus_init)(struct i3c_master_controller *master);
	void (*bus_cleanup)(struct i3c_master_controller *master);
	int (*attach_i3c_dev)(struct i3c_dev_desc *dev);
	int (*reattach_i3c_dev)(struct i3c_dev_desc *dev, u8 old_dyn_addr);
	void (*detach_i3c_dev)(struct i3c_dev_desc *dev);
	int (*do_daa)(struct i3c_master_controller *master);
	int (*send_ccc_cmd)(struct i3c_master_controller *master,
			    struct i3c_ccc_cmd *cmd);
	int (*priv_xfers)(struct i3c_dev_desc *dev,
			  struct i3c_priv_xfer *xfers,
			  int nxfers);
	int (*i2c_xfers)(struct i2c_dev_desc *dev,
			 const struct i2c_msg *xfers, int nxfers);
	int (*request_ibi)(struct i3c_dev_desc *dev,
			   const struct i3c_ibi_setup *req);
	void (*free_ibi)(struct i3c_dev_desc *dev);
	int (*enable_ibi)(struct i3c_dev_desc *dev);
	int (*disable_ibi)(struct i3c_dev_desc *dev);
};
