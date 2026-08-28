/* Головна функція розрахунку МКД */
MstStatusCode mst_solve(
    const MstGraph *graph,
    MstAlgorithmType algo,
    MstSolution *out_solution
);

/* Звільнення динамічного буфера ребер у структурі розв'язку */
void mst_solution_free(MstSolution *solution);

/* Незалежна верифікація ациклічності та зв'язності результату */
bool mst_verify_solution(size_t num_vertices, const MstSolution *solution);
