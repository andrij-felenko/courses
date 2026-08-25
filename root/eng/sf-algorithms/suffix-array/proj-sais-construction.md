# ⚙️ Практична реалізація суфіксного масиву: побудова, LCP та двійковий пошук

Суфіксний індекс є одним із найпотужніших інструментів аналізу послідовностей. На відміну від інвертованого індексу слів, суфіксний масив не залежить від пробілів чи структури природної мови: він однаково ефективно індексує геномні послідовності (ДНК/РНК), скомпільовані бінарні файли, вихідний код довільної мови програмування та текстові документи.

Повноцінний суфіксний рушій об'єднує чотири взаємопов'язані алгоритмічні компоненти:
1. **Побудова суфіксного масиву `SA`:** алгоритм подвоєння префіксів із подвійним порозрядним сортуванням (Prefix Doubling + Counting Sort) за час `O(N log N)`;
2. **Побудова масиву найдовших спільних префіксів `LCP`:** алгоритм Касаї за час `O(N)`;
3. **Таблиця швидких запитів мінімуму (Sparse Table):** попереднє обчислення за `O(N log N)` для знаходження `LCP` між будь-якими двома суфіксами за константний час `O(1)`;
4. **Двійковий пошук підрядків:** знаходження точного діапазону входжень `[L, R]` за `O(M · log N)` або `O(M + log N)`.

Нижче наведено промислову реалізацію повнофункціонального модуля індексування мовами C та C++.

---

## 1. Архітектура та інтерфейс модуля

Модуль інкапсулює вихідний текст і всі допоміжні таблиці в єдиній структурі (у C) або класі `SuffixIndex` (у C++). Для виключення зайвого виділення пам'яті в купі всі рядкові зрізи та діапазони повертаються через легкогінні дескриптори (`std::string_view` та `std::span` у C++, або покажчики зі зміщеннями у C).

:::tabs
```c
#ifndef SUFFIX_INDEX_H
#define SUFFIX_INDEX_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/* Результат пошуку зразка в суфіксному масиві */
typedef struct {
    int left;   /* Початковий індекс у SA */
    int right;  /* Кінцевий індекс у SA */
    int count;  /* Кількість знайдених входжень (right - left + 1) */
} SearchResult;

/* Структура повного суфіксного індексу */
typedef struct {
    char *text;         /* Копія вихідного тексту з термінатором */
    int n;              /* Довжина тексту */
    int *sa;            /* Суфіксний масив: sa[k] = початковий індекс суфікса */
    int *rank;          /* Обернений масив: rank[i] = позиція суфікса S[i] у SA */
    int *lcp;           /* Масив LCP: lcp[k] = спільний префікс sa[k] та sa[k-1] */
    int **st;           /* Розріджена таблиця (Sparse Table) для RMQ на LCP */
    int max_log;        /* Кількість рівнів розрідженої таблиці */
} SuffixIndex;

/* Створення та знищення індексу */
SuffixIndex* suffix_index_create(const char *src);
void suffix_index_destroy(SuffixIndex *idx);

/* Базові пошукові операції */
SearchResult suffix_index_search(const SuffixIndex *idx, const char *pattern);
int suffix_index_query_lcp(const SuffixIndex *idx, int sa_idx_a, int sa_idx_b);

/* Аналітичні запити */
int suffix_index_longest_repeated(const SuffixIndex *idx, int *out_pos);
long long suffix_index_distinct_substrings(const SuffixIndex *idx);

#endif /* SUFFIX_INDEX_H */
```
```cpp
#pragma once
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <cstdint>
#include <algorithm>

struct SearchResult {
    int left{-1};
    int right{-1};
    int count{0};

    [[nodiscard]] bool found() const noexcept { return count > 0; }
};

class SuffixIndex {
public:
    explicit SuffixIndex(std::string_view text);

    // Заборона небезпечного копіювання масивних буферів, дозволено переміщення (RAII)
    SuffixIndex(const SuffixIndex&) = delete;
    SuffixIndex& operator=(const SuffixIndex&) = delete;
    SuffixIndex(SuffixIndex&&) noexcept = default;
    SuffixIndex& operator=(SuffixIndex&&) noexcept = default;
    ~SuffixIndex() = default;

    [[nodiscard]] SearchResult search(std::string_view pattern) const noexcept;
    [[nodiscard]] int query_lcp(int sa_a, int sa_b) const noexcept;
    [[nodiscard]] std::string_view longest_repeated_substring() const noexcept;
    [[nodiscard]] int64_t count_distinct_substrings() const noexcept;

    [[nodiscard]] std::span<const int> get_sa() const noexcept { return sa_; }
    [[nodiscard]] std::span<const int> get_lcp() const noexcept { return lcp_; }
    [[nodiscard]] std::string_view get_text() const noexcept { return text_; }
    [[nodiscard]] int size() const noexcept { return n_; }

private:
    void build_sa();
    void build_lcp();
    void build_sparse_table();

    std::string text_;
    int n_{0};
    std::vector<int> sa_;
    std::vector<int> rank_;
    std::vector<int> lcp_;
    std::vector<std::vector<int>> st_;
};
```
:::

