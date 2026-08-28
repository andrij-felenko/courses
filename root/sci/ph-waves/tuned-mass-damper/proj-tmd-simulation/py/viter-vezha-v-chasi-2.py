mu, zeta_s = 0.02, 0.01
f_dh, z_dh = 1/(1+mu), np.sqrt(3*mu/(8*(1+mu)**3))
dt, T = 0.05, 3000.0
n = int(T/dt)
w  = wind(n, dt, seed=1)
xb = sway(mu, f_dh, z_dh, zeta_s, dt, n, w, tmd=False)
xt = sway(mu, f_dh, z_dh, zeta_s, dt, n, w, tmd=True)
cut = n//4                               # відкинути перехідний процес
rms = lambda a: a[cut:].std()
print(rms(xb), rms(xt), 1 - rms(xt)/rms(xb))
