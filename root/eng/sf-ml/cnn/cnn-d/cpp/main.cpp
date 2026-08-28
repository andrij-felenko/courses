// «Дійсна» згортка одного каналу: ядро K×K ковзає входом H×W,
// на кожній позиції — скалярний добуток вікна на ядро → одне число мапи.
#include <vector>
using Mat = std::vector<std::vector<float>>;

Mat conv2d_valid(const Mat& in, const Mat& kernel) {
    int H = in.size(),  W = in[0].size();
    int K = kernel.size();
    int outH = H - K + 1, outW = W - K + 1;      // формула розміру, P=0, S=1
    Mat out(outH, std::vector<float>(outW, 0.0f));

    for (int y = 0; y < outH; ++y)               // по всіх позиціях мапи
        for (int x = 0; x < outW; ++x) {
            float acc = 0.0f;
            for (int ky = 0; ky < K; ++ky)       // згортка вікна з ядром
                for (int kx = 0; kx < K; ++kx)
                    acc += in[y + ky][x + kx] * kernel[ky][kx];
            out[y][x] = acc;                     // відгук ядра в цій точці
        }
    return out;
}
