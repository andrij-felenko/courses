// Характеризаційний тест: фіксуємо поведінку ЯК Є, перед рефакторингом.
// Ми не питаємо «чи правильно 15%» — ми фіксуємо, що ЗАРАЗ саме 15%,
// щоб рефакторинг випадково цього не зрушив.
func TestLegacyDiscountVipOverThreshold(t *testing.T) {
    cart := Cart{}
    cart.Add(Item{Price: 100.0, Qty: 12})    // сума 1200, поріг VIP
    got := ComputeDiscount(cart, true /*vip*/)
    if math.Abs(got-180.0) > 1e-9 {          // ← спостережена нинішня величина
        t.Errorf("got %v, want 180.0", got)
    }
}
