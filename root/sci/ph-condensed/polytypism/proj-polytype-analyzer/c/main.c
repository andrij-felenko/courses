#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <stdbool.h>

#define PI 3.14159265358979323846
#define MAX_STACKING_LAYERS 128

typedef struct {
    char name[16];
    int zhdanov_n1;
    int zhdanov_n2;
    char sequence[MAX_STACKING_LAYERS];
    char jagodzinski[MAX_STACKING_LAYERS];
    int period;
    double hexagonality;
} PolytypeInfoC99;

bool expand_zhdanov_c99(int n1, int n2, const char *name, PolytypeInfoC99 *info) {
    if (!info || n1 < 0 || n2 < 0 || (n1 + n2) >= MAX_STACKING_LAYERS) {
        return false;
    }
    
    strncpy(info->name, name, sizeof(info->name) - 1);
    info->name[sizeof(info->name) - 1] = '\0';
    info->zhdanov_n1 = n1;
    info->zhdanov_n2 = n2;
    
    int curr = 0;
    int idx = 0;
    info->sequence[idx++] = 'A';
    
    for (int i = 0; i < n1; i++) {
        curr = (curr + 1) % 3;
        info->sequence[idx++] = (curr == 0) ? 'A' : ((curr == 1) ? 'B' : 'C');
    }
    for (int i = 0; i < n2; i++) {
        curr = (curr + 2) % 3;
        info->sequence[idx++] = (curr == 0) ? 'A' : ((curr == 1) ? 'B' : 'C');
    }
    
    info->period = idx - 1;
    info->sequence[info->period] = '\0';
    
    int h_count = 0;
    for (int i = 0; i < info->period; i++) {
        int prev_idx = (i - 1 + info->period) % info->period;
        int next_idx = (i + 1) % info->period;
        char prev = info->sequence[prev_idx];
        char next = info->sequence[next_idx];
        
        if (prev == next) {
            info->jagodzinski[i] = 'h';
            h_count++;
        } else {
            info->jagodzinski[i] = 'k';
        }
    }
    info->jagodzinski[info->period] = '\0';
    info->hexagonality = ((double)h_count / info->period) * 100.0;
    
    return true;
}

double compute_intensity_10L_c99(const PolytypeInfoC99 *info, double l_val) {
    if (!info || info->period <= 0) return 0.0;
    
    double real_sum = 0.0;
    double imag_sum = 0.0;
    
    for (int j = 0; j < info->period; j++) {
        double xj = 0.0;
        if (info->sequence[j] == 'B') {
            xj = 2.0 / 3.0;
        } else if (info->sequence[j] == 'C') {
            xj = 1.0 / 3.0;
        }
        
        double phase = 2.0 * PI * (xj + l_val * ((double)j / info->period));
        real_sum += cos(phase);
        imag_sum += sin(phase);
    }
    
    return (real_sum * real_sum + imag_sum * imag_sum);
}

int main(void) {
    PolytypeInfoC99 poly_3c, poly_4h, poly_6h, poly_15r;
    
    expand_zhdanov_c99(3, 0, "3C-SiC", &poly_3c);
    expand_zhdanov_c99(2, 2, "4H-SiC", &poly_4h);
    expand_zhdanov_c99(3, 3, "6H-SiC", &poly_6h);
    expand_zhdanov_c99(3, 2, "15R-SiC", &poly_15r);
    
    PolytypeInfoC99 *list[] = { &poly_3c, &poly_4h, &poly_6h, &poly_15r };
    
    printf("%-10s | %-8s | %-12s | %-16s | %-8s\n", 
           "Політип", "Період N", "Послідовність", "Ягодзінський", "α_h (%)");
    printf("-------------------------------------------------------------------\n");
    
    for (int i = 0; i < 4; i++) {
        printf("%-10s | %-8d | %-12s | %-16s | %-8.1f%%\n",
               list[i]->name, list[i]->period, list[i]->sequence,
               list[i]->jagodzinski, list[i]->hexagonality);
    }
    
    printf("\nДифракційні піки 4H-SiC (10L стержень):\n");
    for (double l = 0.0; l <= 2.0 + 1e-5; l += 0.25) {
        double intensity = compute_intensity_10L_c99(&poly_4h, l);
        printf("L = %4.2f | I(10L) = %6.3f\n", l, intensity);
    }
    
    return 0;
}
