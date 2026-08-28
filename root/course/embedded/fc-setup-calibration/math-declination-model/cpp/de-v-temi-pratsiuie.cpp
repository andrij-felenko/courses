// Ідея AP_Declination: за координатами GNSS дістати схилення з таблиці у flash.
// Таблиця SAMPLE_DEC[lat][lon] заздалегідь порахована з моделі поля Землі
// на сітці з кроком у кілька градусів; проміжне — білінійна інтерполяція.

float get_declination_deg(float lat_deg, float lon_deg)
{
    // 1) знайти клітину сітки, у яку впала точка
    float flat = (lat_deg - SAMPLE_LAT_MIN) / SAMPLE_STEP;   // дробовий індекс за широтою
    float flon = (lon_deg - SAMPLE_LON_MIN) / SAMPLE_STEP;   // …за довготою
    int   ilat = (int)flat,  ilon = (int)flon;
    float tlat = flat - ilat, tlon = flon - ilon;            // частки всередині клітини [0..1]

    // 2) чотири кутові вузли клітини (значення з таблиці у flash)
    float d00 = table_lookup(ilat,     ilon);
    float d10 = table_lookup(ilat + 1, ilon);
    float d01 = table_lookup(ilat,     ilon + 1);
    float d11 = table_lookup(ilat + 1, ilon + 1);

    // 3) білінійна інтерполяція: спершу за довготою, тоді за широтою
    float d0 = d00 + (d01 - d00) * tlon;    // нижній край клітини
    float d1 = d10 + (d11 - d10) * tlon;    // верхній край
    return  d0 + (d1 - d0) * tlat;          // схилення в точці, градуси
}
