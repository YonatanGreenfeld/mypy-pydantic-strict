from typing import Callable, Optional, Type, cast

from mypy.nodes import TypeInfo
from mypy.plugin import ClassDefContext, Plugin
from mypy.semanal import SemanticAnalyzer

from checks.frozen import test_frozen

BASEMODEL_FULLNAME = 'pydantic.main.BaseModel'


class CustomPlugin(Plugin):
    def get_base_class_hook(self, fullname: str) -> Optional[Callable[[ClassDefContext], None]]:
        sym = self.lookup_fully_qualified(fullname)
        if sym and isinstance(sym.node, TypeInfo):  # pragma: no branch
            # No branching may occur if the mypy cache has not been cleared
            if any(base.fullname == BASEMODEL_FULLNAME for base in sym.node.mro):
                return self._pydantic_model_class_maker_callback
        return None

    @staticmethod
    def _pydantic_model_class_maker_callback(ctx: ClassDefContext) -> None:
        api = cast(SemanticAnalyzer, ctx.api)
        test_frozen(ctx.cls.info, api)


def plugin(version: str) -> Type[CustomPlugin]:
    return CustomPlugin
