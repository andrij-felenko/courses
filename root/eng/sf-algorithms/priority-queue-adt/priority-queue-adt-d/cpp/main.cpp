#include <vector>
#include <utility>   // std::swap

void sift_up(std::vector<int>& h, int i) {
    while (i > 0) {
        int parent = (i - 1) / 2;
        if (h[i] >= h[parent]) break;
        std::swap(h[i], h[parent]);
        i = parent;
    }
}

void sift_down(std::vector<int>& h, int i) {
    int n = (int)h.size();
    for (;;) {
        int smallest = i, l = 2 * i + 1, r = 2 * i + 2;
        if (l < n && h[l] < h[smallest]) smallest = l;
        if (r < n && h[r] < h[smallest]) smallest = r;
        if (smallest == i) break;
        std::swap(h[i], h[smallest]);
        i = smallest;
    }
}

void push(std::vector<int>& h, int x) {
    h.push_back(x);
    sift_up(h, (int)h.size() - 1);
}

int pop_min(std::vector<int>& h) {
    int top = h[0];
    h[0] = h.back();
    h.pop_back();
    if (!h.empty()) sift_down(h, 0);
    return top;
}
