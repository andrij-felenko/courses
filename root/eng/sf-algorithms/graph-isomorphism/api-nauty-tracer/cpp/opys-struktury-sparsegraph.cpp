// C++ RAII обгортка для структури sparsegraph:
class SparseGraphWrapper {
public:
    sparsegraph sg;

    SparseGraphWrapper() {
        SG_INIT(sg);
    }

    ~SparseGraphWrapper() {
        SG_FREE(sg);
    }

    SparseGraphWrapper(const SparseGraphWrapper&) = delete;
    SparseGraphWrapper& operator=(const SparseGraphWrapper&) = delete;
};
