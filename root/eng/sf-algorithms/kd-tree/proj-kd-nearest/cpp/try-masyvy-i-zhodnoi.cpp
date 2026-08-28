#include <algorithm>
#include <cmath>
#include <numeric>
#include <queue>
#include <vector>

constexpr int D = 3;                 // вимірність відома під час компіляції

struct Point { float c[D]; };

struct Node {
    float split;       // значення розрізу
    int   axis;        // вісь розрізу; −1 → листок
    int   right;       // правий нащадок; лівий — завжди наступний вузол
    int   begin, end;  // відрізок idx_, яким володіє це піддерево
};
