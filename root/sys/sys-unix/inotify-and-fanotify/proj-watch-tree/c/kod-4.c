static void free_node(struct node *n)
{
    unlink_hash(n);
    free(n->name);
    free(n);
    nwatch--;
}

static void forget_rec(struct node *n)
{
    for (struct node *ch = n->child, *next; ch; ch = next) { next = ch->sib; forget_rec(ch); }
    free_node(n);
}

static void forget(struct node *n)          /* стеження вже нема в ядрі */
{
    unlink_sib(n);
    forget_rec(n);
}

static void unwatch_rec(struct ctx *c, struct node *n)
{
    for (struct node *ch = n->child, *next; ch; ch = next) { next = ch->sib; unwatch_rec(c, ch); }
    inotify_rm_watch(c->ifd, n->wd);        /* IN_IGNORED прилетить на вже забутий wd */
    free_node(n);
}

static void unwatch_subtree(struct ctx *c, struct node *n)
{
    unlink_sib(n);
    unwatch_rec(c, n);
}
