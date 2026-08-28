def compute_correlation_dimension(matrix: np.ndarray, r_vals: np.ndarray) -> np.ndarray:
    """
    Обчислення кореляційного інтегралу C(r) для масиву радіусів r_vals.
    """
    n_pts, m = matrix.shape
    c_r = np.zeros(len(r_vals))
    
    # Обчислення всіх парних евклідових відстаней
    from scipy.spatial.distance import pdist
    dists = pdist(matrix, metric='euclidean')
    total_pairs = len(dists)
    
    for idx, r in enumerate(r_vals):
        c_r[idx] = np.sum(dists < r) / total_pairs
        
    return c_r
