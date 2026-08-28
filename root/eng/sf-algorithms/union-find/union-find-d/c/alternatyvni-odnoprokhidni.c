#include <stdio.h>
#include <stdlib.h>

// Пошук з ітеративним уполовиненням шляху (Path Halving) на C
int find_path_halving(int *parent, int x) {
    while (parent[x] != x) {
        parent[x] = parent[parent[x]];
        x = parent[x];
    }
    return x;
}

// Пошук з розщепленням шляху (Path Splitting) на C
int find_path_splitting(int *parent, int x) {
    while (parent[x] != x) {
        int next = parent[x];
        parent[x] = parent[next];
        x = next;
    }
    return x;
}
