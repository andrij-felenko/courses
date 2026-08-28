static LIST_HEAD(events);
static DEFINE_MUTEX(events_lock);

static void push_event(u32 code)
{
    struct event *e = kmalloc(sizeof(*e), GFP_KERNEL);
    if (!e)
        return;
    e->code = code;

    mutex_lock(&events_lock);
    list_add_tail(&e->node, &events);
    mutex_unlock(&events_lock);
}
