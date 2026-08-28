struct cmd {
        struct dev_state *d;
        unsigned int      tag;         /* індекс у cmds[] і в бітовій мапі */
        unsigned int      stream_id;   /* tag + 1: нуль зарезервовано */
        struct urb       *data_urb;
        atomic_t          parts;       /* скільки відповідей ще чекаємо */
};

static struct cmd *tag_get(struct dev_state *d)
{
        unsigned long flags;
        struct cmd *c;
        unsigned int t;

        c = kzalloc(sizeof(*c), GFP_ATOMIC);
        if (!c)
                return NULL;

        spin_lock_irqsave(&d->lock, flags);
        t = find_first_zero_bit(d->tag_map, d->n_tags);
        if (t >= d->n_tags) {                     /* усі теги зайняті */
                spin_unlock_irqrestore(&d->lock, flags);
                kfree(c);
                return NULL;                      /* верхній шар почекає */
        }
        __set_bit(t, d->tag_map);
        c->d = d;
        c->tag = t;
        c->stream_id = t + 1;
        d->cmds[t] = c;
        spin_unlock_irqrestore(&d->lock, flags);
        return c;
}

static void tag_put(struct dev_state *d, struct cmd *c)
{
        unsigned long flags;

        spin_lock_irqsave(&d->lock, flags);
        d->cmds[c->tag] = NULL;
        __clear_bit(c->tag, d->tag_map);
        spin_unlock_irqrestore(&d->lock, flags);
        kfree(c);
}
