def rot2(theta):
    """Матриця повороту на кут θ (радіани). Крутить ВЕКТОР на +θ;
       щоб повернути ОСІ на +α, клич із −α."""
    c, s = math.cos(theta), math.sin(theta)
    return ((c, -s),
            (s,  c))

def apply(M, v):
    """Множення матриці на вектор: (M · v)."""
    return tuple(sum(M[i][j] * v[j] for j in range(len(v))) for i in range(len(M)))
