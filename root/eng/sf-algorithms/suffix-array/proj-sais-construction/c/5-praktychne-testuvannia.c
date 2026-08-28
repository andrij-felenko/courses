int main(void) {
    const char *text = "banana";
    SuffixIndex *index = suffix_index_create(text);
    if (!index) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    printf("=== Суфіксний індекс для тексту: \"%s\" ===\n\n", text);
    printf(" k | SA[k] | LCP[k] | Суфікс тексту\n");
    printf("---+-------+--------+-----------------\n");
    for (int i = 0; i < index->n; ++i) {
        printf(" %d |   %d   |   %d    | %s\n", 
               i, index->sa[i], index->lcp[i], index->text + index->sa[i]);
    }

    int rep_pos = 0;
    int rep_len = suffix_index_longest_repeated(index, &rep_pos);
    printf("\nНайдовший повторюваний підрядок: \"%.*s\" (довжина %d)\n", 
           rep_len, index->text + rep_pos, rep_len);

    long long distinct = suffix_index_distinct_substrings(index);
    printf("Кількість унікальних підрядків: %lld (очікувано 15)\n", distinct);

    int lcp_1_3 = suffix_index_query_lcp(index, 1, 3);
    printf("Швидкий запит LCP(SA[1], SA[3]) через Sparse Table: %d (\"a\")\n", lcp_1_3);

    const char *query = "an";
    SearchResult res = suffix_index_search(index, query);
    printf("\nПошук зразка \"%s\": знайдено %d входжень у діапазоні SA[%d..%d]:\n", 
           query, res.count, res.left, res.right);
    for (int i = res.left; i <= res.right && res.found; ++i) {
        printf("  -> зсув у тексті: %d (підрядок \"%s\")\n", 
               index->sa[i], index->text + index->sa[i]);
    }

    suffix_index_destroy(index);
    return 0;
}