---

## 2. Механізм побудови суфіксного масиву: подвоєння та порозрядне сортування

Алгоритм подвоєння префіксів Манбера — Маєрса базується на інваріанті: якщо ранги всіх суфіксів за префіксами довжини `k` вже обчислено, то порядок суфіксів за префіксами довжини `2k` однозначно визначається парою цілих чисел `(Rank[i], Rank[i + k])`.

Для забезпечення гарантованого часу `O(N log N)` сортування пар виконується у два проходи алгоритмом **підрахунку (Counting Sort)**:
1. **Перший прохід:** сортування елементів за другим ключем пари `Rank[i + k]`. Якщо зміщення виходить за межі рядка (`i + k >= N`), ранг вважається найменшим можливим (`-1` або `0`);
2. **Другий прохід:** стійке сортування отриманого масиву за першим ключем `Rank[i]`. Оскільки сортування підрахунком є стійким (Stable), порядок елементів з однаковим першим ключем визначається їхнім відносним порядком за другим ключем.

Після кожного кроку подвоєння формуються нові ранги `new_rank`. Якщо кількість різних рангів сягає `N`, усі суфікси отримали унікальні позиції, і подальші ітерації негайно припиняються.

:::tabs
```c
/* Допоміжне порозрядне сортування пар рангів (Rank[i], Rank[i+k]) */
static void count_sort(int *sa, const int *rank, int n, int k) {
    int *cnt = (int*)calloc((size_t)(n + 256 + 2), sizeof(int));
    int *temp_sa = (int*)malloc((size_t)n * sizeof(int));
    if (!cnt || !temp_sa) {
        free(cnt);
        free(temp_sa);
        return;
    }

    /* 1. Сортування за другим ключем: Rank[i + k] */
    int max_val = 0;
    for (int i = 0; i < n; ++i) {
        int val = (i + k < n) ? rank[i + k] + 1 : 0;
        cnt[val]++;
        if (val > max_val) max_val = val;
    }
    for (int i = 1; i <= max_val; ++i) {
        cnt[i] += cnt[i - 1];
    }
    for (int i = n - 1; i >= 0; --i) {
        int val = (sa[i] + k < n) ? rank[sa[i] + k] + 1 : 0;
        temp_sa[--cnt[val]] = sa[i];
    }

    /* 2. Сортування за першим ключем: Rank[temp_sa[i]] */
    memset(cnt, 0, (size_t)(max_val + 2) * sizeof(int));
    max_val = 0;
    for (int i = 0; i < n; ++i) {
        int val = rank[temp_sa[i]] + 1;
        cnt[val]++;
        if (val > max_val) max_val = val;
    }
    for (int i = 1; i <= max_val; ++i) {
        cnt[i] += cnt[i - 1];
    }
    for (int i = n - 1; i >= 0; --i) {
        int val = rank[temp_sa[i]] + 1;
        sa[--cnt[val]] = temp_sa[i];
    }

    free(cnt);
    free(temp_sa);
}
```
```cpp
void SuffixIndex::build_sa() {
    std::vector<int> temp_sa(n_);
    std::vector<int> cnt;
    std::vector<int> new_rank(n_);

    // 1. Початкова ініціалізація символьними кодами
    for (int i = 0; i < n_; ++i) {
        sa_[i] = i;
        rank_[i] = static_cast<unsigned char>(text_[i]);
    }

    // 2. Ітерації подвоєння префіксів: k = 1, 2, 4, 8...
    for (int k = 1; k < n_; k <<= 1) {
        auto count_sort_pass = [&](int offset) {
            int max_val = 0;
            for (int i = 0; i < n_; ++i) {
                int val = (i + offset < n_) ? rank_[i + offset] + 1 : 0;
                if (val > max_val) max_val = val;
            }
            cnt.assign(max_val + 2, 0);

            for (int i = 0; i < n_; ++i) {
                int val = (i + offset < n_) ? rank_[i + offset] + 1 : 0;
                cnt[val]++;
            }
            for (size_t i = 1; i < cnt.size(); ++i) {
                cnt[i] += cnt[i - 1];
            }
            for (int i = n_ - 1; i >= 0; --i) {
                int val = (sa_[i] + offset < n_) ? rank_[sa_[i] + offset] + 1 : 0;
                temp_sa[--cnt[val]] = sa_[i];
            }
            sa_ = temp_sa;
        };

        // Двопрохідне сортування за парою (rank[i], rank[i + k])
        count_sort_pass(k);
        count_sort_pass(0);

        // Оновлення масиву рангів
        new_rank[sa_[0]] = 0;
        int r = 0;
        for (int i = 1; i < n_; ++i) {
            int prev = sa_[i - 1];
            int curr = sa_[i];
            int prev_r2 = (prev + k < n_) ? rank_[prev + k] : -1;
            int curr_r2 = (curr + k < n_) ? rank_[curr + k] : -1;

            if (rank_[prev] != rank_[curr] || prev_r2 != curr_r2) {
                ++r;
            }
            new_rank[curr] = r;
        }
        rank_ = new_rank;
        if (r == n_ - 1) break; // Ранги всіх суфіксів стали унікальними
    }
}
```
:::

