from dataclasses import dataclass

@dataclass
class Loading: ...                    # жодних полів — і не треба

@dataclass
class Failed:
    message: str                      # лише текст помилки

@dataclass
class Ready:
    value: Data                       # лише дані

RequestState = Loading | Failed | Ready
