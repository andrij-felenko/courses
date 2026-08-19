# ⚙️ Реалізація рушія повнотекстового пошуку на інвертованому індексі

Побудова промислового рушія повнотекстового пошуку вимагає ретельного проектування бінарних форматів та структур даних. Збереження постингових списків у вигляді простих динамічних масивів 32-бітних чи 64-бітних цілих чисел швидко вичерпує оперативну пам'ять: корпус із мільярда документів породжує сотні гігабайтів масивів ідентифікаторів, а сканування довгих списків перетворює виконання запитів на нескінченне очікування читання з пам'яті.

У цьому проекті реалізовано повноцінний компактний рушій інвертованого індексу, що поєднує:
1. **Дельта-кодування (d-gaps)** для зменшення розрядності ідентифікаторів документів;
2. **Побайтове стиснення змінної довжини (VByte / Varint)**, що упаковує малі числа в 1–2 байти;
3. **Блокову структуру зі Skip-вказівниками**, що дозволяє перестрибувати нерелевантні діапазони документів без їхнього розпакування;
4. **Алгоритм кон'юнктивного перетину (Boolean AND Intersection)** з одночасною оцінкою релевантності за моделлю Okapi BM25.

---

## 1. Архітектура та організація пам'яті

Індекс організовано за дворівневою схемою:
* **Словник (Lexicon / InvertedIndex):** таблиця, що зіставляє текстовий рядок терма з його постинговим списком та глобальною статистикою (кількістю документів `doc_freq`);
* **Постинговий список (PostingList):** стиснений байтовий буфер дельт, розбитий на фіксовані блоки (по 8 або 128 документів). Кожен блок споряджений заголовком `SkipBlock` із максимальним `DocID` та зміщенням у байтовому потоці.

```
Структура постингового списку в пам'яті:
┌────────────────────────────────────────────────────────────────────────┐
│ PostingList (Term: "пошук", DocFreq: 1050)                             │
├────────────────────────────────────────────────────────────────────────┤
│ Skip Index:                                                            │
│ [Block 0: max_doc=45, byte_offset=0] ──> [Block 1: max_doc=128, ...]   │
├────────────────────────────────────────────────────────────────────────┤
│ Compressed Byte Stream (VByte d-gaps & frequencies):                   │
│ [d=3, tf=2][d=7, tf=1][d=1, tf=5] ... [d=14, tf=1]                     │
└────────────────────────────────────────────────────────────────────────┘
```

### Фізична організація дельт у потоці
Оскільки ідентифікатори документів `DocID` у межах одного терма строго зростають (`d₁ < d₂ < d₃ < ...`), перехід до різниць дельт гарантує, що замість великих чисел у потік записуються малі значення. Для першого елемента дельта дорівнює його власному значенню `d₁`.

Кожен логічний елемент постингу складається з пари значень:
1. `dgap` — різниця ідентифікатора документа;
2. `tf` — локальна частота входження терма в цей документ.

Обидва числа послідовно кодуються форматом `VByte`. Це забезпечує локальність даних: інформація про документ та його частоту зчитується суміжним блоком байтів без додаткових переходів за вказівниками.

---

## 2. Реалізація мовами C та C++

Нижче наведено повні реалізації модуля індексації та пошуку. У варіанті C++ використано сучасні ідіоми: безпечне володіння пам'яттю (RAII), роботу з переглядом пам'яті (`std::span`, `std::string_view`) та об'єктно-орієнтовану інкапсуляцію стану ітератора.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

#define BLOCK_SIZE 8
#define MAX_TERMS 1024

/* --- 1. Побайтове кодування змінної довжини (VByte / Varint) --- */

/* Кодування одного uint32_t числа у буфер VByte. Повертає кількість записаних байтів. */
size_t vbyte_encode(uint32_t val, uint8_t *out) {
    size_t bytes = 0;
    while (val >= 0x80) {
        out[bytes++] = (uint8_t)((val & 0x7F) | 0x80);
        val >>= 7;
    }
    out[bytes++] = (uint8_t)(val & 0x7F);
    return bytes;
}

/* Декодування одного uint32_t числа з буфера VByte. Зсуває вказівник читання. */
uint32_t vbyte_decode(const uint8_t **ptr) {
    uint32_t result = 0;
    uint32_t shift = 0;
    while (1) {
        uint8_t byte = **ptr;
        (*ptr)++;
        result |= (uint32_t)(byte & 0x7F) << shift;
        if (!(byte & 0x80)) {
            break;
        }
        shift += 7;
    }
    return result;
}

/* --- 2. Структури даних інвертованого індексу --- */

typedef struct {
    uint32_t max_doc_id;   /* Максимальний DocID у блоці для швидкого пропуску */
    size_t byte_offset;    /* Зміщення початку блоку в стисненому потоці */
} SkipBlock;

typedef struct {
    uint8_t *data;          /* Стиснений байтовий потік (VByte d-gaps + TF) */
    size_t data_len;
    size_t data_cap;
    SkipBlock *skips;       /* Масив скіп-вказівників над блоками */
    size_t skip_count;
    size_t skip_cap;
    uint32_t last_doc_id;   /* Останній доданий DocID для обчислення дельти */
    uint32_t doc_count;     /* Загальна кількість документів у постингу */
    size_t cur_block_items; /* Кількість елементів у поточному незавершеному блоці */
    size_t cur_block_start; /* Байт-зміщення поточного блоку */
} PostingList;

