ptp_extts_request extts_req{};
extts_req.index = 0;
extts_req.flags = PTP_ENABLE_FEATURE | PTP_RISING_EDGE;

if (::ioctl(ptp_fd, PTP_EXTTS_REQUEST, &extts_req) < 0) {
    std::perror("PTP_EXTTS_REQUEST failed");
}

ptp_extts_event event{};
while (::read(ptp_fd, &event, sizeof(event)) > 0) {
    std::cout << "Зовнішня подія на піні " << event.index
              << ": час " << event.t.sec << "." << event.t.nsec << " s\n";
}
