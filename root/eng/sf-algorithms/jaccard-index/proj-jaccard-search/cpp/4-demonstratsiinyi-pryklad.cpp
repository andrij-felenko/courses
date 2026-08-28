int main() {
    std::string doc1 = "пошук за схожістю індекс жаккара алгоритми";
    std::string doc2 = "пошук за схожістю індекс жаккара структури";

    auto sh1 = Shingler::create_shingles(doc1, 4);
    auto sh2 = Shingler::create_shingles(doc2, 4);

    double exact_j = jaccard_exact_sorted(sh1, sh2);
    std::cout << "Точний коефіцієнт Жаккара: " << exact_j << "\n";

    MinHashGenerator gen(128);
    auto sig1 = gen.compute(sh1);
    auto sig2 = gen.compute(sh2);

    double approx_j = MinHashGenerator::similarity(sig1, sig2);
    std::cout << "Оцінка MinHash (K=128): " << approx_j << "\n";

    return 0;
}
