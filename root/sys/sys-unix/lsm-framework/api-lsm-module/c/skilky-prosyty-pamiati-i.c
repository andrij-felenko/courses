struct lsm_blob_sizes {
	int lbs_cred;		/* struct cred — облікові дані */
	int lbs_file;		/* struct file — відкритий опис файлу */
	int lbs_ib;		/* об'єкти InfiniBand */
	int lbs_inode;		/* struct inode */
	int lbs_sock;		/* struct sock — сокет із боку ядра */
	int lbs_superblock;	/* змонтована файлова система */
	int lbs_ipc;		/* об'єкт System V IPC */
	int lbs_key;		/* ключ у зв'язці ядра */
	int lbs_msg_msg;	/* окреме повідомлення черги */
	int lbs_perf_event;	/* подія perf */
	int lbs_task;		/* struct task_struct */
	int lbs_xattr_count;	/* НЕ байти — кількість комірок під xattr */
	int lbs_tun_dev;	/* пристрій TUN/TAP */
	int lbs_bdev;		/* блоковий пристрій */
};
