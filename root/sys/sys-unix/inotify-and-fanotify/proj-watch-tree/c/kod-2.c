static struct node *tab[NBUCKET];
static size_t nwatch;

static unsigned slot(int wd)
{
    return (((unsigned) wd * 2654435761u) >> 16) & (NBUCKET - 1);
}

static struct node *map_get(int wd)
{
    if (wd < 0) return NULL;
    for (struct node *n = tab[slot(wd)]; n; n = n->hnext)
        if (n->wd == wd) return n;
    return NULL;
}

static struct node *map_add(int wd, int parent, const char *name)
{
    struct node *n = xmalloc(sizeof *n);
    n->wd = wd;
    n->parent = parent;
    n->name = xstrdup(name);
    n->child = NULL;

    unsigned s = slot(wd);
    n->hnext = tab[s];
    tab[s] = n;

    struct node *p = map_get(parent);          /* у кореня — NULL */
    n->sib = p ? p->child : NULL;
    if (p) p->child = n;

    nwatch++;
    return n;
}

static void unlink_hash(struct node *n)
{
    for (struct node **pp = &tab[slot(n->wd)]; *pp; pp = &(*pp)->hnext)
        if (*pp == n) { *pp = n->hnext; return; }
}

static void unlink_sib(struct node *n)
{
    struct node *p = map_get(n->parent);
    if (!p) return;
    for (struct node **pp = &p->child; *pp; pp = &(*pp)->sib)
        if (*pp == n) { *pp = n->sib; return; }
}

static struct node *child_of(int parent_wd, const char *name)
{
    struct node *p = map_get(parent_wd);
    if (!p) return NULL;
    for (struct node *n = p->child; n; n = n->sib)
        if (strcmp(n->name, name) == 0) return n;
    return NULL;
}

/* Повний шлях будуємо на вимогу: підіймаємось до кореня, збираючи імена,
   і склеюємо їх у зворотному порядку. Жодного повного рядка ніде не лежить. */
static int path_of(int wd, char *out, size_t cap)
{
    const char *part[MAXDEPTH];
    int k = 0;
    for (int cur = wd; cur >= 0; ) {
        struct node *n = map_get(cur);
        if (!n || k == MAXDEPTH) return -1;
        part[k++] = n->name;
        cur = n->parent;
    }
    size_t len = 0;
    for (int i = k - 1; i >= 0; i--) {
        size_t nl = strlen(part[i]);
        int sep = (len > 0 && out[len - 1] != '/');
        if (len + sep + nl + 1 > cap) return -1;
        if (sep) out[len++] = '/';
        memcpy(out + len, part[i], nl);
        len += nl;
    }
    out[len] = '\0';
    return (int) len;
}

static void emit(const char *what, int dir_wd, const char *name)
{
    char path[PATH_MAX];
    int len = path_of(dir_wd, path, sizeof path);
    if (len < 0) return;                       /* каталог уже зник — нема про що казати */
    printf("%s %s%s%s\n", what, path,
           (len && path[len - 1] == '/') ? "" : "/", name);
}
