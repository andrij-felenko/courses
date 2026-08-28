#include <cstdio>
#include <cmath>
#include <vector>
#include <algorithm>
using namespace std;

// Розв'язати лінійну систему M·c = b (n×n) методом Гаусса з вибором головного елемента.
vector<double> solve(vector<vector<double>> M, vector<double> b) {
    int n = (int)b.size();
    for (int col = 0; col < n; col++) {
        int piv = col;                                   // головний рядок — найбільший за модулем у стовпці
        for (int r = col + 1; r < n; r++)
            if (fabs(M[r][col]) > fabs(M[piv][col])) piv = r;
        swap(M[col], M[piv]); swap(b[col], b[piv]);
        for (int r = col + 1; r < n; r++) {              // виключення нижче діагоналі
            double f = M[r][col] / M[col][col];
            for (int k = col; k < n; k++) M[r][k] -= f * M[col][k];
            b[r] -= f * b[col];
        }
    }
    vector<double> c(n);                                 // зворотний хід
    for (int r = n - 1; r >= 0; r--) {
        double s = b[r];
        for (int k = r + 1; k < n; k++) s -= M[r][k] * c[k];
        c[r] = s / M[r][r];
    }
    return c;
}

// Підігнати поліном степеня d до точок (x,y) методом найменших квадратів (нормальні рівняння).
vector<double> polyfit(const vector<double>& x, const vector<double>& y, int d) {
    int m = d + 1;
    vector<vector<double>> M(m, vector<double>(m, 0.0));
    vector<double> b(m, 0.0);
    for (size_t i = 0; i < x.size(); i++) {
        vector<double> p(2 * d + 1);                     // степені x_i: 1, x, x², ...
        p[0] = 1.0;
        for (int k = 1; k <= 2 * d; k++) p[k] = p[k - 1] * x[i];
        for (int r = 0; r < m; r++) {
            for (int col = 0; col < m; col++) M[r][col] += p[r + col];
            b[r] += p[r] * y[i];
        }
    }
    return solve(M, b);
}

double predict(const vector<double>& c, double x) {
    double y = 0.0, xp = 1.0;
    for (double ck : c) { y += ck * xp; xp *= x; }
    return y;
}

double mse(const vector<double>& c, const vector<double>& x, const vector<double>& y) {
    double s = 0.0;
    for (size_t i = 0; i < x.size(); i++) {
        double e = predict(c, x[i]) - y[i];
        s += e * e;
    }
    return s / x.size();
}

int main() {
    // Справжня закономірність — пряма y = x. Тренувальні точки з шумом у середині.
    vector<double> xtr = {0, 1, 2}, ytr = {0.0, 1.2, 1.9};
    // Небачені (тестові) точки — теж на прямій y = x.
    vector<double> xte = {3, 4}, yte = {3.0, 4.0};

    for (int d = 1; d <= 2; d++) {
        vector<double> c = polyfit(xtr, ytr, d);
        printf("степінь %d:  train MSE = %.4f   test MSE = %.4f\n",
               d, mse(c, xtr, ytr), mse(c, xte, yte));
    }
    return 0;
}
