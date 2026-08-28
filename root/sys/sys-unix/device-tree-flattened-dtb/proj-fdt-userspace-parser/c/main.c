#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <endian.h>

#define FDT_MAGIC       0xd00dfeed
#define FDT_BEGIN_NODE  0x00000001
#define FDT_END_NODE    0x00000002
#define FDT_PROP        0x00000003
#define FDT_NOP         0x00000004
#define FDT_END         0x00000009

struct fdt_header {
    uint32_t magic;
    uint32_t totalsize;
    uint32_t off_dt_struct;
    uint32_t off_dt_strings;
    uint32_t off_mem_rsvmap;
    uint32_t version;
    uint32_t last_comp_version;
    uint32_t boot_cpuid_phys;
    uint32_t size_dt_strings;
    uint32_t size_dt_struct;
};

static uint32_t align4(uint32_t val) {
    return (val + 3) & ~3U;
}

static void print_indent(int depth) {
    for (int i = 0; i < depth; ++i) {
        printf("  ");
    }
}

static int parse_fdt_buffer(const uint8_t *buf, size_t buf_size) {
    if (buf_size < sizeof(struct fdt_header)) {
        fprintf(stderr, "Помилка: буфер занадто малий для заголовка\n");
        return -1;
    }

    const struct fdt_header *hdr = (const struct fdt_header *)buf;
    uint32_t magic = be32toh(hdr->magic);
    if (magic != FDT_MAGIC) {
        fprintf(stderr, "Помилка: некоректне сигнатурне число 0x%x (очікувалося 0x%x)\n",
                magic, FDT_MAGIC);
        return -1;
    }

    uint32_t totalsize = be32toh(hdr->totalsize);
    uint32_t off_struct = be32toh(hdr->off_dt_struct);
    uint32_t off_strings = be32toh(hdr->off_dt_strings);

    printf("FDT Header: totalsize=%u, struct_offset=%u, strings_offset=%u\n",
           totalsize, off_struct, off_strings);

    const uint32_t *pstruct = (const uint32_t *)(buf + off_struct);
    const char *pstrings = (const char *)(buf + off_strings);

    int depth = 0;
    int running = 1;

    while (running) {
        uint32_t tag = be32toh(*pstruct++);

        switch (tag) {
        case FDT_BEGIN_NODE: {
            const char *name = (const char *)pstruct;
            if (*name == '\0') {
                name = "/";
            }
            print_indent(depth);
            printf("Node: %s {\n", name);
            depth++;

            size_t name_len = strlen((const char *)pstruct) + 1;
            pstruct += align4(name_len) / 4;
            break;
        }
        case FDT_END_NODE:
            depth--;
            print_indent(depth);
            printf("};\n");
            break;

        case FDT_PROP: {
            uint32_t len = be32toh(*pstruct++);
            uint32_t nameoff = be32toh(*pstruct++);
            const char *prop_name = pstrings + nameoff;

            print_indent(depth);
            printf("Property '%s' (len=%u)\n", prop_name, len);

            pstruct += align4(len) / 4;
            break;
        }
        case FDT_NOP:
            break;

        case FDT_END:
            running = 0;
            break;

        default:
            fprintf(stderr, "Помилка: невідомий токен 0x%08x\n", tag);
            return -1;
        }
    }

    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("Використання: %s <file.dtb>\n", argv[0]);
        return 1;
    }

    FILE *f = fopen(argv[1], "rb");
    if (!f) {
        perror("Не вдалося відкрити файл");
        return 1;
    }

    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);

    uint8_t *buf = (uint8_t *)malloc(size);
    if (!buf) {
        fclose(f);
        return 1;
    }

    if (fread(buf, 1, size, f) != (size_t)size) {
        perror("Помилка читання файлу");
        free(buf);
        fclose(f);
        return 1;
    }
    fclose(f);

    int res = parse_fdt_buffer(buf, size);

    free(buf);
    return res;
}
