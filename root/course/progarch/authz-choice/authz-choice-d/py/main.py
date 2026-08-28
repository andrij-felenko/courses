# Гібридний авторизатор: політика — з центру, ОЦІНКА — локальна, дані — за місцем
class HybridAuthorizer:
    def __init__(self, policy, rels):
        self.policy = policy   # роздано з ЦЕНТРУ (підписаний бандл), оновлюється фоном
        self.rels = rels       # кеш наскрізних зв'язків над центральним сховищем

    def can(self, user, action, resource) -> bool:
        # наскрізний факт — з кеша над центром (мережа лише на промах, і то рідко)
        is_member = self.rels.is_member_of(user.id, resource.home_id)
        # локальний факт — тут-таки, поруч
        role = user.role_in_home.get(resource.home_id)

        # ВЕРДИКТ обчислюється ЛОКАЛЬНО, без стрибка — за центральним правилом
        return self.policy.evaluate(action=action, role=role,
                                    is_member=is_member, now=time.time())

# обробник як був — гейт лишився викликом функції, начинку не видно
if not authz.can(user, "unlock", door):
    return Response(status=403)
door.unlock()
