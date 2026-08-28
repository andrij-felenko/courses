static const struct usb_device_id id_table[] = {
	/* будь-який інтерфейс класу Video, підклас 1 (Video Control) */
	{ USB_INTERFACE_INFO(USB_CLASS_VIDEO, 1, 0) },
	{ }   /* порожній запис — обмежувач таблиці */
};
MODULE_DEVICE_TABLE(usb, id_table);

static struct usb_driver uvc_driver = {
	.name       = "uvcvideo",
	.id_table   = id_table,
	.probe      = uvc_probe,
	.disconnect = uvc_disconnect,
};
