from __future__ import annotations

from sqlglot import exp
from sqlglot.generators.tsql import TSQLGenerator


class SynapseGenerator(TSQLGenerator):
    def clusteredcolumnstoreindexproperty_sql(self, expression):
        return (
            f"CLUSTERED COLUMNSTORE INDEX ORDER ({self.expressions(expression, flat=True)})"
            if expression.expressions
            else "CLUSTERED COLUMNSTORE INDEX"
        )

    def heapproperty_sql(self, expression):
        return "HEAP"

    def clusteredindexproperty_sql(self, expression):
        return f"CLUSTERED INDEX ({self.expressions(expression, flat=True)})"

    def distributionproperty_sql(self, expression):
        return f"DISTRIBUTION = {self.sql(expression, 'this')}"

    def hashdistribution_sql(self, expression):
        return f"HASH({self.expressions(expression, flat=True)})"

    def roundrobindistribution_sql(self, expression):
        return "ROUND_ROBIN"

    def replicatedistribution_sql(self, expression):
        return "REPLICATE"

    def synapsepartitionproperty_sql(self, expression):
        return "PARTITION ({} RANGE{} FOR VALUES ({}))".format(
            self.sql(expression, "this"),
            " {}".format(expression.args["side"]) if expression.args.get("side") else "",
            ", ".join(self.sql(v) for v in (expression.args.get("values") or [])),
        )

    TRANSFORMS = {
        **TSQLGenerator.TRANSFORMS,
        exp.LocationProperty: lambda self, e: f"LOCATION={self.sql(e, 'this')}",
    }

    PROPERTIES_LOCATION = {
        **TSQLGenerator.PROPERTIES_LOCATION,
    }
