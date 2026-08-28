export enum SourceType {
    SinglePhoton = "SinglePhoton",
    Coherent = "Coherent",
    Thermal = "Thermal"
}

export class HBTSimulation {
    private totalBins: number;
    private dtNs: number;
    private maxLag: number;
    private countsA: Int32Array;
    private countsB: Int32Array;
    private g2Results: Float64Array;

    constructor(totalBins: number, dtNs: number, maxLag: number) {
        this.totalBins = totalBins;
        this.dtNs = dtNs;
        this.maxLag = maxLag;
        this.countsA = new Int32Array(totalBins);
        this.countsB = new Int32Array(totalBins);
        this.g2Results = new Float64Array(maxLag + 1);
    }

    public run(type: SourceType, meanPhotons: number): void {
        for (let i = 0; i < this.totalBins; i++) {
            let nPhotons = 0;

            if (type === SourceType.SinglePhoton) {
                nPhotons = Math.random() < meanPhotons ? 1 : 0;
            } else if (type === SourceType.Coherent) {
                // Алгоритм Кнута для пуассонівського розподілу
                const L = Math.exp(-meanPhotons);
                let k = 0;
                let p = 1.0;
                do {
                    k++;
                    p *= Math.random();
                } while (p > L);
                nPhotons = k - 1;
            } else {
                // Статистика Бозе — Ейнштейна
                const u = Math.random();
                nPhotons = Math.floor(-meanPhotons * Math.log(1.0 - u + 1e-12));
            }

            for (let p = 0; p < nPhotons; p++) {
                if (Math.random() < 0.5) {
                    this.countsA[i]++;
                } else {
                    this.countsB[i]++;
                }
            }
        }
    }

    public calculateG2(): Float64Array {
        let sumA = 0;
        let sumB = 0;
        for (let i = 0; i < this.totalBins; i++) {
            sumA += this.countsA[i];
            sumB += this.countsB[i];
        }

        const meanA = sumA / this.totalBins;
        const meanB = sumB / this.totalBins;
        const norm = meanA * meanB;

        if (norm === 0) return this.g2Results;

        for (let lag = 0; lag <= this.maxLag; lag++) {
            let correlationSum = 0;
            const validPairs = this.totalBins - lag;

            for (let i = 0; i < validPairs; i++) {
                correlationSum += this.countsA[i] * this.countsB[i + lag];
            }

            this.g2Results[lag] = (correlationSum / validPairs) / norm;
        }

        return this.g2Results;
    }
}
