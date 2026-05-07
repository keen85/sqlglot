from __future__ import annotations

from sqlglot import exp
from sqlglot.generators.tsql import TSQLGenerator


class SynapseGenerator(TSQLGenerator):
    """
    Azure Synapse Analytics Dedicated SQL Pool is a variant of the TSQL dialect.
    """

    def heapproperty_sql(self, expression: exp.HeapProperty) -> str:
        return "HEAP"

    def clusteredcolumnstoreindexproperty_sql(
        self, expression: exp.ClusteredColumnstoreIndexProperty
    ) -> str:
        return (
            f"CLUSTERED COLUMNSTORE INDEX ORDER ({self.expressions(expression, flat=True)})"
            if expression.expressions
            else "CLUSTERED COLUMNSTORE INDEX"
        )

    def clusteredindexproperty_sql(self, expression: exp.ClusteredIndexProperty) -> str:
        return f"CLUSTERED INDEX ({self.expressions(expression, flat=True)})"

    def distributionproperty_sql(self, expression: exp.DistributionProperty) -> str:
        return f"DISTRIBUTION = {self.sql(expression, 'this')}"

    def hashdistribution_sql(self, expression: exp.HashDistribution) -> str:
        return f"HASH({self.expressions(expression, flat=True)})"

    def roundrobindistribution_sql(self, expression: exp.RoundRobinDistribution) -> str:
        return "ROUND_ROBIN"

    def replicatedistribution_sql(self, expression: exp.ReplicateDistribution) -> str:
        return "REPLICATE"

    def locationproperty_sql(self, expression: exp.LocationProperty) -> str:
        return f"LOCATION = {self.sql(expression, 'this')}"

    def synapsepartitionproperty_sql(self, expression: exp.SynapsePartitionProperty) -> str:
        this = self.sql(expression, "this")
        side = f" {expression.args['side']}" if expression.args.get("side") else ""
        values = self.expressions(expression, key="values", flat=True)
        return f"PARTITION ({this} RANGE{side} FOR VALUES ({values}))"

    TRANSFORMS = {
        **{k: v for k, v in TSQLGenerator.TRANSFORMS.items() if k is not exp.LocationProperty},
    }

    PROPERTIES_LOCATION = {
        **TSQLGenerator.PROPERTIES_LOCATION,
    }
