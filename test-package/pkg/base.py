from pydantic import BaseModel


class RootClass(BaseModel):
    def foo(self) -> int:
        return 41

    class Config:
        frozen = False


class BaseClass(RootClass):
    def foo(self) -> int:
        return 42

    class Config:
        frozen = True
