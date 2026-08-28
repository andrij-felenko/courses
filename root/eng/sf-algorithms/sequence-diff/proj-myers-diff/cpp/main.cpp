#include <iostream>
#include <string_view>
#include <vector>
#include <memory>
#include <cstdint>
#include <algorithm>

namespace diff {

enum class EditOp : uint8_t {
    Keep,
    Insert,
    Delete
};

struct Step {
    EditOp op{EditOp::Keep};
    size_t line_a{0};
    size_t line_b{0};
    std::string_view text;
};

struct Script {
    std::vector<Step> steps;
    size_t edit_distance{0};
};

struct Line {
    std::string_view text;
    uint64_t hash{0};

    [[nodiscard]] bool operator==(const Line& other) const noexcept {
        return hash == other.hash && text == other.text;
    }
};

/* Обчислення 64-бітного FNV-1a хешу для string_view */
[[nodiscard]] constexpr uint64_t fnv1a_hash(std::string_view sv) noexcept {
    uint64_t h = 14695981039346656037ULL;
    for (char c : sv) {
        h ^= static_cast<uint8_t>(c);
        h *= 1099511628211ULL;
    }
    return h;
}

/* Розбиття тексту на рядки з підрахунком хешів */
[[nodiscard]] std::vector<Line> split_lines(std::string_view text) {
    std::vector<Line> lines;
    size_t start = 0;
    while (start < text.size()) {
        size_t end = text.find('\n', start);
        if (end == std::string_view::npos) end = text.size();
        
        std::string_view sv = text.substr(start, end - start);
        if (!sv.empty() && sv.back() == '\r') sv.remove_suffix(1);
        
        lines.push_back(Line{sv, fnv1a_hash(sv)});
        start = end + 1;
    }
    return lines;
}

/* Алгоритм Маєрса на C++20 */
[[nodiscard]] Script compute_myers(std::string_view text_a, std::string_view text_b) {
    const auto a = split_lines(text_a);
    const auto b = split_lines(text_b);
    const size_t n = a.size();
    const size_t m = b.size();

    const size_t max_d = n + m;
    const size_t offset = max_d;
    std::vector<int> v(2 * max_d + 1, -1);
    std::vector<std::vector<int>> trace;
    trace.reserve(max_d + 1);

    // Базова початкова змія
    int x0 = 0, y0 = 0;
    while (static_cast<size_t>(x0) < n && static_cast<size_t>(y0) < m && a[x0] == b[y0]) {
        x0++; y0++;
    }
    v[offset] = x0;
    trace.push_back(v);

    size_t final_d = 0;
    bool found = (static_cast<size_t>(x0) == n && static_cast<size_t>(y0) == m);

    for (size_t d = 1; d <= max_d && !found; ++d) {
        const int d_int = static_cast<int>(d);
        for (int k = -d_int; k <= d_int; k += 2) {
            int x = 0;
            if (k == -d_int || (k != d_int && v[offset + k - 1] < v[offset + k + 1])) {
                x = v[offset + k + 1]; // Крок вниз (вставка)
            } else {
                x = v[offset + k - 1] + 1; // Крок вправо (видалення)
            }

            int y = x - k;

            // Змія (протягування збігів)
            while (static_cast<size_t>(x) < n && static_cast<size_t>(y) < m && a[x] == b[y]) {
                x++; y++;
            }

            v[offset + k] = x;

            if (static_cast<size_t>(x) >= n && static_cast<size_t>(y) >= m) {
                final_d = d;
                found = true;
                break;
            }
        }
        trace.push_back(v);
    }

    Script script;
    script.edit_distance = final_d;
    std::vector<Step> rev_steps;
    rev_steps.reserve(n + m + 1);

    int cur_x = static_cast<int>(n);
    int cur_y = static_cast<int>(m);

    for (int d = static_cast<int>(final_d); d > 0; --d) {
        const int k = cur_x - cur_y;
        const auto& v_prev = trace[d - 1];
        
        int prev_k = (k == -d || (k != d && v_prev[offset + k - 1] < v_prev[offset + k + 1]))
                     ? (k + 1) : (k - 1);

        const int prev_x = v_prev[offset + prev_k];
        const int prev_y = prev_x - prev_k;

        // Збираємо змію
        while (cur_x > prev_x && cur_y > prev_y) {
            cur_x--; cur_y--;
            rev_steps.push_back(Step{EditOp::Keep, static_cast<size_t>(cur_x + 1),
                                     static_cast<size_t>(cur_y + 1), a[cur_x].text});
        }

        // Недіагональний крок
        if (cur_x > prev_x) {
            cur_x--;
            rev_steps.push_back(Step{EditOp::Delete, static_cast<size_t>(cur_x + 1), 0, a[cur_x].text});
        } else if (cur_y > prev_y) {
            cur_y--;
            rev_steps.push_back(Step{EditOp::Insert, 0, static_cast<size_t>(cur_y + 1), b[cur_y].text});
        }
    }

    while (cur_x > 0 && cur_y > 0) {
        cur_x--; cur_y--;
        rev_steps.push_back(Step{EditOp::Keep, static_cast<size_t>(cur_x + 1),
                                 static_cast<size_t>(cur_y + 1), a[cur_x].text});
    }

    std::reverse(rev_steps.begin(), rev_steps.end());
    script.steps = std::move(rev_steps);
    return script;
}

/* Форматування уніфікованого diff */
void print_unified_diff(const Script& script) {
    std::cout << "--- a/original\n+++ b/modified\n";
    for (const auto& s : script.steps) {
        char prefix = ' ';
        if (s.op == EditOp::Insert) prefix = '+';
        else if (s.op == EditOp::Delete) prefix = '-';
        std::cout << prefix << ' ' << s.text << '\n';
    }
}

} // namespace diff
