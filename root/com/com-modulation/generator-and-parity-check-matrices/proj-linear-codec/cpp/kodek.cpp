#include <bit>        // std::popcount (C++20)
#include <cstdint>
#include <queue>
#include <vector>

using word = std::uint32_t;   // слово, рядок і стовпець — усе це маски; звідси межа n ≤ 32

// Рядок матриці, ЯК НАДРУКОВАНО, зліва направо ("110") → маска: позиція i ↔ біт i.
// Уся домовленість про порядок бітів живе тут і більше ніде.
constexpr word bits(const char* s)
{
    word m = 0;
    for (int i = 0; s[i] != '\0'; ++i)
        if (s[i] == '1') m |= word{1} << i;
    return m;
}

class LinearCode {
public:
    // P — k рядків по (n−k) бітів; більше про код знати нічого не треба.
    LinearCode(int n, int k, const std::vector<word>& P)
        : n_(n), k_(k), g_(k), hcol_(n), table_(std::size_t{1} << (n - k), NONE)
    {
        for (int j = 0; j < k; ++j)
            g_[j] = (word{1} << j) | (P[j] << k);            // G = [ I | P ]

        for (int j = 0; j < n; ++j)                          // стовпці H = [ Pᵀ | I ]:
            hcol_[j] = (j < k) ? P[j]                        //   рядок P, як лежить
                               : (word{1} << (j - k));       //   одиничний вектор

        for (int i = 0; i < n - k; ++i) {                    // рядки H — для другого шляху
            word row = word{1} << (k + i);
            for (int j = 0; j < k; ++j)
                row |= ((P[j] >> i) & 1u) << j;
            hrow_.push_back(row);
        }
        buildLeaders();
    }

    int n() const { return n_; }
    int k() const { return k_; }

    word encode(word m)   const { return xorSelected(g_, m); }
    word syndrome(word r) const { return xorSelected(hcol_, r); }

    // Той самий синдром «по рядках»: n−k згорток замість n проходів.
    // Для кодів із високою швидкістю (n−k мале) помітно дешевше.
    word syndromeByRows(word r) const
    {
        word s = 0;
        for (std::size_t i = 0; i < hrow_.size(); ++i)
            s |= word(std::popcount(hrow_[i] & r) & 1) << i;
        return s;
    }

    struct Fix { word data; word err; };      // err — які саме біти ми перевернули
    Fix decode(word r) const
    {
        word e = table_[syndrome(r)];         // table_[0] == 0 → чисте слово лишиться цілим
        word c = r ^ e;
        return { c & ((word{1} << k_) - 1), e };   // систематичність: дані — нижні k бітів
    }

private:
    static constexpr word NONE = ~word{0};

    // Єдиний примітив: XOR тих масок, проти яких у селекторі стоїть одиниця.
    static word xorSelected(const std::vector<word>& masks, word selector)
    {
        word acc = 0;
        for (std::size_t i = 0; i < masks.size(); ++i)
            if (selector >> i & 1u) acc ^= masks[i];
        return acc;
    }

    // Лідери суміжних класів = найкоротші шляхи від нульового синдрому.
    void buildLeaders()
    {
        table_[0] = 0;
        std::queue<word> q;
        q.push(0);
        while (!q.empty()) {
            word s = q.front(); q.pop();
            for (std::size_t j = 0; j < hcol_.size(); ++j) {
                word s2 = s ^ hcol_[j];
                if (table_[s2] == NONE) {            // перший, хто дійшов, — найлегший
                    table_[s2] = table_[s] ^ (word{1} << j);
                    q.push(s2);
                }
            }
        }
    }

    int n_, k_;
    std::vector<word> g_, hcol_, hrow_, table_;
};
