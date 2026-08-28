from dataclasses import dataclass

@dataclass(frozen=True)
class Profile:
    email: str
    display_name: str
    verified: bool

    # осмислені входи в клас — кожен зі СВОЄЮ назвою і своїм добором
    @classmethod
    def register(cls, email: str, display_name: str) -> "Profile":
        return cls(email.lower(), display_name, False)

    @classmethod
    def from_verified_invite(cls, email: str) -> "Profile":
        return cls(email.lower(), email.split("@")[0], True)

    @classmethod
    def anonymous(cls) -> "Profile":
        return cls("", "Гість", False)

a = Profile.register("Ann@Ex.com", "Ann")       # → verified=False
b = Profile.from_verified_invite("bob@ex.com")  # → verified=True
