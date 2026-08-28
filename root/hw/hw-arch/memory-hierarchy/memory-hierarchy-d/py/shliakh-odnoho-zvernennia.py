# Оцінка середнього часу доступу за різної частки влучань.
# (Ілюстративний розрахунок, не прошивковий гарячий шлях.)

def avg_access_ns(hit_rate, t_cache, t_dram):
    return hit_rate * t_cache + (1.0 - hit_rate) * t_dram


t_cache, t_dram = 1.0, 100.0  # наносекунди

# h = 0.90:  0.90·1 + 0.10·100 = 0.9 + 10.0 = 10.9 нс
print(f"{avg_access_ns(0.90, t_cache, t_dram):.1f} ns")

# h = 0.99:  0.99·1 + 0.01·100 = 0.99 + 1.0 = 1.99 нс
print(f"{avg_access_ns(0.99, t_cache, t_dram):.2f} ns")
