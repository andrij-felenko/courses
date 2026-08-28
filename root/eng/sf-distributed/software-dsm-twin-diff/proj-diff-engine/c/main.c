#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/mman.h>

#define PAGE_SIZE 4096
#define MAX_PAGES 16
#define MAX_DIFF_BYTES 4096

typedef enum {
    PAGE_STATE_INVALID = 0,
    PAGE_STATE_READ_ONLY,
    PAGE_STATE_DIRTY_TWINNED
} PageState;

typedef struct {
    uint16_t offset;
    uint16_t length;
} __attribute__((packed)) DiffChunkHeader;

typedef struct {
    uint8_t *virtual_addr;
    uint8_t *twin_buffer;
    PageState state;
    bool is_dirty;
} PageDescriptor;

typedef struct {
    uint8_t *shared_region;
    size_t num_pages;
    PageDescriptor pages[MAX_PAGES];
    uint8_t twin_pool[MAX_PAGES][PAGE_SIZE];
} DsmEngine;

static DsmEngine g_dsm;

static void dsm_sigsegv_handler(int sig, siginfo_t *info, void *ucontext) {
    (void)sig;
    (void)ucontext;
    uintptr_t fault_addr = (uintptr_t)info->si_addr;
    uintptr_t base_addr = (uintptr_t)g_dsm.shared_region;
    uintptr_t limit_addr = base_addr + (g_dsm.num_pages * PAGE_SIZE);

    if (fault_addr < base_addr || fault_addr >= limit_addr) {
        /* Адреса не належить керованому простору DSM — аварійне завершення */
        const char msg[] = "Fatal: Unhandled SIGSEGV outside DSM region\n";
        write(STDERR_FILENO, msg, sizeof(msg) - 1);
        _exit(EXIT_FAILURE);
    }

    size_t page_idx = (fault_addr - base_addr) / PAGE_SIZE;
    PageDescriptor *desc = &g_dsm.pages[page_idx];

    if (desc->state == PAGE_STATE_READ_ONLY) {
        /* Перший запис у сторінку: створюємо двійник і відкриваємо права */
        memcpy(desc->twin_buffer, desc->virtual_addr, PAGE_SIZE);

        if (mprotect(desc->virtual_addr, PAGE_SIZE, PROT_READ | PROT_WRITE) != 0) {
            const char err[] = "Fatal: mprotect failed in signal handler\n";
            write(STDERR_FILENO, err, sizeof(err) - 1);
            _exit(EXIT_FAILURE);
        }

        desc->state = PAGE_STATE_DIRTY_TWINNED;
        desc->is_dirty = true;
    } else {
        const char unk[] = "Fatal: Unexpected page state on fault\n";
        write(STDERR_FILENO, unk, sizeof(unk) - 1);
        _exit(EXIT_FAILURE);
    }
}

