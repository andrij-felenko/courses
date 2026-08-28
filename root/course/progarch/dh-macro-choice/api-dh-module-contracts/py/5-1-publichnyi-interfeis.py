class INotificationsModule(ABC):
    @abstractmethod
    def send_critical_alert(self, home_id: str, title: str, message: str, payload: dict[str, Any]) -> str:
        """Надсилає термінове сповіщення високого пріоритету всім мешканцям дому.
        
        Параметри:
          - home_id: GUID дому.
          - title: Короткий заголовок сповіщення (наприклад, 'УВАГА: Виявлено протікання води!').
          - message: Текст сповіщення.
          - payload: Додаткові дані для відкриття конкретного екрана у мобільному застосунку.
        Повертає:
          - notification_id відправленого сповіщення.
        """
        pass
