#include <stdio.h>
#include <stdint.h>
#include <stddef.h>

struct MemoryBlock {
    int id;              /* 4 байти */
    long tag;            /* 4 байти в Windows LLP64, але 8 байтів у Linux LP64! */
    void* payload;       /* 8 байтів на обох 64-бітних системах */
};

int main(void) {
    printf("Розмір int:       %zu байтів\n", sizeof(int));
    printf("Розмір long:      %zu байтів\n", sizeof(long));
    printf("Розмір void*:     %zu байтів\n", sizeof(void*));
    printf("Розмір uintptr_t: %zu байтів\n", sizeof(uintptr_t));
    printf("Розмір структури: %zu байтів\n", sizeof(struct MemoryBlock));
    printf("Зміщення payload: %zu байтів\n", offsetof(struct MemoryBlock, payload));

    /* НЕБЕЗПЕЧНО: непереносне перетворення покажчика у long */
    void* ptr = (void*)0x123456789ABCDEF0ULL;
    /* long p_bad = (long)ptr;  -- На Windows x64 зріже старші 32 біти! */
    uintptr_t p_safe = (uintptr_t)ptr; /* Працює всюди */
    printf("Безпечна адреса:  0x%jx\n", (uintmax_t)p_safe);
    return 0;
}
