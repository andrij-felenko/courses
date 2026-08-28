static void report_range(int fd, unsigned lr, const char *pw)
{
        static const char *state[8] = { [OPAL_RO] = "лише читання",
                                        [OPAL_RW] = "відкрито",
                                        [OPAL_LK] = "замкнено" };
        struct opal_lr_status s = { 0 };
        size_t pwlen = strlen(pw);

        if (pwlen >= OPAL_KEY_MAX)   /* key_len — один байт, тож не більше 255 */
                return;
        s.session.who = OPAL_ADMIN1;          /* sum = 0 — не режим одного користувача */
        s.session.opal_key.lr = lr;           /* саме тут номер діапазону */
        s.session.opal_key.key_len = (unsigned char)pwlen;
        memcpy(s.session.opal_key.key, pw, pwlen);

        if (ioctl(fd, IOC_OPAL_GET_LR_STATUS, &s) < 0) {
                printf("  діапазон %u: %s\n", lr, strerror(errno));
                return;
        }
        printf("  діапазон %u: LBA %" PRIu64 " + %" PRIu64 ", замикання читання=%u запису=%u, %s\n",
               lr, s.range_start, s.range_length, s.RLE, s.WLE,
               s.l_state < 8 && state[s.l_state] ? state[s.l_state] : "?");
}

int main(int argc, char **argv)
{
        if (argc < 2) {
                fprintf(stderr, "вжиток: %s /dev/nvme0n1 [пароль-адміна]\n", argv[0]);
                return 2;
        }
        int fd = open(argv[1], O_RDONLY | O_CLOEXEC);
        if (fd < 0) {
                perror(argv[1]);
                return 1;
        }
        report_status(fd);
        report_discovery(fd);
        if (argc > 2)
                for (unsigned lr = 0; lr < OPAL_MAX_LRS; lr++)
                        report_range(fd, lr, argv[2]);
        close(fd);
        return 0;
}
