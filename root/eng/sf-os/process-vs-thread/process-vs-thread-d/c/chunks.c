#include "chunks.h"

void chunk_split(size_t n, size_t parts, chunk_t *out)
{
    if (parts == 0)
        return;

    const size_t base = n / parts;
    const size_t rest = n % parts;
    size_t pos = 0;

    for (size_t i = 0; i < parts; ++i) {
        const size_t len = base + (i < rest ? 1 : 0);
        out[i].start = pos;
        out[i].end = pos + len;
        pos += len;
    }
}

long long sum_range(const int *data, chunk_t part)
{
    long long sum = 0;
    for (size_t i = part.start; i < part.end; ++i)
        sum += data[i];
    return sum;
}
