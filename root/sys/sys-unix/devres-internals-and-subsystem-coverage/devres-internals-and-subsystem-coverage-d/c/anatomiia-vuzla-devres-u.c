struct devres_node {
	struct list_head		entry;
	dr_release_t			release;
	const char			*name;
	size_t				size;
};

struct devres {
	struct devres_node		node;
	/* гнучкий масив або вирівняне корисне навантаження */
	u8				data[];
};
