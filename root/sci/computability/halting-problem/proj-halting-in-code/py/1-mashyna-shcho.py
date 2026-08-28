import inspect

def make_paradox(guess):
    def paradox():
        src = inspect.getsource(paradox)   # програма читає власний текст
        if guess(src, src):                # суддя: чи спиниться paradox на собі?
            while True:                    # каже «спиниться» -> крутимось вічно
                pass
        else:
            return "спинилась"             # каже «не спиниться» -> стоп негайно
    return paradox

def always_halts(src, arg):  return True
def always_loops(src, arg):  return False
def guess_by_text(src, arg): return "while True" not in src   # наївна статична евристика

def defeat(name, guess):
    src = inspect.getsource(make_paradox(guess))   # текст paradox — той самий для всіх суддів
    verdict   = guess(src, src)                    # пророцтво про paradox(paradox)
    predicted = "halts" if verdict else "loops"
    actual    = "loops" if verdict else "halts"    # береться протилежна гілка
    print("%-13s пророчить: %-5s | paradox робить: %-5s | суддя збрехав: %s"
          % (name, predicted, actual, "так" if predicted != actual else "ні"))

for name, g in [("always_halts", always_halts),
                ("always_loops", always_loops),
                ("guess_by_text", guess_by_text)]:
    defeat(name, g)
