for (size_t k = 0; k < n; ++k) {
    for (size_t i = 0; i < n; ++i) {
        // Значення ik стабільне протягом усього циклу по j
        T ik = dist[i * n + k];
        for (size_t j = 0; j < n; ++j) {
            T kj = dist[k * n + j];
            if (ik + kj < dist[i * n + j]) {
                dist[i * n + j] = ik + kj;
            }
        }
    }
}
