void segmentedSieve(int n) {
    int limit = floor(sqrt(n)) + 1;
    vector<int> prime;
    prime.reserve(limit);
    simpleSieve(limit, prime);

    int low = limit;
    int high = 2 * limit;
    
    // Якщо n менше за limit
    if (low >= n) return;

    while (low < n) {
        if (high >= n) {
            high = n;
        }

        // Масив для поточного сегмента
        vector<bool> mark(high - low + 1, true);

        for (int i = 0; i < prime.size(); i++) {
            // Знаходимо найменше число у сегменті, яке є кратним prime[i]
            int loLim = floor(low / prime[i]) * prime[i];
            if (loLim < low)
                loLim += prime[i];
            
            // Якщо loLim дорівнює самому простому числу, починаємо з наступного кратного
            if (loLim == prime[i])
                loLim += prime[i];

            for (int j = loLim; j <= high; j += prime[i]) {
                mark[j - low] = false;
            }
        }

        // Тут ми можемо виводити або зберігати знайдені прості числа у сегменті
        for (int i = low; i <= high; i++) {
            if (mark[i - low]) {
                cout << i << " ";
            }
        }

        low = low + limit;
        high = high + limit;
    }
}
