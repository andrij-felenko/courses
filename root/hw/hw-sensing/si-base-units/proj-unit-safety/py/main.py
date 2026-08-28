import pint
u = pint.UnitRegistry()

def apply_impulse(j):
    j_ns = j.to("newton * second")   # вимагаємо саме Н·с — або виняток
    # ... коригуємо траєкторію, маючи j_ns у Н·с ...
    return j_ns

apply_impulse(1.85 * u("pound_force * second"))  # ✓ pint сам переведе → 8.23 Н·с
apply_impulse(1.85 * u.metre)                    # ✗ pint.DimensionalityError,
#   Cannot convert from 'meter' ([length]) to 'newton*second' ([mass]·[length]/[time])
