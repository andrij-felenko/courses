def civil_from_days(n: int) -> tuple[int, int, int]:
    n += 719468
    era = n // 146097
    doe = n - era * 146097                                      # [0, 146096]
    yoe = (doe - doe//1460 + doe//36524 - doe//146096) // 365    # [0, 399]
    y   = yoe + era * 400
    doy = doe - (365*yoe + yoe//4 - yoe//100)                   # [0, 365]
    k   = (5*doy + 2) // 153                                    # [0, 11]
    d   = doy - (153*k + 2)//5 + 1                              # [1, 31]
    m   = k + 3 if k < 10 else k - 9
    return (y + (m <= 2), m, d)
