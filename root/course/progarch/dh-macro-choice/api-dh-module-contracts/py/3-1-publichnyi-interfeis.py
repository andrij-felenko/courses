class IAutomationModule(ABC):
    @abstractmethod
    def create_rule(self, home_id: str, rule_name: str, trigger_conditions: list[dict[str, Any]], actions: list[dict[str, Any]]) -> RuleDTO:
        """Створює нове правило автоматизації для дому.
        
        Параметри:
          - home_id: GUID дому, якому належить правило.
          - rule_name: Описова назва правила (наприклад, 'Нічне опалення вітальні').
          - trigger_conditions: Список тригерів (наприклад, [{'device_id': 'sensor_1', 'property': 'temp', 'op': '<', 'val': 18}]).
          - actions: Список дій (наприклад, [{'device_id': 'heater_1', 'property': 'power', 'val': 'ON'}]).
        Повертає:
          - Створений об'єкт RuleDTO з присвоєним rule_id.
        """
        pass

    @abstractmethod
    def evaluate_triggers_for_device(self, device_id: str, property_name: str, new_value: Any) -> list[str]:
        """Синхронно оцінює всі правила, прив'язані до зміни властивості пристрою,
        та повертає список ідентифікаторів виконаних правил.
        
        Параметри:
          - device_id: GUID пристрою, стан якого змінився.
          - property_name: Назва властивості, що зазнала змін.
          - new_value: Нове фактичне значення властивості.
        Повертає:
          - Список rule_id рядків, які спрацювали у результаті оцінки.
        """
        pass
