int main(int argc, char **argv)
{
    const char *dev = argc > 1 ? argv[1] : "/dev/nvme0";
    int fd = open(dev, O_RDONLY);          /* вузол контролера, не простору імен */
    if (fd < 0) { perror(dev); return 1; }

    uint32_t sanicap;
    int rc = read_sanicap(fd, &sanicap);
    if (rc) { fprintf(stderr, "Identify не вдався: %d\n", rc); return 1; }

    if (!(sanicap & 0x2)) {
        fprintf(stderr, "блокового стирання немає (SANICAP = 0x%08x)\n", sanicap);
        return 1;
    }
    rc = sanitize_start(fd, 2 /* block erase */, 0);
    if (rc) { fprintf(stderr, "Sanitize відхилено: %d\n", rc); return 1; }

    return watch(fd) ? 1 : 0;
}
