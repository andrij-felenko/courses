#include <math.h>
#include <string.h>

#define S        13          // сітка S×S
#define B        3           // якорів на клітинку
#define C        20          // класів
#define STRIDE   32          // крок сітки: вхід 416 / S(13) = 32
#define K        (B*5 + C)   // глибина на клітинку = 35
#define MAX_DET  256         // стеля рамок після фільтра

typedef struct {
    float x1, y1, x2, y2;    // рамка у пікселях (кути)
    float score;             // підсумкова оцінка = objectness · max(class)
    int   cls;               // індекс класу
} det_t;

// форми якорів у пікселях (ширина, висота) — підібрані під дані, не випадкові
static const float ANCHOR_W[B] = { 116.0f, 30.0f, 60.0f };
static const float ANCHOR_H[B] = {  90.0f, 61.0f, 45.0f };

static float sigmoidf(float x) { return 1.0f / (1.0f + expf(-x)); }
