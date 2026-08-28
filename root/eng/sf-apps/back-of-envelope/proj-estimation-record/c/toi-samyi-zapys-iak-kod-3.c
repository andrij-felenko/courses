#define GiB (1024ULL * 1024 * 1024)     // 1 гігабайт у байтах

int main(void) {
    // ЗАПИС ОЦІНКИ: індекс на 50 млн записів у пам'ять?
    IndexAssumptions a = {
        .records      = 50000000ULL,    // шт — поточна БД, округлено вгору
        .key_bytes    = 16,             // Б  — UUID/хеш за чинною схемою
        .ptr_bytes    = 8,              // Б  — 64-бітна адреса
        .overhead_num = 2,              // ×2 — грубо на службові поля…
        .overhead_den = 1,              // …  = 2/1
    };

    uint64_t bytes = index_size_bytes(a);
    printf("Оцінка індексу: %llu Б  (~%llu.%llu ГБ)\n",
           (unsigned long long)bytes,
           (unsigned long long)(bytes / GiB),
           (unsigned long long)(bytes % GiB * 10 / GiB));   // один знак після коми

    // Поріг залежить від машини — той самий запис, різні відповіді:
    verdict("Сервер (64 ГБ)     ", bytes, 64 * GiB);
    verdict("Вбудований (256 МБ)", bytes, 256ULL * 1024 * 1024);
    return 0;
}
