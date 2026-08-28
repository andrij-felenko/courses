# зростаюча таблиця калібрування (код АЦП → °C)
code_lut = [  410, 1230, 2050, 2870, 3686 ]
temp_lut = [ 0.0, 25.0, 50.0, 75.0, 100.0 ]

def temp_from_code(code):
    if code <= code_lut[0]:     return temp_lut[0]
    if code >= code_lut[-1]:    return temp_lut[-1]
    i = 0
    while code > code_lut[i+1]:  i += 1          # знайти інтервал
    frac = (code - code_lut[i]) \
         / (code_lut[i+1] - code_lut[i])         # частка всередині
    return temp_lut[i] + frac * (temp_lut[i+1] - temp_lut[i])
