#include <stdio.h>
#include "interval_tree.h"

int main(void) {
    IntervalNode* tree = NULL;
    tree = interval_insert(tree, create_interval(15.0, 20.0));
    tree = interval_insert(tree, create_interval(10.0, 30.0));
    
    Interval query = {21.0, 25.0};
    IntervalNode* result = interval_search(tree, query);
    if (result != NULL) {
        printf("Знайдено перетин: [%g, %g]\n", result->interval.low, result->interval.high);
    }
    
    free_interval_tree(tree);
    return 0;
}
