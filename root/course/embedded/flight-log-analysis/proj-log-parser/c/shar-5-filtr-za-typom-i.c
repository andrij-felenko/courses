// Накопичувач кривих ATT для графіка.
typedef struct {
    double  *t;         // час, с (з TimeUS / 1e6)
    double  *des;       // DesRoll
    double  *act;       // Roll
    size_t   n, cap;
} AttSeries;

static void series_push(AttSeries *s, double t, double des, double act) {
    if (s->n == s->cap) {                       // місця нема — подвоюємо
        s->cap = s->cap ? s->cap * 2 : 1024;
        s->t   = realloc(s->t,   s->cap * sizeof *s->t);
        s->des = realloc(s->des, s->cap * sizeof *s->des);
        s->act = realloc(s->act, s->cap * sizeof *s->act);
    }
    s->t[s->n] = t; s->des[s->n] = des; s->act[s->n] = act;
    s->n++;
}

// Дістати з одного запису ATT пару (DesRoll, Roll) і час, покласти в серію.
static void collect_att(const MsgFormat *f, const uint8_t *rec, AttSeries *s) {
    int i_t   = index_of_label(f->labels, "TimeUS");
    int i_des = index_of_label(f->labels, "DesRoll");
    int i_act = index_of_label(f->labels, "Roll");
    if (i_t < 0 || i_des < 0 || i_act < 0) return;   // не той ATT — тихо мимо

    double t_us, des, act;
    if (field_by_index(f, rec, i_t,   &t_us) &&
        field_by_index(f, rec, i_des, &des)  &&
        field_by_index(f, rec, i_act, &act))
        series_push(s, t_us / 1e6, des, act);        // мкс → с
}
