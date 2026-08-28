# ПОГАНО: будь-яка відсутність → FREE, обидва баги проковтнуто
def load_bad(row: Optional[Row]) -> Subscription:
    return PaidSubscription(row) if row else FREE

# ДОБРЕ: розвилку проходимо явно, перш ніж підставляти порожній об'єкт
def load_subscription(user_id: str) -> Subscription:
    user = users[user_id]                        # KeyError, якщо юзера немає — це вже не «вільний»
    row = plans.find(user.plan_id)               # find кидає на збій запиту, не повертає None

    if user.tier == "enterprise" and row is None:
        # enterprise без плану — порушення інваріанта, а не вільний тариф
        raise IntegrityError(f"enterprise-акаунт {user_id} без плану — цілісність порушено")

    return FREE if row is None else PaidSubscription(row)   # рядка нема → законно вільний
