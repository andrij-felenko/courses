#include <algorithm>
#include <iterator>

struct Ranked {
    Scenario scenario;
    std::string attribute;
    int score;          // важливість × складність
};

// Ключова ухвала — ДОБУТОК, не сума.
int score(const Scenario& s) { return s.importance * s.difficulty; }

std::vector<Ranked> rank(const UtilityTree& tree) {
    std::vector<Ranked> flat;
    for (const auto& attr : tree.attributes)
        for (const auto& s : attr.scenarios)
            flat.push_back({s, attr.name, score(s)});

    // Спад за добутком; за рівних — важливіший наперед, тоді складніший.
    // Три ключі поспіль роблять порядок цілком детермінованим.
    std::sort(flat.begin(), flat.end(), [](const Ranked& a, const Ranked& b) {
        if (a.score != b.score) return a.score > b.score;
        if (a.scenario.importance != b.scenario.importance)
            return a.scenario.importance > b.scenario.importance;
        return a.scenario.difficulty > b.scenario.difficulty;
    });
    return flat;
}

// Драйвери — крайній квадрант (В, В): і найцінніше, і найважче.
std::vector<Ranked> drivers(const std::vector<Ranked>& ranked) {
    std::vector<Ranked> out;
    std::copy_if(ranked.begin(), ranked.end(), std::back_inserter(out),
                 [](const Ranked& r) {
                     return r.scenario.importance == 3 && r.scenario.difficulty == 3;
                 });
    return out;
}
