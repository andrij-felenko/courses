#include <array>
#include <cstdint>
#include <queue>
#include <utility>   // std::swap
#include <vector>

using i64 = int64_t;
using Triple = std::array<i64, 3>;
using Mat = std::array<std::array<int, 3>, 3>;

// Три матриці Барнінґа–Голла — діють на стовпчик (a, b, c)ᵀ.
static const Mat A = {{{ 1, -2, 2}, { 2, -1, 2}, { 2, -2, 3}}};
static const Mat B = {{{ 1,  2, 2}, { 2,  1, 2}, { 2,  2, 3}}};
static const Mat C = {{{-1,  2, 2}, {-2,  1, 2}, {-2,  2, 3}}};

Triple times(const Mat& M, const Triple& t) {
    return {{ M[0][0]*t[0] + M[0][1]*t[1] + M[0][2]*t[2],
              M[1][0]*t[0] + M[1][1]*t[1] + M[1][2]*t[2],
              M[2][0]*t[0] + M[2][1]*t[1] + M[2][2]*t[2] }};
}

// Усі примітивні трійки з c ≤ limit — обхід дерева від (3, 4, 5).
std::vector<Triple> primitive_tree(i64 limit) {
    std::vector<Triple> out;
    if (limit < 5) return out;
    std::queue<Triple> q;
    q.push({{3, 4, 5}});
    while (!q.empty()) {
        Triple t = q.front(); q.pop();
        Triple s = t;
        if (s[0] > s[1]) std::swap(s[0], s[1]);
        out.push_back(s);
        for (const Mat& M : {A, B, C}) {
            Triple ch = times(M, t);
            if (ch[2] <= limit) q.push(ch);      // дитина завжди «глибша» за гіпотенузою
        }
    }
    return out;
}
