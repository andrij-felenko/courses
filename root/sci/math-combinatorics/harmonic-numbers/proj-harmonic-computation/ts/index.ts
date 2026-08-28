const EULER_MASCHERONI = 0.57721566490153286060;

export interface HarmonicResult {
    n: number;
    value: number;
    method: 'kahan' | 'asymptotic';
}

export function computeHarmonic(n: number): HarmonicResult {
    if (!Number.isInteger(n) || n < 1) {
        throw new RangeError("Аргумент n повинен бути цілим числом >= 1");
    }

    if (n <= 1000) {
        let sum = 0.0;
        let c = 0.0;
        for (let k = 1; k <= n; k++) {
            const y = (1.0 / k) - c;
            const t = sum + y;
            c = (t - sum) - y;
            sum = t;
        }
        return { n, value: sum, method: 'kahan' };
    }

    const nd = n;
    const n2 = nd * nd;
    const n4 = n2 * n2;
    const n6 = n4 * n2;

    const val = Math.log(nd) + EULER_MASCHERONI
        + (1.0 / (2.0 * nd))
        - (1.0 / (12.0 * n2))
        + (1.0 / (120.0 * n4))
        - (1.0 / (252.0 * n6));

    return { n, value: val, method: 'asymptotic' };
}

// Приклад використання:
const testValues = [1, 5, 10, 1000, 1000000];
for (const n of testValues) {
    const res = computeHarmonic(n);
    console.log(`H[${res.n}] = ${res.value.toFixed(15)} (${res.method})`);
}