---

## 3. Лінійна побудова LCP за алгоритмом Касаї та Sparse Table

Масив `LCP` будується за лінійний час `O(N)` завдяки нерівності `h(i) >= h(i-1) - 1`. Після завершення побудови `LCP` над ним створюється таблиця `Sparse Table` для відповідей на запити найдовшого спільного префікса між будь-якими двома суфіксами за `O(1)`:

:::tabs
```c
static void build_lcp_and_sparse_table(SuffixIndex *idx) {
    int n = idx->n;
    const char *text = idx->text;
    const int *sa = idx->sa;
    const int *rank = idx->rank;
    int *lcp = idx->lcp;

    /* 1. Алгоритм Касаї: побудова LCP за O(N) */
    int h = 0;
    for (int i = 0; i < n; ++i) {
        if (rank[i] > 0) {
            int j = sa[rank[i] - 1];
            while (i + h < n && j + h < n && text[i + h] == text[j + h]) {
                h++;
            }
            lcp[rank[i]] = h;
            if (h > 0) h--;
        } else {
            lcp[0] = 0;
        }
    }

    /* 2. Побудова Sparse Table для RMQ на LCP */
    int max_log = 0;
    while ((1 << max_log) <= n) max_log++;
    idx->max_log = max_log;

    idx->st = (int**)malloc((size_t)max_log * sizeof(int*));
    for (int k = 0; k < max_log; ++k) {
        idx->st[k] = (int*)malloc((size_t)n * sizeof(int));
    }

    for (int i = 0; i < n; ++i) {
        idx->st[0][i] = lcp[i];
    }

    for (int k = 1; k < max_log; ++k) {
        int span = 1 << (k - 1);
        for (int i = 0; i + (1 << k) <= n; ++i) {
            int a = idx->st[k - 1][i];
            int b = idx->st[k - 1][i + span];
            idx->st[k][i] = (a < b) ? a : b;
        }
    }
}

int suffix_index_query_lcp(const SuffixIndex *idx, int sa_a, int sa_b) {
    if (!idx || sa_a == sa_b) return idx ? idx->n - idx->sa[sa_a] : 0;
    if (sa_a > sa_b) {
        int tmp = sa_a; sa_a = sa_b; sa_b = tmp;
    }
    int l = sa_a + 1;
    int r = sa_b;
    int len = r - l + 1;
    int k = 31 - __builtin_clz((unsigned int)len);
    int a = idx->st[k][l];
    int b = idx->st[k][r - (1 << k) + 1];
    return (a < b) ? a : b;
}
```
```cpp
void SuffixIndex::build_lcp() {
    int h = 0;
    for (int i = 0; i < n_; ++i) {
        if (rank_[i] > 0) {
            int j = sa_[rank_[i] - 1];
            while (i + h < n_ && j + h < n_ && text_[i + h] == text_[j + h]) {
                ++h;
            }
            lcp_[rank_[i]] = h;
            if (h > 0) --h;
        } else {
            lcp_[0] = 0;
        }
    }
}

void SuffixIndex::build_sparse_table() {
    int max_log = 0;
    while ((1 << max_log) <= n_) ++max_log;

    st_.assign(max_log, std::vector<int>(n_, 0));
    st_[0] = lcp_;

    for (int k = 1; k < max_log; ++k) {
        int span = 1 << (k - 1);
        for (int i = 0; i + (1 << k) <= n_; ++i) {
            st_[k][i] = std::min(st_[k - 1][i], st_[k - 1][i + span]);
        }
    }
}

int SuffixIndex::query_lcp(int sa_a, int sa_b) const noexcept {
    if (sa_a == sa_b) return n_ - sa_[sa_a];
    if (sa_a > sa_b) std::swap(sa_a, sa_b);

    int l = sa_a + 1;
    int r = sa_b;
    int len = r - l + 1;
    int k = 31 - __builtin_clz(static_cast<unsigned int>(len));
    return std::min(st_[k][l], st_[k][r - (1 << k) + 1]);
}
```
:::