typedef struct {
    char term[64];
    PostingList postings;
} TermEntry;

typedef struct {
    TermEntry terms[MAX_TERMS];
    size_t term_count;
    uint32_t total_docs;
    double avg_doc_len;
    uint32_t doc_lengths[1024]; /* Довжини документів для BM25 */
} InvertedIndex;

/* Ініціалізація постингового списку */
void posting_list_init(PostingList *pl) {
    pl->data_cap = 64;
    pl->data_len = 0;
    pl->data = (uint8_t *)malloc(pl->data_cap);
    pl->skip_cap = 8;
    pl->skip_count = 0;
    pl->skips = (SkipBlock *)malloc(pl->skip_cap * sizeof(SkipBlock));
    pl->last_doc_id = 0;
    pl->doc_count = 0;
    pl->cur_block_items = 0;
    pl->cur_block_start = 0;
}

void posting_list_free(PostingList *pl) {
    free(pl->data);
    free(pl->skips);
}

/* Додавання документа до постингового списку */
void posting_list_append(PostingList *pl, uint32_t doc_id, uint32_t tf) {
    if (pl->doc_count == 0) {
        pl->cur_block_start = 0;
    }

    uint32_t dgap = (pl->doc_count == 0) ? doc_id : (doc_id - pl->last_doc_id);
    pl->last_doc_id = doc_id;
    pl->doc_count++;

    /* Запис d-gap та tf у VByte буфер */
    uint8_t buf[10];
    size_t enc_sz = vbyte_encode(dgap, buf);
    enc_sz += vbyte_encode(tf, buf + enc_sz);

    if (pl->data_len + enc_sz > pl->data_cap) {
        pl->data_cap *= 2;
        pl->data = (uint8_t *)realloc(pl->data, pl->data_cap);
    }
    memcpy(pl->data + pl->data_len, buf, enc_sz);
    pl->data_len += enc_sz;

    pl->cur_block_items++;
    if (pl->cur_block_items == BLOCK_SIZE) {
        /* Фіксація завершеного блоку в Skip Index */
        if (pl->skip_count >= pl->skip_cap) {
            pl->skip_cap *= 2;
            pl->skips = (SkipBlock *)realloc(pl->skips, pl->skip_cap * sizeof(SkipBlock));
        }
        pl->skips[pl->skip_count].max_doc_id = doc_id;
        pl->skips[pl->skip_count].byte_offset = pl->cur_block_start;
        pl->skip_count++;

        pl->cur_block_items = 0;
        pl->cur_block_start = pl->data_len;
    }
}

/* Фіналізація індексу: закриття останнього неповного блоку */
void posting_list_finalize(PostingList *pl) {
    if (pl->cur_block_items > 0) {
        if (pl->skip_count >= pl->skip_cap) {
            pl->skip_cap += 1;
            pl->skips = (SkipBlock *)realloc(pl->skips, pl->skip_cap * sizeof(SkipBlock));
        }
        pl->skips[pl->skip_count].max_doc_id = pl->last_doc_id;
        pl->skips[pl->skip_count].byte_offset = pl->cur_block_start;
        pl->skip_count++;
        pl->cur_block_items = 0;
    }
}

/* --- 3. Ітератор постингового списку зі Skip-підтримкою --- */

typedef struct {
    const PostingList *pl;
    const uint8_t *cursor;
    const uint8_t *end;
    size_t current_skip_idx;
    uint32_t current_doc_id;
    uint32_t current_tf;
    bool at_end;
} PostingIterator;

void iterator_init(PostingIterator *it, const PostingList *pl) {
    it->pl = pl;
    it->cursor = pl->data;
    it->end = pl->data + pl->data_len;
    it->current_skip_idx = 0;
    it->current_doc_id = 0;
    it->current_tf = 0;
    it->at_end = (pl->doc_count == 0);
    if (!it->at_end) {
        /* Читання першого запису */
        uint32_t dgap = vbyte_decode(&it->cursor);
        it->current_doc_id = dgap;
        it->current_tf = vbyte_decode(&it->cursor);
    }
}

/* Перехід до наступного елемента */
void iterator_next(PostingIterator *it) {
    if (it->cursor >= it->end) {
        it->at_end = true;
        return;
    }
    uint32_t dgap = vbyte_decode(&it->cursor);
    it->current_doc_id += dgap;
    it->current_tf = vbyte_decode(&it->cursor);
}

/* Стрибок (Advance / Skip) до документа з DocID >= target_doc */
void iterator_advance(PostingIterator *it, uint32_t target_doc) {
    if (it->at_end || it->current_doc_id >= target_doc) {
        return;
    }

    /* 1. Стрибок по скіп-індексу через цілі блоки */
    while (it->current_skip_idx + 1 < it->pl->skip_count &&
           it->pl->skips[it->current_skip_idx].max_doc_id < target_doc) {
        it->current_skip_idx++;
        it->cursor = it->pl->data + it->pl->skips[it->current_skip_idx].byte_offset;
        /* Перезапуск базового doc_id для нового блоку */
        if (it->current_skip_idx > 0) {
            it->current_doc_id = it->pl->skips[it->current_skip_idx - 1].max_doc_id;
        } else {
            it->current_doc_id = 0;
        }
    }

    /* 2. Лінійне сканування всередині цільового блоку */
    while (!it->at_end && it->current_doc_id < target_doc) {
        if (it->cursor >= it->end) {
            it->at_end = true;
            break;
        }
        uint32_t dgap = vbyte_decode(&it->cursor);
        it->current_doc_id += dgap;
        it->current_tf = vbyte_decode(&it->cursor);
    }
}

