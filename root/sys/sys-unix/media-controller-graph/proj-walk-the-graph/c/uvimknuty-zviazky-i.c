static struct media_v2_link *data_link(struct graph *g, __u32 src, __u32 sink)
{
    for (__u32 i = 0; i < g->nlnk; i++)
        if (is_type(&g->lnk[i], MEDIA_LNK_FL_DATA_LINK) &&
            g->lnk[i].source_id == src && g->lnk[i].sink_id == sink)
            return &g->lnk[i];
    return NULL;
}

static int enable_path(int mfd, struct graph *g, const int *path, int n)
{
    for (int i = 0; i + 1 < n; i++) {
        struct media_v2_pad *a = &g->pad[path[i]], *b = &g->pad[path[i + 1]];
        struct media_v2_link *l;
        struct media_link_desc d;

        if (a->entity_id == b->entity_id)
            continue;                            /* перехід усередині сутности */
        l = data_link(g, a->id, b->id);
        if (!l || (l->flags & MEDIA_LNK_FL_ENABLED))
            continue;

        memset(&d, 0, sizeof d);
        d.source.entity = a->entity_id; d.source.index = a->index;
        d.source.flags  = MEDIA_PAD_FL_SOURCE;
        d.sink.entity   = b->entity_id; d.sink.index   = b->index;
        d.sink.flags    = MEDIA_PAD_FL_SINK;
        d.flags         = MEDIA_LNK_FL_ENABLED;

        if (xioctl(mfd, MEDIA_IOC_SETUP_LINK, &d) < 0) {
            fprintf(stderr, "SETUP_LINK %u:%u -> %u:%u: %s\n", a->entity_id,
                    a->index, b->entity_id, b->index, strerror(errno));
            return -1;
        }
    }
    return 0;
}
