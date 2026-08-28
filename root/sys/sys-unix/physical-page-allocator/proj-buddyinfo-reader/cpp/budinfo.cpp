// budinfo.cpp — форма вільної пам'яті: зони, найбільший блок, avail(k).
// Збірка: c++ -O2 -std=c++20 -o budinfo budinfo.cpp
// Запуск: ./budinfo [--zone НАЗВА] [--need БАЙТІВ] [--hidden]
#include <charconv>
#include <fstream>
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unistd.h>

struct ZoneRow {
    int node{};
    std::string name;
    int norders{};
    std::vector<unsigned long> nr_free;
    std::vector<unsigned long> avail;
    unsigned long free_pages{};
    int top{-1};
};

static std::string slurp(const std::string &path)
{
    std::ifstream f(path, std::ios::binary);
    if (!f) return {};
    return std::string((std::istreambuf_iterator<char>(f)), std::istreambuf_iterator<char>());
}
