int main(int argc, char **argv)
{
    const char *mdev  = argc > 1 ? argv[1] : "/dev/media0";
    const char *video = argc > 2 ? argv[2] : "/dev/video0";
    struct media_device_info info;
    struct v4l2_mbus_framefmt fmt;
    struct graph g;
    __u32 sensor = 0, sink;
    int mfd, n, *path;

    memset(&g, 0, sizeof g);
    if ((mfd = open(mdev, O_RDWR)) < 0) { perror(mdev); return 1; }

    memset(&info, 0, sizeof info);
    if (xioctl(mfd, MEDIA_IOC_DEVICE_INFO, &info) < 0) { perror("DEVICE_INFO"); return 1; }
    if (!MEDIA_V2_PAD_HAS_INDEX(info.media_version)) {
        fprintf(stderr, "ядро старіше за 4.19: у падах немає index\n");
        return 1;
    }
    if (graph_read(mfd, &g) < 0) { perror("G_TOPOLOGY"); return 1; }
    graph_print(&g);

    for (__u32 i = 0; i < g.nent; i++)
        if (g.ent[i].function == MEDIA_ENT_F_CAM_SENSOR) { sensor = g.ent[i].id; break; }
    sink = entity_of_devnode(&g, video);
    if (!sensor || !sink) { fprintf(stderr, "не знайшов кінців тракту\n"); return 1; }

    path = xcalloc(g.npad, sizeof *path);
    n = find_path(&g, sensor, sink, path);
    if (!n) { fprintf(stderr, "дороги від сенсора до %s у графі немає\n", video); return 1; }
    if (enable_path(mfd, &g, path, n) < 0) return 1;

    memset(&fmt, 0, sizeof fmt);
    fmt.width  = argc > 3 ? strtoul(argv[3], NULL, 0) : 1920;
    fmt.height = argc > 4 ? strtoul(argv[4], NULL, 0) : 1080;
    fmt.code   = MEDIA_BUS_FMT_SGRBG10_1X10;
    fmt.field  = V4L2_FIELD_NONE;
    return set_fmt_along(&g, path, n, &fmt) < 0;
}
