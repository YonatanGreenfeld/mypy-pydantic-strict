from typing import Callable, Optional, Type, cast

from mypy.nodes import AssignmentStmt, ClassDef, NameExpr, TypeInfo
from mypy.plugin import ClassDefContext, Plugin
from mypy.semanal import SemanticAnalyzer


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
        FrozenChecker().check(ctx.cls.info, api)


class Checker:
    def check(self, info: TypeInfo, api: SemanticAnalyzer) -> None:
        raise NotImplementedError()


class FrozenChecker(Checker):
    VALUE = "value"
    IS_FROZEN = "is_frozen"

    def check(self, info: TypeInfo, api: SemanticAnalyzer) -> None:
        # look for own configuration:
        for defn in info.defn.defs.body:
            if isinstance(defn, ClassDef):
                if defn.name == "Config":
                    for assignment in (node for node in defn.defs.body if isinstance(node, AssignmentStmt)):
                        if self.is_frozen_assignment(assignment, True):
                            info.metadata[self.IS_FROZEN] = {self.VALUE: True}
                            return
                        if self.is_frozen_assignment(assignment, False):
                            info.metadata[self.IS_FROZEN] = {self.VALUE: False}
                            api.fail("Class is not frozen", ctx=assignment)
                            return
        # look for base class definitions:
        for base in info.bases:
            if base.type.metadata.get(self.IS_FROZEN, {}).get(self.VALUE) is True:
                return
            if base.type.metadata.get(self.IS_FROZEN, {}).get(self.VALUE) is False:
                api.fail(f"Class is not frozen - base class {base} explicitly marked it as False", ctx=info)
                return
        api.fail("Class is not frozen", ctx=info)

    @staticmethod
    def is_frozen_assignment(assignment: AssignmentStmt, value: bool) -> bool:
        # TODO: support weird assignments (bla, frozen = False)
        return (isinstance(assignment.lvalues[0], NameExpr) and
                assignment.lvalues[0].name == 'frozen' and
                isinstance(assignment.rvalue, NameExpr) and
                assignment.rvalue.fullname == f'builtins.{value}')


def plugin(version: str) -> Type[CustomPlugin]:
    return CustomPlugin
