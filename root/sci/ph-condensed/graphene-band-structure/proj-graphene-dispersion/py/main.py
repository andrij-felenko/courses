import numpy as np

def graphene_dispersion(kx, ky, t=2.8, acc=1.42):
    """
    Обчислення енергії валентної зони та зони провідності графену.
    t: інтеграл перескоку (еВ)
    acc: відстань C-C (Ангстрем)
    """
    kx_a = kx * acc * np.sqrt(3) / 2.0
    ky_a = ky * acc * 1.5
    
    # Модуль структурного фактора |f(k)|^2
    f_sq = 1.0 + 4.0 * np.cos(kx_a) * np.cos(ky_a) + 4.0 * (np.cos(kx_a) ** 2)
    # Запобігання від'ємним значенням під коренем через чисельну похибку
    f_sq = np.maximum(f_sq, 0.0)
    
    E_val = -t * np.sqrt(f_sq)
    E_cond = t * np.sqrt(f_sq)
    return E_val, E_cond

def generate_k_path(acc=1.42, num_points=200):
    """
    Генерація точок уздовж контуру високої симетрії Gamma -> K -> M -> Gamma.
    """
    K_x = 4.0 * np.pi / (3.0 * np.sqrt(3) * acc)
    K_y = 0.0
    
    M_x = np.pi / (np.sqrt(3) * acc)
    M_y = np.pi / (3.0 * acc)
    
    # Шлях Gamma -> K
    path1_x = np.linspace(0, K_x, num_points)
    path1_y = np.linspace(0, K_y, num_points)
    
    # Шлях K -> M
    path2_x = np.linspace(K_x, M_x, num_points)
    path2_y = np.linspace(K_y, M_y, num_points)
    
    # Шлях M -> Gamma
    path3_x = np.linspace(M_x, 0, num_points)
    path3_y = np.linspace(M_y, 0, num_points)
    
    kx = np.concatenate([path1_x, path2_x[1:], path3_x[1:]])
    ky = np.concatenate([path1_y, path2_y[1:], path3_y[1:]])
    
    return kx, ky

def calculate_dos(t=2.8, acc=1.42, grid_size=300, energy_points=500, sigma=0.05):
    """
    Обчислення густини станів g(E) методом розширення Гаусса.
    """
    k_max = 4.0 * np.pi / (3.0 * np.sqrt(3) * acc)
    kx_range = np.linspace(-k_max * 1.5, k_max * 1.5, grid_size)
    ky_range = np.linspace(-k_max * 1.5, k_max * 1.5, grid_size)
    
    KX, KY = np.meshgrid(kx_range, ky_range)
    E_v, E_c = graphene_dispersion(KX, KY, t=t, acc=acc)
    
    energies = np.ravel(np.block([E_v, E_c]))
    E_axis = np.linspace(-3 * t, 3 * t, energy_points)
    dos = np.zeros(energy_points)
    
    for i, E in enumerate(E_axis):
        # Гауссівське розширення дельта-функції
        gauss = np.exp(-((energies - E) ** 2) / (2.0 * sigma ** 2)) / (sigma * np.sqrt(2.0 * np.pi))
        dos[i] = np.mean(gauss)
        
    return E_axis, dos

if __name__ == "__main__":
    kx, ky = generate_k_path()
    E_val, E_cond = graphene_dispersion(kx, ky)
    print(f"Згенеровано {len(kx)} точок вздовж симетричного шляху.")
    print(f"Мінімальна енергія валентної зони: {np.min(E_val):.3f} еВ")
    print(f"Максимальна енергія зони провідності: {np.max(E_cond):.3f} еВ")
