#include <complex>

using Cplx = std::complex<double>;

// F пишемо шаблоном, щоб її можна було інстанціювати і для double,
// і для std::complex<double>. Це головна вимога способу.
template <class T>
std::vector<T> F(const std::vector<T>& v)
{
    return { v[0] * v[0] + v[1] * v[1] - T(4.0),
             v[0] * v[1]               - T(1.0) };
}

Mat jacobianComplexStep(const Vec& x, std::size_t m)
{
    const double h = 1e-30;
    const std::size_t n = x.size();
    Mat J(m, Vec(n));
    std::vector<Cplx> z(x.begin(), x.end());
    for (std::size_t j = 0; j < n; ++j) {
        z[j] = Cplx(x[j], h);
        const std::vector<Cplx> f = F(z);
        z[j] = Cplx(x[j], 0.0);
        for (std::size_t i = 0; i < m; ++i)
            J[i][j] = f[i].imag() / h;
    }
    return J;
}
