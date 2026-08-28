const MAGNUS_A = 6.112;
const MAGNUS_B = 17.67;
const MAGNUS_C = 243.5;
const PSYCHRO_A = 0.000662;

export interface HumidityMetrics {
    relativeHumidityPct: number;
    dewPointCelsius: number;
    actualVaporPressureHpa: number;
    saturationVaporPressureHpa: number;
}

export function saturationVaporPressure(tempCelsius: number): number {
    return MAGNUS_A * Math.exp((MAGNUS_B * tempCelsius) / (MAGNUS_C + tempCelsius));
}

export function dewPoint(tempCelsius: number, relativeHumidityPct: number): number | null {
    if (relativeHumidityPct <= 0 || relativeHumidityPct > 100) return null;
    const gamma = Math.log(relativeHumidityPct / 100) + (MAGNUS_B * tempCelsius) / (MAGNUS_C + tempCelsius);
    return (MAGNUS_C * gamma) / (MAGNUS_B - gamma);
}

export function calculatePsychrometrics(tDry: number, tWet: number, pressureHpa: number = 1013.25): HumidityMetrics {
    if (tWet > tDry) throw new Error("tWet cannot exceed tDry");
    
    const eSWet = saturationVaporPressure(tWet);
    const eSDry = saturationVaporPressure(tDry);
    const actualE = eSWet - PSYCHRO_A * pressureHpa * (tDry - tWet);
    
    const rh = Math.min(100, Math.max(0, (actualE / eSDry) * 100));
    const td = dewPoint(tDry, rh) ?? 0;
    
    return {
        relativeHumidityPct: rh,
        dewPointCelsius: td,
        actualVaporPressureHpa: actualE,
        saturationVaporPressureHpa: eSDry
    };
}

// Приклад виклику
const res = calculatePsychrometrics(25.0, 18.5, 1013.25);
console.log(`TS Result: RH=${res.relativeHumidityPct.toFixed(2)}%, Td=${res.dewPointCelsius.toFixed(2)}°C`);
