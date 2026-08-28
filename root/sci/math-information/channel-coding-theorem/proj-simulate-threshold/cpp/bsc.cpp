// bsc.cpp — те саме, але книга спакована в 64-бітні слова
// збірка:  g++ -O3 -march=native -std=c++20 bsc.cpp -o bsc
#include <bit>
#include <cstdint>
#include <cstdio>
#include <random>
#include <vector>

int main() {
    const int n = 70, k = 14;                 // R = k/n = 0.2
    const double p = 0.1;
    const int trials = 400000;
    const size_t M = size_t(1) << k;
    const int W = (n + 63) / 64;              // машинних слів на кодове слово

    std::mt19937_64 rng(900 + n);
    std::bernoulli_distribution flip(p), coin(0.5);

    // книга: M випадкових слів; біти за межами n лишаються нулями в ОБОХ
    // операндах XOR, тож у відстань не потрапляють
    std::vector<uint64_t> book(M * W, 0);
    for (size_t m = 0; m < M; ++m)
        for (int i = 0; i < n; ++i)
            if (coin(rng)) book[m * W + i / 64] |= uint64_t(1) << (i % 64);

    std::uniform_int_distribution<size_t> pick(0, M - 1);
    std::vector<uint64_t> recv(W);
    long long errors = 0;

    for (int t = 0; t < trials; ++t) {
        size_t msg = pick(rng);
        for (int w = 0; w < W; ++w) recv[w] = book[msg * W + w];
        for (int i = 0; i < n; ++i)
            if (flip(rng)) recv[i / 64] ^= uint64_t(1) << (i % 64);

        int best = n + 1;
        size_t guess = 0;
        for (size_t m = 0; m < M; ++m) {       // груба сила, але 64 біти за такт
            int d = 0;
            for (int w = 0; w < W; ++w)
                d += std::popcount(recv[w] ^ book[m * W + w]);
            if (d < best) { best = d; guess = m; }
        }
        errors += (guess != msg);
    }
    std::printf("n=%d k=%d M=%zu R=%.3f  P_block=%.6f  (%lld/%d)\n",
                n, k, M, double(k) / n, double(errors) / trials, errors, trials);
}
