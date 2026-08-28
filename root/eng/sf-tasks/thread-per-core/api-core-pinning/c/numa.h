#include <numa.h>
#include <numaif.h>

/* Виділення блоку пам'яті строго на вказаному NUMA-вузлі */
void *numa_alloc_onnode(size_t size, int node);

/* Звільнення пам'яті, виділеної через numa_alloc_* */
void numa_free(void *start, size_t size);

/* Отримання індексу NUMA-вузла для вказаного ядра CPU */
int numa_node_of_cpu(int cpu);

/* Встановлення бажаного вузла виділення пам'яті для поточного потоку */
void numa_set_preferred(int node);

/* Системний виклик mbind для прив'язки діапазону віртуальних адрес */
long mbind(void *addr, unsigned long len, int mode,
           const unsigned long *nodemask, unsigned long maxnode, unsigned flags);
