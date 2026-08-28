/* ❌ НЕКОРЕКТНО (Верифікатор відхилить програму під час завантаження) */
struct iphdr *iph = (void *)(eth + 1);
if (iph->protocol == IPPROTO_TCP) { ... }

/* ✅ КОРЕКТНО (Bounds Check перед розімкнутим вказівника) */
struct iphdr *iph = (void *)(eth + 1);
if ((void *)(iph + 1) > data_end) {
    return XDP_PASS; /* Пакет занадто короткий */
}
if (iph->protocol == IPPROTO_TCP) { ... }
