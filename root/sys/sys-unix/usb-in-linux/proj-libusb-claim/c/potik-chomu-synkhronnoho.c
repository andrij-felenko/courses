struct stream {
	libusb_context         *ctx;
	libusb_device_handle   *h;
	struct libusb_transfer *ring[RING];
	int  inflight;
	int  alive;              /* 0 — пристрій зник або нас спиняють  */
	int  pkt;                /* wMaxPacketSize кінцевої точки       */
	unsigned char stalled;   /* точку треба розтикати в головному циклі */
};

static void consume(const unsigned char *data, int len)
{
	printf("[.] потік: %d байтів, перший 0x%02x\n", len, len ? data[0] : 0);
}

static void LIBUSB_CALL on_done(struct libusb_transfer *t)
{
	struct stream *s = t->user_data;

	switch (t->status) {
	case LIBUSB_TRANSFER_COMPLETED:
		consume(t->buffer, t->actual_length);   /* actual_length, не length */
		break;
	case LIBUSB_TRANSFER_TIMED_OUT:
		break;                                  /* просто нічого не було */
	case LIBUSB_TRANSFER_STALL:
		s->stalled = t->endpoint;   /* синхронних викликів тут не можна */
		s->alive = 0;
		break;
	default:                        /* NO_DEVICE, CANCELLED, ERROR… */
		s->alive = 0;
		break;
	}

	if (s->alive && libusb_submit_transfer(t) == 0)
		return;                     /* пішла в чергу знову — не чіпаємо */

	for (int i = 0; i < RING; i++)
		if (s->ring[i] == t)
			s->ring[i] = NULL;
	s->inflight--;
	libusb_free_transfer(t);        /* FREE_BUFFER звільнить і буфер */
}

static int stream_start(struct stream *s)
{
	s->alive = 1;
	for (int i = 0; i < RING; i++) {
		struct libusb_transfer *t = libusb_alloc_transfer(0);
		int len = s->pkt * 8;
		unsigned char *buf = t ? malloc(len) : NULL;

		if (!buf) {
			libusb_free_transfer(t);
			break;
		}
		libusb_fill_bulk_transfer(t, s->h, EP_IN, buf, len,
		                          on_done, s, 0);   /* 0 — без таймауту */
		t->flags = LIBUSB_TRANSFER_FREE_BUFFER;

		if (libusb_submit_transfer(t) != 0) {
			libusb_free_transfer(t);
			break;
		}
		s->ring[i] = t;
		s->inflight++;
	}
	return s->inflight;
}

static void stream_stop(struct stream *s)
{
	s->alive = 0;                  /* зворотні виклики більше не подають */
	for (int i = 0; i < RING; i++)
		if (s->ring[i])
			libusb_cancel_transfer(s->ring[i]);

	/* Скасування лише просить. Заявка жива, поки не прийшов її
	   зворотний виклик, — тож качаємо події, доки не спорожніє.  */
	while (s->inflight > 0) {
		struct timeval tv = { 1, 0 };
		if (libusb_handle_events_timeout_completed(s->ctx, &tv, NULL) < 0)
			break;
	}
}
