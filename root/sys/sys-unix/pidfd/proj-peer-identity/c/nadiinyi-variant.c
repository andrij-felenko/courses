struct peer {
    uid_t    uid;         /* знімок миті connect() — від SO_PEERCRED */
    uid_t    euid_now;    /* чинний просто зараз — від дескриптора */
    uint64_t cgroupid;    /* ідентифікатор cgroup, не шлях */
    int      alive;
};

static int probe_pidfd(int conn, struct peer *p)
{
    struct ucred uc;
    socklen_t len = sizeof uc;
    if (getsockopt(conn, SOL_SOCKET, SO_PEERCRED, &uc, &len) < 0)
        return -1;
    p->uid = uc.uid;             /* права беремо СТАНОМ НА connect() */

    int pidfd;
    len = sizeof pidfd;
    if (getsockopt(conn, SOL_SOCKET, SO_PEERPIDFD, &pidfd, &len) < 0) {
        if (errno == ESRCH || errno == EINVAL) {   /* до 6.16 було EINVAL */
            p->alive = 0;                          /* прохача вже прибрали */
            return 0;
        }
        return -1;   /* ENOPROTOOPT — ядро до 6.5; ENODATA — не той сокет */
    }

    struct pidfd_info info = { .mask = PIDFD_INFO_CREDS | PIDFD_INFO_CGROUPID };
    int rc = ioctl(pidfd, PIDFD_GET_INFO, &info);
    int e = errno;
    close(pidfd);
    if (rc < 0) {
        if (e == ESRCH) { p->alive = 0; return 0; }
        return -1;
    }

    /* Ядро віддає лише те, що вміє, і каже про це тією самою маскою. */
    if (~info.mask & (PIDFD_INFO_CREDS | PIDFD_INFO_CGROUPID))
        return -1;

    p->euid_now = info.euid;
    p->cgroupid = info.cgroupid;
    p->alive    = 1;
    return 0;
}

/* Ідентифікатор cgroup за шляхом — раз на старті, поза гарячим шляхом. */
static uint64_t cgroup_id_of(const char *path)
{
    union {
        struct file_handle fh;
        char raw[sizeof(struct file_handle) + sizeof(uint64_t)];
    } u = { .fh = { .handle_bytes = sizeof(uint64_t) } };
    int mount_id;
    uint64_t id;

    if (name_to_handle_at(AT_FDCWD, path, &u.fh, &mount_id, 0) < 0)
        return 0;
    memcpy(&id, u.fh.f_handle, sizeof id);
    return id;
}

int main(void)
{
    const uint64_t allowed = cgroup_id_of("/sys/fs/cgroup/user.slice");
    struct sockaddr_un a = { .sun_family = AF_UNIX };
    strcpy(a.sun_path, "/run/mountd.sock");
    unlink(a.sun_path);

    int srv = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (srv < 0 || bind(srv, (struct sockaddr *)&a, sizeof a) < 0
                || listen(srv, 16) < 0) {
        perror("сокет");
        return 1;
    }

    for (;;) {
        int c = accept4(srv, NULL, NULL, SOCK_CLOEXEC);
        if (c < 0) continue;

        struct peer p = { 0 };
        if (probe_pidfd(c, &p) < 0)
            dprintf(c, "тотожності не встановлено — відмова\n");
        else if (!p.alive)
            dprintf(c, "прохач уже завершився — робити нічого\n");
        else if (p.cgroupid == allowed)
            dprintf(c, "дозволено: uid=%u\n", p.uid);
        else
            dprintf(c, "відмовлено\n");
        close(c);
    }
}
