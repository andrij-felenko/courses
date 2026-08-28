from datetime import datetime
from dateutil.rrule import rrulestr

# dtstart передають окремим аргументом
rule = rrulestr(
    "RRULE:FREQ=MONTHLY;BYMONTHDAY=15,30;COUNT=5",
    dtstart=datetime(2026, 1, 15, 9, 0),
)

list(rule)                         # усі п'ять митей
rule.after(datetime.now(), inc=True)  # найближча після «зараз»
rule.between(frm, to)              # усе у вікні
rule.count()                       # скільки всього (скінченне правило)
