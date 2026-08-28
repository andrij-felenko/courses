#include <vector>
#include <cstdio>

// Число пар (комунікаційних шляхів) у групі з n людей: n·(n−1)/2.
// Порядок множення (n−1) перед діленням гарантує, що n·(n−1) — завжди
// парне (два послідовні цілі), тож ділення на 2 точне, без утрати дробу.
long long paths(long long n) {
    return n * (n - 1) / 2;
}

// Незалежна перевірка через лему про рукостискання:
// у повному графі кожна з n вершин має степінь (n−1);
// сума степенів = подвоєне число ребер, тож ребер = сума/2.
long long paths_via_handshake(long long n) {
    long long sum_of_degrees = 0;
    for (long long v = 0; v < n; ++v)
        sum_of_degrees += (n - 1);        // степінь кожної вершини у Kₙ
    return sum_of_degrees / 2;            // ребро лічиться з обох кінців
}

int main() {
    // 1) Дві формули мають дати те саме число — це наша страховка.
    for (long long n : {3, 5, 10, 20, 50}) {
        long long a = paths(n);
        long long b = paths_via_handshake(n);
        std::printf("n=%2lld:  формула=%lld  лема=%lld  %s\n",
                    n, a, b, (a == b ? "збіг" : "РОЗБІЖНІСТЬ!"));
    }
    std::printf("\n");

    // 2) Моноліт із 12 у купі проти трьох автономних команд по 4.
    long long mono = paths(12);

    std::vector<long long> teams = {4, 4, 4};
    long long inside = 0;
    for (long long t : teams) inside += paths(t);   // густо всередині кожної
    long long between = teams.size() - 1;           // тонкі контракти між ними

    std::printf("Моноліт (12 разом):        %lld шляхів\n", mono);
    std::printf("3 команди — усередині:     %lld шляхів\n", inside);
    std::printf("3 команди — між командами: %lld контракти\n", between);
    std::printf("Разом при розбитті:        %lld проти %lld\n",
                inside + between, mono);
    return 0;
}
