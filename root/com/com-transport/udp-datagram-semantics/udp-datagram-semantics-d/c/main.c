uint8_t buf[1500];
struct sockaddr_in from;
socklen_t flen = sizeof from;

ssize_t n = recvfrom(fd, buf, sizeof buf, MSG_TRUNC,
                     (struct sockaddr *)&from, &flen);
if (n > (ssize_t)sizeof buf) {
    // датаграма була довша за буфер — хвіст (n - sizeof buf) байтів утрачено
    stats.truncated++;
}
