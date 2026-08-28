struct pending {
    int used;
    uint32_t cookie;
    int from_parent;        /* wd каталогу, з якого пішло */
    int moved_wd;           /* wd самого об'єкта, якщо це доглянутий каталог; інакше -1 */
    char name[NAME_MAX + 1];
    long deadline;
};
static struct pending moves[MOVE_SLOTS];

static long now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000L + ts.tv_nsec / 1000000L;
}

static void move_out(struct ctx *c, struct node *dir, const char *name,
                     int isdir, uint32_t cookie)
{
    struct node *sub = isdir ? child_of(dir->wd, name) : NULL;
    for (int i = 0; i < MOVE_SLOTS; i++) {
        if (moves[i].used) continue;
        moves[i].used = 1;
        moves[i].cookie = cookie;
        moves[i].from_parent = dir->wd;
        moves[i].moved_wd = sub ? sub->wd : -1;
        snprintf(moves[i].name, sizeof moves[i].name, "%s", name);
        moves[i].deadline = now_ms() + MOVE_TIMEOUT_MS;
        return;
    }
    c->rebuild = 1;         /* стільки незакритих переїздів — картина вже ненадійна */
}

/* Ось воно: перейменування каталогу в середині дерева — один запис у карті. */
static void reparent(struct node *n, int new_parent, const char *new_name)
{
    unlink_sib(n);
    free(n->name);
    n->name = xstrdup(new_name);
    n->parent = new_parent;
    struct node *p = map_get(new_parent);
    n->sib = p ? p->child : NULL;
    if (p) p->child = n;
}

static void move_in(struct ctx *c, struct node *dir, const char *name,
                    int isdir, uint32_t cookie)
{
    for (int i = 0; i < MOVE_SLOTS; i++) {
        if (!moves[i].used || moves[i].cookie != cookie) continue;

        char from[PATH_MAX], to[PATH_MAX];
        if (path_of(moves[i].from_parent, from, sizeof from) >= 0 &&
            path_of(dir->wd, to, sizeof to) >= 0)
            printf("> %s/%s %s/%s\n", from, moves[i].name, to, name);

        struct node *sub = map_get(moves[i].moved_wd);
        if (sub)        reparent(sub, dir->wd, name);
        else if (isdir) defer_scan(c, dir->wd, name);   /* каталог ще не був доглянутий */
        moves[i].used = 0;
        return;
    }
    emit("+", dir->wd, name);                           /* прийшло ззовні дерева */
    if (isdir) defer_scan(c, dir->wd, name);
}

static void expire_moves(struct ctx *c)
{
    long now = now_ms();
    for (int i = 0; i < MOVE_SLOTS; i++) {
        if (!moves[i].used || moves[i].deadline > now) continue;
        emit("-", moves[i].from_parent, moves[i].name); /* пішло за межі дерева */
        struct node *sub = map_get(moves[i].moved_wd);
        if (sub) unwatch_subtree(c, sub);
        moves[i].used = 0;
    }
}

static int next_timeout(void)
{
    long now = now_ms(), best = -1;
    for (int i = 0; i < MOVE_SLOTS; i++) {
        if (!moves[i].used) continue;
        long d = moves[i].deadline - now;
        if (d < 0) d = 0;
        if (best < 0 || d < best) best = d;
    }
    return best < 0 ? -1 : (int) best;
}
