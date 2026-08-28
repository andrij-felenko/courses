#include <cstdint>
#include <cstddef>
#include <vector>
#include <string_view>
#include <optional>
#include <span>
#include <memory>

class QuotientFilter {
public:
    struct Slot {
        uint8_t is_occupied : 1 = 0;
        uint8_t is_continuation : 1 = 0;
        uint8_t is_shifted : 1 = 0;
        uint8_t remainder : 5 = 0;
    };

    static constexpr double kMaxLoadFactor = 0.85;

    explicit QuotientFilter(size_t q_bits, size_t r_bits)
        : q_bits_(q_bits),
          r_bits_(r_bits),
          num_slots_(size_t{1} << q_bits),
          slot_mask_(num_slots_ - 1),
          table_(num_slots_) {}

    [[nodiscard]] size_t size() const noexcept { return count_; }
    [[nodiscard]] size_t capacity() const noexcept { return num_slots_; }
    [[nodiscard]] double load_factor() const noexcept {
        return static_cast<double>(count_) / static_cast<double>(num_slots_);
    }

    [[nodiscard]] bool contains(std::string_view key) const noexcept {
        const auto hash = hash_bytes(key);
        const size_t f_q = (hash >> r_bits_) & slot_mask_;
        const auto f_r = static_cast<uint8_t>(hash & ((uint64_t{1} << r_bits_) - 1));

        if (!table_[f_q].is_occupied) {
            return false;
        }

        size_t curr = find_run_start(f_q);

        do {
            if (table_[curr].remainder == f_r) {
                return true;
            }
            if (table_[curr].remainder > f_r) {
                return false;
            }
            curr = (curr + 1) & slot_mask_;
        } while (table_[curr].is_continuation);

        return false;
    }

    bool insert(std::string_view key) {
        if (load_factor() >= kMaxLoadFactor) {
            return false;
        }

        const auto hash = hash_bytes(key);
        const size_t f_q = (hash >> r_bits_) & slot_mask_;
        const auto f_r = static_cast<uint8_t>(hash & ((uint64_t{1} << r_bits_) - 1));

        if (is_empty(table_[f_q])) {
            table_[f_q].is_occupied = 1;
            table_[f_q].is_continuation = 0;
            table_[f_q].is_shifted = 0;
            table_[f_q].remainder = f_r;
            ++count_;
            return true;
        }

        if (!table_[f_q].is_occupied) {
            table_[f_q].is_occupied = 1;
        }

        size_t insert_pos = find_run_start(f_q);
        const bool has_run = (table_[f_q].is_occupied == 1);

        if (has_run) {
            while (table_[insert_pos].remainder < f_r && table_[(insert_pos + 1) & slot_mask_].is_continuation) {
                insert_pos = (insert_pos + 1) & slot_mask_;
            }
            if (table_[insert_pos].remainder < f_r) {
                insert_pos = (insert_pos + 1) & slot_mask_;
            }
        }

        Slot prev_slot{
            .is_occupied = 0,
            .is_continuation = 0,
            .is_shifted = static_cast<uint8_t>(insert_pos != f_q ? 1 : 0),
            .remainder = f_r
        };
        size_t curr = insert_pos;

        while (true) {
            Slot temp = table_[curr];
            const bool was_empty = is_empty(temp);

            table_[curr].remainder = prev_slot.remainder;
            table_[curr].is_shifted = static_cast<uint8_t>(curr != f_q ? 1 : 0);
            if (curr == insert_pos && has_run && insert_pos != find_run_start(f_q)) {
                table_[curr].is_continuation = 1;
            }

            if (was_empty) break;

            prev_slot = temp;
            prev_slot.is_shifted = 1;
            curr = (curr + 1) & slot_mask_;
        }

        ++count_;
        return true;
    }

    bool remove(std::string_view key) noexcept {
        const auto hash = hash_bytes(key);
        const size_t f_q = (hash >> r_bits_) & slot_mask_;
        const auto f_r = static_cast<uint8_t>(hash & ((uint64_t{1} << r_bits_) - 1));

        if (!table_[f_q].is_occupied) return false;

        const size_t run_start = find_run_start(f_q);
        size_t target = run_start;
        bool found = false;

        do {
            if (table_[target].remainder == f_r) {
                found = true;
                break;
            }
            target = (target + 1) & slot_mask_;
        } while (table_[target].is_continuation);

        if (!found) return false;

        size_t curr = target;
        while (true) {
            const size_t next = (curr + 1) & slot_mask_;
            if (is_empty(table_[next]) || !table_[next].is_shifted) {
                table_[curr] = Slot{};
                break;
            }
            table_[curr].remainder = table_[next].remainder;
            table_[curr].is_continuation = table_[next].is_continuation;
            table_[curr].is_shifted = static_cast<uint8_t>(curr != f_q ? 1 : 0);
            curr = next;
        }

        --count_;
        return true;
    }

private:
    size_t q_bits_;
    size_t r_bits_;
    size_t num_slots_;
    size_t slot_mask_;
    size_t count_ = 0;
    std::vector<Slot> table_;

    [[nodiscard]] static bool is_empty(const Slot& s) noexcept {
        return !s.is_occupied && !s.is_continuation && !s.is_shifted;
    }

    [[nodiscard]] static uint64_t hash_bytes(std::string_view data) noexcept {
        uint64_t h = 14695981039346656037ULL;
        for (const char c : data) {
            h ^= static_cast<uint8_t>(c);
            h *= 1099511628211ULL;
        }
        return h;
    }

    [[nodiscard]] size_t find_run_start(size_t f_q) const noexcept {
        size_t curr = f_q;
        while (table_[curr].is_shifted) {
            curr = (curr - 1) & slot_mask_;
        }

        size_t scan = curr;
        size_t run_start = curr;

        while (scan != f_q) {
            do {
                run_start = (run_start + 1) & slot_mask_;
            } while (table_[run_start].is_continuation);

            do {
                scan = (scan + 1) & slot_mask_;
            } while (!table_[scan].is_occupied);
        }
        return run_start;
    }
};
