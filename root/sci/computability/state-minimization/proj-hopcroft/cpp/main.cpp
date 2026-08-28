#include <vector>
#include <unordered_set>
#include <unordered_map>
#include <utility>
using std::vector, std::unordered_set, std::unordered_map;

// Класи нерозрізнюваності за O(|Σ|·n·log n). Повертає список блоків.
vector<unordered_set<int>> hopcroft(const vector<vector<int>>& delta,
                                    const unordered_set<int>& accept) {
    const int n = (int)delta.size();
    const int k = n ? (int)delta[0].size() : 0;

    // обернені переходи: inv[a][t] — усі s, що по a йдуть у t
    vector<vector<vector<int>>> inv(k, vector<vector<int>>(n));
    for (int s = 0; s < n; ++s)
        for (int a = 0; a < k; ++a)
            inv[a][delta[s][a]].push_back(s);

    // стартовий поділ: приймальні окремо від решти
    unordered_set<int> F(accept.begin(), accept.end()), rest;
    for (int s = 0; s < n; ++s)
        if (!F.count(s)) rest.insert(s);
    vector<unordered_set<int>> blocks;
    if (!F.empty())    blocks.push_back(std::move(F));
    if (!rest.empty()) blocks.push_back(std::move(rest));
    if (blocks.size() == 1) return blocks;          // усі стани в одному класі

    vector<int> where(n);                           // where[s] — індекс блоку стану s
    for (int i = 0; i < (int)blocks.size(); ++i)
        for (int s : blocks[i]) where[s] = i;

    // у чергу — лише МЕНША з двох стартових половин (лема про доповнення)
    unordered_set<int> work{ blocks[0].size() <= blocks[1].size() ? 0 : 1 };
    while (!work.empty()) {
        int wi = *work.begin();
        work.erase(work.begin());
        // знімок: блок ще може подрібнитись, поки ми ним працюємо
        vector<int> splitter(blocks[wi].begin(), blocks[wi].end());
        for (int a = 0; a < k; ++a) {
            // згрупувати δ⁻¹(splitter, a) за блоками — торкаємось лише їх
            unordered_map<int, vector<int>> touched;
            for (int t : splitter)
                for (int s : inv[a][t])
                    touched[where[s]].push_back(s);
            for (auto& [j, part] : touched) {
                if (part.size() == blocks[j].size())
                    continue;                       // блок цілком у splitter — стабільний
                int fresh = (int)blocks.size();
                blocks.emplace_back();              // Y∩X виїжджає в новий блок
                for (int s : part) {
                    blocks[j].erase(s);             // Y лишається як Y∖X
                    blocks[fresh].insert(s);
                    where[s] = fresh;
                }
                if (work.count(j))                  // Y ще не оброблений — обидві половини
                    work.insert(fresh);
                else                                // інакше досить МЕНШОЇ
                    work.insert(blocks[fresh].size() <= blocks[j].size() ? fresh : j);
            }
        }
    }
    return blocks;
}
