// tests/unit/test_calculator.cpp
#include <gtest/gtest.h>
#include "calculator.hpp"

class CalculatorTest : public ::testing::Test {
protected:
    engine::Calculator calc;
};

TEST_F(CalculatorTest, HandlesValidDivision) {
    auto res = calc.divide(10.0, 2.0);
    ASSERT_TRUE(res.has_value());
    EXPECT_DOUBLE_EQ(*res, 5.0);
}

TEST_F(CalculatorTest, RejectsDivisionByZero) {
    auto res = calc.divide(5.0, 0.0);
    ASSERT_FALSE(res.has_value());
    EXPECT_EQ(res.error(), engine::MathError::DivisionByZero);
}
