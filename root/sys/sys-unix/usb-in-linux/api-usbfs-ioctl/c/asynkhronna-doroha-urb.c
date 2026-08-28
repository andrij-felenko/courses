struct usbdevfs_iso_packet_desc {
	unsigned int length;         /* заповнює програма: скільки просимо */
	unsigned int actual_length;  /* заповнює ядро: скільки прийшло */
	unsigned int status;         /* заповнює ядро: код для цього пакета */
};

struct usbdevfs_urb {
	unsigned char type;          /* USBDEVFS_URB_TYPE_* */
	unsigned char endpoint;      /* адреса з бітом напряму */
	int           status;        /* ← ядро: результат */
	unsigned int  flags;         /* USBDEVFS_URB_* */
	void         *buffer;
	int           buffer_length;
	int           actual_length; /* ← ядро: скільки байтів реально пройшло */
	int           start_frame;   /* iso: номер кадру */
	union {
		int          number_of_packets;  /* лише iso */
		unsigned int stream_id;          /* лише bulk streams */
	};
	int           error_count;   /* ← ядро: скільки iso-пакетів провалилося */
	unsigned int  signr;         /* сигнал по завершенні; 0 — не слати */
	void         *usercontext;   /* ядро не чіпає — це поле програми */
	struct usbdevfs_iso_packet_desc iso_frame_desc[];
};
