def compute_fnn(signal: np.ndarray, delay: int, max_m: int = 6, r_tol: float = 15.0) -> np.ndarray:
    """
    Обчислення частки хибних найближчих сусідів FNN(m) для вимірностей від 1 до max_m.
    """
    n = len(signal)
    fnn_ratios = np.zeros(max_m)
    r_attr = np.std(signal)
    
    for m in range(1, max_m + 1):
        n_vectors = n - m * delay
        if n_vectors <= 0:
            break
            
        # Побудова векторів у вимірності m
        vectors_m = np.zeros((n_vectors, m))
        for j in range(m):
            vectors_m[:, j] = signal[j * delay : j * delay + n_vectors]
            
        false_neighbors = 0
        
        # Пошук найближчих сусідів методом найменшої евклідової відстані
        for i in range(n_vectors):
            dists = np.linalg.norm(vectors_m - vectors_m[i], axis=1)
            dists[i] = np.inf # Виключення самої точки
            
            nn_idx = np.argmin(dists)
            dist_m = dists[nn_idx]
            
            if dist_m == 0:
                continue
                
            # Додаткова координата при переході до m+1
            val_i_next = signal[i + m * delay]
            val_j_next = signal[nn_idx + m * delay]
            diff_next = abs(val_i_next - val_j_next)
            
            # Умова Kennel R1 та R2
            if (diff_next / dist_m > r_tol) or (np.sqrt(dist_m**2 + diff_next**2) / r_attr > 2.0):
                false_neighbors += 1
                
        fnn_ratios[m - 1] = false_neighbors / n_vectors
        
    return fnn_ratios
