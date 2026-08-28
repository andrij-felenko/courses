// Інваріант ЦИКЛУ: на вході в кожну ітерацію max — найбільший з переглянутих.
int32_t find_max(const int32_t *a, size_t n) {
    assert(n > 0);                       // передумова
    int32_t max = a[0];
    for (size_t i = 1; i < n; i++) {
        assert(max >= a[i - 1]);         // інваріант циклу: попереднє вже враховано
        if (a[i] > max) max = a[i];
    }
    return max;                          // звідси постумова: max >= кожного a[k]
}
