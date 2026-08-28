struct usbdevfs_ctrltransfer {
	__u8  bRequestType;   /* напрям + тип + отримувач, як у SETUP-пакеті */
	__u8  bRequest;
	__u16 wValue;
	__u16 wIndex;
	__u16 wLength;        /* скільки байтів у data */
	__u32 timeout;        /* мілісекунди; 0 — чекати вічно */
	void *data;           /* буфер у просторі користувача */
};

struct usbdevfs_bulktransfer {
	unsigned int ep;      /* адреса кінцевої точки з бітом напряму */
	unsigned int len;
	unsigned int timeout; /* мілісекунди; 0 — чекати вічно */
	void *data;
};
