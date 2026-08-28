/* c */
typedef struct {
    double dX;    /* Зміна X [нТл/рік] */
    double dY;    /* Зміна Y [нТл/рік] */
    double dZ;    /* Зміна Z [нТл/рік] */
    double dH;    /* Зміна H [нТл/рік] */
    double dF;    /* Зміна F [нТл/рік] */
    double dI;    /* Зміна кута нахилу [мінути/рік] */
    double dD;    /* Зміна кута схилення [мінути/рік] */
} wmm_secular_variation_t;
