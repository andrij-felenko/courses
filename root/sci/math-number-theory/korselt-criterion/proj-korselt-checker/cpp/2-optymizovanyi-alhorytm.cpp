std::vector<uint64_t> getPrimeFactors(uint64_t n) {
    std::vector<uint64_t> factors;
    
    if (n % 2 == 0) {
        factors.push_back(2);
        while (n % 2 == 0) n /= 2;
    }
    
    for (uint64_t i = 3; i * i <= n; i += 2) {
        if (n % i == 0) {
            factors.push_back(i);
            while (n % i == 0) n /= i;
        }
    }
    
    if (n > 2) {
        factors.push_back(n);
    }
    return factors;
}
