struct fb {                       /* буфер: пам'ять, її опис і вікно в неї */
    uint32_t handle, pitch, fb_id;
    uint64_t size;
    uint8_t *map;
};

static int fb_create(int fd, struct fb *b, uint32_t w, uint32_t h)
{
    struct drm_mode_create_dumb creq = { .width = w, .height = h, .bpp = 32 };
    if (drmIoctl(fd, DRM_IOCTL_MODE_CREATE_DUMB, &creq) < 0)
        return -errno;
    b->handle = creq.handle;
    b->pitch  = creq.pitch;
    b->size   = creq.size;

    uint32_t handles[4] = { b->handle }, pitches[4] = { b->pitch }, offsets[4] = { 0 };
    int rc = drmModeAddFB2(fd, w, h, DRM_FORMAT_XRGB8888,
                           handles, pitches, offsets, &b->fb_id, 0);
    if (rc)
        return rc;

    struct drm_mode_map_dumb mreq = { .handle = b->handle };
    if (drmIoctl(fd, DRM_IOCTL_MODE_MAP_DUMB, &mreq) < 0)
        return -errno;
    b->map = mmap(NULL, b->size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, mreq.offset);
    if (b->map == MAP_FAILED)
        return -errno;
    memset(b->map, 0, b->size);
    return 0;
}

/* Смуга їде вправо по градієнту — розрив кадру на такій картинці видно оком. */
static void draw(struct fb *b, uint32_t w, uint32_t h, int frame)
{
    uint32_t bar = (uint32_t)((frame * 8) % w);
    for (uint32_t y = 0; y < h; y++) {
        uint32_t *row = (uint32_t *)(b->map + (size_t)y * b->pitch);
        uint32_t g = y * 255 / h;
        for (uint32_t x = 0; x < w; x++) {
            uint32_t d = (x >= bar) ? x - bar : bar - x;
            row[x] = (d < 40) ? 0x00ffffff
                              : ((x * 255 / w) << 16) | (g << 8) | 0x40;
        }
    }
}
