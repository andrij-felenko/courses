#include <sys/prctl.h>
#include <linux/prctl.h>

struct prctl_mm_map m = {
    .start_code = 0x400000,   .end_code  = 0x4a1000,
    .start_data = 0x6a1000,   .end_data  = 0x6b2000,
    .start_brk  = 0x6b3000,   .brk       = 0x71c000,
    .start_stack = 0x7ffd0000,
    .arg_start  = 0x7ffd0100, .arg_end   = 0x7ffd0140,
    .env_start  = 0x7ffd0140, .env_end   = 0x7ffd0800,
    .auxv = auxv_words, .auxv_size = auxv_bytes,
    .exe_fd = exe_fd,         /* дескриптор виконуваного файлу */
};
prctl(PR_SET_MM, PR_SET_MM_MAP, &m, sizeof m, 0);

/* скільки байтів чекає САМЕ ЦЕ ядро — щоб програма, зібрана під інше,
   не подала структуру не того розміру */
unsigned int want;
prctl(PR_SET_MM, PR_SET_MM_MAP_SIZE, &want, 0, 0);
