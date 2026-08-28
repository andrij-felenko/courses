#define _GNU_SOURCE
#include <sys/types.h>
#include <unistd.h>
#include <grp.h>

/* Незворотний перехід у чужу ідентичність. 0 — вдалося, -1 — ні. */
static int drop_forever(uid_t uid, gid_t gid)
{
    /* 1. Додаткові групи — першими: прибирати їх дозволено лише привілейованому. */
    if (setgroups(1, &gid) != 0)
        return -1;

    /* 2. Усі три групові числа одразу, інакше egid можна підняти зі збереженого. */
    if (setresgid(gid, gid, gid) != 0)
        return -1;

    /* 3. Аж тепер користувач: після цього кроку привілеїв уже не буде. */
    if (setresuid(uid, uid, uid) != 0)
        return -1;

    /* 4. Звірка: жоден із викликів вище не зобов'язаний був
          зробити рівно те, що ми просили. */
    uid_t r, e, s;
    gid_t rg, eg, sg;
    if (getresuid(&r, &e, &s) != 0 || getresgid(&rg, &eg, &sg) != 0)
        return -1;
    if (r != uid || e != uid || s != uid)    return -1;
    if (rg != gid || eg != gid || sg != gid) return -1;

    /* 5. І окремо — що зайвих груп справді не лишилося. */
    gid_t list[2];
    int n = getgroups(2, list);
    if (n < 0 || n > 1 || (n == 1 && list[0] != gid))
        return -1;

    return 0;
}
