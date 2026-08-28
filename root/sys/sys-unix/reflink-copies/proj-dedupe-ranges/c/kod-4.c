struct dest { uint32_t f, w, run; };

static uint64_t g_asked, g_moved;
static uint64_t g_same, g_differs, g_failed;

static void send_batch(struct filerec *src, uint32_t sw,
                       struct dest *d, size_t n, uint32_t run)
{
    uint64_t len = (uint64_t)run * win;
    g_asked += len * n;

    for (size_t i = 0; i < n; i++)                     /* другий раз не пробуємо */
        for (uint32_t k = 0; k < run; k++)
            fr[d[i].f].merged[d[i].w + k] = 1;
    if (dry_run) return;

    int sfd = open(src->path, O_RDONLY);
    if (sfd < 0) { perror(src->path); return; }

    size_t nn = 0;
    for (size_t i = 0; i < n; i++) {
        const char *p = fr[d[i].f].path;
        int fd = open(p, O_RDWR);
        if (fd < 0 && errno == ETXTBSY)                /* виконуваний файл у роботі */
            fd = open(p, O_RDONLY);                    /* власникові цього досить   */
        if (fd < 0) { perror(p); continue; }
        dfd[nn] = fd;
        d[nn]   = d[i];
        nn++;
    }

    struct file_dedupe_range *req = calloc(1, pagesz);
    if (!req) { fprintf(stderr, "бракує пам'яті\n"); exit(1); }

    for (uint64_t done = 0; done < len && nn; ) {
        uint64_t part = (len - done > CHUNK) ? CHUNK : len - done;

        memset(req, 0, pagesz);
        req->src_offset = (uint64_t)sw * win + done;
        req->src_length = part;
        req->dest_count = (uint16_t)nn;
        for (size_t i = 0; i < nn; i++) {
            req->info[i].dest_fd     = dfd[i];
            req->info[i].dest_offset = (uint64_t)d[i].w * win + done;
        }

        if (ioctl(sfd, FIDEDUPERANGE, req) < 0) {
            fprintf(stderr, "%s: FIDEDUPERANGE: %s\n", src->path, strerror(errno));
            break;
        }

        for (size_t i = 0; i < nn; i++) {
            struct file_dedupe_range_info *in = &req->info[i];
            if (in->status == FILE_DEDUPE_RANGE_DIFFERS) { g_differs++; continue; }
            if (in->status < 0) {
                g_failed++;
                fprintf(stderr, "%s: %s\n", fr[d[i].f].path, strerror(-in->status));
                continue;
            }
            g_same++;
            g_moved += in->bytes_deduped;
        }
        done += part;         /* НЕ по bytes_deduped: він буває нулем — зациклимося */
    }

    free(req);
    for (size_t i = 0; i < nn; i++) close(dfd[i]);
    close(sfd);
}
