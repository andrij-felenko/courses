// sink — усе, що отримувач склав із прийнятих кадрів; tx — геш кінця A.
store("copy.bin", sink.data(), sink.size());
rot("copy.bin", 4096, 4098);                 // однакова парність — сумі байдуже

Fnv1a from_buffer;
from_buffer.feed(sink.data(), sink.size());
const uint64_t from_disk = hash_stored("copy.bin");

std::printf("геш із буфера %016llx  %s\n", (unsigned long long)from_buffer.h,
            from_buffer.h == tx.h ? "збігся" : "РОЗБІЖНІСТЬ");
std::printf("геш із файла  %016llx  %s\n", (unsigned long long)from_disk,
            from_disk == tx.h ? "збігся" : "РОЗБІЖНІСТЬ");
