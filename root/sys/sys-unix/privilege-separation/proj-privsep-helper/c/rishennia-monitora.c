static int streq_ct(const char *a, const char *b)      /* без витоку по часу */
{
    size_t la = strlen(a), lb = strlen(b);
    unsigned diff = (unsigned)(la ^ lb);
    for (size_t i = 0; i < la && i < lb; i++)
        diff |= (unsigned)((unsigned char)a[i] ^ (unsigned char)b[i]);
    return diff == 0;
}

static int pick_user(const struct req *rq, char *user, uid_t *uid, gid_t *gid)
{
    if (user[0] != '\0') return 1;                     /* ім'я беруть ОДИН раз */
    if (rq->user_len == 0 || rq->user_len >= MAX_USER) return 0;
    for (uint32_t i = 0; i < rq->user_len; i++) {
        char c = rq->user[i];
        if (!((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_' || c == '-'))
            return 0;
    }
    memcpy(user, rq->user, rq->user_len);
    user[rq->user_len] = '\0';

    struct passwd *pw = getpwnam(user);                /* база — своя, не з повідомлення */
    if (!pw || pw->pw_uid == 0) { user[0] = '\0'; return 0; }   /* root крізь канал — ніколи */
    *uid = pw->pw_uid; *gid = pw->pw_gid;
    return 1;
}

static int check_password(const char *user, const char *pw, uint32_t len)
{
    if (len == 0 || len > MAX_PW) return 0;
    char attempt[MAX_PW + 1];
    memcpy(attempt, pw, len);
    attempt[len] = '\0';

    struct spwd *sp = getspnam(user);                  /* перший дотик до таємниці */
    int ok = 0;
    if (sp && sp->sp_pwdp) {
        char *got = crypt(attempt, sp->sp_pwdp);
        ok = got && streq_ct(got, sp->sp_pwdp);
    }
    explicit_bzero(attempt, sizeof attempt);
    return ok;                                         /* назовні йде рівно один біт */
}

static int open_session_log(uid_t uid)
{
    char path[64];
    snprintf(path, sizeof path, "/var/log/privsepd/%lu.log", (unsigned long)uid);
    return open(path, O_WRONLY | O_APPEND | O_CREAT | O_NOFOLLOW | O_CLOEXEC, 0600);
}
