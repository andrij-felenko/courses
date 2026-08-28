# Перехоплювач: поки що прозорий — усі шляхи ведуть у старий моноліт.
import re

def legacy(req):            # старий застосунок
    return call_monolith(req)

routes = []                 # порожньо: жодну можливість ще не перенесено

def intercept(req):
    path = req.path
    for pattern, handler in routes:
        if pattern.match(path):     # є новий маршрут — туди
            return handler(req)
    return legacy(req)              # немає — у старе, як завжди
