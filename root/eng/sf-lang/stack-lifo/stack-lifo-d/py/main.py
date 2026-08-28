def g(a, b):
    total = a + b           # 'total' — локальна: живе в кадрі g
    return total            # повернення: pop кадру g, адреса → PC

def f(x):
    bias = 100              # 'bias' — локальна: живе в кадрі f
    return g(x, bias)       # виклик g: push кадру g поверх кадру f

def main():
    r = f(7)                # виклик f: push кадру f поверх кадру main
    return r                # r == 107

if __name__ == "__main__":
    main()
