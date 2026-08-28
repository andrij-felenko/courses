std::array<char, 4096> buf;
for (;;) {
    ssize_t k = read(fd, buf.data(), buf.size());
    if (k > 0) {
        consume(std::span<const char>(buf.data(), static_cast<size_t>(k)));
        continue;
    }
    if (k == 0) {
        peer_closed(fd);
        break;
    }
    if (errno == EINTR) continue;
    if (errno == EAGAIN || errno == EWOULDBLOCK) break; /* єдиний вихід із циклу */
    throw std::system_error(errno, std::generic_category(), "read");
}
