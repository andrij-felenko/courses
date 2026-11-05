#ifndef IEC60751_H
#define IEC60751_H

#include <stddef.h>

typedef struct {
    double r0;
} IEC60751;

typedef struct {
    double t_min;
    double step;
    size_t size;
    double* resistances;
    double* temperatures;
} LookupTable;

void iec60751_init(IEC60751* sensor, double r0);
double iec60751_temp_to_res(const IEC60751* sensor, double t);
double iec60751_res_to_temp(const IEC60751* sensor, double r);

void lut_init(LookupTable* lut, const IEC60751* sensor, double t_min, double t_max, double step);
void lut_free(LookupTable* lut);
double lut_lookup_temp(const LookupTable* lut, double r);

#endif // IEC60751_H
