struct i3c_ccc_cmd {
	u8 rnw;
	u8 id;
	struct {
		u16 len;
		void *data;
	} payload;
	struct i3c_ccc_target_payload *targets;
	int ndests;
	int err;
};
