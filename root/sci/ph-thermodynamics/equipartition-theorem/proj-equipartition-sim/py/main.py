import numpy as np

def run_equipartition_sim(num_molecules=100, steps=3000, dt=0.001):
    m1, m2 = 1.0, 1.0
    M = m1 + m2
    mu = (m1 * m2) / M
    r0 = 1.0
    k_spring = 100.0

    r1 = np.zeros((num_molecules, 2))
    r2 = np.zeros((num_molecules, 2))
    for i in range(num_molecules):
        cx, cy = (i % 10) * 4.0, (i // 10) * 4.0
        r1[i] = [cx - 0.5 * r0, cy]
        r2[i] = [cx + 0.5 * r0, cy]

    v1 = np.random.normal(0.0, 2.0, size=(num_molecules, 2))
    v2 = np.random.normal(0.0, 2.0, size=(num_molecules, 2))

    def calc_forces(r1, r2):
        r_rel = r2 - r1
        dist = np.linalg.norm(r_rel, axis=1, keepdims=True)
        dr = dist - r0
        n = r_rel / np.maximum(dist, 1e-9)
        f_spring = n * (k_spring * dr)
        return f_spring, -f_spring

    f1, f2 = calc_forces(r1, r2)

    print("Крок\tE_trans\tE_rot\tE_vib")
    for step in range(steps + 1):
        v1 += 0.5 * (dt / m1) * f1
        v2 += 0.5 * (dt / m2) * f2
        r1 += dt * v1
        r2 += dt * v2

        f1, f2 = calc_forces(r1, r2)

        v1 += 0.5 * (dt / m1) * f1
        v2 += 0.5 * (dt / m2) * f2

        if step % 1000 == 0:
            v_cm = (m1 * v1 + m2 * v2) / M
            e_trans = 0.5 * M * np.sum(v_cm**2, axis=1)

            r_rel = r2 - r1
            dist = np.linalg.norm(r_rel, axis=1)
            n = r_rel / np.maximum(dist[:, None], 1e-9)
            v_rel = v2 - v1

            v_vib = np.sum(v_rel * n, axis=1)
            v_rot = v_rel[:, 0] * n[:, 1] - v_rel[:, 1] * n[:, 0]

            e_vib = 0.5 * mu * (v_vib**2) + 0.5 * k_spring * ((dist - r0)**2)
            e_rot = 0.5 * mu * (v_rot**2)

            print(f"{step}\t{np.mean(e_trans):.4f}\t{np.mean(e_rot):.4f}\t{np.mean(e_vib):.4f}")

if __name__ == "__main__":
    run_equipartition_sim()
