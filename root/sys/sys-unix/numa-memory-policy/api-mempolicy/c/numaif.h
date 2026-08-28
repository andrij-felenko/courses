#define _GNU_SOURCE
#include <numaif.h>
#include <unistd.h>
#include <sys/syscall.h>

/* Встановлення політики за замовчуванням для поточного потоку */
long set_mempolicy(int mode, const unsigned long *nodemask, unsigned long maxnode);

/* Прив'язка політики пам'яті до конкретного віртуального діапазону [addr, addr + len) */
long mbind(void *addr, unsigned long len, int mode,
           const unsigned long *nodemask, unsigned long maxnode, unsigned int flags);

/* Отримання поточної політики процесу або інформації про вузол конкретної адреси */
long get_mempolicy(int *mode, unsigned long *nodemask, unsigned long maxnode,
                  void *addr, unsigned long flags);

/* Пакетна міграція сторінок процесу з одного набору вузлів на інший */
long migrate_pages(int pid, unsigned long maxnode,
                   const unsigned long *old_nodes, const unsigned long *new_nodes);

/* Встановлення «домашнього вузла» для діапазону пам'яті (Linux 5.17+) */
long set_mempolicy_home_node(unsigned long start, unsigned long len,
                            unsigned long home_node, unsigned long flags);
