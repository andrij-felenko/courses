import math
import random
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, o: 'Vec3') -> 'Vec3':
        return Vec3(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o: 'Vec3') -> 'Vec3':
        return Vec3(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, s: float) -> 'Vec3':
        return Vec3(self.x * s, self.y * s, self.z * s)

    def norm_sq(self) -> float:
        return self.x * self.x + self.y * self.y + self.z * self.z

class Particle:
    def __init__(self, pos: Vec3):
        self.pos = pos
        self.vel = Vec3()
        self.force = Vec3()
        self.last_pos = Vec3(pos.x, pos.y, pos.z)

class LJSimulation:
    def __init__(self, num_particles: int = 256, density: float = 0.8442, target_temp: float = 0.728):
        self.num_particles = num_particles
        self.target_temp = target_temp
        self.box_len = (num_particles / density) ** (1.0 / 3.0)
        self.rcut = 2.5
        self.rskin = 0.3
        self.rlist = self.rcut + self.rskin
        self.rcut2 = self.rcut * self.rcut
        self.rlist2 = self.rlist * self.rlist
        self.tau_temp = 0.1

        self.particles: List[Particle] = []
        self.neighbor_list: List[Tuple[int, int]] = []

        self._init_positions_fcc()
        self._init_velocities()
        self._rebuild_neighbor_list()

    def _init_positions_fcc(self):
        n_side = math.ceil((self.num_particles / 4.0) ** (1.0 / 3.0))
        a = self.box_len / n_side
        basis = [
            Vec3(0.0, 0.0, 0.0),
            Vec3(0.5 * a, 0.5 * a, 0.0),
            Vec3(0.5 * a, 0.0, 0.5 * a),
            Vec3(0.0, 0.5 * a, 0.5 * a)
        ]
        idx = 0
        for ix in range(n_side):
            for iy in range(n_side):
                for iz in range(n_side):
                    base = Vec3(ix * a, iy * a, iz * a)
                    for b in basis:
                        if idx < self.num_particles:
                            self.particles.append(Particle(base + b))
                            idx += 1

    def _init_velocities(self):
        random.seed(42)
        sum_v = Vec3()
        for p in self.particles:
            p.vel = Vec3(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
            sum_v += p.vel

        v_cm = sum_v * (1.0 / self.num_particles)
        v2_sum = 0.0
        for p in self.particles:
            p.vel -= v_cm
            v2_sum += p.vel.norm_sq()

        current_temp = v2_sum / (3.0 * self.num_particles)
        scale = math.sqrt(self.target_temp / current_temp)
        for p in self.particles:
            p.vel *= scale

    def _min_image(self, dr: Vec3) -> Vec3:
        inv_b = 1.0 / self.box_len
        return Vec3(
            dr.x - self.box_len * round(dr.x * inv_b),
            dr.y - self.box_len * round(dr.y * inv_b),
            dr.z - self.box_len * round(dr.z * inv_b)
        )

    def _rebuild_neighbor_list(self):
        self.neighbor_list.clear()
        for i in range(self.num_particles - 1):
            p_i = self.particles[i]
            for j in range(i + 1, self.num_particles):
                p_j = self.particles[j]
                dr = self._min_image(p_i.pos - p_j.pos)
                if dr.norm_sq() < self.rlist2:
                    self.neighbor_list.append((i, j))
        for p in self.particles:
            p.last_pos = Vec3(p.pos.x, p.pos.y, p.pos.z)

    def _check_neighbor_rebuild(self):
        max_dr2 = 0.0
        for p in self.particles:
            dr = self._min_image(p.pos - p.last_pos)
            dr2 = dr.norm_sq()
            if dr2 > max_dr2:
                max_dr2 = dr2
        if 2.0 * math.sqrt(max_dr2) > self.rskin:
            self._rebuild_neighbor_list()

    def compute_forces() -> float:
        pe = 0.0
        for p in self.particles:
            p.force = Vec3()

        for i, j in self.neighbor_list:
            p_i = self.particles[i]
            p_j = self.particles[j]
            dr = self._min_image(p_i.pos - p_j.pos)
            r2 = dr.norm_sq()
            if r2 < self.rcut2:
                inv_r2 = 1.0 / r2
                inv_r6 = inv_r2 * inv_r2 * inv_r2
                f_scalar = 48.0 * inv_r6 * (inv_r6 - 0.5) * inv_r2
                f_vec = dr * f_scalar
                p_i.force += f_vec
                p_j.force -= f_vec
                pe += 4.0 * inv_r6 * (inv_r6 - 1.0)
        return pe

    def apply_thermostat(self, dt: float, inst_temp: float):
        if inst_temp <= 1e-10:
            return
        lam = math.sqrt(1.0 + (dt / self.tau_temp) * (self.target_temp / inst_temp - 1.0))
        for p in self.particles:
            p.vel *= lam

    def run(self, steps: int = 1000, dt: float = 0.005):
        pe = self.compute_forces()
        print(f"{'Step':>6} | {'E_kin/N':>10} | {'E_pot/N':>10} | {'E_tot/N':>10} | {'Temp*':>8}")
        print("-" * 55)
        for step in range(steps + 1):
            for p in self.particles:
                p.pos += p.vel * dt + p.force * (0.5 * dt * dt)
                p.pos.x -= self.box_len * math.floor(p.pos.x / self.box_len)
                p.pos.y -= self.box_len * math.floor(p.pos.y / self.box_len)
                p.pos.z -= self.box_len * math.floor(p.pos.z / self.box_len)
                p.vel += p.force * (0.5 * dt)

            self._check_neighbor_rebuild()
            pe = self.compute_forces()

            ke = 0.0
            for p in self.particles:
                p.vel += p.force * (0.5 * dt)
                ke += 0.5 * p.vel.norm_sq()

            inst_temp = (2.0 * ke) / (3.0 * self.num_particles)
            if step < 500:
                self.apply_thermostat(dt, inst_temp)

            if step % 100 == 0:
                n_inv = 1.0 / self.num_particles
                print(f"{step:6d} | {ke * n_inv:10.4f} | {pe * n_inv:10.4f} | {(ke + pe) * n_inv:10.4f} | {inst_temp:8.4f}")

if __name__ == "__main__":
    sim = LJSimulation()
    sim.run(steps=1000, dt=0.005)
