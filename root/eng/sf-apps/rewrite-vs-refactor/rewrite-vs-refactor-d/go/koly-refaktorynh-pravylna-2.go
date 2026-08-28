// Крок рефакторингу: та сама поведінка, зрозуміліша будова.
// Магічні числа стали іменами, гілки — окремими функціями.
const (
    VipThreshold = 1000.0
    VipRate      = 0.15
)

func ComputeDiscount(cart Cart, vip bool) float64 {
    subtotal := cart.Subtotal()
    if vip && subtotal >= VipThreshold {
        return subtotal * VipRate            // 1200 · 0.15 = 180 — тест досі зелений
    }
    return regularDiscount(subtotal)
}
