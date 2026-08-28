#include <algorithm>
#include <bit>
#include <cstdint>
#include <cstdlib>
#include <vector>

// Граф комітів у стисненому вигляді: батьки вершини v лежать
// підряд у par[par_off[v] .. par_off[v+1]).
struct Dag {
    int              n = 0;   // скільки всього комітів
    std::vector<int> par_off; // n + 1 зсувів
    std::vector<int> par;     // батьки всіх вершин підряд
};
