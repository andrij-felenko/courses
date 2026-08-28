#include <stdint.h>
#include <stdio.h>

/* Проміжний тензор: розмір і замкнутий проміжок життя [birth, death]
   у кроках графа (крок = індекс операції). */
typedef struct {
    uint32_t size;    /* байтів                           */
    int32_t  birth;   /* крок, де тензор порахували        */
    int32_t  death;   /* останній крок, де його читають    */
} Tensor;

#define MAX_T 64      /* стеля моделі — жодних malloc, усе статичне */

/* Перетин проміжків життя: якщо є бодай одна спільна мить —
   тензори не можна класти на ті самі байти. */
static int overlap(Tensor a, Tensor b) {
    return a.birth <= b.death && b.birth <= a.death;
}

/* Округлити офсет угору до межі align (align — степінь двійки). */
static uint32_t align_up(uint32_t x, uint32_t align) {
    return (x + align - 1u) & ~(align - 1u);
}

/* Жадібний first-fit. Тензори кладуть у порядку народження order[].
   Заповнює offset[] для кожного тензора; повертає розмір арени. */
uint32_t plan_arena(const Tensor t[], int n, const int order[],
                    uint32_t offset[], uint32_t align)
{
    uint32_t arena = 0;
    int placed[MAX_T], np = 0;

    for (int k = 0; k < n; ++k) {
        int i = order[k];

        /* 1. зібрати зайняті діапазони [lo,hi) конфліктних сусідів */
        uint32_t lo[MAX_T], hi[MAX_T];
        int m = 0;
        for (int p = 0; p < np; ++p) {
            int j = placed[p];
            if (overlap(t[i], t[j])) {
                lo[m] = offset[j];
                hi[m] = offset[j] + t[j].size;
                ++m;
            }
        }

        /* 2. упорядкувати зайняті блоки за початком (вставками — m мале) */
        for (int a = 1; a < m; ++a) {
            uint32_t L = lo[a], H = hi[a];
            int b = a - 1;
            while (b >= 0 && lo[b] > L) { lo[b+1] = lo[b]; hi[b+1] = hi[b]; --b; }
            lo[b+1] = L; hi[b+1] = H;
        }

        /* 3. знизу вгору шукаємо першу щілину, у яку влазить t[i] */
        uint32_t off = 0;
        for (int a = 0; a < m; ++a) {
            off = align_up(off, align);
            if (off + t[i].size <= lo[a]) break;   /* щілина перед блоком a досить широка */
            if (hi[a] > off) off = hi[a];          /* ні — стрибаємо за кінець блоку a    */
        }
        off = align_up(off, align);

        offset[i] = off;
        placed[np++] = i;
        if (off + t[i].size > arena) arena = off + t[i].size;
    }
    return arena;
}

int main(void) {
    /* приклад із пропущеним зв'язком x0→op4 (t4 = склейка x0 і t3) */
    Tensor t[] = {
        /* x0 */ { 4000, 0, 4 },
        /* t1 */ { 8000, 1, 2 },
        /* t2 */ { 2000, 2, 3 },
        /* t3 */ {  500, 3, 4 },
        /* t4 */ { 4500, 4, 4 },
    };
    const char *name[] = { "x0", "t1", "t2", "t3", "t4" };
    int n = 5;
    int order[] = { 0, 1, 2, 3, 4 };          /* уже в порядку народження */
    uint32_t offset[5];

    uint32_t arena = plan_arena(t, n, order, offset, 1 /* без вирівнювання */);

    for (int i = 0; i < n; ++i)
        printf("%s: офсет %5u  [%u, %u)\n",
               name[i], offset[i], offset[i], offset[i] + t[i].size);
    printf("арена = %u байтів\n", arena);
    return 0;
}
