# БЕЗ шару: чужий формат розповзається по доменному коду
class OrderService:
    def place(self, dto: CrmOrderDto) -> None:
        parts = dto.sku.split("/")            # знання про їхній формат — тут
        article = parts[0]
        color = parts[1]                       # а завтра формат зміниться…
        if dto.qty < 0:
            ...                                # якось окремо на повернення
        if dto.status_code == 7:               # магічне число в домені
            ...                                # тягнемо чуже поняття у свою модель
        client_id = dto.client_ref[3:]         # зрізаємо "CL:"
        # …і так у кожному місці, що торкається замовлення
