#include <sys/sendfile.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <errno.h>

int send_single_range_response(int client_socket, int file_fd, uint64_t start, uint64_t end, uint64_t total_size) {
    char header_buf[512];
    uint64_t range_len = end - start + 1;

    int hdr_len = snprintf(header_buf, sizeof(header_buf),
        "HTTP/1.1 206 Partial Content\r\n"
        "Accept-Ranges: bytes\r\n"
        "Content-Type: video/mp4\r\n"
        "Content-Range: bytes %llu-%llu/%llu\r\n"
        "Content-Length: %llu\r\n"
        "Connection: keep-alive\r\n\r\n",
        (unsigned long long)start,
        (unsigned long long)end,
        (unsigned long long)total_size,
        (unsigned long long)range_len);

    /* Відправляємо HTTP-заголовки */
    if (write(client_socket, header_buf, (size_t)hdr_len) != hdr_len) {
        return -1;
    }

    /* Zero-copy передача корисного навантаження з диска в сокет */
    off_t offset = (off_t)start;
    size_t remaining = (size_t)range_len;

    while (remaining > 0) {
        ssize_t sent = sendfile(client_socket, file_fd, &offset, remaining);
        if (sent <= 0) {
            if (errno == EAGAIN || errno == EINTR) continue;
            return -1; /* Помилка мережі або обрив сокета клієнтом */
        }
        remaining -= (size_t)sent;
    }
    return 0;
}
