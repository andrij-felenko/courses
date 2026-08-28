static void free_node(Node* n) {
    if (!n) return;
    int wd = n->wd;
    unlink_sib(n);
    node_map.erase(wd);
    nwatch--;
}

static void forget_rec(Node* n) {
    if (!n) return;
    for (Node *ch = n->child, *next; ch; ch = next) {
        next = ch->sib;
        forget_rec(ch);
    }
    free_node(n);
}

static void forget(Node* n) {
    forget_rec(n);
}

static void unwatch_rec(Context& c, Node* n) {
    if (!n) return;
    for (Node *ch = n->child, *next; ch; ch = next) {
        next = ch->sib;
        unwatch_rec(c, ch);
    }
    inotify_rm_watch(c.ifd, n->wd);
    free_node(n);
}

static void unwatch_subtree(Context& c, Node* n) {
    unwatch_rec(c, n);
}