---

## 4. Пошук підрядків та аналітичні запити

Метод `search` знаходить діапазон індексів `[left, right]` у суфіксному масиві за допомогою двох послідовних бінарних пошуків:
1. `lower_bound`: знаходить перший суфікс у `SA`, що лексикографічно не менший за шуканий шаблон `pattern`;
2. `upper_bound`: знаходить останній суфікс у `SA`, що має `pattern` як свій початковий префікс.

Аналітичні запити демонструють простоту обробки тексту:
* **Найдовший повторюваний підрядок:** сканує `LCP` за `O(N)` і знаходить `max(LCP[i])`;
* **Кількість унікальних підрядків:** підсумовує `(N - SA[i]) - LCP[i]` за один лінійний прохід.

:::tabs
```c
SuffixIndex* suffix_index_create(const char *src) {
    if (!src) return NULL;
    SuffixIndex *idx = (SuffixIndex*)malloc(sizeof(SuffixIndex));
    if (!idx) return NULL;

    idx->n = (int)strlen(src);
    idx->text = (char*)malloc((size_t)(idx->n + 1));
    idx->sa = (int*)malloc((size_t)idx->n * sizeof(int));
    idx->rank = (int*)malloc((size_t)idx->n * sizeof(int));
    idx->lcp = (int*)malloc((size_t)idx->n * sizeof(int));

    if (!idx->text || !idx->sa || !idx->rank || !idx->lcp) {
        suffix_index_destroy(idx);
        return NULL;
    }

    memcpy(idx->text, src, (size_t)idx->n + 1);
    int n = idx->n;

    for (int i = 0; i < n; ++i) {
        idx->sa[i] = i;
        idx->rank[i] = (unsigned char)src[i];
    }

    int *new_rank = (int*)malloc((size_t)n * sizeof(int));
    for (int k = 1; k < n; k <<= 1) {
        count_sort(idx->sa, idx->rank, n, k);

        new_rank[idx->sa[0]] = 0;
        int r = 0;
        for (int i = 1; i < n; ++i) {
            int prev = idx->sa[i - 1];
            int curr = idx->sa[i];
            int prev_r2 = (prev + k < n) ? idx->rank[prev + k] : -1;
            int curr_r2 = (curr + k < n) ? idx->rank[curr + k] : -1;

            if (idx->rank[prev] != idx->rank[curr] || prev_r2 != curr_r2) {
                r++;
            }
            new_rank[curr] = r;
        }
        memcpy(idx->rank, new_rank, (size_t)n * sizeof(int));
        if (r == n - 1) break;
    }
    free(new_rank);

    build_lcp_and_sparse_table(idx);
    return idx;
}

void suffix_index_destroy(SuffixIndex *idx) {
    if (!idx) return;
    if (idx->st) {
        for (int k = 0; k < idx->max_log; ++k) {
            free(idx->st[k]);
        }
        free(idx->st);
    }
    free(idx->text);
    free(idx->sa);
    free(idx->rank);
    free(idx->lcp);
    free(idx);
}

SearchResult suffix_index_search(const SuffixIndex *idx, const char *pattern) {
    SearchResult res = {-1, -1, 0};
    if (!idx || !pattern || idx->n == 0) return res;

    int m = (int)strlen(pattern);
    if (m == 0) return res;

    int low = 0, high = idx->n - 1;
    int first = -1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        int cmp = strncmp(idx->text + idx->sa[mid], pattern, (size_t)m);
        if (cmp >= 0) {
            first = mid;
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }

    if (first == -1 || strncmp(idx->text + idx->sa[first], pattern, (size_t)m) != 0) {
        return res;
    }

    low = first;
    high = idx->n - 1;
    int last = first;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        int cmp = strncmp(idx->text + idx->sa[mid], pattern, (size_t)m);
        if (cmp == 0) {
            last = mid;
            low = mid + 1;
        } else if (cmp < 0) {
            low = mid + 1;
        } else {
            high = mid - 1;
        }
    }

    res.left = first;
    res.right = last;
    res.count = last - first + 1;
    return res;
}

int suffix_index_longest_repeated(const SuffixIndex *idx, int *out_pos) {
    if (!idx || idx->n <= 1) return 0;
    int max_len = 0;
    int best_sa_idx = -1;

    for (int i = 1; i < idx->n; ++i) {
        if (idx->lcp[i] > max_len) {
            max_len = idx->lcp[i];
            best_sa_idx = idx->sa[i];
        }
    }

    if (out_pos && best_sa_idx != -1) {
        *out_pos = best_sa_idx;
    }
    return max_len;
}

long long suffix_index_distinct_substrings(const SuffixIndex *idx) {
    if (!idx || idx->n == 0) return 0;
    long long total = 0;
    for (int i = 0; i < idx->n; ++i) {
        total += (idx->n - idx->sa[i]) - idx->lcp[i];
    }
    return total;
}
```
```cpp
SuffixIndex::SuffixIndex(std::string_view text)
    : text_(text), n_(static_cast<int>(text.size())) {
    if (n_ == 0) return;
    sa_.resize(n_);
    rank_.resize(n_);
    lcp_.resize(n_, 0);

    build_sa();
    build_lcp();
    build_sparse_table();
}

SearchResult SuffixIndex::search(std::string_view pattern) const noexcept {
    SearchResult res;
    if (pattern.empty() || n_ == 0) return res;

    int m = static_cast<int>(pattern.size());

    // 1. Нижня межа
    int low = 0, high = n_ - 1;
    int first = -1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        std::string_view suffix(text_.data() + sa_[mid], std::min(m, n_ - sa_[mid]));
        if (suffix >= pattern) {
            first = mid;
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }

    if (first == -1) return res;

    std::string_view found_suffix(text_.data() + sa_[first], std::min(m, n_ - sa_[first]));
    if (!found_suffix.starts_with(pattern)) {
        return res;
    }

    // 2. Верхня межа
    low = first;
    high = n_ - 1;
    int last = first;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        std::string_view suffix(text_.data() + sa_[mid], std::min(m, n_ - sa_[mid]));
        if (suffix.starts_with(pattern)) {
            last = mid;
            low = mid + 1;
        } else if (suffix < pattern) {
            low = mid + 1;
        } else {
            high = mid - 1;
        }
    }

    res.left = first;
    res.right = last;
    res.count = last - first + 1;
    return res;
}

std::string_view SuffixIndex::longest_repeated_substring() const noexcept {
    if (n_ <= 1) return {};

    int max_len = 0;
    int best_pos = -1;

    for (int i = 1; i < n_; ++i) {
        if (lcp_[i] > max_len) {
            max_len = lcp_[i];
            best_pos = sa_[i];
        }
    }

    if (best_pos == -1 || max_len == 0) return {};
    return std::string_view(text_.data() + best_pos, max_len);
}

int64_t SuffixIndex::count_distinct_substrings() const noexcept {
    int64_t total = 0;
    for (int i = 0; i < n_; ++i) {
        total += (n_ - sa_[i]) - lcp_[i];
    }
    return total;
}
```
:::

