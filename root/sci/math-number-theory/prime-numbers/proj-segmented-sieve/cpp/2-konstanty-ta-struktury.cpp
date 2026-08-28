#include <iostream>
#include <vector>
#include <cmath>

using namespace std;

// Функція для знаходження простих чисел до границі (базове решето)
void simpleSieve(int limit, vector<int>& prime) {
    vector<bool> mark(limit + 1, true);
    for (int p = 2; p * p <= limit; p++) {
        if (mark[p]) {
            for (int i = p * p; i <= limit; i += p)
                mark[i] = false;
        }
    }
    for (int p = 2; p <= limit; p++) {
        if (mark[p]) {
            prime.push_back(p);
        }
    }
}
