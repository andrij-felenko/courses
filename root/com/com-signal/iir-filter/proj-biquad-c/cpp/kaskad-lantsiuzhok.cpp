#include <vector>

struct BiquadChain {
    std::vector<Biquad> stage;   // масив ланок

    float step(float x) {
        float v = x;
        for (auto &s : stage)
            v = s.step(v);       // вихід однієї → вхід наступної
        return v;
    }
};
