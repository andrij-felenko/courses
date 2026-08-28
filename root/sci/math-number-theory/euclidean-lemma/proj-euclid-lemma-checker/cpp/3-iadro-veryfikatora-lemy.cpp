void verify_euclid_lemma(const cpp_int& p, const cpp_int& a, const cpp_int& b) {
    cout << "------------------------------------------\n";
    cout << "Перевірка леми Евкліда:\n";
    
    // 1. Обчислюємо добуток (може бути дуже великим!)
    cpp_int product = a * b;
    
    // 2. Перевіряємо початкову умову (p | a·b)
    if (product % p != 0) {
        cout << "[ПОМИЛКА] Число p не ділить добуток a·b.\n";
        cout << "Умова леми не виконується, перевірка зупинена.\n";
        return;
    }
    
    cout << "[УСПІХ] Число p успішно ділить добуток a·b.\n";
    
    // 3. Перевіряємо наслідок (p | a або p | b)
    bool p_divides_a = (a % p == 0);
    bool p_divides_b = (b % p == 0);
    
    if (p_divides_a || p_divides_b) {
        cout << "[УСПІХ] Лема підтверджена!\n";
        if (p_divides_a) cout << "        p ділить число a.\n";
        if (p_divides_b) cout << "        p ділить число b.\n";
    } else {
        cout << "[КРИТИЧНА ПОМИЛКА] p ділить добуток, але не ділить жодного множника!\n";
        cout << "Це означає, що число p ТОЧНО НЕ Є ПРОСТИМ.\n";
        cout << "НСД(p, a) = " << gcd_large(p, a) << "\n";
        cout << "НСД(p, b) = " << gcd_large(p, b) << "\n";
    }
}
