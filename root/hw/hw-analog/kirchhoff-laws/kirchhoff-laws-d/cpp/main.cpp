// Струм і спади в простій послідовній петлі з одним джерелом.
// За KVL: E = I·(R1+R2); за Омом: U = I·R. Усе у вольтах, омах, амперах.
struct Loop { float I, U1, U2; };

Loop series_loop(float E, float R1, float R2)
{
    float I  = E / (R1 + R2);   // KVL дає єдиний струм петлі
    float U1 = I * R1;          // закон Ома: спад на R1
    float U2 = I * R2;          // закон Ома: спад на R2
    // інваріант: U1 + U2 має дорівнювати E (контроль KVL)
    return { I, U1, U2 };
}
// auto r = series_loop(12.0f, 1000.0f, 2000.0f); -> r.I=4 мА, U1=4 В, U2=8 В
