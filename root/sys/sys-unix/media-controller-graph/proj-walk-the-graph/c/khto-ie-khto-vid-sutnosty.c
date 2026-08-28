/* Ім'я вузла за номерами: /sys/dev/char/<major>:<minor>/uevent, рядок DEVNAME. */
static int devnode_name(__u32 maj, __u32 min, char *out, size_t n)
{
    char path[64], line[256];
    FILE *f;

    snprintf(path, sizeof path, "/sys/dev/char/%u:%u/uevent", maj, min);
    if (!(f = fopen(path, "r")))
        return -1;
    while (fgets(line, sizeof line, f))
        if (!strncmp(line, "DEVNAME=", 8)) {
            line[strcspn(line, "\n")] = '\0';
            snprintf(out, n, "/dev/%s", line + 8);
            fclose(f);
            return 0;
        }
    fclose(f);
    return -1;
}

/* Сутність → її вузол. want == 0 — будь-який інтерфейс. */
static int entity_devnode(struct graph *g, __u32 ent, __u32 want, char *out, size_t n)
{
    for (__u32 i = 0; i < g->nlnk; i++) {
        struct media_v2_link *l = &g->lnk[i];
        struct media_v2_interface *it;

        if (!is_type(l, MEDIA_LNK_FL_INTERFACE_LINK) || l->sink_id != ent)
            continue;
        it = itf_by_id(g, l->source_id);
        if (it && (!want || it->intf_type == want))
            return devnode_name(it->devnode.major, it->devnode.minor, out, n);
    }
    return -1;
}

/* Зворотний бік: /dev/video0 → сутність, до якої він веде (0 — не знайшли). */
static __u32 entity_of_devnode(struct graph *g, const char *path)
{
    struct stat st;

    if (stat(path, &st) < 0 || !S_ISCHR(st.st_mode))
        return 0;
    for (__u32 i = 0; i < g->nitf; i++) {
        if (g->itf[i].devnode.major != major(st.st_rdev) ||
            g->itf[i].devnode.minor != minor(st.st_rdev))
            continue;
        for (__u32 k = 0; k < g->nlnk; k++)
            if (is_type(&g->lnk[k], MEDIA_LNK_FL_INTERFACE_LINK) &&
                g->lnk[k].source_id == g->itf[i].id)
                return g->lnk[k].sink_id;
    }
    return 0;
}
