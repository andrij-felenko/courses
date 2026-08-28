#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <arpa/inet.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include "shared_tree.h"

#define ARENA_SIZE_BYTES (1024 * 4096)

int main(int argc, char **argv)
{
    int map_fd = bpf_map_create(BPF_MAP_TYPE_ARENA, "arena_map", 0, 0, 1024, NULL);
    if (map_fd < 0) {
        perror("bpf_map_create failed");
        return 1;
    }

    void *arena_base = mmap(NULL, ARENA_SIZE_BYTES, PROT_READ | PROT_WRITE, MAP_SHARED, map_fd, 0);
    if (arena_base == MAP_FAILED) {
        perror("mmap failed");
        close(map_fd);
        return 1;
    }

    printf("[+] BPF Arena mmap success: %p\n", arena_base);

    /* Ініціалізація заголовка у спільній пам'яті */
    struct arena_root_header *hdr = (struct arena_root_header *)arena_base;
    hdr->magic = ARENA_MAGIC;
    hdr->version = 1;
    hdr->total_lookups = 0;
    hdr->total_matches = 0;

    /* Алокація коріння дерева безпосередньо у арені */
    struct radix_node *root_node = (struct radix_node *)((char *)arena_base + sizeof(struct arena_root_header));
    memset(root_node, 0, sizeof(struct radix_node));
    root_node->prefix = 0;
    root_node->prefix_len = 0;
    root_node->action = 0;

    /* Створення дочірнього вузла для заблокованої підмережі (наприклад 10.0.0.0/8) */
    struct radix_node *drop_node = root_node + 1;
    memset(drop_node, 0, sizeof(struct radix_node));
    drop_node->prefix = 0x0A000000;
    drop_node->prefix_len = 8;
    drop_node->action = 1; /* DROP */

    /* Прив'язка дочірнього вузла за вказівником арени */
    root_node->child[0] = drop_node;

    /* Атомна публікація коріння дерева для eBPF у ядрі */
    hdr->root = drop_node;
    printf("[+] Radix Tree initialized in shared BPF Arena. Root=%p\n", drop_node);

    printf("[+] Monitoring traffic... Press Enter to exit.\n");
    getchar();

    munmap(arena_base, ARENA_SIZE_BYTES);
    close(map_fd);
    return 0;
}