int dsm_engine_init(size_t num_pages) {
    if (num_pages > MAX_PAGES || num_pages == 0) {
        return -1;
    }

    g_dsm.num_pages = num_pages;
    size_t total_bytes = num_pages * PAGE_SIZE;

    /* Виділяємо анонімний вирівняний регіон для спільної пам'яті */
    g_dsm.shared_region = (uint8_t*)mmap(NULL, total_bytes, PROT_READ,
                                         MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (g_dsm.shared_region == MAP_FAILED) {
        return -1;
    }

    /* Налаштовуємо дескриптори сторінок */
    for (size_t i = 0; i < num_pages; i++) {
        g_dsm.pages[i].virtual_addr = g_dsm.shared_region + (i * PAGE_SIZE);
        g_dsm.pages[i].twin_buffer = g_dsm.twin_pool[i];
        g_dsm.pages[i].state = PAGE_STATE_READ_ONLY;
        g_dsm.pages[i].is_dirty = false;
        memset(g_dsm.twin_pool[i], 0, PAGE_SIZE);
    }

    /* Реєструємо обробник сигналу SIGSEGV */
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_sigaction = dsm_sigsegv_handler;
    sa.sa_flags = SA_SIGINFO | SA_NODEFER;
    sigemptyset(&sa.sa_mask);

    if (sigaction(SIGSEGV, &sa, NULL) != 0) {
        munmap(g_dsm.shared_region, total_bytes);
        return -1;
    }

    return 0;
}

size_t dsm_compute_page_diff(size_t page_idx, uint8_t *diff_buffer, size_t max_out) {
    if (page_idx >= g_dsm.num_pages) return 0;
    PageDescriptor *desc = &g_dsm.pages[page_idx];

    if (!desc->is_dirty || desc->state != PAGE_STATE_DIRTY_TWINNED) {
        return 0;
    }

    const uint64_t *page_words = (const uint64_t*)desc->virtual_addr;
    const uint64_t *twin_words = (const uint64_t*)desc->twin_buffer;
    size_t total_words = PAGE_SIZE / sizeof(uint64_t);
    size_t out_pos = 0;
    size_t w = 0;

    while (w < total_words) {
        if (page_words[w] == twin_words[w]) {
            w++;
            continue;
        }

        /* Знаходимо точний перший байт розбіжності */
        size_t start_byte = w * sizeof(uint64_t);
        while (start_byte < PAGE_SIZE && desc->virtual_addr[start_byte] == desc->twin_buffer[start_byte]) {
            start_byte++;
        }

        size_t end_byte = (w + 1) * sizeof(uint64_t);
        if (end_byte > PAGE_SIZE) end_byte = PAGE_SIZE;

        while (end_byte < PAGE_SIZE && desc->virtual_addr[end_byte] != desc->twin_buffer[end_byte]) {
            end_byte++;
        }

        size_t chunk_len = end_byte - start_byte;
        if (out_pos + sizeof(DiffChunkHeader) + chunk_len > max_out) {
            break; /* Переповнення вихідного буфера */
        }

        DiffChunkHeader hdr;
        hdr.offset = (uint16_t)start_byte;
        hdr.length = (uint16_t)chunk_len;

        memcpy(&diff_buffer[out_pos], &hdr, sizeof(DiffChunkHeader));
        out_pos += sizeof(DiffChunkHeader);

        memcpy(&diff_buffer[out_pos], &desc->virtual_addr[start_byte], chunk_len);
        out_pos += chunk_len;

        w = (end_byte / sizeof(uint64_t)) + 1;
    }

    return out_pos;
}

void dsm_apply_diff(uint8_t *target_page, const uint8_t *diff_data, size_t diff_size) {
    size_t in_pos = 0;
    while (in_pos + sizeof(DiffChunkHeader) <= diff_size) {
        DiffChunkHeader hdr;
        memcpy(&hdr, &diff_data[in_pos], sizeof(DiffChunkHeader));
        in_pos += sizeof(DiffChunkHeader);

        if (hdr.offset + hdr.length <= PAGE_SIZE && in_pos + hdr.length <= diff_size) {
            memcpy(target_page + hdr.offset, &diff_data[in_pos], hdr.length);
        }
        in_pos += hdr.length;
    }
}

void dsm_end_epoch_page(size_t page_idx) {
    if (page_idx >= g_dsm.num_pages) return;
    PageDescriptor *desc = &g_dsm.pages[page_idx];

    if (desc->state == PAGE_STATE_DIRTY_TWINNED) {
        /* Скидаємо захист назад до PROT_READ */
        mprotect(desc->virtual_addr, PAGE_SIZE, PROT_READ);
        desc->state = PAGE_STATE_READ_ONLY;
        desc->is_dirty = false;
    }
}

void dsm_engine_destroy(void) {
    if (g_dsm.shared_region && g_dsm.shared_region != MAP_FAILED) {
        munmap(g_dsm.shared_region, g_dsm.num_pages * PAGE_SIZE);
        g_dsm.shared_region = NULL;
    }
}
