/* C API для Угорського алгоритму зваженого паросполучення */
typedef struct {
    int u;
    int v;
    double weight;
} CWeightedEdge;

typedef struct {
    double total_weight;
    int count;
    CWeightedEdge* edges;
} CWeightedMatchingSolution;

CWeightedMatchingSolution* hungarian_solve_max(const double* weight_matrix, int n, int m);
void hungarian_solution_free(CWeightedMatchingSolution* sol);
