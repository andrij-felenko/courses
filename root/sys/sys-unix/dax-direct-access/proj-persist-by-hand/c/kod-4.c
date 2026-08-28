static uint64_t recover(struct slot *ring)
{
    uint64_t newest = 0, good = 0, broken = 0;

    for (uint32_t i = 0; i < SLOTS; i++) {
        struct slot *s = &ring[i];
        uint64_t c = s->commit;
        if (c == 0) continue;                       /* слот ніколи не фіксували */
        if ((c - 1) % SLOTS != i || s->len > sizeof s->body ||
            crc32_bitwise(s->body, s->len) != s->crc) {
            broken++;                               /* сюди падає обірваний запис */
            continue;
        }
        good++;
        if (c > newest) newest = c;
    }
    printf("цілих: %llu, відкинутих: %llu, наступний номер: %llu\n",
           (unsigned long long)good, (unsigned long long)broken,
           (unsigned long long)newest);
    return newest;
}

int main(int argc, char **argv)
{
    int fd;
    struct slot *ring = map_log(argc > 1 ? argv[1] : "/mnt/pmem/log", &fd);
    if (!ring) return 1;

    seq = recover(ring);

    char line[256];
    while (fgets(line, sizeof line, stdin))
        if (append(ring, line, (uint32_t)strlen(line)) < 0)
            perror("append");

    munmap(ring, (size_t)SLOT * SLOTS);
    close(fd);
    return 0;
}
