from math import sqrt

# Діючий струм вхідного конденсатора buck-перетворювача.
# I — вихідний струм навантаження, A;  D — шпаруватість (0..1).
def cin_rms(I, D):
    return I * sqrt(D * (1.0 - D))          # I·√(D(1−D))

# Діючий струм верхнього ключа (прямокутник зі шпаруватістю D).
def highside_rms(I, D):
    return I * sqrt(D)                      # I·√D
