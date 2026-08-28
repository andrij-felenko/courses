#include <cstdint>
#include <array>
#include <bit>
#include <iostream>
#include <span>
#include <vector>

class ChessAttackGenerator {
public:
    struct MagicEntry {
        uint64_t mask{0};
        uint64_t magic{0};
        std::span<const uint64_t> table{};
        uint8_t shift{0};
    };

    ChessAttackGenerator() {
        init_knight_table();
    }

    [[nodiscard]] constexpr uint64_t get_knight_attacks(int square) const noexcept {
        return m_knight_attacks[square];
    }

    [[nodiscard]] uint64_t get_rook_attacks(int square, uint64_t occupancy) const noexcept {
        const auto& entry = m_rook_magics[square];
        const uint64_t blockers = occupancy & entry.mask;
        const uint64_t index = (blockers * entry.magic) >> entry.shift;
        return entry.table[index];
    }

    template <typename MoveCallback>
    void generate_knight_moves(uint64_t knights, uint64_t friendly_pieces, MoveCallback&& on_move) const {
        while (knights != 0) {
            const int from = std::countr_zero(knights);
            uint64_t targets = m_knight_attacks[from] & ~friendly_pieces;

            while (targets != 0) {
                const int to = std::countr_zero(targets);
                on_move(from, to);
                targets &= (targets - 1);
            }
            knights &= (knights - 1);
        }
    }

    template <typename MoveCallback>
    void generate_rook_moves(uint64_t rooks, uint64_t all_pieces, uint64_t friendly_pieces, MoveCallback&& on_move) const {
        while (rooks != 0) {
            const int from = std::countr_zero(rooks);
            uint64_t targets = get_rook_attacks(from, all_pieces) & ~friendly_pieces;

            while (targets != 0) {
                const int to = std::countr_zero(targets);
                on_move(from, to);
                targets &= (targets - 1);
            }
            rooks &= (rooks - 1);
        }
    }

private:
    void init_knight_table() noexcept {
        constexpr std::array<int, 8> dx{-2, -2, -1, -1,  1,  1,  2,  2};
        constexpr std::array<int, 8> dy{-1,  1, -2,  2, -2,  2, -1,  1};

        for (int sq = 0; sq < 64; ++sq) {
            const int x = sq % 8;
            const int y = sq / 8;
            uint64_t mask = 0;

            for (size_t i = 0; i < 8; ++i) {
                const int nx = x + dx[i];
                const int ny = y + dy[i];
                if (nx >= 0 && nx < 8 && ny >= 0 && ny < 8) {
                    mask |= (1ULL << (ny * 8 + nx));
                }
            }
            m_knight_attacks[sq] = mask;
        }
    }

    std::array<uint64_t, 64> m_knight_attacks{};
    std::array<MagicEntry, 64> m_rook_magics{};
    std::vector<uint64_t> m_rook_storage{};
};
