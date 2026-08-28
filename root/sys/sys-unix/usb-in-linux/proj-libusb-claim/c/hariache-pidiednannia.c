static int LIBUSB_CALL on_hotplug(libusb_context *ctx, libusb_device *dev,
                                  libusb_hotplug_event ev, void *user)
{
	(void)ctx; (void)dev; (void)ev;
	/* Тут лише прапорець: ніякого відкриття й ніякого очікування. */
	*(int *)user = 1;
	return 0;                    /* 0 — лишити підписку, 1 — зняти */
}

int main(void)
{
	libusb_context *ctx = NULL;
	libusb_hotplug_callback_handle cbh;
	struct stream s = { 0 };
	int arrived = 0, rc;

	signal(SIGINT, on_sigint);

#if defined(LIBUSB_API_VERSION) && LIBUSB_API_VERSION >= 0x0100010A
	rc = libusb_init_context(&ctx, NULL, 0);   /* із 1.0.27 */
#else
	rc = libusb_init(&ctx);                    /* до 1.0.27 іншого не було */
#endif
	if (rc != 0 || !libusb_has_capability(LIBUSB_CAP_HAS_HOTPLUG))
		return 1;
	s.ctx = ctx;

	libusb_hotplug_register_callback(ctx,
		LIBUSB_HOTPLUG_EVENT_DEVICE_ARRIVED,
		LIBUSB_HOTPLUG_ENUMERATE,       /* покликати й на вже під'єднані */
		VID, PID, LIBUSB_HOTPLUG_MATCH_ANY,
		on_hotplug, &arrived, &cbh);

	while (running) {
		struct timeval tv = { 0, 200000 };
		libusb_handle_events_timeout_completed(ctx, &tv, NULL);

		if (arrived && !s.h) {
			arrived = 0;
			s.h = find_device(ctx, "A7F3");
			if (s.h && claim_iface(s.h) == 0) {
				unsigned char cmd[] = { 0x01, 0x00 }, rsp[64];
				int got = 0;

				if (ask(s.h, cmd, sizeof cmd, rsp, sizeof rsp, &got) == 0)
					printf("[i] відповідь: %d байтів\n", got);

				s.pkt = libusb_get_max_packet_size(
						libusb_get_device(s.h), EP_IN);
				if (s.pkt <= 0)
					s.pkt = 512;
				stream_start(&s);
			} else if (s.h) {
				libusb_close(s.h);
				s.h = NULL;
			}
		}

		if (s.h && !s.alive) {
			stream_stop(&s);
			if (s.stalled) {                 /* точка застрягла, плата жива */
				libusb_clear_halt(s.h, s.stalled);
				s.stalled = 0;
				stream_start(&s);
			} else {
				printf("[-] пристрій зник — закриваю дескриптор\n");
				libusb_release_interface(s.h, IFACE);
				libusb_close(s.h);
				s.h = NULL;
			}
		}
	}

	if (s.h) {
		stream_stop(&s);
		libusb_release_interface(s.h, IFACE);  /* авто-відчеплення поверне драйвер */
		libusb_close(s.h);
	}
	libusb_hotplug_deregister_callback(ctx, cbh);
	libusb_exit(ctx);
	return 0;
}
