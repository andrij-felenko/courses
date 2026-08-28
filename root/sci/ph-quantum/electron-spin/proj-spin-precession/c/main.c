#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double real;
    double imag;
} Complex;

static Complex c_add(Complex a, Complex b) {
    return (Complex){a.real + b.real, a.imag + b.imag};
}

static Complex c_sub(Complex a, Complex b) {
    return (Complex){a.real - b.real, a.imag - b.imag};
}

static Complex c_mul(Complex a, Complex b) {
    return (Complex){
        a.real * b.real - a.imag * b.imag,
        a.real * b.imag + a.imag * b.real
    };
}

static Complex c_scale(Complex a, double s) {
    return (Complex){a.real * s, a.imag * s};
}

typedef struct {
    Complex alpha;
    Complex beta;
} Spinor;

typedef struct {
    double Bx;
    double By;
    double Bz;
} Vector3D;

typedef struct {
    Spinor d_alpha_dt;
    Spinor d_beta_dt;
} SpinorDeriv;

static SpinorDeriv compute_derivative(Spinor s, Vector3D B, double gamma) {
    /* dalpha/dt = -i (gamma/2) [ Bz * alpha + (Bx - i By) * beta ] */
    /* dbeta/dt  = -i (gamma/2) [ (Bx + i By) * alpha - Bz * beta ] */
    double factor = -0.5 * gamma;
    
    Complex Bx_minus_iBy = {B.Bx, -B.By};
    Complex Bx_plus_iBy  = {B.Bx,  B.By};

    Complex term_a1 = c_scale(s.alpha, B.Bz);
    Complex term_a2 = c_mul(Bx_minus_iBy, s.beta);
    Complex rhs_a   = c_add(term_a1, term_a2);
    
    /* Mnemonic: multiply by -i means (x + i y)*(-i) = y - i x */
    Complex d_alpha = {factor * rhs_a.imag, -factor * rhs_a.real};

    Complex term_b1 = c_mul(Bx_plus_iBy, s.alpha);
    Complex term_b2 = c_scale(s.beta, -B.Bz);
    Complex rhs_b   = c_add(term_b1, term_b2);

    Complex d_beta = {factor * rhs_b.imag, -factor * rhs_b.real};

    SpinorDeriv res;
    res.d_alpha_dt.alpha = d_alpha;
    res.d_alpha_dt.beta  = (Complex){0, 0};
    res.d_beta_dt.beta   = d_beta;
    return res;
}

static Spinor rk4_step(Spinor s, Vector3D B, double gamma, double dt) {
    SpinorDeriv k1 = compute_derivative(s, B, gamma);

    Spinor s_k2 = {
        c_add(s.alpha, c_scale(k1.d_alpha_dt.alpha, 0.5 * dt)),
        c_add(s.beta,  c_scale(k1.d_beta_dt.beta,   0.5 * dt))
    };
    SpinorDeriv k2 = compute_derivative(s_k2, B, gamma);

    Spinor s_k3 = {
        c_add(s.alpha, c_scale(k2.d_alpha_dt.alpha, 0.5 * dt)),
        c_add(s.beta,  c_scale(k2.d_beta_dt.beta,   0.5 * dt))
    };
    SpinorDeriv k3 = compute_derivative(s_k3, B, gamma);

    Spinor s_k4 = {
        c_add(s.alpha, c_scale(k3.d_alpha_dt.alpha, dt)),
        c_add(s.beta,  c_scale(k3.d_beta_dt.beta,   dt))
    };
    SpinorDeriv k4 = compute_derivative(s_k4, B, gamma);

    Complex d_alpha_sum = c_add(k1.d_alpha_dt.alpha, c_scale(k2.d_alpha_dt.alpha, 2.0));
    d_alpha_sum = c_add(d_alpha_sum, c_scale(k3.d_alpha_dt.alpha, 2.0));
    d_alpha_sum = c_add(d_alpha_sum, k4.d_alpha_dt.alpha);

    Complex d_beta_sum = c_add(k1.d_beta_dt.beta, c_scale(k2.d_beta_dt.beta, 2.0));
    d_beta_sum = c_add(d_beta_sum, c_scale(k3.d_beta_dt.beta, 2.0));
    d_beta_sum = c_add(d_beta_sum, k4.d_beta_dt.beta);

    Spinor next_s = {
        c_add(s.alpha, c_scale(d_alpha_sum, dt / 6.0)),
        c_add(s.beta,  c_scale(d_beta_sum,  dt / 6.0))
    };

    /* Normalize to prevent numerical drift */
    double norm = sqrt(next_s.alpha.real * next_s.alpha.real + next_s.alpha.imag * next_s.alpha.imag +
                       next_s.beta.real  * next_s.beta.real  + next_s.beta.imag  * next_s.beta.imag);
    if (norm > 1e-12) {
        next_s.alpha = c_scale(next_s.alpha, 1.0 / norm);
        next_s.beta  = c_scale(next_s.beta,  1.0 / norm);
    }
    return next_s;
}

int main(void) {
    /* Initialize spinor state: spin along +x axis: (|up> + |down>) / sqrt(2) */
    Spinor s = {
        {1.0 / sqrt(2.0), 0.0},
        {1.0 / sqrt(2.0), 0.0}
    };

    Vector3D B = {0.0, 0.0, 1.0}; /* Constant B_z field = 1 Tesla */
    double gamma = 1.7608596e11;   /* Electron gyromagnetic ratio (rad/(s*T)) */
    double dt = 1e-13;            /* Time step in seconds */
    int steps = 100;

    printf("Time (ps) | <Sx>       | <Sy>       | <Sz>\n");
    printf("---------------------------------------------\n");

    for (int i = 0; i <= steps; ++i) {
        double t = i * dt;
        /* <Sx> = (alpha* beta + beta* alpha) / 2 */
        double Sx = s.alpha.real * s.beta.real + s.alpha.imag * s.beta.imag;
        /* <Sy> = (alpha.imag * beta.real - alpha.real * beta.imag) */
        double Sy = s.alpha.imag * s.beta.real - s.alpha.real * s.beta.imag;
        /* <Sz> = (|alpha|^2 - |beta|^2) / 2 */
        double Sz = 0.5 * ((s.alpha.real * s.alpha.real + s.alpha.imag * s.alpha.imag) -
                           (s.beta.real  * s.beta.real  + s.beta.imag  * s.beta.imag));

        if (i % 10 == 0) {
            printf("%9.3f | %10.6f | %10.6f | %10.6f\n", t * 1e12, Sx, Sy, Sz);
        }
        s = rk4_step(s, B, gamma, dt);
    }
    return 0;
}
