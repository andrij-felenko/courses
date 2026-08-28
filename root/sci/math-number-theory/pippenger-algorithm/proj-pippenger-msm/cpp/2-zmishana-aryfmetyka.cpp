namespace msm {

/* Додавання афінної точки до точки в координатах Якобі: res = p_jac + p_aff */
PointJacobian add_mixed(const PointJacobian& p_jac, const PointAffine& p_aff) noexcept {
    if (p_aff.is_infinity) {
        return p_jac;
    }
    if (p_jac.is_infinity()) {
        return PointJacobian{p_aff.x, p_aff.y, FieldElement{{1, 0, 0, 0}}};
    }

    FieldElement Z1Z1 = sqr(p_jac.Z);
    FieldElement U2 = mul(p_aff.x, Z1Z1);
    FieldElement S2 = mul(mul(p_aff.y, p_jac.Z), Z1Z1);

    FieldElement H = sub(U2, p_jac.X);
    FieldElement r = sub(S2, p_jac.Y);

    if (H.is_zero()) {
        if (r.is_zero()) {
            return double_point(p_jac);
        }
        return PointJacobian::infinity();
    }

    FieldElement HH = sqr(H);
    FieldElement I = add(HH, HH);
    I = add(I, I);
    FieldElement J = mul(H, I);
    FieldElement V = mul(p_jac.X, I);

    PointJacobian res;
    res.X = sub(sub(sqr(r), J), add(V, V));
    res.Y = sub(mul(r, sub(V, res.X)), mul(mul(p_jac.Y, J), FieldElement{{2, 0, 0, 0}}));

    FieldElement Z1plusH = add(p_jac.Z, H);
    res.Z = sub(sub(sqr(Z1plusH), Z1Z1), HH);
    return res;
}

/* Додавання двох точок Якобі */
PointJacobian add_jacobian(const PointJacobian& p1, const PointJacobian& p2) noexcept {
    if (p1.is_infinity()) return p2;
    if (p2.is_infinity()) return p1;

    FieldElement Z1Z1 = sqr(p1.Z);
    FieldElement Z2Z2 = sqr(p2.Z);

    FieldElement U1 = mul(p1.X, Z2Z2);
    FieldElement U2 = mul(p2.X, Z1Z1);

    FieldElement S1 = mul(mul(p1.Y, p2.Z), Z2Z2);
    FieldElement S2 = mul(mul(p2.Y, p1.Z), Z1Z1);

    FieldElement H = sub(U2, U1);
    FieldElement r = sub(S2, S1);

    if (H.is_zero()) {
        if (r.is_zero()) return double_point(p1);
        return PointJacobian::infinity();
    }

    FieldElement I = sqr(add(H, H));
    FieldElement J = mul(H, I);
    FieldElement V = mul(U1, I);

    PointJacobian res;
    res.X = sub(sub(sqr(r), J), add(V, V));
    res.Y = sub(mul(r, sub(V, res.X)), mul(mul(S1, J), FieldElement{{2, 0, 0, 0}}));

    FieldElement Z1plusZ2 = add(p1.Z, p2.Z);
    res.Z = mul(sub(sub(sqr(Z1plusZ2), Z1Z1), Z2Z2), H);
    return res;
}

} // namespace msm
