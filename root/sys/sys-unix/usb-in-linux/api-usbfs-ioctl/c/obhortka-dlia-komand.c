struct usbdevfs_setinterface {
	unsigned int interface;
	unsigned int altsetting;
};

struct usbdevfs_getdriver {
	unsigned int interface;
	char driver[256];      /* ← ядро вписує ім'я, наприклад "uvcvideo" */
};

struct usbdevfs_disconnect_claim {
	unsigned int interface;
	unsigned int flags;    /* 0 — відчіплюй будь-кого */
	char driver[256];      /* ім'я для порівняння, якщо flags не 0 */
};

#define USBDEVFS_DISCONNECT_CLAIM_IF_DRIVER      0x01  /* лише якщо драйвер — саме driver */
#define USBDEVFS_DISCONNECT_CLAIM_EXCEPT_DRIVER  0x02  /* лише якщо драйвер — НЕ driver */
