# heisenberg_mc.py — Симуляція моделі Гейзенберга на Python + NumPy
import numpy as np

class HeisenbergModel2D:
    def __init__(self, size=16, J=1.0, h=0.05, temp=0.8):
        self.L = size
        self.J = J
        self.h = h
        self.temp = temp
        # Просторові спіни (L, L, 3)
        angles_z = 2.0 * np.random.random((size, size)) - 1.0
        angles_phi = 2.0 * np.pi * np.random.random((size, size))
        r = np.sqrt(1.0 - angles_z**2)
        
        self.spins = np.stack([r * np.cos(angles_phi), r * np.sin(angles_phi), angles_z], axis=-1)

    def step(self):
        for _ in range(self.L * self.L):
            r = np.random.randint(0, self.L)
            c = np.random.randint(0, self.L)
            
            # Сума 4 найближчих сусідів з періодичними межами
            nbr_sum = (self.spins[(r-1)%self.L, c] + self.spins[(r+1)%self.L, c] +
                       self.spins[r, (c-1)%self.L] + self.spins[r, (c+1)%self.L])
            
            old_spin = self.spins[r, c].copy()
            
            # Новий випадковий спін на сфері
            z = 2.0 * np.random.random() - 1.0
            phi = 2.0 * np.pi * np.random.random()
            rad = np.sqrt(1.0 - z**2)
            new_spin = np.array([rad * np.cos(phi), rad * np.sin(phi), z])
            
            dE = -self.J * (np.dot(new_spin, nbr_sum) - np.dot(old_spin, nbr_sum)) - self.h * (new_spin[2] - old_spin[2])
            
            if dE <= 0 or np.random.random() < np.exp(-dE / self.temp):
                self.spins[r, c] = new_spin

    def measure(self):
        # Сума взаємодій вздовж правого та нижнього сусіда
        east_spins = np.roll(self.spins, -1, axis=1)
        south_spins = np.roll(self.spins, -1, axis=0)
        
        e_pairs = np.sum(self.spins * east_spins) + np.sum(self.spins * south_spins)
        total_E = -self.J * e_pairs - self.h * np.sum(self.spins[:, :, 2])
        
        total_M = np.sum(self.spins, axis=(0, 1))
        mag = np.linalg.norm(total_M) / (self.L * self.L)
        energy = total_E / (self.L * self.L)
        return energy, mag

if __name__ == "__main__":
    sim = HeisenbergModel2D(size=16, temp=0.8, h=0.05)
    print("Термалізація Python моделі...")
    for _ in range(1000):
        sim.step()
    
    energies, mags = [], []
    for _ in range(500):
        sim.step()
        e, m = sim.measure()
        energies.append(e)
        mags.append(m)
        
    print(f"Python Результати (T=0.8, h=0.05):")
    print(f" Середня енергія: {np.mean(energies):.4f}")
    print(f" Середня намагніченість: {np.mean(mags):.4f}")
