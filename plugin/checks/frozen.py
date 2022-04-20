from mypy.nodes import AssignmentStmt, ClassDef, NameExpr, TypeInfo
from mypy.semanal import SemanticAnalyzer

VALUE = "value"

IS_FROZEN = "is_frozen"


def test_frozen(info: TypeInfo, api: SemanticAnalyzer) -> None:
    # look for own configuration:
    for defn in info.defn.defs.body:
        if isinstance(defn, ClassDef):
            if defn.name == "Config":
                for assignment in (node for node in defn.defs.body if isinstance(node, AssignmentStmt)):
                    if is_frozen_assignment(assignment, True):
                        info.metadata[IS_FROZEN] = {VALUE: True}
                        return
                    if is_frozen_assignment(assignment, False):
                        info.metadata[IS_FROZEN] = {VALUE: False}
                        api.fail("Class is not frozen", ctx=assignment)
                        return
    # look for base class definitions:
    for base in info.bases:
        if base.type.metadata.get(IS_FROZEN, {}).get(VALUE) is True:
            return
        if base.type.metadata.get(IS_FROZEN, {}).get(VALUE) is False:
            api.fail(f"Class is not frozen - base class {base} explicitly marked it as False", ctx=info)
            return
    api.fail("Class is not frozen", ctx=info)


def is_frozen_assignment(assignment: AssignmentStmt, value: bool) -> bool:
    # TODO: support weird assignments (bla, frozen = False)
    return (isinstance(assignment.lvalues[0], NameExpr) and
            assignment.lvalues[0].name == 'frozen' and
            isinstance(assignment.rvalue, NameExpr) and
            assignment.rvalue.fullname == f'builtins.{value}')
