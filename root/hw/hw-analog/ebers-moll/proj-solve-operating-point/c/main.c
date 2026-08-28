#include <stdio.h>
#include <math.h>

/* --- Параметри транзистора (Еберс — Молл у формі з I_S) --- */
static const double Vt = 0.02585;    /* тепловий потенціал, В   */
static const double I_S = 1e-14;     /* струм насичення, А      */
static const double aF = 0.99, aR = 0.5;

/* --- Схема --- */
static const double VBB = 5.0, RB = 220e3;
static const double VCC = 5.0, RC = 1.0e3;

typedef struct { double Ic, Ib, gF, gR; } Dev;

static Dev device(double vbe, double vbc) {
    double I_ES = I_S/aF, I_CS = I_S/aR;
    double IF = I_ES*(exp(vbe/Vt) - 1.0);   /* прямий діод   */
    double IR = I_CS*(exp(vbc/Vt) - 1.0);   /* обернений діод */
    Dev d;
    d.Ic = aF*IF - IR;
    d.Ib = (1 - aF)*IF + (1 - aR)*IR;
    d.gF = (I_ES/Vt)*exp(vbe/Vt);
    d.gR = (I_CS/Vt)*exp(vbc/Vt);
    return d;
}

/* Обмеження стрибка напруги на переході — pnjlim із SPICE */
static double limitv(double vnew, double vold, double isat) {
    double vcrit = Vt*log(Vt/(sqrt(2.0)*isat));
    if (vnew > vcrit && fabs(vnew - vold) > 2*Vt) {
        if (vold > 0) {
            double arg = 1.0 + (vnew - vold)/Vt;
            return arg > 0 ? vold + Vt*log(arg) : vcrit;
        }
        return Vt*log(vnew/Vt);
    }
    return vnew;
}

int main(void) {
    const double I_ES = I_S/aF, I_CS = I_S/aR;
    double vb = 0.0, vc = 0.0;

    for (int k = 0; k < 100; k++) {
        double vbe = vb, vbc = vb - vc;
        Dev d = device(vbe, vbc);

        double fB = (VBB - vb)/RB - d.Ib;      /* нев'язки KCL */
        double fC = (VCC - vc)/RC - d.Ic;

        double J11 = -1.0/RB - ((1 - aF)*d.gF + (1 - aR)*d.gR);
        double J12 =  (1 - aR)*d.gR;
        double J21 = -aF*d.gF + d.gR;
        double J22 = -1.0/RC - d.gR;

        double det = J11*J22 - J12*J21;        /* J·Δ = −f, 2×2 */
        double b1 = -fB, b2 = -fC;
        double dvb = (J22*b1 - J12*b2)/det;
        double dvc = (J11*b2 - J21*b1)/det;
        double vbn = vb + dvb, vcn = vc + dvc;

        double vbe_l = limitv(vbn,        vbe, I_ES);   /* обмеження */
        double vbc_l = limitv(vbn - vcn,  vbc, I_CS);
        vbn = vbe_l; vcn = vbe_l - vbc_l;

        double step = fmax(fabs(vbn - vb), fabs(vcn - vc));
        vb = vbn; vc = vcn;
        if (step < 1e-9) {
            printf("V_BE=%.4f В  V_CE=%.4f В  I_C=%.4f мА  за %d ітерацій\n",
                   vb, vc, d.Ic*1e3, k + 1);
            return 0;
        }
    }
    printf("не збіглося\n");
    return 1;
}
