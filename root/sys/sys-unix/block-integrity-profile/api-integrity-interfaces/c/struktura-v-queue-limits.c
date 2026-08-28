struct blk_integrity {
	unsigned char			flags;
	enum blk_integrity_checksum	csum_type;
	unsigned char			metadata_size;   /* усіх службових байтів на інтервал */
	unsigned char			pi_offset;       /* зсув кортежу всередині них */
	unsigned char			interval_exp;    /* log₂ інтервалу даних */
	unsigned char			tag_size;        /* вільних байтів для власника вище */
	unsigned char			pi_tuple_size;   /* 8 або 16 */
};

enum blk_integrity_checksum {
	BLK_INTEGRITY_CSUM_NONE  = 0,
	BLK_INTEGRITY_CSUM_IP    = 1,
	BLK_INTEGRITY_CSUM_CRC   = 2,
	BLK_INTEGRITY_CSUM_CRC64 = 3,
};

enum blk_integrity_flags {
	BLK_INTEGRITY_NOVERIFY       = 1 << 0,  /* ← read_verify = 0 */
	BLK_INTEGRITY_NOGENERATE     = 1 << 1,  /* ← write_generate = 0 */
	BLK_INTEGRITY_DEVICE_CAPABLE = 1 << 2,  /* → device_is_integrity_capable */
	BLK_INTEGRITY_REF_TAG        = 1 << 3,  /* → TYPE1 у рядку format */
	BLK_INTEGRITY_STACKED        = 1 << 4,  /* профіль зібрано з нижніх шарів */
	BLK_SPLIT_INTERVAL_CAPABLE   = 1 << 5,  /* інтервал можна різати між сторінками */
};
