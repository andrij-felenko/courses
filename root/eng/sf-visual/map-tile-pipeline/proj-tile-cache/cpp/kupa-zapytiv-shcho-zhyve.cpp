struct Request {
    TileId   id;
    uint64_t generation = 0;
    int32_t  levelDelta = 0;
    double   d2 = 0.0;
};

// Раніше йде той, у кого свіже покоління; далі — свій рівень; далі — центр.
inline bool better(const Request& a, const Request& b) noexcept {
    if (a.generation != b.generation) return a.generation > b.generation;
    if (a.levelDelta != b.levelDelta) return a.levelDelta < b.levelDelta;
    return a.d2 < b.d2;
}
// std::priority_queue кладе наверх «найбільший за Compare»,
// тому Compare мусить означати саме «гірший».
struct Worse {
    bool operator()(const Request& a, const Request& b) const noexcept {
        return better(b, a);
    }
};
