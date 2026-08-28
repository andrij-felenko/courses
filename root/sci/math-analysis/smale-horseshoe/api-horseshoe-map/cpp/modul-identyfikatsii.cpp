namespace physics::mechanics {

struct TransitionMatrix {
    size_t states_count{2};
    std::vector<std::vector<int>> matrix;
};

class MarkovAnalyzer {
public:
    static TransitionMatrix computeTransitionMatrix(const Config& cfg) noexcept {
        return TransitionMatrix{
            .states_count = 2,
            .matrix = {{1, 1}, {1, 1}}
        };
    }
};

}
