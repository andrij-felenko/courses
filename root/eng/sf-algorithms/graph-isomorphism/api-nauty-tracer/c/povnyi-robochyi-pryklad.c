#include <stdio.h>
#include <stdlib.h>
#include "nauty.h"

int main(void) {
    int n = 5;
    int m = SETWORDSNEEDED(n);

    nauty_check(WORDSIZE, m, n, NAUTYVERSION);

    graph *g = (graph*)malloc(m * n * sizeof(graph));
    graph *cg = (graph*)malloc(m * n * sizeof(graph));
    int *lab = (int*)malloc(n * sizeof(int));
    int *ptn = (int*)malloc(n * sizeof(int));
    int *orbits = (int*)malloc(n * sizeof(int));

    optionblk options;
    statsblk stats;
    DEFAULTOPTIONS_GRAPH(&options);
    options.getcanon = TRUE;

    EMPTYGRAPH(g, m, n);
    ADDONEEDGE(g, 0, 1, m);
    ADDONEEDGE(g, 1, 2, m);
    ADDONEEDGE(g, 2, 3, m);
    ADDONEEDGE(g, 3, 4, m);
    ADDONEEDGE(g, 4, 0, m);

    #define WORKSIZE (16 * SETWORDSNEEDED(5))
    set workspace[WORKSIZE];

    nauty(g, lab, ptn, NULL, orbits, &options, &stats, workspace, WORKSIZE, m, n, cg);

    printf("Порядок групи автоморфізмів Aut(G): %.0f\n", stats.grpsize1);
    printf("Кількість орбіт вершин: %d\n", stats.numorbits);
    printf("Канонічне маркування вершин (lab):\n");
    for (int i = 0; i < n; i++) {
        printf("  v[%d] -> canonical[%d]\n", i, lab[i]);
    }

    free(g);
    free(cg);
    free(lab);
    free(ptn);
    free(orbits);
    return 0;
}
