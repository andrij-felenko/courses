static int ep0, ep_out, ep_in;

static void *echo_loop(void *unused)
{
    char buf[4096];             /* кратний максимальному пакетові обох швидкостей */
    (void)unused;

    for (;;) {
        ssize_t n = read(ep_out, buf, sizeof buf);
        if (n < 0) {
            if (errno == EINTR)                     /* сигнал урвав сон */
                continue;
            if (errno == ESHUTDOWN || errno == ECONNRESET)
                continue;       /* точку вимкнули: наступний read засне до ENABLE */
            perror("read ep1");
            return NULL;
        }
        for (ssize_t off = 0; off < n; ) {
            ssize_t w = write(ep_in, buf + off, n - off);
            if (w < 0) {
                if (errno == EINTR)
                    continue;
                break;          /* обмін обірвався — назад у читання */
            }
            off += w;
        }
    }
}

static void on_event(const struct usb_functionfs_event *e)
{
    switch (e->type) {
    case FUNCTIONFS_BIND:       /* гаджет прив'язано до контролера */
    case FUNCTIONFS_UNBIND:     /* … і відв'язано: точок більше немає */
    case FUNCTIONFS_ENABLE:     /* хост вибрав конфігурацію — обмін ожив */
    case FUNCTIONFS_DISABLE:    /* точки вимкнено, заявки скасовано */
    case FUNCTIONFS_SUSPEND:
    case FUNCTIONFS_RESUME:
        break;                  /* потік обміну сам упорається зі сном і прокиданням */
    case FUNCTIONFS_SETUP:
        /* Керуючий запит нам. Відповісти треба негайно, напрям — у bRequestType.
           Нічого не вміємо, тож закриваємо стадію порожньою передачею. */
        if (e->u.setup.bRequestType & USB_DIR_IN)
            write(ep0, NULL, 0);
        else
            read(ep0, NULL, 0);
        break;
    }
}

int main(int argc, char **argv)
{
    const char *dir = argc > 1 ? argv[1] : "/dev/ffs-echo";
    char path[256];
    pthread_t th;

    snprintf(path, sizeof path, "%s/ep0", dir);
    if ((ep0 = open(path, O_RDWR)) < 0) { perror(path); return 1; }

    if (write(ep0, &descs, sizeof descs) < 0) { perror("дескриптори"); return 1; }
    if (write(ep0, &strs,  sizeof strs)  < 0) { perror("рядки");      return 1; }

    snprintf(path, sizeof path, "%s/ep1", dir);          /* точка OUT */
    if ((ep_out = open(path, O_RDWR)) < 0) { perror(path); return 1; }
    snprintf(path, sizeof path, "%s/ep2", dir);          /* точка IN */
    if ((ep_in  = open(path, O_RDWR)) < 0) { perror(path); return 1; }

    pthread_create(&th, NULL, echo_loop, NULL);

    for (;;) {
        struct usb_functionfs_event ev[8];
        ssize_t n = read(ep0, ev, sizeof ev);
        if (n < 0) {
            if (errno == EINTR)
                continue;
            perror("read ep0");
            return 1;
        }
        for (size_t i = 0; i < (size_t)n / sizeof ev[0]; i++)
            on_event(&ev[i]);
    }
}
