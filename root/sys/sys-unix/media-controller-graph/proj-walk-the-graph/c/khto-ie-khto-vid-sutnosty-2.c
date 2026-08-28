static void graph_print(struct graph *g)
{
    char node[64];

    for (__u32 i = 0; i < g->nent; i++) {
        struct media_v2_entity *e = &g->ent[i];

        if (entity_devnode(g, e->id, 0, node, sizeof node) < 0)
            strcpy(node, "—");
        printf("сутність %u: %.64s  функція 0x%08x  вузол %s\n",
               e->id, e->name, e->function, node);

        for (__u32 j = 0; j < g->npad; j++) {
            struct media_v2_pad *p = &g->pad[j];

            if (p->entity_id != e->id)
                continue;
            printf("  пад %u %s%s\n", p->index,
                   (p->flags & MEDIA_PAD_FL_SINK) ? "приймач" : "джерело",
                   (p->flags & MEDIA_PAD_FL_MUST_CONNECT) ? " (обов'язковий)" : "");

            for (__u32 k = 0; k < g->nlnk; k++) {
                struct media_v2_link *l = &g->lnk[k];
                struct media_v2_pad *s;
                struct media_v2_entity *se;

                if (!is_type(l, MEDIA_LNK_FL_DATA_LINK) || l->source_id != p->id)
                    continue;
                s = pad_by_id(g, l->sink_id);
                se = s ? ent_by_id(g, s->entity_id) : NULL;
                printf("    -> \"%.64s\":%u %s%s\n", se ? se->name : "?",
                       s ? s->index : 0,
                       (l->flags & MEDIA_LNK_FL_ENABLED) ? "[увімкнено]" : "[вимкнено]",
                       (l->flags & MEDIA_LNK_FL_IMMUTABLE) ? " [незмінний]" : "");
            }
        }
    }
}
