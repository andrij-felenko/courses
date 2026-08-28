#include <stdint.h>
#include <stddef.h>
#include <stdio.h>

#define ENTRIES 512ULL          /* 4096 байтів таблиці / 8 байтів запису */

/* Скільки таблиць того рівня, один запис якого покриває entry_span байтів,
   перетинає ділянка [start, start + len). */
static uint64_t tables_for(uint64_t start, uint64_t len, uint64_t entry_span)
{
        uint64_t table_span = entry_span * ENTRIES;

        return (start + len - 1) / table_span - start / table_span + 1;
}

int main(void)
{
        static const struct { uint64_t start, len; } vma[] = {
                { 0x555555554000ULL,   6ULL << 20 },   /* код і дані     */
                { 0x555555b54000ULL,  64ULL << 20 },   /* купа           */
                { 0x7f3c9a123000ULL, 200ULL << 20 },   /* файл через mmap */
                { 0x7ffffffdf000ULL, 128ULL << 10 },   /* торкнутий стек */
        };
        uint64_t leaves = 0;

        for (size_t i = 0; i < sizeof vma / sizeof *vma; i++)
                leaves += tables_for(vma[i].start, vma[i].len, 4096);

        printf("таблиць листя: %llu (%llu КіБ)\n",
               (unsigned long long)leaves,
               (unsigned long long)(leaves * 4096 / 1024));
        return 0;
}
