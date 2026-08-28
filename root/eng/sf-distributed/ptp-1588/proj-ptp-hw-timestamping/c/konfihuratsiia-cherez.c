struct ptp_extts_request extts_req;
memset(&extts_req, 0, sizeof(extts_req));
extts_req.index = 0; // Номер вхідного каналу (channel 0)
extts_req.flags = PTP_ENABLE_FEATURE | PTP_RISING_EDGE;

if (ioctl(ptp_fd, PTP_EXTTS_REQUEST, &extts_req) < 0) {
    perror("PTP_EXTTS_REQUEST failed");
}

// Читання захоплених зовнішніх подій
struct ptp_extts_event event;
while (read(ptp_fd, &event, sizeof(event)) > 0) {
    printf("Зовнішня подія на піні %d: час %ld.%09ld s\n",
           event.index, event.t.sec, event.t.nsec);
}
