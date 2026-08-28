// pendulum_sim.ts - Реалізація симулятора маятника на TypeScript
interface PendulumParams {
    length: number;
    gravity: number;
    dt: number;
}

interface PendulumState {
    theta: number;
    omega: number;
    time: number;
}

export function simulatePendulum(params: PendulumParams, initialDeg: number): { tSim: number; tTheory: number } {
    const theta0 = (initialDeg * Math.PI) / 180.0;
    let state: PendulumState = { theta: theta0, omega: 0, time: 0 };
    const peaks: number[] = [];

    let prevTheta = state.theta;
    let prevPrevTheta = state.theta;

    const derivatives = (th: number, om: number): [number, number] => {
        return [om, -(params.gravity / params.length) * Math.sin(th)];
    };

    while (state.time < 30.0 && peaks.length < 2) {
        const [k1Th, k1Om] = derivatives(state.theta, state.omega);
        const [k2Th, k2Om] = derivatives(state.theta + 0.5 * params.dt * k1Th, state.omega + 0.5 * params.dt * k1Om);
        const [k3Th, k3Om] = derivatives(state.theta + 0.5 * params.dt * k2Th, state.omega + 0.5 * params.dt * k2Om);
        const [k4Th, k4Om] = derivatives(state.theta + params.dt * k3Th, state.omega + params.dt * k4Om);

        state.theta += (params.dt / 6.0) * (k1Th + 2 * k2Th + 2 * k3Th + k4Th);
        state.omega += (params.dt / 6.0) * (k1Om + 2 * k2Om + 2 * k3Om + k4Om);
        state.time += params.dt;

        if (prevTheta > 0 && prevTheta >= prevPrevTheta && prevTheta >= state.theta) {
            peaks.push(state.time - params.dt);
        }
        prevPrevTheta = prevTheta;
        prevTheta = state.theta;
    }

    const tSim = peaks.length === 2 ? peaks[1] - peaks[0] : 0;
    const t0 = 2 * Math.PI * Math.sqrt(params.length / params.gravity);
    const k = Math.sin(theta0 / 2);
    const tTheory = t0 * (1 + 0.25 * k * k + (9 / 64) * Math.pow(k, 4) + (225 / 2304) * Math.pow(k, 6));

    return { tSim, tTheory };
}
