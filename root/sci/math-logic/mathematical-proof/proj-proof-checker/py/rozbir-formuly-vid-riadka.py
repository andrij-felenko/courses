from itertools import product

OPS = {'¬': 'not', '~': 'not', '!': 'not',
       '∧': 'and', '&': 'and',
       '∨': 'or',  '|': 'or',
       '⟹': 'imp', '→': 'imp'}          # приймаємо і ⟹, і →

def tokenize(s):
    toks, i = [], 0
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
        elif s.startswith('->', i) or s.startswith('=>', i):
            toks.append('imp'); i += 2
        elif c in '()':
            toks.append(c); i += 1
        elif c in OPS:
            toks.append(OPS[c]); i += 1
        elif c.isalpha():                  # назва змінної: p, q, rain, …
            j = i
            while j < len(s) and s[j].isalnum():
                j += 1
            toks.append(('var', s[i:j])); i = j
        else:
            raise SyntaxError('невідомий символ %r у позиції %d' % (c, i))
    return toks
