def xor(*bits):                 # додавання за модулем 2
    r = 0
    for b in bits: r ^= b
    return r

for a in (0, 1):
    for b in (0, 1):
        left  = a | b                        # звичайне «або»
        right = xor(a, b, a & b)             # a ⊕ b ⊕ a·b
        assert left == right, (a, b)
print("a ∨ b = a ⊕ b ⊕ a·b — збігається на всіх входах")
