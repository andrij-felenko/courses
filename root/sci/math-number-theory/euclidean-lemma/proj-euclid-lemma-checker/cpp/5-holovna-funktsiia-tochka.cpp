int main() {
    cout << "=== Верифікатор Леми Евкліда (BigInt Edition) ===\n\n";
    
    cpp_int p = read_big_int("Введіть передбачуване просте число p: ");
    cpp_int a = read_big_int("Введіть ціле число a: ");
    cpp_int b = read_big_int("Введіть ціле число b: ");
    
    verify_euclid_lemma(p, a, b);
    
    return 0;
}
