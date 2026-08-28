# Три булеві осі → один із семи класів вагомості (за Мітчеллом–Ейглом–Вудом).
SALIENCE = {
    (True,  False, False): "сплячий",      # лише влада — сила є, та дрімає
    (False, True,  False): "на-розсуд",    # лише легітимність — право без сили й поспіху
    (False, False, True):  "вимогливий",   # лише терміновість — галас без важеля й права
    (True,  True,  False): "панівний",     # влада + легітимність — чути завжди
    (True,  False, True):  "небезпечний",  # влада + терміновість — примус без права
    (False, True,  True):  "залежний",     # право + поспіх, та безсилий
    (True,  True,  True):  "визначальний", # усі три — кидай усе
}

def salience_class(s: Stakeholder) -> str:
    return SALIENCE.get((s.power, s.legitimacy, s.urgency), "не стейкхолдер")

# Груба міра ваги: латентний = 1 вісь, очікувальний = 2, визначальний = 3.
def salience_score(s: Stakeholder) -> int:
    return s.power + s.legitimacy + s.urgency  # bool сумується як 0/1

HIGH_SALIENCE = 2  # від двох осей — уже «високовагомий»

# Квадрант сітки «влада–інтерес»: не «наскільки важливий», а скільки й якого роду уваги.
def quadrant(s: Stakeholder) -> str:
    if s.power:
        return "вести щільно" if s.interest else "тримати вдоволеним"
    return "тримати в курсі" if s.interest else "спостерігати"