---

## 5. Практичне тестування та верифікація

Наступна тестова програма перевіряє коректність роботи індексу на класичному прикладі `"banana"`.

:::tabs
```c
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
```
```cpp
#include <iostream>

int main() {
    std::string_view text = "banana";
    SuffixIndex index(text);

    std::cout << "=== Суфіксний індекс для тексту: \"" << text << "\" ===\n\n";
    std::cout << " k | SA[k] | LCP[k] | Суфікс тексту\n";
    std::cout << "---+-------+--------+-----------------\n";

    auto sa = index.get_sa();
    auto lcp = index.get_lcp();
    for (size_t i = 0; i < sa.size(); ++i) {
        std::cout << " " << i << " |   " << sa[i] << "   |   " << lcp[i] 
                  << "    | " << text.substr(sa[i]) << "\n";
    }

    auto repeated = index.longest_repeated_substring();
    std::cout << "\nНайдовший повторюваний підрядок: \"" << repeated 
              << "\" (довжина " << repeated.size() << ")\n";

    auto distinct = index.count_distinct_substrings();
    std::cout << "Кількість унікальних підрядків: " << distinct << " (очікувано 15)\n";

    int lcp_1_3 = index.query_lcp(1, 3);
    std::cout << "Швидкий запит LCP(SA[1], SA[3]) через Sparse Table: " 
              << lcp_1_3 << " (\"a\")\n";

    std::string_view query = "an";
    auto res = index.search(query);
    std::cout << "\nПошук зразка \"" << query << "\": знайдено " << res.count 
              << " входжень у діапазоні SA[" << res.left << ".." << res.right << "]:\n";
    if (res.found()) {
        for (int i = res.left; i <= res.right; ++i) {
            std::cout << "  -> зсув у тексті: " << sa[i] 
                      << " (підрядок \"" << text.substr(sa[i]) << "\")\n";
        }
    }

    return 0;
}
```
:::

