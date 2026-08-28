/* audit.h — спільний заголовок обох одиниць трансляції */
#ifndef AUDIT_H
#define AUDIT_H
#include <sys/types.h>

struct span {
    off_t start;       /* ширина ЗАЛЕЖИТЬ від прапорців збирання */
    long  records;
    int   truncated;
};

off_t tail_offset(off_t size, off_t back);
void  fill_span(struct span *out);

#endif
