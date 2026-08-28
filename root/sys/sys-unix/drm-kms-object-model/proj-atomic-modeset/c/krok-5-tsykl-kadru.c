    int front = 0;
    for (int frame = 1; frame <= 600 && !stop; frame++) {
        int back = front ^ 1;
        draw(&b[back], mode->hdisplay, mode->vdisplay, frame);

        req = drmModeAtomicAlloc();
        drmModeAtomicAddProperty(req, plane_id, p_fb, b[back].fb_id);
        rc = drmModeAtomicCommit(fd, req,
                 DRM_MODE_ATOMIC_NONBLOCK | DRM_MODE_PAGE_FLIP_EVENT, NULL);
        drmModeAtomicFree(req);
        if (rc) {
            fprintf(stderr, "кадр %d: %s\n", frame, strerror(-rc));
            break;
        }

        struct pollfd pfd = { .fd = fd, .events = POLLIN };
        if (poll(&pfd, 1, 1000) <= 0)
            break;                       /* EINTR або мовчання — виходимо */

        char buf[256];
        ssize_t n = read(fd, buf, sizeof buf);
        for (ssize_t o = 0; o + (ssize_t)sizeof(struct drm_event) <= n; ) {
            struct drm_event *ev = (struct drm_event *)(buf + o);
            if (ev->length < sizeof(struct drm_event))
                break;                   /* без цього — вічний цикл */
            if (ev->type == DRM_EVENT_FLIP_COMPLETE && frame % 60 == 0) {
                struct drm_event_vblank *fl = (struct drm_event_vblank *)ev;
                printf("кадр апаратури %u, час %u.%06u\n",
                       fl->sequence, fl->tv_sec, fl->tv_usec);
            }
            o += ev->length;
        }
        front = back;
    }

    drmModeDestroyPropertyBlob(fd, blob);
    for (int i = 0; i < 2; i++) {
        munmap(b[i].map, b[i].size);
        drmModeRmFB(fd, b[i].fb_id);
        struct drm_mode_destroy_dumb dreq = { .handle = b[i].handle };
        drmIoctl(fd, DRM_IOCTL_MODE_DESTROY_DUMB, &dreq);
    }
    drmDropMaster(fd);
    close(fd);
    return 0;
}
