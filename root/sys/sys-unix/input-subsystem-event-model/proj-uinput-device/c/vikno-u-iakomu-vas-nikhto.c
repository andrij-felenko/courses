static void wait_for_node(int ui)
{
        char sysname[32] = { 0 }, path[64], node[64] = { 0 };
        struct dirent *e;
        DIR *d;

        if (ioctl(ui, UI_GET_SYSNAME(sizeof sysname), sysname) < 0)
                return;                       /* старе ядро — лишиться сама пауза */

        snprintf(path, sizeof path, "/sys/class/input/%s", sysname);
        if ((d = opendir(path))) {
                while ((e = readdir(d)))
                        if (!strncmp(e->d_name, "event", 5)) {
                                snprintf(node, sizeof node, "/dev/input/%s", e->d_name);
                                break;
                        }
                closedir(d);
        }
        for (int i = 0; i < 300 && node[0]; i++) {      /* до 3 с на udev */
                if (access(node, F_OK) == 0) break;
                usleep(10 * 1000);
        }
}
