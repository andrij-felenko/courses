#define PRIO_URGENT  9u
#define STAGE        8            /* навмисно мало: протитиск має лишитися в ядрі */
#define URGENT_QUOTA 4

struct order { unsigned prio; size_t len; char body[SLOT]; };
struct shelf { struct order v[STAGE]; int head, n; };

static struct shelf urgent, routine;

/* власне робота служби; тут — заглушка, яка лише показує порядок видачі */
static void execute(const struct order *o)
{
    printf("%s prio %u: %.*s\n", o->prio >= PRIO_URGENT ? "ТЕРМІНОВО" : "рутина",
           o->prio, (int)o->len, o->body);
    fflush(stdout);
}

static int shelf_put(struct shelf *s, unsigned prio, const char *body, size_t len)
{
    struct order *o;
    if (s->n == STAGE) return 0;
    o = &s->v[(s->head + s->n) % STAGE];
    if (len > sizeof o->body) len = sizeof o->body;   /* успадкована черга могла мати
                                                         слот, ширший за наш формат */
    o->prio = prio; o->len = len; memcpy(o->body, body, len);
    s->n++;
    return 1;
}

static int shelf_take(struct shelf *s, struct order *out)
{
    if (s->n == 0) return 0;
    *out = s->v[s->head];
    s->head = (s->head + 1) % STAGE;
    s->n--;
    return 1;
}

/* Читаємо, доки є місце в ОБИДВОХ полицях: ранг наступного запису наперед невідомий. */
static void drain(mqd_t q, char *buf, size_t cap)
{
    for (;;) {
        unsigned prio;
        ssize_t n;

        if (urgent.n == STAGE || routine.n == STAGE) return;

        n = mq_receive(q, buf, cap, &prio);
        if (n == -1) {
            if (errno == EINTR)  continue;
            if (errno == EAGAIN) return;                 /* у ядрі порожньо */
            perror("mq_receive"); exit(1);
        }
        shelf_put(prio >= PRIO_URGENT ? &urgent : &routine, prio, buf, (size_t)n);
    }
}

static int dispatch_one(void)
{
    static int streak = 0;
    struct order o;

    if (urgent.n && streak < URGENT_QUOTA) { shelf_take(&urgent,  &o); streak++;   }
    else if (routine.n)                    { shelf_take(&routine, &o); streak = 0; }
    else if (urgent.n)                     { shelf_take(&urgent,  &o);             }
    else return 0;

    execute(&o);
    return 1;
}
