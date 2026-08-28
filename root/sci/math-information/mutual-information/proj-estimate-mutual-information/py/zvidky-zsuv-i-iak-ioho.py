def entropy_bits(counts):
    """Наївна плаг-ін ентропія масиву лічильників, біт."""
    N = counts.sum()
    p = counts[counts > 0] / N
    return -(p * np.log2(p)).sum()

def mi_miller_madow(joint):
    """I(X;Y) з поправкою Міллера–Мадоу на кожну з трьох ентропій."""
    N = joint.sum()
    def H_mm(counts):
        m_plus = np.count_nonzero(counts)          # заповнені клітини
        return entropy_bits(counts) + (m_plus - 1) / (2 * N * np.log(2))
    return H_mm(joint.sum(axis=1)) + H_mm(joint.sum(axis=0)) - H_mm(joint)
