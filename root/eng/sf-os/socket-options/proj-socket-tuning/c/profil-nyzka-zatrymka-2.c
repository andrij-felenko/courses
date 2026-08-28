static const char *state_word(opt_state s)
{
    switch (s) {
        case OPT_OK:          return "ок";
        case OPT_CHANGED:     return "інше число";
        case OPT_UNSUPPORTED: return "немає на цій системі";
        default:              return "помилка";
    }
}

void sock_report_print(const sock_report *rep)
{
    if (rep->too_late)
        printf("! сокет уже з'єднаний або слухає — розміри буферів пропущено\n");
    for (int i = 0; i < rep->n; i++) {
        const opt_result *o = &rep->item[i];
        printf("%-18s просив %-8ld маю %-8ld %s",
               o->name, o->want, o->got, state_word(o->state));
        if (o->err) printf(" (%s)", strerror(o->err));
        putchar('\n');
    }
}
