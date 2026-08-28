#include <vector>

std::vector<int> de_bruijn_greedy(int k, int n) {
    std::size_t kn = 1;                          // kn = k^n
    for (int i = 0; i < n; ++i) kn *= static_cast<std::size_t>(k);
    std::size_t kn1 = kn / k;                    // k^(n-1)

    std::vector<char> seen(kn, 0);               // вікна кодуємо числом 0..k^n-1
    std::vector<int> seq(n, 0);
    std::size_t win = 0;                         // код поточного вікна довжини n
    seen[0] = 1;                                 // вікно з самих нулів

    while (true) {
        std::size_t base = (win % kn1) * k;      // відкинули старший символ, зсунули
        int chosen = -1;
        for (int c = k - 1; c >= 0; --c)         // найбільший символ першим
            if (!seen[base + c]) { chosen = c; break; }
        if (chosen < 0) break;                   // жоден не годиться — стоп
        seq.push_back(chosen);
        win = base + chosen;
        seen[win] = 1;
    }
    seq.resize(kn);                              // циклічна частина
    return seq;
}
