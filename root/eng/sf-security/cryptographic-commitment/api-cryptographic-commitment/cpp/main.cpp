namespace crypto::kzg {

struct Polynomial {
    std::vector<Scalar> coefficients; // f(X) = a0 + a1*X + ... + ad*X^d
};

struct KZGCommitment {
    G1Point point; // C = [f(tau)]1
};

struct KZGProof {
    G1Point proof_point; // pi = [q(tau)]1
};

class KZGScheme {
public:
    // Завантаження Structured Reference String (SRS) з файлу Trusted Setup
    static KZGScheme load_srs(const std::string& srs_file_path, size_t max_degree);

    // Створення зобов'язання C для полінома f(X)
    KZGCommitment commit(const Polynomial& poly) const;

    // Створення доказу оцінки в точці z: f(z) = y
    KZGProof open_eval(const Polynomial& poly, const Scalar& z, const Scalar& y) const;

    // Верифікація доказу через білінійне спарювання e(C - [y]1, [1]2) == e(pi, [tau - z]2)
    bool verify_eval(const KZGCommitment& commitment, 
                     const Scalar& z, 
                     const Scalar& y, 
                     const KZGProof& proof) const;
};

} // namespace crypto::kzg
