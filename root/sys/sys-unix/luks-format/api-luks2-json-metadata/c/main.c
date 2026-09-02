/* luks2dump — читає обидві копії метаданих LUKS2, обирає чинну за seqid
 * і проганяє документ JSON через перевірки §11.
 *
 * Збірка:
 *   cc -std=c11 -Wall -Wextra -O2 -o luks2dump main.c luks2_hdr.c luks2_json.c \
 *      -lcrypto -ljson-c
 * Запуск (треба право читати сирий пристрій):
 *   sudo ./luks2dump /dev/nvme0n1p3
 *   ./luks2dump luks2_header_backup.img
 */
#include "luks2_hdr.h"
#include "luks2_json.h"

#include <fcntl.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

static void print_hdr(const char *name, const struct luks2_hdr *h)
{
    printf("%s: seqid=%" PRIu64 " hdr_size=%" PRIu64 " (%" PRIu64 " КіБ) csum_alg=%s\n",
           name, h->seqid, h->hdr_size, h->hdr_size / 1024, h->csum_alg);
    printf("    uuid=%s label=\"%s\" subsystem=\"%s\"\n",
           h->uuid, h->label, h->subsystem);
    printf("    json: %zu із %zu байтів, хвіст занулено\n", h->json_len, h->json_size);
}

/* Коли первинна копія читається, вторинна лежить рівно за hdr_size.
   Коли ні — доводиться перебирати стандартні зсуви. */
static int read_secondary(int fd, const struct luks2_hdr *primary,
                          struct luks2_hdr *out, uint64_t *at)
{
    size_t i;
    int rc;

    if (primary != NULL) {
        *at = primary->hdr_size;
        return luks2_hdr_read(fd, primary->hdr_size, out);
    }
    for (i = 0; i < luks2_hdr_offsets_count; i++) {
        rc = luks2_hdr_read(fd, luks2_hdr_offsets[i], out);
        if (rc == LUKS2_OK) {
            *at = luks2_hdr_offsets[i];
            return rc;
        }
    }
    *at = 0;
    return LUKS2_E_MAGIC;
}

int main(int argc, char **argv)
{
    struct luks2_hdr pri, sec;
    struct luks2_json_report rep;
    const struct luks2_hdr *use;
    uint64_t sec_at = 0;
    int rc_pri, rc_sec, fd, exit_code;

    if (argc != 2) {
        fprintf(stderr, "вжиток: %s <пристрій|образ заголовка>\n", argv[0]);
        return 2;
    }

    fd = open(argv[1], O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        perror(argv[1]);
        return 1;
    }

    rc_pri = luks2_hdr_read(fd, 0, &pri);
    rc_sec = read_secondary(fd, rc_pri == LUKS2_OK ? &pri : NULL, &sec, &sec_at);

    if (rc_pri == LUKS2_OK)
        print_hdr("первинний (зсув 0)", &pri);
    else
        printf("первинний (зсув 0): %s\n", luks2_strerror(rc_pri));

    if (rc_sec == LUKS2_OK) {
        char name[64];
        snprintf(name, sizeof(name), "вторинний (зсув %" PRIu64 ")", sec.at_offset);
        print_hdr(name, &sec);
    } else {
        printf("вторинний (зсув %" PRIu64 "): %s\n", sec_at, luks2_strerror(rc_sec));
    }

    /* Арбітраж: перемагає валідна копія з більшим seqid. */
    if (rc_pri == LUKS2_OK && rc_sec == LUKS2_OK) {
        use = (sec.seqid > pri.seqid) ? &sec : &pri;
        if (pri.seqid != sec.seqid)
            printf("\nseqid копій розбігся (%" PRIu64 " проти %" PRIu64
                   ") — том просить cryptsetup repair\n", pri.seqid, sec.seqid);
        if (strcmp(pri.uuid, sec.uuid) != 0)
            printf("UUID копій різні — у вікні заголовка лежать два різні томи\n");
    } else if (rc_pri == LUKS2_OK) {
        use = &pri;
        printf("\nпрацюємо на первинній копії: вторинна непридатна\n");
    } else if (rc_sec == LUKS2_OK) {
        use = &sec;
        printf("\nпрацюємо на вторинній копії: первинну доведеться відновлювати\n");
    } else {
        fprintf(stderr, "\nжодна копія метаданих не читається\n");
        close(fd);
        return 1;
    }

    printf("\nчинна копія: зсув %" PRIu64 ", seqid %" PRIu64 "\n",
           use->at_offset, use->seqid);

    luks2_json_check(use->json, use->json_len, use->hdr_size, stdout, &rep);
    printf("\nпідсумок: помилок %d, попереджень %d\n", rep.errors, rep.warnings);
    exit_code = rep.errors ? 3 : 0;

    if (rc_pri == LUKS2_OK)
        luks2_hdr_free(&pri);
    if (rc_sec == LUKS2_OK)
        luks2_hdr_free(&sec);
    close(fd);
    return exit_code;
}
