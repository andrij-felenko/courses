#include <vector>
#include <cstdio>

// Число пар (комунікаційних шляхів) у групі з n людей: n·(n−1)/2.
int paths(int n) {
    return n * (n - 1) / 2;
}

int main() {
    // Варіант A: один моноліт — усі 12 в одній групі, кожен з кожним.
    int mono = paths(12);

    // Варіант B: три автономні команди по 4 людини.
    // Усередині кожної — густе спілкування (усі пари),
    // а МІЖ командами лишаємо один тонкий контракт (одна пара-зв'язок на межу).
    std::vector<int> teams = {4, 4, 4};
    int inside = 0;
    for (int t : teams) inside += paths(t);   // пари всередині команд
    int between = 3;                           // 3 межі → 3 тонкі контракти

    std::printf("Моноліт (12 в купі):        %d шляхів\n", mono);
    std::printf("3 команди — усередині:      %d шляхів\n", inside);
    std::printf("3 команди — між командами:  %d контракти\n", between);
    std::printf("Разом при розбитті:         %d проти %d\n",
                inside + between, mono);
    return 0;
}
