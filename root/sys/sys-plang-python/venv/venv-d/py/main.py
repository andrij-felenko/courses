import sys
import site

print(f"sys.prefix:      {sys.prefix}")
print(f"sys.base_prefix: {sys.base_prefix}")
print("\nКаталоги пошуку sys.path:")
for idx, path in enumerate(sys.path):
    print(f"  [{idx}] {path}")

print("\nЗареєстровані каталоги site-packages:")
for sp in site.getsitepackages():
    print(f"  • {sp}")
