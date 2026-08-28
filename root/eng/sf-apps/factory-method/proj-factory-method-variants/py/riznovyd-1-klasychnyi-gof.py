from abc import ABC, abstractmethod

class ProfileImporter(ABC):
    @abstractmethod
    def _create_parser(self) -> "ProfileParser":   # діра для нащадка
        ...

    # спільний процес — той самий для всіх форматів
    def import_(self, raw: str) -> "Profile":
        parser = self._create_parser()             # ...кличе діру...
        profile = parser.parse(raw)
        self._assert_required_fields(profile)
        self._log(f"Імпортовано {profile.email}")
        return profile

    def _assert_required_fields(self, p: "Profile") -> None:
        if not p.email:
            raise ValueError("Профіль без email")

    def _log(self, msg: str) -> None: ...

class JsonProfileImporter(ProfileImporter):
    def _create_parser(self) -> "ProfileParser":   # нащадок ОБИРАЄ клас
        return JsonProfileParser()

class CsvProfileImporter(ProfileImporter):
    def _create_parser(self) -> "ProfileParser":
        return CsvProfileParser()
