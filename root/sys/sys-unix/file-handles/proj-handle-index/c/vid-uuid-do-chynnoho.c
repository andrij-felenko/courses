struct mnt { int id; char uuid[64]; char point[PATH_MAX]; };
static struct mnt mtab[256];
static int mtab_n;

static void uuid_lookup(dev_t sb_dev, const char *source, char *out, size_t n)
{
    char link[PATH_MAX], real_src[PATH_MAX], real_lnk[PATH_MAX];
    struct dirent *e;
    struct stat st;
    DIR *d;

    snprintf(out, n, "-");                       /* «UUID невідомий» */
    if (!(d = opendir("/dev/disk/by-uuid")))
        return;
    if (!realpath(source, real_src))
        real_src[0] = '\0';
    while ((e = readdir(d))) {
        if (e->d_name[0] == '.')
            continue;
        snprintf(link, sizeof link, "/dev/disk/by-uuid/%s", e->d_name);
        if (stat(link, &st) < 0)
            continue;
        /* ext4, XFS та інші однодискові: номер пристрою в mountinfo справжній */
        if (major(sb_dev) && st.st_rdev == sb_dev) {
            snprintf(out, n, "%s", e->d_name);
            break;
        }
        /* Btrfs і подібні беруть анонімний номер (major 0) —
           там лишається звіряти самі шляхи до пристрою */
        if (real_src[0] && realpath(link, real_lnk) && !strcmp(real_lnk, real_src)) {
            snprintf(out, n, "%s", e->d_name);
            break;
        }
    }
    closedir(d);
}

static void load_mounts(void)
{
    char line[8192], point[PATH_MAX], source[PATH_MAX], *sep;
    FILE *f = fopen("/proc/self/mountinfo", "r");
    int id, maj, min;

    if (!f) {
        perror("mountinfo");
        exit(1);
    }
    /* поля: 1 id · 2 батько · 3 major:minor · 4 корінь ФС · 5 точка монтування,
       далі змінне число полів, роздільник " - ", по ньому тип і джерело */
    while (mtab_n < 256 && fgets(line, sizeof line, f)) {
        if (sscanf(line, "%d %*d %d:%d %*s %4095s", &id, &maj, &min, point) != 4)
            continue;
        if (!(sep = strstr(line, " - ")))
            continue;
        if (sscanf(sep + 3, "%*s %4095s", source) != 1)
            continue;
        mtab[mtab_n].id = id;
        snprintf(mtab[mtab_n].point, PATH_MAX, "%s", point);
        uuid_lookup(makedev(maj, min), source, mtab[mtab_n].uuid, 64);
        mtab_n++;
    }
    fclose(f);
}

static const char *uuid_of_mount(int id)
{
    for (int i = 0; i < mtab_n; i++)
        if (mtab[i].id == id)
            return mtab[i].uuid;
    return "-";
}

static int open_mount_by_uuid(const char *uuid)
{
    for (int i = 0; i < mtab_n; i++)
        if (!strcmp(mtab[i].uuid, uuid))
            return open(mtab[i].point, O_RDONLY | O_DIRECTORY);
    return -1;
}
