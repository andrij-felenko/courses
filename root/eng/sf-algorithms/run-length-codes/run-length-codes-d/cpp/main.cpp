#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>

namespace compression::mr {

enum class Mode {
    Pass,
    Vertical,
    Horizontal
};

struct StepDecision {
    Mode mode;
    int  vertical_offset{0};  // [-3..+3] для режиму Vertical
    int  first_run{0};         // Довжина першої серії для Horizontal
    int  second_run{0};        // Довжина другої серії для Horizontal
    int  next_a0{0};           // Нова опорна координата
    int  next_color{0};        // 0 = білий, 1 = чорний
};

class LineClassifier {
public:
    static int get_pixel(std::span<const uint8_t> row, int x, int width) noexcept {
        if (x < 0 || x >= width) return 0;
        return (row[static_cast<size_t>(x >> 3)] >> (7 - (x & 7))) & 1;
    }

    static int find_next_edge(std::span<const uint8_t> row, int x, int width) noexcept {
        int initial = get_pixel(row, x, width);
        int pos = (x < 0) ? 0 : x + 1;
        while (pos < width) {
            if (get_pixel(row, pos, width) != initial) {
                return pos;
            }
            ++pos;
        }
        return width;
    }

    static int find_b1(std::span<const uint8_t> ref_row, int a0, int width, int a0_color) noexcept {
        int target = 1 - a0_color;
        int pos = (a0 < 0) ? 0 : a0 + 1;
        while (pos < width) {
            int current = get_pixel(ref_row, pos, width);
            int prev = get_pixel(ref_row, pos - 1, width);
            if (current == target && current != prev) {
                return pos;
            }
            ++pos;
        }
        return width;
    }

    static StepDecision evaluate_step(std::span<const uint8_t> ref,
                                      std::span<const uint8_t> curr,
                                      int width, int a0, int a0_color) noexcept {
        StepDecision decision;
        int a1 = find_next_edge(curr, a0, width);
        int b1 = find_b1(ref, a0, width, a0_color);
        int b2 = find_next_edge(ref, b1, width);

        if (b2 < a1) {
            decision.mode = Mode::Pass;
            decision.next_a0 = b2;
            decision.next_color = a0_color;
        } else {
            int diff = a1 - b1;
            if (diff >= -3 && diff <= 3) {
                decision.mode = Mode::Vertical;
                decision.vertical_offset = diff;
                decision.next_a0 = a1;
                decision.next_color = 1 - a0_color;
            } else {
                int a2 = find_next_edge(curr, a1, width);
                decision.mode = Mode::Horizontal;
                decision.first_run = a1 - ((a0 < 0) ? 0 : a0);
                decision.second_run = a2 - a1;
                decision.next_a0 = a2;
                decision.next_color = a0_color;
            }
        }
        return decision;
    }
};

} // namespace compression::mr