/* --- 4. Ранжування Okapi BM25 та перетин списків (AND) --- */

double compute_bm25(uint32_t tf, uint32_t doc_len, double avg_doc_len,
                    uint32_t total_docs, uint32_t doc_freq) {
    double k1 = 1.2;
    double b = 0.75;
    double idf = log(((double)total_docs - (double)doc_freq + 0.5) / ((double)doc_freq + 0.5) + 1.0);
    double b_scale = (1.0 - b) + b * ((double)doc_len / avg_doc_len);
    double tf_norm = ((double)tf * (k1 + 1.0)) / ((double)tf + k1 * b_scale);
    return idf * tf_norm;
}

void search_and_rank(InvertedIndex *idx, const char *term1, const char *term2) {
    PostingList *pl1 = NULL, *pl2 = NULL;
    for (size_t i = 0; i < idx->term_count; i++) {
        if (strcmp(idx->terms[i].term, term1) == 0) pl1 = &idx->terms[i].postings;
        if (strcmp(idx->terms[i].term, term2) == 0) pl2 = &idx->terms[i].postings;
    }

    if (!pl1 || !pl2) {
        printf("Один із термів не знайдено в індексі.\n");
        return;
    }

    PostingIterator it1, it2;
    iterator_init(&it1, pl1);
    iterator_init(&it2, pl2);

    printf("Результати пошуку [ %s AND %s ]:\n", term1, term2);

    while (!it1.at_end && !it2.at_end) {
        if (it1.current_doc_id == it2.current_doc_id) {
            uint32_t did = it1.current_doc_id;
            uint32_t dlen = idx->doc_lengths[did];
            double s1 = compute_bm25(it1.current_tf, dlen, idx->avg_doc_len, idx->total_docs, pl1->doc_count);
            double s2 = compute_bm25(it2.current_tf, dlen, idx->avg_doc_len, idx->total_docs, pl2->doc_count);
            double total_score = s1 + s2;

            printf("  -> DocID: %u | Довжина: %u | BM25 Скор: %.4f (TF1: %u, TF2: %u)\n",
                   did, dlen, total_score, it1.current_tf, it2.current_tf);

            iterator_next(&it1);
            iterator_next(&it2);
        } else if (it1.current_doc_id < it2.current_doc_id) {
            iterator_advance(&it1, it2.current_doc_id);
        } else {
            iterator_advance(&it2, it1.current_doc_id);
        }
    }
}

