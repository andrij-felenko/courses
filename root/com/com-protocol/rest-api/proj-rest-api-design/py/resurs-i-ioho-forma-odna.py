from fastapi import FastAPI, HTTPException, Header, Response
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional

app = FastAPI()
Priority = Literal['low', 'normal', 'high']

class TaskIn(BaseModel):                        # тіло на СТВОРЕННЯ
    model_config = ConfigDict(extra='forbid')   # зайве поле (напр. id) → відмова
    title: str = Field(min_length=1, max_length=200)
    done: bool = False
    priority: Priority = 'normal'

class TaskReplace(BaseModel):                    # тіло на PUT — усі поля обов'язкові
    model_config = ConfigDict(extra='forbid')
    title: str = Field(min_length=1, max_length=200)
    done: bool
    priority: Priority

class TaskPatch(BaseModel):                      # тіло на PATCH — будь-яка підмножина
    model_config = ConfigDict(extra='forbid')
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    done: Optional[bool] = None
    priority: Optional[Priority] = None

class Task(BaseModel):                           # доменна модель / вихідне представлення
    id: int
    title: str
    done: bool
    priority: Priority

tasks: dict[int, Task] = {}                       # СПІЛЬНЕ сховище, а не сесія клієнта
_next_id = 1
