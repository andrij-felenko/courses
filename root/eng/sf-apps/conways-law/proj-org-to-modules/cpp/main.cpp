// Оргсхема -> передбачений граф модулів за законом Конвея.
// Вхід: команди й канали спілкування. Вихід: шви (інтерфейси) та
// компоненти зв'язності (майбутні автономні частини системи).
#include <algorithm>
#include <cstddef>
#include <iostream>
#include <map>
#include <queue>
#include <set>
#include <string>
#include <utility>
#include <vector>

using Pair = std::pair<std::string, std::string>;

// ВХІД: граф організації як дані.
// У базовому випадку "одна команда — один модуль" team == module.
const std::vector<std::string> teams = {"ord", "pay", "shp", "rep", "anl"};

// Канал = пара команд, які РЕАЛЬНО регулярно узгоджують роботу.
// Саме ці пари закон Конвея відіб'є як стики між модулями.
const std::vector<Pair> channels = {
    {"ord", "pay"},  // замовлення ↔ оплата
    {"ord", "shp"},  // замовлення ↔ доставка
    {"rep", "anl"},  // звіти ↔ аналітика (окрема пара)
};

// Матриця суміжності як мапа сусідств. Симетрична: канал двобічний,
// тож ребро додаємо в обидва боки.
std::map<std::string, std::set<std::string>>
adjacency(const std::vector<std::string>& teams,
          const std::vector<Pair>& chans) {
    std::map<std::string, std::set<std::string>> adj;
    for (const auto& t : teams)
        adj[t] = {};                    // кожна команда — вузол, навіть без каналів
    for (const auto& [a, b] : chans) {
        adj[a].insert(b);
        adj[b].insert(a);               // «говорити» взаємне: той самий стик в обидва боки
    }
    return adj;
}

// Передбачені інтерфейси = канали, нормалізовані як (менший, більший),
// щоб (ord,pay) і (pay,ord) не рахувались двічі.
std::vector<Pair> seams(const std::vector<Pair>& chans) {
    std::set<Pair> uniq;                // std::set сам упорядковує й прибирає дублі
    for (auto [a, b] : chans) {
        if (a > b) std::swap(a, b);
        uniq.insert({a, b});
    }
    return {uniq.begin(), uniq.end()};
}

// Компоненти зв'язності = майбутні автономні частини системи.
// Кожна — максимальна група модулів, зчеплених прямо чи ланцюжком.
std::vector<std::vector<std::string>>
components(const std::vector<std::string>& teams,
          const std::map<std::string, std::set<std::string>>& adj) {
    std::set<std::string> seen;
    std::vector<std::vector<std::string>> result;
    for (const auto& start : teams) {
        if (seen.count(start)) continue;
        // обхід завширшки від непозначеного вузла — збираємо весь досяжний шматок
        std::vector<std::string> group;
        std::queue<std::string> queue;
        queue.push(start);
        seen.insert(start);
        while (!queue.empty()) {
            std::string node = queue.front();
            queue.pop();
            group.push_back(node);
            for (const auto& nb : adj.at(node)) {
                if (!seen.count(nb)) {
                    seen.insert(nb);
                    queue.push(nb);
                }
            }
        }
        std::sort(group.begin(), group.end());
        result.push_back(group);
    }
    return result;
}

int main() {
    const auto adj = adjacency(teams, channels);
    const auto ss = seams(channels);
    const auto cc = components(teams, adj);

    std::cout << "Передбачені шви (інтерфейси): " << ss.size() << "\n";
    for (const auto& [a, b] : ss)
        std::cout << "  " << a << " <-> " << b << "\n";

    std::cout << "\nАвтономні частини (компоненти зв'язності): " << cc.size() << "\n";
    for (std::size_t i = 0; i < cc.size(); ++i) {
        std::cout << "  #" << i + 1 << ": {";
        for (std::size_t j = 0; j < cc[i].size(); ++j) {
            if (j) std::cout << ", ";
            std::cout << cc[i][j];
        }
        std::cout << "}\n";
    }
}
