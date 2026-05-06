from __future__ import annotations

from sqlglot import exp
from sqlglot.expressions.synapse import (
    ClusteredColumnstoreIndexProperty,
    ClusteredIndexProperty,
    DistributionProperty,
    HashDistribution,
    HeapProperty,
    ReplicateDistribution,
    RoundRobinDistribution,
    SynapsePartitionProperty,
)
from sqlglot.generators.tsql import TSQLGenerator


class SynapseGenerator(TSQLGenerator):
    TRANSFORMS = {
        **TSQLGenerator.TRANSFORMS,
        # structure
        ClusteredColumnstoreIndexProperty: lambda self, e: (
            f"CLUSTERED COLUMNSTORE INDEX ORDER ({self.expressions(e, flat=True)})"
            if e.expressions
            else "CLUSTERED COLUMNSTORE INDEX"
        ),
        HeapProperty: lambda self, e: "HEAP",
        ClusteredIndexProperty: lambda self, e: (
            f"CLUSTERED INDEX ({self.expressions(e, flat=True)})"
        ),
        # distribution
        DistributionProperty: lambda self, e: "DISTRIBUTION = {}".format(self.sql(e, "this")),
        HashDistribution: lambda self, e: f"HASH({self.expressions(e, flat=True)})",
        RoundRobinDistribution: lambda self, e: "ROUND_ROBIN",
        ReplicateDistribution: lambda self, e: "REPLICATE",
        # partition
        SynapsePartitionProperty: lambda self, e: "PARTITION ({} RANGE{} FOR VALUES ({}))".format(
            self.sql(e, "this"),
            " {}".format(e.args["side"]) if e.args.get("side") else "",
            ", ".join(self.sql(v) for v in (e.args.get("values") or [])),
        ),
        # --- override for external table LOCATION behavior ---
        exp.LocationProperty: lambda self, e: "LOCATION={}".format(self.sql(e, "this")),
    }

    PROPERTIES_LOCATION = {
        **TSQLGenerator.PROPERTIES_LOCATION,
        ClusteredColumnstoreIndexProperty: exp.Properties.Location.POST_WITH,
        HeapProperty: exp.Properties.Location.POST_WITH,
        ClusteredIndexProperty: exp.Properties.Location.POST_WITH,
        DistributionProperty: exp.Properties.Location.POST_WITH,
        SynapsePartitionProperty: exp.Properties.Location.POST_WITH,
        exp.LocationProperty: exp.Properties.Location.POST_WITH,
    }
