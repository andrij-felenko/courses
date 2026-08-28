TEST(PhysicsVectorTest, InvarianceUnderImproperRotation) {
    PhysicsVector v{3.2, -1.5, 4.8, VectorKind::Polar};
    PhysicsVector B{-0.5, 2.1, 1.1, VectorKind::Axial};
    PhysicsVector F = v.cross(B);

    Matrix3x3 reflectionMatrix = Matrix3x3::inversion();
    PhysicsVector v_trans = v.transform(reflectionMatrix);
    PhysicsVector B_trans = B.transform(reflectionMatrix);
    PhysicsVector F_trans = F.transform(reflectionMatrix);
    PhysicsVector F_recalc = v_trans.cross(B_trans);

    EXPECT_NEAR(F_trans.x, F_recalc.x, 1e-9);
    EXPECT_NEAR(F_trans.y, F_recalc.y, 1e-9);
    EXPECT_NEAR(F_trans.z, F_recalc.z, 1e-9);
}
