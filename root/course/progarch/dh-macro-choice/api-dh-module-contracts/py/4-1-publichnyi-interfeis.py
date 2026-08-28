class IUserIdentityModule(ABC):
    @abstractmethod
    def check_user_permission(self, user_id: str, home_id: str, required_permission: str) -> bool:
        """Перевіряє наявність права користувача на виконання дії у конкретному домі.
        
        Параметри:
          - user_id: GUID користувача.
          - home_id: GUID дому.
          - required_permission: Рядковий код права ('control_devices', 'manage_rules', 'view_telemetry').
        Повертає:
          - True, якщо користувач має активне право доступу.
        """
        pass

    @abstractmethod
    def get_user_profile(self, user_id: str) -> UserProfileDTO | None:
        """Отримує профіль користувача з його налаштуваннями сповіщень та мовою."""
        pass
