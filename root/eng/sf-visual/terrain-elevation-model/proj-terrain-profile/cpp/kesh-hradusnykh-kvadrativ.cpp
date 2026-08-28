#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <list>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

static constexpr int     SPD  = 3600;             // інтервалів сітки на градус (1″)
static constexpr int64_t GW   = int64_t(360) * SPD;   // ширина світу у вузлах
static constexpr int64_t GH   = int64_t(180) * SPD;   // висота світу у вузлах
static constexpr int16_t VOID = -32768;           // прогалина: НЕ число, арифметики не терпить

// Один градусний файл: N×N вузлів, big-endian int16, рядок 0 — північний край.
struct HgtTile {
    const uint8_t* data  = nullptr;
    size_t         bytes = 0;
    int            n     = 0;      // 3601 (1″) або 1201 (3″)
    int            step  = 0;      // інтервалів на градус: n − 1

    int16_t node(int row, int col) const noexcept {
        const uint8_t* p = data + 2 * (size_t(row) * n + col);
        // p[0] << 8 підіймається до int; звужуємо ЯВНО через uint16_t, щоб не
        // залежати від того, як стандарт трактує втрату старших бітів
        // (до C++20 — визначено реалізацією, з C++20 — обгортання).
        return int16_t(uint16_t((uint16_t(p[0]) << 8) | uint16_t(p[1])));
    }
};

class HgtLibrary {
public:
    HgtLibrary(std::string dir, size_t budgetBytes, int advice = MADV_NORMAL)
        : dir_(std::move(dir)), budget_(budgetBytes), advice_(advice) {}

    ~HgtLibrary() {
        for (Entry& e : lru_) ::munmap(const_cast<uint8_t*>(e.tile.data), e.tile.bytes);
    }

    // Висота у вузлі глобальної сітки. false — прогалина або немає покриття.
    // Значення КОПІЮЄТЬСЯ негайно: покажчик на квадрат назовні не виходить,
    // тому витіснення між двома викликами нікому не шкодить.
    bool node(int64_t gi, int64_t gj, int16_t& out) {
        gi = ((gi % GW) + GW) % GW;              // світ замикається по довготі
        if (gj < 0 || gj >= GH) return false;    // за полюс виходу немає

        const HgtTile* t = acquire(int(gi / SPD) - 180, 89 - int(gj / SPD));
        if (!t) return false;

        // Крок квадрата може бути грубішим за робочу сітку — тоді це
        // східчаста передискретизація; змішувати роздільності в одному
        // маршруті краще не тут, а заздалегідь, перегнавши 3″ у 1″.
        const int col = int(gi % SPD) * t->step / SPD;
        const int row = int(gj % SPD) * t->step / SPD;

        const int16_t h = t->node(row, col);
        if (h == VOID) return false;             // ← перевірка ДО будь-якої арифметики
        out = h;
        return true;
    }

private:
    struct Entry { uint64_t key; HgtTile tile; };

    static uint64_t keyOf(int lonDeg, int latDeg) noexcept {
        return (uint64_t(uint32_t(lonDeg + 180)) << 16) | uint32_t(latDeg + 90);
    }

    const HgtTile* acquire(int lonDeg, int latDeg) {
        const uint64_t k = keyOf(lonDeg, latDeg);
        if (k == memoKey_) return memoTile_;             // чотири кути комірки — майже завжди один квадрат
        if (missing_.count(k)) { memoKey_ = k; memoTile_ = nullptr; return nullptr; }

        if (auto it = index_.find(k); it != index_.end()) {
            lru_.splice(lru_.begin(), lru_, it->second); // список — ітератори переживають перестановку
            memoKey_ = k; memoTile_ = &lru_.front().tile;
            return memoTile_;
        }

        HgtTile t;
        if (!mapFile(lonDeg, latDeg, t)) {
            missing_.insert(k);   // ← без негативного кеша кожна вибірка над океаном робить невдалий open()
            memoKey_ = k; memoTile_ = nullptr;
            return nullptr;
        }

        memoKey_ = kNoKey; memoTile_ = nullptr;          // витіснення нижче може знести memo
        while (bytes_ + t.bytes > budget_ && lru_.size() >= kMinResident) {
            Entry& victim = lru_.back();
            ::munmap(const_cast<uint8_t*>(victim.tile.data), victim.tile.bytes);
            bytes_ -= victim.tile.bytes;
            index_.erase(victim.key);
            lru_.pop_back();
        }

        lru_.push_front(Entry{ k, t });
        index_[k] = lru_.begin();
        bytes_ += t.bytes;
        memoKey_ = k; memoTile_ = &lru_.front().tile;
        return memoTile_;
    }

    bool mapFile(int lonDeg, int latDeg, HgtTile& out) const {
        char name[32];
        std::snprintf(name, sizeof name, "%c%02d%c%03d.hgt",
                      latDeg < 0 ? 'S' : 'N', std::abs(latDeg),
                      lonDeg < 0 ? 'W' : 'E', std::abs(lonDeg));
        const std::string path = dir_ + "/" + name;

        const int fd = ::open(path.c_str(), O_RDONLY);
        if (fd < 0) return false;
        struct stat st {};
        if (::fstat(fd, &st) != 0) { ::close(fd); return false; }

        // Заголовка у .hgt немає взагалі — роздільність каже сам розмір файла.
        int n = 0;
        if      (st.st_size == 3601LL * 3601 * 2) n = 3601;
        else if (st.st_size == 1201LL * 1201 * 2) n = 1201;
        else { ::close(fd); return false; }

        void* p = ::mmap(nullptr, size_t(st.st_size), PROT_READ, MAP_PRIVATE, fd, 0);
        ::close(fd);                    // відображення тримає файл саме — дескриптор більше не потрібен
        if (p == MAP_FAILED) return false;

        // Підказку ядру дають ЗА ХАРАКТЕРОМ запиту, а не «про всяк випадок»:
        // хід уздовж маршруту рухається рядками майже монотонно, і попереднє
        // читання йому допомагає; розсіяним поодиноким вибіркам — шкодить.
        if (advice_ != MADV_NORMAL) ::madvise(p, size_t(st.st_size), advice_);

        out.data = static_cast<const uint8_t*>(p);
        out.bytes = size_t(st.st_size);
        out.n = n;
        out.step = n - 1;
        return true;
    }

    static constexpr uint64_t kNoKey = ~uint64_t(0);
    static constexpr size_t kMinResident = 4;   // комірка в куті квадрата чіпає рівно чотири файли

    std::string dir_;
    size_t      budget_;
    int         advice_;
    size_t      bytes_ = 0;

    std::list<Entry> lru_;                                    // найсвіжіший спереду
    std::unordered_map<uint64_t, std::list<Entry>::iterator> index_;
    std::unordered_set<uint64_t> missing_;

    uint64_t       memoKey_  = kNoKey;
    const HgtTile* memoTile_ = nullptr;
};