---

## 6. Інженерні пастки та оптимізації продуктивності

При промисловому розгортанні суфіксних індексів слід зважати на такі апаратні та алгоритмічні аспекти:
1. **Просторова локальність проти Pointer Chasing.** Масиви `sa`, `rank` та `lcp` розташовані в неперервних блоках пам'яті. Це забезпечує максимальну швидкість читання за рахунок апаратної вибірки рядків кешу (Cache Lines по 64 байти). На відміну від суфіксних дерев, де кожен перехід за покажчиком викликає промах кешу L1/L2, сканування масиву LCP або бінарний пошук у SA працюють у 10–30 разів швидше на реальних процесорах;
2. **Обмеження 32-бітної адресації.** При розмірі тексту `N > 2·10⁹` символів (наприклад, повнотекстовий індекс Вікіпедії або великі геноми) масиви `int` переповнюються. Для таких обсягів слід переходити на 64-бітні індекси (`int64_t` або `uint32_t` для `N < 4.29·10⁹`);
3. **Обробка спільних префіксів у бінарному пошуку.** У стандартному бінарному пошуку функція `strncmp` порівнює до `M` символів на кожному кроці. Для довгих зразків (`M > 1000`) слід використовувати алгоритм з оптимізацією через LCP: якщо відомо, що `LCP(Pattern, L) = k_l` та `LCP(Pattern, R) = k_r`, порівняння починається не з нульового символу, а з позиції `min(k_l, k_r)`, що скорочує час пошуку до строгого `O(M + log N)`;
4. **Вирівнювання та SIMD-порівняння.** При порівнянні рядкових префіксів у `search` компілятор може генерувати векторні інструкції AVX2 / AVX-512, порівнюючи по 32 або 64 байти за одну інструкцію `_mm256_cmpeq_epi8`, що практично усуває вплив довжини шаблону `M` на загальний час пошуку для типових запитів;
5. **Профілювання витрат пам'яті.** Повний індекс складається з:
   * Вихідний текст: `1 · N` байтів;
   * Суфіксний масив `SA`: `4 · N` байтів;
   * Масив рангів `Rank`: `4 · N` байтів;
   * Масив `LCP`: `4 · N` байтів;
   * Таблиця `Sparse Table`: `4 · N · ⌈log₂ N⌉` байтів (для `N = 10⁶` це близько `20 · 4N = 80 МБ`).
   Якщо обсяг пам'яті є критичним, масив рангів `Rank` та `Sparse Table` можна видалити після завершення побудови `LCP`, скоротивши розмір індексу до мінімальних `9 байтів на символ` (текст + `SA` + `LCP`), а запити LCP між довільними суфіксами замінити двійковим пошуком або стисненою деревоподібною структурою RMQ за Фішером — Хойном за `O(N)` додаткової пам'яті.
