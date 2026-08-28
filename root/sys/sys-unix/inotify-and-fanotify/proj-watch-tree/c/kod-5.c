struct todo { int parent; char name[NAME_MAX + 1]; };
static struct todo todo[TODO_MAX];
static int ntodo;

static void defer_scan(struct ctx *c, int parent, const char *name)
{
    if (ntodo == TODO_MAX) { c->rebuild = 1; return; }   /* не влазить — простіше почати спочатку */
    todo[ntodo].parent = parent;
    snprintf(todo[ntodo].name, sizeof todo[ntodo].name, "%s", name);
    ntodo++;
}

static void run_todo(struct ctx *c)
{
    for (int i = 0; i < ntodo; i++) {
        int len = path_of(todo[i].parent, c->buf, PATH_MAX);
        if (len < 0) continue;                           /* батька вже нема */
        size_t nl = strlen(todo[i].name);
        if ((size_t) len + 1 + nl >= PATH_MAX) continue;
        c->buf[len] = '/';
        memcpy(c->buf + len + 1, todo[i].name, nl + 1);
        scan(c, len + 1 + nl, todo[i].parent, todo[i].name);
    }
    ntodo = 0;
}
