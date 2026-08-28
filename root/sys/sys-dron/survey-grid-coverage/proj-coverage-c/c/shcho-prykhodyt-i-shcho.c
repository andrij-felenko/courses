#include <math.h>
#include <stdio.h>

/* Точка в місцевій пласкій системі, метри. */
typedef struct { double x, y; } Pt;

/* Один галс у системі галсів: горизонтальний відрізок [x0, x1] на висоті y. */
typedef struct { double y, x0, x1; int cell; } Seg;

#define MAX_V    256    /* вершин полігона                                  */
#define MAX_CUT   64    /* перетинів однієї січної з контуром               */
#define MAX_SEG  512    /* галсів у плані                                   */
#define EPS     1e-9    /* «нуль» у частках смуги, не в метрах              */
#define Y_TOL   1e-6    /* ближче за мікрон до вершини — вважаємо «в неї»   */
#define Y_STEP  1e-5    /* на стільки зсуваємо січну, щоб зійти з вершини   */
