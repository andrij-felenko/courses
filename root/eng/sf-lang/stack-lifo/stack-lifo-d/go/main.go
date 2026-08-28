func g(a, b int) int {
    sum := a + b            // 'sum' — локальна: живе в кадрі g
    return sum              // повернення: pop кадру g, адреса → PC
}

func f(x int) int {
    bias := 100             // 'bias' — локальна: живе в кадрі f
    return g(x, bias)       // виклик g: push кадру g поверх кадру f
}

func main() {
    r := f(7)               // виклик f: push кадру f поверх кадру main
    _ = r                   // r == 107
}
