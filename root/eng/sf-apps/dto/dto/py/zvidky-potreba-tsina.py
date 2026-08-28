from dataclasses import dataclass

# Один об'єкт із усіма полями — один перетин межі замість чотирьох
@dataclass
class UserDto:
    name: str
    email: str
    phone: str
    address: str

dto = user_service.get_user_card(id)  # єдиний перетин межі — усе разом
