# Таблиці CLDR у стандартній бібліотеці немає — її дає Babel.
from decimal import Decimal
from babel import Locale
from babel.numbers import format_decimal

uk = Locale.parse("uk")

[f"{n}→{uk.plural_form(n)}" for n in (1, 2, 5, 11, 21, Decimal("1.5"))]
# ['1→one', '2→few', '5→many', '11→many', '21→one', '1.5→other']

format_decimal(1234.5, locale="uk")   # '1 234,5'
format_decimal(1234.5, locale="en")   # '1,234.5'
