#define FUSE_USE_VERSION 31

#include <fuse.h>

#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#define SQUARES  12          /* скільки файлів у каталозі squares/ */
#define MAXBODY  256         /* найдовший можливий вміст, із запасом */

static const char HELLO[] = "Привіт із простору користувача!\n";

enum { C_GETATTR, C_READDIR, C_OPEN, C_READ, C_LAST };

static pthread_mutex_t g_lock = PTHREAD_MUTEX_INITIALIZER;
static unsigned long   g_calls[C_LAST];   /* під g_lock */
static time_t          g_born;            /* мить запуску демона */

static void tick(int which)
{
    pthread_mutex_lock(&g_lock);
    g_calls[which]++;
    pthread_mutex_unlock(&g_lock);
}

/* ─── вміст ──────────────────────────────────────────────────────────────
   Одна функція малює вміст будь-якого файлу. Нею користується і read()
   (щоб віддати байти), і getattr() (щоб дізнатися st_size) — інакше
   оголошений розмір і справжній вміст рано чи пізно розійдуться.         */

/* «/squares/N» → N, якщо N у межах; інакше 0 */
static int square_of(const char *path)
{
    char *end;
    long  n;

    if (strncmp(path, "/squares/", 9) != 0)
        return 0;
    n = strtol(path + 9, &end, 10);
    if (end == path + 9 || *end != '\0' || n < 1 || n > SQUARES)
        return 0;
    return (int)n;
}

/* Повертає довжину вмісту в байтах або -ENOENT, якщо такого файлу немає. */
static int render(const char *path, char *body)
{
    int n = square_of(path);

    if (n != 0)
        return snprintf(body, MAXBODY, "%d · %d = %d\n", n, n, n * n);

    if (strcmp(path, "/hello") == 0)
        return snprintf(body, MAXBODY, "%s", HELLO);

    if (strcmp(path, "/now") == 0) {
        struct timespec ts;
        struct tm       tm;
        char            stamp[32];

        clock_gettime(CLOCK_REALTIME, &ts);
        localtime_r(&ts.tv_sec, &tm);
        strftime(stamp, sizeof stamp, "%Y-%m-%d %H:%M:%S", &tm);
        return snprintf(body, MAXBODY, "%s.%03ld\n", stamp,
                        ts.tv_nsec / 1000000);
    }

    if (strcmp(path, "/stats") == 0) {
        unsigned long c[C_LAST];

        pthread_mutex_lock(&g_lock);
        memcpy(c, g_calls, sizeof c);
        pthread_mutex_unlock(&g_lock);
        return snprintf(body, MAXBODY,
                        "getattr %lu\nreaddir %lu\nopen    %lu\nread    %lu\n",
                        c[C_GETATTR], c[C_READDIR], c[C_OPEN], c[C_READ]);
    }

    return -ENOENT;
}

/* Файли, довжина яких міняється сама собою, поки ніхто не дивиться. */
static int is_volatile(const char *path)
{
    return strcmp(path, "/now") == 0 || strcmp(path, "/stats") == 0;
}

/* ─── операції ─────────────────────────────────────────────────────────── */

static int gen_getattr(const char *path, struct stat *st,
                       struct fuse_file_info *fi)
{
    char body[MAXBODY];
    int  len;

    (void)fi;
    tick(C_GETATTR);

    memset(st, 0, sizeof *st);
    st->st_uid = getuid();
    st->st_gid = getgid();
    /* Сталому вмісту — сталий час зміни: тоді ядро має право тримати кеш.
       Мінливому — свіжий: це для ядра сигнал, що вміст оновився.          */
    st->st_atime = st->st_mtime = st->st_ctime =
        is_volatile(path) ? time(NULL) : g_born;

    if (strcmp(path, "/") == 0) {
        st->st_mode  = S_IFDIR | 0555;
        st->st_nlink = 3;      /* «.», запис у батьках і «squares/..» */
        return 0;
    }
    if (strcmp(path, "/squares") == 0) {
        st->st_mode  = S_IFDIR | 0555;
        st->st_nlink = 2;      /* підкаталогів немає */
        return 0;
    }

    len = render(path, body);
    if (len < 0)
        return len;            /* саме -ENOENT, зі знаком мінус */

    st->st_mode  = S_IFREG | 0444;
    st->st_nlink = 1;
    st->st_size  = len;
    return 0;
}

/* Один запис у відповідь на readdir. Коли ядро просило READDIRPLUS,
   віддаємо повні атрибути; коли ні — воно однаково візьме з цієї
   структури тип файлу, і цього досить, щоб «ls» не питав окремо
   про кожне ім'я.                                                        */
static void put(void *buf, fuse_fill_dir_t filler, int plus,
                const char *name, const char *full)
{
    struct stat st;

    if (gen_getattr(full, &st, NULL) != 0)
        return;
    filler(buf, name, &st, 0,
           plus ? FUSE_FILL_DIR_PLUS : FUSE_FILL_DIR_DEFAULTS);
}

static int gen_readdir(const char *path, void *buf, fuse_fill_dir_t filler,
                       off_t offset, struct fuse_file_info *fi,
                       enum fuse_readdir_flags flags)
{
    int  plus = (flags & FUSE_READDIR_PLUS) != 0;
    char name[16], full[64];
    int  i;

    (void)offset;
    (void)fi;
    tick(C_READDIR);

    filler(buf, ".",  NULL, 0, FUSE_FILL_DIR_DEFAULTS);
    filler(buf, "..", NULL, 0, FUSE_FILL_DIR_DEFAULTS);

    if (strcmp(path, "/") == 0) {
        put(buf, filler, plus, "hello",   "/hello");
        put(buf, filler, plus, "now",     "/now");
        put(buf, filler, plus, "stats",   "/stats");
        put(buf, filler, plus, "squares", "/squares");
        return 0;
    }
    if (strcmp(path, "/squares") == 0) {
        for (i = 1; i <= SQUARES; i++) {
            snprintf(name, sizeof name, "%d", i);
            snprintf(full, sizeof full, "/squares/%d", i);
            put(buf, filler, plus, name, full);
        }
        return 0;
    }
    return -ENOENT;
}

static int gen_open(const char *path, struct fuse_file_info *fi)
{
    char body[MAXBODY];

    tick(C_OPEN);

    if (render(path, body) < 0)
        return -ENOENT;
    if ((fi->flags & O_ACCMODE) != O_RDONLY)
        return -EACCES;
    /* Довжину цих файлів наперед не пообіцяєш — хай ядро не кешує їх
       і не обрізає читання за оголошеним розміром.                       */
    if (is_volatile(path))
        fi->direct_io = 1;
    return 0;
}

static int gen_read(const char *path, char *buf, size_t size, off_t offset,
                    struct fuse_file_info *fi)
{
    char body[MAXBODY];
    int  len;

    (void)fi;
    tick(C_READ);

    len = render(path, body);
    if (len < 0)
        return len;

    if (offset >= (off_t)len)
        return 0;                        /* кінець файлу */
    if ((off_t)size > len - offset)
        size = (size_t)(len - offset);

    memcpy(buf, body + offset, size);
    return (int)size;
}

static const struct fuse_operations gen_ops = {
    .getattr = gen_getattr,
    .readdir = gen_readdir,
    .open    = gen_open,
    .read    = gen_read,
};

int main(int argc, char *argv[])
{
    g_born = time(NULL);
    return fuse_main(argc, argv, &gen_ops, NULL);
}
