// heisenberg_mc.ts — TypeScript симуляція Метрополіса для Гейзенберга
interface Spin3D {
    x: number;
    y: number;
    z: number;
}

class HeisenbergLatticeTS {
    private spins: Spin3D[];
    private L: number;
    private J: number;
    private h: number;
    private temp: number;

    constructor(size: number, J: number, h: number, temp: number) {
        this.L = size;
        this.J = J;
        this.h = h;
        this.temp = temp;
        this.spins = new Array(size * size);
        for (let i = 0; i < this.spins.length; i++) {
            this.spins[i] = this.randomSpin();
        }
    }

    private randomSpin(): Spin3D {
        const z = 2.0 * Math.random() - 1.0;
        const phi = 2.0 * Math.PI * Math.random();
        const r = Math.sqrt(1.0 - z * z);
        return { x: r * Math.cos(phi), y: r * Math.sin(phi), z };
    }

    private dot(a: Spin3D, b: Spin3D): number {
        return a.x * b.x + a.y * b.y + a.z * b.z;
    }

    public step(): void {
        const total = this.L * this.L;
        for (let s = 0; s < total; s++) {
            const idx = Math.floor(Math.random() * total);
            const r = Math.floor(idx / this.L);
            const c = idx % this.L;

            const nbrIdx = [
                ((r - 1 + this.L) % this.L) * this.L + c,
                ((r + 1) % this.L) * this.L + c,
                r * this.L + ((c + 1) % this.L),
                r * this.L + ((c - 1 + this.L) % this.L)
            ];

            const sumNbr: Spin3D = { x: 0, y: 0, z: 0 };
            for (const n of nbrIdx) {
                sumNbr.x += this.spins[n].x;
                sumNbr.y += this.spins[n].y;
                sumNbr.z += this.spins[n].z;
            }

            const oldS = this.spins[idx];
            const newS = this.randomSpin();

            const dE = -this.J * (this.dot(newS, sumNbr) - this.dot(oldS, sumNbr))
                       - this.h * (newS.z - oldS.z);

            if (dE <= 0 || Math.random() < Math.exp(-dE / this.temp)) {
                this.spins[idx] = newS;
            }
        }
    }

    public measure(): { energy: number; mag: number } {
        let totalE = 0;
        let mx = 0, my = 0, mz = 0;

        for (let r = 0; r < this.L; r++) {
            for (let c = 0; c < this.L; c++) {
                const idx = r * this.L + c;
                const south = ((r + 1) % this.L) * this.L + c;
                const east = r * this.L + ((c + 1) % this.L);

                const ePair = this.dot(this.spins[idx], this.spins[south]) +
                              this.dot(this.spins[idx], this.spins[east]);

                totalE -= this.J * ePair + this.h * this.spins[idx].z;
                mx += this.spins[idx].x;
                my += this.spins[idx].y;
                mz += this.spins[idx].z;
            }
        }

        const n = this.L * this.L;
        const mag = Math.sqrt(mx * mx + my * my + mz * mz) / n;
        return { energy: totalE / n, mag };
    }
}

const simTS = new HeisenbergLatticeTS(16, 1.0, 0.05, 0.8);
for (let i = 0; i < 1000; i++) simTS.step();
let sumE = 0, sumM = 0;
for (let i = 0; i < 500; i++) {
    simTS.step();
    const res = simTS.measure();
    sumE += res.energy;
    sumM += res.mag;
}
console.log(`TypeScript TS: Energy=${(sumE/500).toFixed(4)}, |M|=${(sumM/500).toFixed(4)}`);
