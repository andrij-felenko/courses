static struct media_v2_entity *ent_by_id(struct graph *g, __u32 id)
{
    for (__u32 i = 0; i < g->nent; i++) if (g->ent[i].id == id) return &g->ent[i];
    return NULL;
}

static struct media_v2_pad *pad_by_id(struct graph *g, __u32 id)
{
    for (__u32 i = 0; i < g->npad; i++) if (g->pad[i].id == id) return &g->pad[i];
    return NULL;
}

static struct media_v2_interface *itf_by_id(struct graph *g, __u32 id)
{
    for (__u32 i = 0; i < g->nitf; i++) if (g->itf[i].id == id) return &g->itf[i];
    return NULL;
}

static int is_type(const struct media_v2_link *l, __u32 type)
{
    return (l->flags & MEDIA_LNK_FL_LINK_TYPE) == type;
}
