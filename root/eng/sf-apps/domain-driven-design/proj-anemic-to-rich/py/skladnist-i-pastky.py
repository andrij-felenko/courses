# ПАСТКА: геттер віддає САМ список — і вся охорона add_payment знецінена
@property
def payments(self):
    return self._payments            # ← НЕ роби так
# зовні: policy.payments.append(-999)  ← клали що завгодно повз перевірку

# ЯК ТРЕБА: назовні тече лише незмінний знімок
@property
def payments(self):
    return tuple(self._payments)
