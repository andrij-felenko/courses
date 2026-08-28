from math import sqrt

# Дальність до радіообрію (км) для антени на висоті h (метрів).
def radio_horizon_km(h_m):
    return 3.57 * sqrt(h_m)

d_ground = radio_horizon_km(10.0)    # станція на щоглі 10 м
d_drone  = radio_horizon_km(100.0)   # дрон на висоті 100 м
d_max    = d_ground + d_drone        # повний просвіт між ними
# d_ground ≈ 11.3 км
# d_drone  ≈ 35.7 км
# d_max    ≈ 47.0 км
