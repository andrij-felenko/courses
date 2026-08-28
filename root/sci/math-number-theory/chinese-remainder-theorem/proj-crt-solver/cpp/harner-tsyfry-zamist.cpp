#include <cstdint>
#include <vector>

// Мішано-основні цифри: x = d[0] + d[1]·n[0] + d[2]·n[0]n[1] + …
std::vector<int64_t> garner_digits(const std::vector<int64_t> &a,
                                   const std::vector<int64_t> &n) {
    size_t k = n.size();
    // модулі сталі → таблицю обернених рахують РАЗ і тримають поруч із ними
    std::vector<std::vector<int64_t>> inv(k, std::vector<int64_t>(k, 0));
    for (size_t i = 0; i < k; ++i)
        for (size_t j = 0; j < i; ++j)
            inv[i][j] = inv_mod(n[j], n[i]);

    std::vector<int64_t> d(k);
    for (size_t i = 0; i < k; ++i) {
        int64_t di = a[i] % n[i];
        for (size_t j = 0; j < i; ++j) {
            int64_t t = (di - d[j]) % n[i];
            if (t < 0) t += n[i];
            // t < n[i] та inv < n[i] → добуток < n[i]²: стеля у два машинні слова
            di = (int64_t)((__int128)t * inv[i][j] % n[i]);
        }
        d[i] = di;
    }
    return d;                          // жодне число тут не переросло n[i]²
}
