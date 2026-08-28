static void *serve(void *arg)
{
    int fd = (int)(intptr_t)arg;
    char *body = malloc(MAX_BODY);

    if (body != NULL) {
        for (;;) {
            uint32_t hdr;
            if (read_full(fd, &hdr, 4) != 1) break;

            uint32_t len = ntohl(hdr);
            if (len > MAX_BODY) break;

            if (read_full(fd, body, len) != 1) break;
            if (write_full(fd, &hdr, 4) != 1) break;
            if (write_full(fd, body, len) != 1) break;
        }
    }

    free(body);
    close(fd);
    return NULL;
}
