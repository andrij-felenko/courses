/* svcctl — рівно ті дії, що дозволені операторові, і жодної іншої.
   Збірка:    cc -O2 -Wall -Wextra -o svcctl svcctl.c
   Установка: root:root, 0755, у каталозі, куди ніхто, крім root, не пише.
   Біт setuid НЕ ставимо: права дає правило в sudoers.  */

#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <syslog.h>
#include <unistd.h>

#define EXIT_REFUSED  2     /* відмовили ми самі */
#define EXIT_NOEXEC 127     /* не змогли запустити ціль */

/* Увесь словник дозволеного. Ліворуч — слово, яке називає прохач;
   праворуч — готовий рядок, жодного байта якого він не складав.
   --no-pager тут не окраса: без нього systemctl віддасть вивід
   переглядачеві, а з переглядача набирається !sh — уже від root.  */
struct action {
    const char *word;
    const char *argv[6];            /* завершується NULL */
};

static const struct action TABLE[] = {
    { "web-restart", { "systemctl", "--no-pager", "restart", "nginx.service", NULL } },
    { "web-stop",    { "systemctl", "--no-pager", "stop",    "nginx.service", NULL } },
    { "web-status",  { "systemctl", "--no-pager", "status",  "nginx.service", NULL } },
};

/* Оточення дитини — повний перелік, а не залишок після чистки. */
static char *const CHILD_ENV[] = {
    "PATH=/usr/sbin:/usr/bin:/sbin:/bin",
    "LC_ALL=C",
    "SYSTEMD_PAGER=",
    NULL
};

/* Дескриптори 0, 1 і 2 мусять бути відкриті ЩЕ ДО першого open():
   якщо прохач закрив stdout, перший же відкритий нами файл дістане
   номер 1 — і все, що програма надрукує, поллється в цей файл.  */
static void fix_std_fds(void)
{
    for (int fd = 0; fd <= 2; fd++)
        if (fcntl(fd, F_GETFD) == -1 && open("/dev/null", O_RDWR) != fd)
            _exit(EXIT_NOEXEC);
}

int main(int argc, char **argv)
{
    /* Порожній argv (argc == 0) відсікається саме тут, ДО того як
       щось звернеться до argv[i]. І в підказці немає argv[0]: це
       текст від прохача, і друкувати його ми не зобов'язані.  */
    if (argc != 2) {
        fputs("usage: svcctl <web-restart|web-stop|web-status>\n", stderr);
        return EXIT_REFUSED;
    }

    fix_std_fds();
    close_range(3, ~0U, 0);   /* Linux 5.9+, обгортка в glibc з 2.34 */

    const struct action *act = NULL;
    for (size_t i = 0; i < sizeof TABLE / sizeof *TABLE; i++)
        if (strcmp(argv[1], TABLE[i].word) == 0) { act = &TABLE[i]; break; }

    if (act == NULL) {
        fputs("svcctl: невідома дія\n", stderr);
        return EXIT_REFUSED;
    }

    /* Хто просив — лише з SUDO_UID: усі три ідентифікатори нашого
       процесу вже цільові, справжнього прохача в них не лишилося.
       Це підказка читачеві журналу, а не доказ: доказ пише sudo.  */
    const char *who = getenv("SUDO_UID");
    openlog("svcctl", LOG_PID, LOG_AUTHPRIV);
    syslog(LOG_NOTICE, "action=%s sudo_uid=%s", act->word, who ? who : "?");

    closelog();               /* сокет журналу відкрився ПІСЛЯ close_range */
    execve("/usr/bin/systemctl", (char *const *)act->argv, CHILD_ENV);

    /* Сюди потрапляємо, лише якщо exec не стався. */
    fprintf(stderr, "svcctl: execve: %s\n", strerror(errno));
    return EXIT_NOEXEC;
}
