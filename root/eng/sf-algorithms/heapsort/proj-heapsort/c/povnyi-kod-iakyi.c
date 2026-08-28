#include <stdio.h>

/* ... сюди sift_down і heapsort з попередніх блоків ... */

int main(void) {
    int a[] = {9, 7, 8, 3, 6, 2};
    int n = sizeof a / sizeof a[0];

    heapsort(a, n);

    for (int i = 0; i < n; i++)
        printf("%d ", a[i]);        /* друкує: 2 3 6 7 8 9 */
    putchar('\n');
    return 0;
}
