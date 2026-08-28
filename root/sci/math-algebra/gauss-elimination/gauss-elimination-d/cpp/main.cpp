#include <cmath>
#include <vector>

// Розв'язати a*x = b методом Гаусса з частковим впорядкуванням.
// a — розширена матриця N×(N+1): останній стовпець це праві частини b.
// Повертає true й кладе результат у x; false — якщо розв'язок не єдиний.
bool gauss(std::vector<std::vector<double>>& a, std::vector<double>& x)
{
    const int N = static_cast<int>(a.size());
    x.assign(N, 0.0);

    for (int col = 0; col < N; col++) {
        // 1) часткове впорядкування: знайти найбільший за модулем півот у стовпці
        int piv = col;
        for (int r = col + 1; r < N; r++)
            if (std::fabs(a[r][col]) > std::fabs(a[piv][col]))
                piv = r;

        if (std::fabs(a[piv][col]) < 1e-12)
            return false;                 // увесь стовпець ~0 → нема єдиного розв'язку

        // підняти знайдений рядок на діагональ (перестановка рядків)
        if (piv != col)
            std::swap(a[col], a[piv]);

        // 2) прямий хід: обнулити стовпець під опорним рядком
        for (int r = col + 1; r < N; r++) {
            double m = a[r][col] / a[col][col];   // множник виключення
            for (int c = col; c <= N; c++)
                a[r][c] -= m * a[col][c];
        }
    }

    // 3) зворотний хід: знизу вгору
    for (int r = N - 1; r >= 0; r--) {
        double s = a[r][N];                       // права частина рядка
        for (int c = r + 1; c < N; c++)
            s -= a[r][c] * x[c];                  // відняти вже відомі змінні
        x[r] = s / a[r][r];                       // поділити на півот
    }
    return true;
}
