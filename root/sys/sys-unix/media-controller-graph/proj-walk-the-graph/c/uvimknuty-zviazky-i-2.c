static int set_fmt_along(struct graph *g, const int *path, int n,
                         struct v4l2_mbus_framefmt *fmt)
{
    for (int i = 0; i < n; i++) {
        struct media_v2_pad *p = &g->pad[path[i]];
        struct v4l2_subdev_format sf;
        char node[64];
        int fd;

        if (entity_devnode(g, p->entity_id, MEDIA_INTF_T_V4L_SUBDEV,
                           node, sizeof node) < 0)
            continue;                        /* відеовузол — не субпристрій, його потім */
        if ((fd = open(node, O_RDWR)) < 0) {
            perror(node);
            return -1;
        }

        memset(&sf, 0, sizeof sf);
        sf.pad = p->index;
        sf.format = *fmt;
        sf.which = V4L2_SUBDEV_FORMAT_TRY;
        if (xioctl(fd, VIDIOC_SUBDEV_S_FMT, &sf) < 0)
            sf.format = *fmt;                /* TRY не всі підтримують — ставимо як є */

        sf.which = V4L2_SUBDEV_FORMAT_ACTIVE;
        if (xioctl(fd, VIDIOC_SUBDEV_S_FMT, &sf) < 0) {
            fprintf(stderr, "%s пад %u: %s\n", node, p->index, strerror(errno));
            close(fd);
            return -1;
        }
        *fmt = sf.format;                    /* далі несемо погоджене драйвером */
        printf("%s пад %u: %ux%u code 0x%04x\n", node, p->index,
               fmt->width, fmt->height, fmt->code);
        close(fd);
    }
    return 0;
}
