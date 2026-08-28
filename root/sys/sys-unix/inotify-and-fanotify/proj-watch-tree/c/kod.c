#define _GNU_SOURCE
#include <sys/inotify.h>
#include <sys/epoll.h>
#include <sys/stat.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define NBUCKET   (1u << 16)     /* 512 КіБ вказівників — вистачає на мільйон стежень */
#define MAXDEPTH  256
#define MOVE_SLOTS 64
#define TODO_MAX   4096
#define MOVE_TIMEOUT_MS 200

/* IN_ONLYDIR    — стежимо лише за каталогами; файл дасть ENOTDIR замість тихої дурниці
   IN_DONT_FOLLOW — символьне посилання не розкриваємо, інакше вийдемо з дерева
   IN_EXCL_UNLINK — не сповіщати про дітей, уже від'єднаних від каталогу */
static const uint32_t WATCH_MASK =
      IN_CREATE | IN_DELETE | IN_MOVED_FROM | IN_MOVED_TO | IN_CLOSE_WRITE
    | IN_DELETE_SELF | IN_MOVE_SELF
    | IN_ONLYDIR | IN_DONT_FOLLOW | IN_EXCL_UNLINK;

struct node {
    int wd, parent;             /* parent == -1 лише в кореня */
    char *name;                 /* базове ім'я в батькові; у кореня — увесь шлях */
    struct node *hnext;         /* ланцюжок кошика хеш-таблиці */
    struct node *child, *sib;   /* дерево: перша дитина й наступний брат */
};

struct ctx {
    int ifd, ep;
    const char *root;
    char *buf;                  /* робочий буфер шляху завдовжки PATH_MAX */
    int rebuild;                /* прапорець «картина втрачена, почати спочатку» */
};

static void *xmalloc(size_t n)
{
    void *p = malloc(n);
    if (!p) { perror("malloc"); exit(1); }
    return p;
}

static char *xstrdup(const char *s)
{
    char *p = strdup(s);
    if (!p) { perror("strdup"); exit(1); }
    return p;
}
