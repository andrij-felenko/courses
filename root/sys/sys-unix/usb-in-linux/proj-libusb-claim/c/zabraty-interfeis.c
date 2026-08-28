static int claim_iface(libusb_device_handle *h)
{
	int rc = libusb_set_auto_detach_kernel_driver(h, 1);

	if (rc == LIBUSB_ERROR_NOT_SUPPORTED) {          /* не Linux */
		if (libusb_kernel_driver_active(h, IFACE) == 1)
			libusb_detach_kernel_driver(h, IFACE);
	}

	rc = libusb_claim_interface(h, IFACE);
	if (rc == LIBUSB_ERROR_BUSY)
		fprintf(stderr, "інтерфейс %d зайнятий: ядерний драйвер "
		        "або інший примірник цієї ж програми\n", IFACE);
	else if (rc != 0)
		fprintf(stderr, "claim: %s\n", libusb_error_name(rc));
	return rc;
}

/* Один синхронний обмін: команда → відповідь. */
static int ask(libusb_device_handle *h,
               const unsigned char *cmd, int cmd_len,
               unsigned char *rsp, int rsp_cap, int *rsp_len)
{
	int sent = 0;
	int rc = libusb_bulk_transfer(h, EP_OUT, (unsigned char *)cmd,
	                              cmd_len, &sent, 1000);
	if (rc != 0)
		return rc;
	if (sent != cmd_len)          /* половина команди гірша за жодну */
		return LIBUSB_ERROR_IO;

	return libusb_bulk_transfer(h, EP_IN, rsp, rsp_cap, rsp_len, 1000);
}
