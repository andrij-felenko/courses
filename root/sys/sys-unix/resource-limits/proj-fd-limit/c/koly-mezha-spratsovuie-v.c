/* Резервний номер: відкриваємо заздалегідь і не використовуємо. */
static int spare = -1;

static void spare_open(void)
{
    spare = open("/dev/null", O_RDONLY | O_CLOEXEC);
}

/* Викликати, коли accept4() повернув EMFILE. Мета не в тому, щоб обслужити
   клієнта, а в тому, щоб прибрати з'єднання з черги — інакше слухач
   лишиться «готовим» назавжди. */
static void emfile_relief(int listen_fd)
{
    if (spare < 0)
        return;

    close(spare);                    /* один номер під межею звільнився */
    spare = -1;

    for (;;) {
        int c = accept4(listen_fd, NULL, NULL, SOCK_CLOEXEC);
        if (c < 0)
            break;                   /* черга спорожніла або знову EMFILE */
        close(c);                    /* клієнт бачить розрив одразу */
    }

    spare_open();                    /* резерв на місці до наступного разу */
}
