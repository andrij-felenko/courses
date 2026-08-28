void handle_http_get_request(int client_socket, const char *file_path, const char *range_hdr, const char *if_range_hdr) {
    int file_fd = open(file_path, O_RDONLY);
    if (file_fd < 0) {
        const char *not_found = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n";
        write(client_socket, not_found, strlen(not_found));
        return;
    }

    struct stat st;
    if (fstat(file_fd, &st) < 0) {
        close(file_fd);
        return;
    }
    uint64_t file_size = (uint64_t)st.st_size;
    const char *current_etag = "\"a98c7e-524\"";
    const char *last_modified = "Wed, 20 Aug 2026 10:00:00 GMT";

    /* Перевіряємо If-Range */
    bool can_use_range = validate_if_range(if_range_hdr, current_etag, last_modified);

    if (range_hdr && can_use_range) {
        RangeResult res = parse_range_header(range_hdr, file_size);
        if (res.unsatisfiable) {
            char err_buf[256];
            int len = snprintf(err_buf, sizeof(err_buf),
                "HTTP/1.1 416 Range Not Satisfiable\r\n"
                "Content-Range: bytes */%llu\r\n"
                "Content-Length: 0\r\n\r\n", (unsigned long long)file_size);
            write(client_socket, err_buf, (size_t)len);
            close(file_fd);
            return;
        }

        if (res.count == 1) {
            send_single_range_response(client_socket, file_fd, res.ranges[0].start, res.ranges[0].end, file_size);
            close(file_fd);
            return;
        } else if (res.count > 1) {
            send_multipart_range_response(client_socket, file_fd, &res, file_size, "video/mp4");
            close(file_fd);
            return;
        }
    }

    /* Fallback: віддаємо повний файл зі статусом 200 OK через sendfile */
    char full_hdr[256];
    int flen = snprintf(full_hdr, sizeof(full_hdr),
        "HTTP/1.1 200 OK\r\n"
        "Accept-Ranges: bytes\r\n"
        "ETag: %s\r\n"
        "Last-Modified: %s\r\n"
        "Content-Length: %llu\r\n"
        "Content-Type: video/mp4\r\n\r\n",
        current_etag, last_modified, (unsigned long long)file_size);
    write(client_socket, full_hdr, (size_t)flen);

    off_t offset = 0;
    size_t rem = (size_t)file_size;
    while (rem > 0) {
        ssize_t s = sendfile(client_socket, file_fd, &offset, rem);
        if (s <= 0) break;
        rem -= (size_t)s;
    }
    close(file_fd);
}
