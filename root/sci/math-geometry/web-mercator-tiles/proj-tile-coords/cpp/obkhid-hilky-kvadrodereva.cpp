// Усі нащадки тайла — від нього самого до рівня max_z включно.
// Явний стек, не рекурсія: глибина відома, зайві кадри на гарячій дорозі ні до чого.
template <class F>
void for_each_descendant(TileId root, int max_z, F&& visit) {
    std::vector<TileId> stack{ root };
    while (!stack.empty()) {
        const TileId cur = stack.back();
        stack.pop_back();
        visit(cur);
        if (cur.z >= max_z) continue;
        const int z = cur.z + 1;
        const std::int64_t x = cur.x * 2, y = cur.y * 2;
        stack.push_back({ z, x,     y     });
        stack.push_back({ z, x + 1, y     });
        stack.push_back({ z, x,     y + 1 });
        stack.push_back({ z, x + 1, y + 1 });
    }
}

// Скільки тайлів це буде. Викликати ПЕРЕД завантаженням.
std::int64_t descendant_count(int from_z, int to_z, std::int64_t seeds) {
    if (to_z < from_z) return 0;
    const int d = to_z - from_z;
    if (d > 30) return -1;                       // 4^31 уже не влазить — сигналимо
    const std::int64_t total = ((std::int64_t{1} << (2 * (d + 1))) - 1) / 3;
    return seeds * total;                        // ділимо ПЕРЕД множенням
}
