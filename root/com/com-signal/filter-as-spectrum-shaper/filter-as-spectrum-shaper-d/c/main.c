/* ковзне середнє по N=10 = ФНЧ зі зрізом ~44 Гц при fs=1000 Гц */
#define N 10
static float buf[N];          /* кільцевий буфер останніх відліків */
static int   pos = 0;
static float run = 0.0f;      /* поточна сума вікна */

float ma_lowpass(float x) {
    run -= buf[pos];          /* викинути найстаріший відлік */
    buf[pos] = x;             /* записати новий */
    run += x;                 /* додати його до суми */
    pos = (pos + 1) % N;
    return run / N;           /* середнє = вихід ФНЧ */
}
