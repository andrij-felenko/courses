#include <sys/uio.h>

int send_multipart_range_response(int client_socket, int file_fd, const RangeResult *res, uint64_t total_size, const char *content_type) {
    const char *boundary = "3d92f57df30dec";
    char main_hdr[512];

    int hlen = snprintf(main_hdr, sizeof(main_hdr),
        "HTTP/1.1 206 Partial Content\r\n"
        "Accept-Ranges: bytes\r\n"
        "Content-Type: multipart/byteranges; boundary=%s\r\n"
        "Connection: keep-alive\r\n\r\n", boundary);

    if (write(client_socket, main_hdr, (size_t)hlen) != hlen) return -1;

    for (size_t i = 0; i < res->count; ++i) {
        char part_hdr[512];
        uint64_t start = res->ranges[i].start;
        uint64_t end = res->ranges[i].end;
        uint64_t rlen = end - start + 1;

        int plen = snprintf(part_hdr, sizeof(part_hdr),
            "--%s\r\n"
            "Content-Type: %s\r\n"
            "Content-Range: bytes %llu-%llu/%llu\r\n\r\n",
            boundary, content_type,
            (unsigned long long)start,
            (unsigned long long)end,
            (unsigned long long)total_size);

        if (write(client_socket, part_hdr, (size_t)plen) != plen) return -1;

        off_t offset = (off_t)start;
        size_t rem = (size_t)rlen;
        while (rem > 0) {
            ssize_t s = sendfile(client_socket, file_fd, &offset, rem);
            if (s <= 0) {
                if (errno == EAGAIN || errno == EINTR) continue;
                return -1;
            }
            rem -= (size_t)s;
        }
        if (write(client_socket, "\r\n", 2) != 2) return -1;
    }

    char final_bnd[128];
    int flen = snprintf(final_bnd, sizeof(final_bnd), "--%s--\r\n", boundary);
    if (write(client_socket, final_bnd, (size_t)flen) != flen) return -1;

    return 0;
}
