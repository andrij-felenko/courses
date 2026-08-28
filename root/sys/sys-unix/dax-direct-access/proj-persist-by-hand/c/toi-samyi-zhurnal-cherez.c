#include <libpmem.h>

size_t mapped; int is_pmem;
void *base = pmem_map_file(path, 0, 0, 0, &mapped, &is_pmem);  /* сама спробує MAP_SYNC */
if (!base) { perror("pmem_map_file"); return 1; }
if (!is_pmem) { fprintf(stderr, "це не постійна пам'ять\n"); return 1; }

pmem_memcpy_persist(s->body, rec, n);      /* копіювання + доведення до довговічності */
s->len = n; s->crc = crc32_bitwise(rec, n);
pmem_persist(&s->len, 8);                  /* виштовхування + очікування */

__atomic_store_n(&s->commit, seq + 1, __ATOMIC_RELAXED);
pmem_persist(&s->commit, 8);
