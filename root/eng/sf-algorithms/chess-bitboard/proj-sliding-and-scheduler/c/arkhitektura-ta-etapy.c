#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

#if defined(_MSC_VER)
#include <intrin.h>
static inline int bit_scan_forward64(uint64_t bb) {
    unsigned long index;
    _BitScanForward64(&index, bb);
    return (int)index;
}
static inline int popcount64(uint64_t bb) {
    return (int)__popcnt64(bb);
}
#else
static inline int bit_scan_forward64(uint64_t bb) {
    return __builtin_ctzll(bb);
}
static inline int popcount64(uint64_t bb) {
    return __builtin_popcountll(bb);
}
#endif

/* Таблиця попередньо обчислених атак коня для всіх 64 клітинок */
static uint64_t knight_attacks[64];

/* Структура магічного бітборда для ковзної фігури (тури) */
typedef struct {
    uint64_t mask;      /* Маска релевантних блокерів уздовж ліній */
    uint64_t magic;     /* 64-бітна магічна константа */
    uint64_t *table;    /* Вказівник на підмасив передрахованих атак */
    uint8_t shift;      /* Величина зсуву: 64 - b */
} MagicEntry;

static MagicEntry rook_magics[64];
static uint64_t rook_attack_storage[102400]; /* Буфер для збереження всіх атак тур */

/* Ініціалізація атак коня */
void init_knight_attacks(void) {
    static const int dx[8] = {-2, -2, -1, -1,  1,  1,  2,  2};
    static const int dy[8] = {-1,  1, -2,  2, -2,  2, -1,  1};

    for (int sq = 0; sq < 64; ++sq) {
        int x = sq % 8;
        int y = sq / 8;
        uint64_t mask = 0;

        for (int i = 0; i < 8; ++i) {
            int nx = x + dx[i];
            int ny = y + dy[i];
            if (nx >= 0 && nx < 8 && ny >= 0 && ny < 8) {
                mask |= (1ULL << (ny * 8 + nx));
            }
        }
        knight_attacks[sq] = mask;
    }
}

/* Отримання маски атак тури за константний час O(1) */
static inline uint64_t get_rook_attacks(int square, uint64_t occupancy) {
    const MagicEntry *entry = &rook_magics[square];
    uint64_t blockers = occupancy & entry->mask;
    uint64_t index = (blockers * entry->magic) >> entry->shift;
    return entry->table[index];
}

/* Генерація всіх дозволених ходів для коней та тур */
void generate_moves(uint64_t knights, uint64_t rooks, uint64_t all_pieces, uint64_t friendly_pieces) {
    /* Обхід усіх коней на дошці */
    while (knights != 0) {
        int from = bit_scan_forward64(knights);
        uint64_t moves = knight_attacks[from] & ~friendly_pieces;

        while (moves != 0) {
            int to = bit_scan_forward64(moves);
            printf("Кінь: %d -> %d\n", from, to);
            moves &= (moves - 1); /* Скидання молодшого біта */
        }
        knights &= (knights - 1);
    }

    /* Обхід усіх тур на дошці */
    while (rooks != 0) {
        int from = bit_scan_forward64(rooks);
        uint64_t attacks = get_rook_attacks(from, all_pieces);
        uint64_t moves = attacks & ~friendly_pieces;

        while (moves != 0) {
            int to = bit_scan_forward64(moves);
            printf("Тура: %d -> %d\n", from, to);
            moves &= (moves - 1);
        }
        rooks &= (rooks - 1);
    }
}
