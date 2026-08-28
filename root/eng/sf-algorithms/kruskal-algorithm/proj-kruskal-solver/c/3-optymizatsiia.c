// Порозрядне сортування масиву ребер (32-бітні беззнакові ваги)
void radix_sort_edges(Edge *edges, size_t n) {
    Edge *temp = (Edge *)malloc(n * sizeof(Edge));
    if (!temp) return;

    for (int shift = 0; shift < 32; shift += 8) {
        size_t count[256] = {0};

        // Підрахунок частот для поточного байта
        for (size_t i = 0; i < n; ++i) {
            uint8_t byte = (uint8_t)((edges[i].weight >> shift) & 0xFF);
            count[byte]++;
        }

        // Перетворення частот на префіксні суми
        size_t total = 0;
        for (int i = 0; i < 256; ++i) {
            size_t old = count[i];
            count[i] = total;
            total += old;
        }

        // Стабільне перенесення в тимчасовий буфер
        for (size_t i = 0; i < n; ++i) {
            uint8_t byte = (uint8_t)((edges[i].weight >> shift) & 0xFF);
            temp[count[byte]++] = edges[i];
        }

        // Копіювання назад
        for (size_t i = 0; i < n; ++i) {
            edges[i] = temp[i];
        }
    }
    free(temp);
}
