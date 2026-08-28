#define WGS84_A  6378137.0
#define WGS84_F  (1.0/298.257223563)
#define WGS84_E2 (WGS84_F*(2.0 - WGS84_F))

static void ned_to_geodetic(double lat0, double lon0, double h,
                            double dN, double dE, double *lat, double *lon)
{
    double s = sin(lat0), W = sqrt(1.0 - WGS84_E2*s*s);
    double M = WGS84_A*(1.0 - WGS84_E2)/(W*W*W);   /* радіус кривини меридіана */
    double N = WGS84_A/W;                          /* радіус першого вертикала */
    *lat = lat0 + dN/(M + h);
    *lon = lon0 + dE/((N + h)*cos(lat0));
}
