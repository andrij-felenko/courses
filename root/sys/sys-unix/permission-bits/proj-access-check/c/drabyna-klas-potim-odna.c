enum cls { OWNER, GROUP, OTHER };
static const char *cls_name[] = { "власник", "група", "решта" };

static enum cls classify(const struct stat *st, const struct ident *me)
{
    if (st->st_uid == me->fsuid)
        return OWNER;
    if (st->st_gid == me->fsgid)
        return GROUP;
    for (int i = 0; i < me->ngroups; i++)
        if (st->st_gid == me->groups[i])
            return GROUP;
    return OTHER;                      /* перше «так» уже обрало — назад не вертаємось */
}

static unsigned triple(const struct stat *st, enum cls c)
{
    unsigned m = (unsigned)st->st_mode;
    return c == OWNER ? (m >> 6) & 7u
         : c == GROUP ? (m >> 3) & 7u
                      :  m       & 7u;
}

static int decide(const struct stat *st, const struct ident *me, unsigned want,
                  enum cls *chosen, const char **rule)
{
    int over = (int)((me->capeff >> CAP_DAC_OVERRIDE)    & 1);
    int look = (int)((me->capeff >> CAP_DAC_READ_SEARCH) & 1);
    unsigned have;

    *chosen = classify(st, me);
    have = triple(st, *chosen);
    if ((want & ~have) == 0) {
        *rule = "біти класу";
        return 1;
    }

    if (S_ISDIR(st->st_mode)) {
        if (!(want & WANT_W) && look) { *rule = "CAP_DAC_READ_SEARCH"; return 1; }
        if (over)                     { *rule = "CAP_DAC_OVERRIDE";    return 1; }
        *rule = "ні бітів, ні можливості";
        return 0;
    }
    if (want == WANT_R && look) { *rule = "CAP_DAC_READ_SEARCH"; return 1; }
    if ((!(want & WANT_X) || (st->st_mode & 0111)) && over) {
        *rule = "CAP_DAC_OVERRIDE";
        return 1;
    }
    *rule = (want & WANT_X) && !(st->st_mode & 0111)
          ? "жодного біта x — тут не рятує й CAP_DAC_OVERRIDE"
          : "ні бітів, ні можливості";
    return 0;
}