int main(void) {
    InvertedIndex idx;
    memset(&idx, 0, sizeof(idx));
    idx.total_docs = 100;
    idx.avg_doc_len = 150.0;
    for (uint32_t d = 0; d < 100; d++) {
        idx.doc_lengths[d] = 100 + (d * 7) % 120;
    }

    strcpy(idx.terms[0].term, "алгоритм");
    posting_list_init(&idx.terms[0].postings);
    strcpy(idx.terms[1].term, "пошук");
    posting_list_init(&idx.terms[1].postings);
    idx.term_count = 2;

    /* Додаємо документи до списків */
    posting_list_append(&idx.terms[0].postings, 5, 2);
    posting_list_append(&idx.terms[0].postings, 18, 1);
    posting_list_append(&idx.terms[0].postings, 42, 4);
    posting_list_append(&idx.terms[0].postings, 85, 1);
    posting_list_finalize(&idx.terms[0].postings);

    posting_list_append(&idx.terms[1].postings, 2, 1);
    posting_list_append(&idx.terms[1].postings, 18, 3);
    posting_list_append(&idx.terms[1].postings, 30, 1);
    posting_list_append(&idx.terms[1].postings, 42, 2);
    posting_list_append(&idx.terms[1].postings, 99, 1);
    posting_list_finalize(&idx.terms[1].postings);

    search_and_rank(&idx, "алгоритм", "пошук");

    posting_list_free(&idx.terms[0].postings);
    posting_list_free(&idx.terms[1].postings);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <cmath>
#include <span>
#include <cstdint>

namespace ir {

constexpr size_t BLOCK_SIZE = 8;

/* --- 1. Побайтовий компресор Varint (VByte) --- */
class VByteCodec {
public:
    static void encode(uint32_t val, std::vector<uint8_t>& dest) {
        while (val >= 0x80) {
            dest.push_back(static_cast<uint8_t>((val & 0x7F) | 0x80));
            val >>= 7;
        }
        dest.push_back(static_cast<uint8_t>(val & 0x7F));
    }

    static uint32_t decode(std::span<const uint8_t>& stream) {
        uint32_t result = 0;
        uint32_t shift = 0;
        size_t bytes_read = 0;

        for (uint8_t byte : stream) {
            bytes_read++;
            result |= static_cast<uint32_t>(byte & 0x7F) << shift;
            if (!(byte & 0x80)) {
                break;
            }
            shift += 7;
        }
        stream = stream.subspan(bytes_read);
        return result;
    }
};

/* --- 2. Постинговий список із блоковими Skip-покажчиками --- */
struct SkipBlock {
    uint32_t max_doc_id;
    size_t byte_offset;
};

class PostingList {
public:
    PostingList() = default;

    void append(uint32_t doc_id, uint32_t tf) {
        if (doc_count_ == 0) {
            cur_block_start_ = 0;
        }

        uint32_t dgap = (doc_count_ == 0) ? doc_id : (doc_id - last_doc_id_);
        last_doc_id_ = doc_id;
        doc_count_++;

        VByteCodec::encode(dgap, data_);
        VByteCodec::encode(tf, data_);

        cur_block_items_++;
        if (cur_block_items_ == BLOCK_SIZE) {
            skips_.push_back({doc_id, cur_block_start_});
            cur_block_items_ = 0;
            cur_block_start_ = data_.size();
        }
    }

    void finalize() {
        if (cur_block_items_ > 0) {
            skips_.push_back({last_doc_id_, cur_block_start_});
            cur_block_items_ = 0;
        }
    }

    [[nodiscard]] const std::vector<uint8_t>& data() const noexcept { return data_; }
    [[nodiscard]] const std::vector<SkipBlock>& skips() const noexcept { return skips_; }
    [[nodiscard]] uint32_t doc_count() const noexcept { return doc_count_; }

private:
    std::vector<uint8_t> data_;
    std::vector<SkipBlock> skips_;
    uint32_t last_doc_id_ = 0;
    uint32_t doc_count_ = 0;
    size_t cur_block_items_ = 0;
    size_t cur_block_start_ = 0;
};

/* --- 3. Стрибковий ітератор (Skip Iterator) --- */
class PostingIterator {
public:
    explicit PostingIterator(const PostingList& pl)
        : pl_(pl), stream_(pl.data()) {
        if (pl_.doc_count() > 0) {
            uint32_t dgap = VByteCodec::decode(stream_);
            current_doc_id_ = dgap;
            current_tf_ = VByteCodec::decode(stream_);
        } else {
            at_end_ = true;
        }
    }

    [[nodiscard]] bool at_end() const noexcept { return at_end_; }
    [[nodiscard]] uint32_t doc_id() const noexcept { return current_doc_id_; }
    [[nodiscard]] uint32_t tf() const noexcept { return current_tf_; }

    void next() {
        if (stream_.empty()) {
            at_end_ = true;
            return;
        }
        uint32_t dgap = VByteCodec::decode(stream_);
        current_doc_id_ += dgap;
        current_tf_ = VByteCodec::decode(stream_);
    }

    void advance(uint32_t target_doc) {
        if (at_end_ || current_doc_id_ >= target_doc) {
            return;
        }

        const auto& skips = pl_.skips();
        while (skip_idx_ + 1 < skips.size() && skips[skip_idx_].max_doc_id < target_doc) {
            skip_idx_++;
            size_t offset = skips[skip_idx_].byte_offset;
            stream_ = std::span<const uint8_t>(pl_.data()).subspan(offset);
            current_doc_id_ = (skip_idx_ > 0) ? skips[skip_idx_ - 1].max_doc_id : 0;
        }

        while (!at_end_ && current_doc_id_ < target_doc) {
            if (stream_.empty()) {
                at_end_ = true;
                break;
            }
            uint32_t dgap = VByteCodec::decode(stream_);
            current_doc_id_ += dgap;
            current_tf_ = VByteCodec::decode(stream_);
        }
    }

private:
    const PostingList& pl_;
    std::span<const uint8_t> stream_;
    size_t skip_idx_ = 0;
    uint32_t current_doc_id_ = 0;
    uint32_t current_tf_ = 0;
    bool at_end_ = false;
};

/* --- 4. Повнотекстовий індекс та ранжування BM25 --- */
struct SearchResult {
    uint32_t doc_id;
    double score;
};

class SearchIndex {
public:
    explicit SearchIndex(uint32_t total_docs, double avg_doc_len)
        : total_docs_(total_docs), avg_doc_len_(avg_doc_len), doc_lengths_(total_docs, 100) {}

    void set_doc_length(uint32_t doc_id, uint32_t len) {
        if (doc_id < doc_lengths_.size()) {
            doc_lengths_[doc_id] = len;
        }
    }

    void add_term_entry(std::string_view term, uint32_t doc_id, uint32_t tf) {
        index_[std::string(term)].append(doc_id, tf);
    }

    void finalize() {
        for (auto& [term, plist] : index_) {
            plist.finalize();
        }
    }

    [[nodiscard]] std::vector<SearchResult> search_and(std::string_view t1, std::string_view t2) const {
        auto it1_entry = index_.find(std::string(t1));
        auto it2_entry = index_.find(std::string(t2));

        if (it1_entry == index_.end() || it2_entry == index_.end()) {
            return {};
        }

        const auto& pl1 = it1_entry->second;
        const auto& pl2 = it2_entry->second;

        PostingIterator it1(pl1);
        PostingIterator it2(pl2);
        std::vector<SearchResult> results;

        while (!it1.at_end() && !it2.at_end()) {
            if (it1.doc_id() == it2.doc_id()) {
                uint32_t did = it1.doc_id();
                uint32_t dlen = doc_lengths_[did];

                double s1 = bm25_score(it1.tf(), dlen, pl1.doc_count());
                double s2 = bm25_score(it2.tf(), dlen, pl2.doc_count());
                results.push_back({did, s1 + s2});

                it1.next();
                it2.next();
            } else if (it1.doc_id() < it2.doc_id()) {
                it1.advance(it2.doc_id());
            } else {
                it2.advance(it1.doc_id());
            }
        }
        return results;
    }

private:
    [[nodiscard]] double bm25_score(uint32_t tf, uint32_t doc_len, uint32_t doc_freq) const noexcept {
        constexpr double k1 = 1.2;
        constexpr double b = 0.75;
        double idf = std::log((static_cast<double>(total_docs_) - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0);
        double b_scale = (1.0 - b) + b * (static_cast<double>(doc_len) / avg_doc_len_);
        double tf_norm = (static_cast<double>(tf) * (k1 + 1.0)) / (static_cast<double>(tf) + k1 * b_scale);
        return idf * tf_norm;
    }

    uint32_t total_docs_;
    double avg_doc_len_;
    std::vector<uint32_t> doc_lengths_;
    std::unordered_map<std::string, PostingList> index_;
};

} // namespace ir

int main() {
    ir::SearchIndex index(100, 150.0);

    for (uint32_t d = 0; d < 100; ++d) {
        index.set_doc_length(d, 100 + (d * 7) % 120);
    }

    index.add_term_entry("алгоритм", 5, 2);
    index.add_term_entry("алгоритм", 18, 1);
    index.add_term_entry("алгоритм", 42, 4);
    index.add_term_entry("алгоритм", 85, 1);

    index.add_term_entry("пошук", 2, 1);
    index.add_term_entry("пошук", 18, 3);
    index.add_term_entry("пошук", 30, 1);
    index.add_term_entry("пошук", 42, 2);
    index.add_term_entry("пошук", 99, 1);

    index.finalize();

    auto matches = index.search_and("алгоритм", "пошук");
    std::cout << "Результати C++ пошуку [ алгоритм AND пошук ]:\n";
    for (const auto& match : matches) {
        std::cout << "  -> DocID: " << match.doc_id
                  << " | BM25 Скор: " << match.score << "\n";
    }

    return 0;
}
```
:::

---

## 3. Покроковий розбір кодування та декодування VByte

Формат `VByte` (або `Varint`) використовує старший біт (`MSB`, біт номер 7) кожного байта як індикатор продовження послідовності (**continuation bit**), а молодші 7 бітів (біти 0–6) — для збереження корисного навантаження числа.

### Алгоритм кодування (Little-Endian VByte)
1. Число перевіряється на умову `val >= 0x80` (чи перевищує воно 127);
2. Якщо число більше або дорівнює 128, записується байт `(val & 0x7F) | 0x80` — молодші 7 біт зі встановленим старшим бітом продовження;
3. Число зсувається праворуч на 7 бітів: `val >>= 7`;
4. Процедура повторюється, доки в числі не залишиться менше 128;
5. Останній байт записується як `val & 0x7F` із нульовим старшим бітом, що свідчить про кінець поточного числа.

```
Трасування кодування числа delta = 855:
1. Двійкове представлення 855: 00000011 01010111 (10 біт)
2. Перший крок:
   - Молодші 7 біт (855 & 0x7F): 1010111 (число 87)
   - Встановлюємо MSB: 1010111 | 0x80 = 11010111 (0xD7)
   - Зсув на 7: 855 >> 7 = 6
3. Другий крок:
   - Залишок 6 < 128, скидаємо MSB: 00000110 (0x06)
4. Результат у пам'яті: [ 0xD7, 0x06 ] (рівно 2 байти)
```

### Алгоритм декодування
Під час читання ітератор послідовно вибирає байти:
* Витягує 7 бітів: `byte & 0x7F`;
* Зсуває їх на накопичений лічильник `shift` (0, 7, 14, 21, 28) та об'єднує побітовим `OR` із результуючим акумулятором;
* Якщо біт `0x80` встановлено — збільшує `shift += 7` і переходить до наступного байта;
* Якщо біт `0x80` дорівнює нулю — число завершено, результат повертається викликачу.

---

## 4. Стрибкова механіка ітератора (Skip Navigation)

Стрибковий пошук `iterator_advance(target_doc)` є ключем до швидкого виконання кон'юнктивних запитів. Розглянемо його роботу на рівні кінцевого автомата.

Коли пошуковий алгоритм порівнює два списки постингу і з'ясовує, що поточний `it1.doc_id < it2.doc_id`, йому не потрібно перебирати всі проміжні документи першого списку. Він викликає `it1.advance(it2.doc_id)`.

```
Схема прийняття рішень під час Advance(target_doc):
                   ┌────────────────────────────────────┐
                   │        it.current_doc >= target?   │
                   └─────────────────┬──────────────────┘
                                     │
                         ┌───────────┴───────────┐
                        Так                     Ні
                         │                       │
                  [Нічого не робити]    ┌────────────────────────┐
                                        │  skip_idx+1 < skips?   │
                                        │  skips[idx].max < target?│
                                        └───────────┬────────────┘
                                                    │
                                        ┌───────────┴───────────┐
                                       Так                     Ні
                                        │                       │
                               [Стрибок на блок:          [Лінійне дочитування
                                cursor = offset,           всередині блоку
                                doc_id = prev.max]         до doc >= target]
```

### Відновлення дельта-базису при стрибку
Найнебезпечніша помилка при реалізації скіп-ітераторів — це втрата абсолютного базису дельт. Оскільки всередині блоку числа стиснені як різниці, перше число в блоці відраховується від максимального `DocID` попереднього блоку:

```
doc_id_в_блоці_1 = skips[0].max_doc_id + dgap_1
```

Якщо ітератор стрибає безпосередньо за байтовим зміщенням `byte_offset`, він зобов'язаний встановити свій внутрішній акумулятор `current_doc_id` у значення `skips[current_skip_idx - 1].max_doc_id` (або `0`, якщо це перший блок). Без цього відновлення перша прочитана дельта додасться до випадкового значення, і весь список спотвориться.

---

## 5. Розширення до позиційного індексу та фразовий пошук

Для підтримки точного фразового пошуку (наприклад, `"структури даних"`, де слова мають стояти строго поруч) або операторів близькості (`NEAR / WITHIN k`), постинговий запис розширюється збереженням списку позицій кожного входження слова в документі.

### Формат позиційного постингу
У межах документа позиції входжень `pos₁, pos₂, ..., pos_tf` також строго зростають (`pos_i < pos_{i+1}`). Тому до них застосовується те саме дельта-кодування:

```
Позиційний запис документа:
[dgap_doc] [tf] [pos_1] [pos_2 - pos_1] [pos_3 - pos_2] ...
```

Якщо слово `"пошук"` зустрічається у документі `42` на позиціях `12`, `15` та `28`, у байтовий потік після `DocID` та `TF = 3` записується послідовність дельт: `[12, 3, 13]`.

### Алгоритм перевірки фразового збігу
Коли кон'юнктивний ітератор знаходить збіг за `DocID` для двох термів `t₁` та `t₂`, активується позиційний верифікатор:
1. Ініціалізуються два покажчики на списки позицій: `p₁ = 0` та `p₂ = 0`;
2. Перевіряється умова суміжності: `pos₂(p₂) == pos₁(p₁) + 1`;
3. Якщо умова виконується, знайдено точний фразовий збіг;
4. Якщо `pos₂(p₂) <= pos₁(p₁)`, зсувається покажчик другого терма: `p₂++`;
5. Якщо `pos₂(p₂) > pos₁(p₁) + 1`, зсувається покажчик першого терма: `p₁++`;
6. Цикл триває, поки один із покажчиків не досягне кінця свого локального масиву позицій.

Завдяки впорядкованості позицій складність перевірки фрази всередині документа становить `O(tf₁ + tf₂)`, що виконується практично миттєво в пам'яті.

---

## 6. Алгоритм WAND (Weak AND) для динамічного відсікання

Коли запит складається з багатьох слів (наприклад, 5–10 термів), точний перетин `AND` може повертати занадто мало документів, тоді як диз'юнкція `OR` змушена сканувати мільйони записів. Алгоритм **WAND** (Weak AND) дозволяє знаходити `Top-K` найрелевантніших документів без повного обходу диз'юнктивних списків.

### Механіка роботи WAND:
1. Для кожного терма запиту `t` на етапі побудови індексу обчислюється максимальний теоретичний внесок (Upper Bound):
   ```
   U_t = max_{D} BM25(t, D) = IDF(t) · (k₁ + 1)
   ```
2. Підтримується черга з пріоритетом (Min-Heap) із `K` найкращих знайдених документів. Поточний мінімальний бал у цій черзі позначається як поріг `θ` (**threshold**);
3. Усі ітератори постингових списків запиту впорядковуються за зростанням їхніх поточних `DocID`:
   ```
   it_1.doc_id ≤ it_2.doc_id ≤ it_3.doc_id ≤ ... ≤ it_m.doc_id
   ```
4. Алгоритм послідовно підсумовує верхні межі `U_t` ітераторів, доки накопичена сума не перевищить поріг `θ`:
   ```
   ∑ U_{it_i} ≥ θ
   ```
   Ітератор під індексом `p` називається **опорним ітератором** (**pivot iterator**), а його документ — опорним документом `pivot_doc = it_p.doc_id`;
5. Якщо для першого ітератора `it_1.doc_id == pivot_doc`, отже, всі ітератори від 1 до `p` вказують на той самий документ. Обчислюється точний бал `BM25` для `pivot_doc`. Якщо він більший за `θ`, черга Top-K оновлюється, а поріг `θ` зростає;
6. Якщо `it_1.doc_id < pivot_doc`, перший ітератор здійснює прямий стрибок `it_1.advance(pivot_doc)`.

Завдяки цьому WAND перестрибує понад 90–95% неконкурентних документів, скорочуючи час обробки багатослівних запитів на порядок.

---

## 7. Блокове векторне стиснення: SIMD-PForDelta та SIMD-BP128

Хоча побайтовий `VByte` є простим в інженерній реалізації, він має принципову межу швидкодії на сучасних багатоядерних процесорах: розпакування кожного байта вимагає послідовних зсувів і перевірок умов, що обмежує швидкість декодування приблизно 200–400 мільйонами цілих чисел на секунду на одне ядро.

Сучасні пошукові системи (Tantivy, Lucene, Quickwit) для досягнення пропускної здатності понад 2–4 мільярди чисел на секунду застосовують блокове бітове пакування (**Bit Packing**) та алгоритми **PForDelta** (Patched Frame of Reference).

```
Схема бітового пакування блоку зі 128 чисел:
1. Знаходження b = ceil(log2(max delta)):
   Якщо 90% чисел у блоці < 16, вибираємо ширину b = 4 біти.
2. Пакування 128 чисел по 4 біти -> рівно 64 байти (замість 512 байтів uint32).
3. Аномалії (Patches):
   Числа, які не влізли в 4 біти (наприклад, delta = 855), записуються в окремий
   масив винятків у кінці блоку разом зі своїми 7-бітними індексами зміщення.
```

Векторні розширення процесорів (Intel AVX2 / AVX-512 та ARM NEON) дозволяють розпакувати весь 64-байтний потік у масив 32-розрядних регістрів за кілька векторних операцій зсуву та побітового маскування без жодного розгалуження:

```
Векторне розпакування 8 чисел за такт (AVX2):
__m256i packed = _mm256_loadu_si256((__m256i*)src);
__m256i unpacked = _mm256_and_si256(_mm256_srli_epi32(packed, shift), mask);
```

---

## 8. Block-Max WAND (BMW): Сучасний стандарт швидкого ранжування

У класичному WAND використовується єдина глобальна верхня оцінка `U_t` на весь постинговий список терма. Проте реальні частоти слів та довжини документів суттєво варіюються: в одному документі слово зустрічається 1 раз, а в іншому — 20 разів.

Алгоритм **Block-Max WAND (BMW)** (Ding & Suel, 2011) інтегрує блокову структуру постингу та локальні оцінки верхньої межі:
* Для кожного фізичного блоку (зі 128 документів) у заголовок блоку записується локальний максимум:
  ```
  U_{t, block} = max_{D ∈ block} BM25(t, D)
  ```
* Під час виконання запиту сума `∑ U_{t, block}` обчислюється не за глобальними константами, а за точними локальними максимумами поточних блоків;
* Якщо сума локальних максимумів для поточної комбінації блоків не досягає порогу `θ`, весь блок зі 128 документів ігнорується без декодування жодного байта.

BMW зменшує кількість розпакованих блоків на додаткові 60–80% порівняно з базовим WAND, забезпечуючи час відповіді менше 5–10 мілісекунд навіть на колекціях із десятків мільйонів документів на одному сервері.

---

## 9. Побітові коди: Elias-gamma та Elias-delta

Коли постинговий список є надзвичайно щільним (наприклад, для частих слів, що зустрічаються майже в кожному третьому чи четвертому документі), типові значення дельт становлять `1, 2, 3, 4`. За таких умов побайтовий `VByte` витрачає цілий байт (8 бітів) на збереження числа `1`, що є неекономним.

У таких сценаріях застосовують побітове стиснення за схемами Пітера Еліаса:

### Elias-γ (Гамма-код)
Число `x ≥ 1` розбивається на ступінь двійки `2^k` та залишок `d`:
1. Довжина `k = floor(log2(x))` записується в унарному коді як `k` нулів, за якими слідує одиниця;
2. Двійковий залишок `x - 2^k` записується як `k` бітів звичайного двійкового числа.

```
Приклади кодування Elias-gamma:
x = 1: k = 0 -> унарний код '1'               -> результат: 1        (1 біт)
x = 2: k = 1 -> унарний код '01', залишок '0' -> результат: 010      (3 біти)
x = 3: k = 1 -> унарний код '01', залишок '1' -> результат: 011      (3 біти)
x = 9: k = 3 -> унарний код '0001', зал. '001' -> результат: 0001001  (7 бітів)
```

### Elias-δ (Дельта-код)
Для більших чисел унарне кодування довжини `k` у гамма-коді стає неефективним. Дельта-код кодує саму довжину `k + 1` за допомогою гамма-коду, що скорочує довжину бітового представлення для великих дельт до `O(log(x) + 2·log(log(x)))`.

```
Порівняння витрат пам'яті для 100 000 постингових записів:
Схема кодування             Розмір у RAM   Швидкість декодування
─────────────────────────────────────────────────────────────────
Нестиснений uint32_t        400 KB         > 10.0 млрд чисел/с (пряме читання)
VByte (Varint)              110 KB         0.3 – 0.5 млрд чисел/с
Elias-gamma                 65 KB          0.05 – 0.1 млрд чисел/с (побітовий зсув)
SIMD-PForDelta / BP128      72 KB          2.5 – 4.0 млрд чисел/с
```

---

## 10. Дискова організація сегментів у промислових системах

У виробничих сховищах (наприклад, Apache Lucene) пам'ять не тримає всі списки постингу в купі процесу. Структура розбивається на сукупність спеціалізованих дискових файлів із префіксом сегмента:

```
Специфікація дискових файлів сегмента:
Розширення  Призначення                        Структура збереження
─────────────────────────────────────────────────────────────────────────────────
.tim        Словник термів (Term Dictionary)   Блокове FST-дерево суфіксів слів
.tip        Префіксний індекс термів           Компактний FST у пам'яті (RAM)
.doc        Списки постингу DocID та частот   SIMD-BP128 блоки + Skip Index
.pos        Позиції слів у документах          d-gaps VByte масиви
.pay        Корисні навантаження (Payloads)    Байти зміщень символів та прапорці
.del        Бітова маска видалених документів  Roaring Bitmap живих DocID
```

При виконанні запиту система:
1. За кілька мікросекунд знаходить терм у `.tip` (FST у пам'яті) та отримує точний дисковий офсет у файлі `.tim`;
2. Читає заголовок терма з `.tim`, який вказує на початок постингового списку у `.doc`;
3. Здійснює пряме читання сторінок із `.doc` через системний `mmap()` без проміжного копіювання в пам'ять користувача.

---

## 11. Кешування та бітові маски Roaring Bitmaps

Для часто повторюваних фільтрів (наприклад, `status:published` або `category:electronics`) багаторазове сканування постингових списків є марнотратним. Рушії використовують **Filter Cache**, де результати обчислення булевих умов зберігаються у вигляді стиснених бітових масивів **Roaring Bitmaps**.

### Архітектура Roaring Bitmap:
Простір 32-бітних `DocID` розбивається на чанки по 65536 чисел:
1. **Array Container:** якщо в чанку менше 4096 документів, вони зберігаються як відсортований масив `uint16_t` (до 8 KB);
2. **Bitmap Container:** якщо в чанку більше 4096 документів, вони зберігаються як бітова карта з 65536 біт (фіксовано 8 KB);
3. **Run Container:** якщо документи йдуть неперервними послідовностями (діапазонами), вони кодуються парами `[start, length]`.

Побітові операції `AND` та `OR` між Roaring Bitmaps виконуються за допомогою SIMD інструкцій процесора над цілими 8-кілобайтними блоками за лічені наносекунди.

---

## 12. Пастки продуктивності та крайові випадки

### 1. Штраф за промахи передбачення розгалужень (Branch Misprediction)
У функції `vbyte_decode` внутрішній цикл перевіряє умову `!(byte & 0x80)` для кожного прочитаного байта. Оскільки більшість дельт у реальних індексах є малими числами і займають 1 байт, процесор майже завжди прогнозує вихід із циклу. Проте на розріджених термах, де дельти великі, виникають регулярні промахи передбачення, які скидають конвеєр процесора на 15–20 тактів.

### 2. Вибір розміру блоку `BLOCK_SIZE`
Розмір блоку визначає просторово-часовий компроміс:
* Малий блок (`B = 4` або `B = 8`): скіп-індекс забезпечує майже миттєвий стрибок точно до шуканого документа, але сам масив `skips_` розростається в пам'яті, створюючи додатковий тиск на кеш `L1/L2`;
* Великий блок (`B = 128` або `B = 256`): скіп-індекс займає мізерну частку пам'яті (менше 1%), але всередині блоку доводиться лінійно декодувати в середньому `B / 2` зайвих чисел.

Для більшості корпусів оптимальним є значення `B = 128`, оскільки лінійне розпакування 128 чисел у щільному кеші процесора відбувається швидше, ніж випадкове читання роздутого масиву покажчиків.

### 3. Порядок обходу термів при багаторівневому AND
Якщо запит містить три або більше слів (наприклад, `алгоритм AND пошук AND граф`), об'єднання списків необхідно виконувати за стратегією **Smallest vs Smallest (SvS)**:
1. Списки постингу сортуються за зростанням їхньої довжини `doc_count`: найкоротший список стає провідним (**lead iterator**);
2. Провідний ітератор покроково зчитує свої `DocID`, а всі інші ітератори виконують стрибки `advance(lead_doc)`.

Оскільки найкоротший список містить мінімальну кількість кандидатів, кількість операцій перевірки мінімізується з `O(∑ |L_i|)` до `O(|L_min| · ∑ log |L_i|)`.

### 4. Робота з відображеною пам'яттю (Memory Mapping / mmap)
У промислових пошукових базах даних постингові списки не завантажуються в купу (Heap) через `malloc` або `new`. Замість цього файли індексу відображаються у віртуальний адресний простір процесу за допомогою системного виклику `mmap()` (POSIX) або `CreateFileMapping()` (Windows). Операційна система автоматично кешує сторінки файлу в системному Page Cache. Це усуває накладні витрати на копіювання пам'яті між ядром та користувацьким простором (zero-copy I/O) і дозволяє декільком процесам безпечно спільно читати той самий індекс.

### 5. Алокатори пам'яті на базі арен (Arena Allocators)
Під час паралельної обробки тисяч користувацьких запитів виділення динамічної пам'яті під тимчасові масиви ітераторів та скорів через системний `malloc` призводить до фрагментації купи та блокування глобального м'ютекса алокатора (lock contention).

Високопродуктивні рушії застосовують **позапитну арену пам'яті** (Per-Query Arena / Bump Allocator):
* На початку обробки запиту з пулу виділяється фіксований неперервний блок пам'яті (наприклад, 64 KB або 256 KB);
* Усі внутрішні структури (масиви ітераторів, буфери розпакованих дельт, черги Top-K) розміщуються простим зсувом вказівника верхівки арени (`offset += size`);
* Після повернення відповіді клієнту вся арена скидається в нуль за одну операцію (`offset = 0`), без жодного виклику системного `free()`. Це повністю усуває затримки на деалокацію та гарантує нульову фрагментацію пам'яті в багатопотоковому середовищі.
