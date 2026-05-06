from sqlglot import exp
from sqlglot.dialects.tsql import TSQL
from sqlglot.expressions import Expression, Property
from sqlglot.tokens import TokenType


# ── Custom Expression Classes ──────────────────────────────────────────────


class ClusteredColumnstoreIndexProperty(Property):
    """CLUSTERED COLUMNSTORE INDEX [ORDER (col [,...n])]"""

    arg_types = {"expressions": False}


class HeapProperty(Property):
    """HEAP"""

    arg_types = {}


class ClusteredIndexProperty(Property):
    """CLUSTERED INDEX (col [ASC|DESC] [,...n])"""

    arg_types = {"expressions": True}


class HashDistribution(Expression):
    """HASH (col [,...n])"""

    arg_types = {"expressions": True}


class RoundRobinDistribution(Expression):
    """ROUND_ROBIN"""

    arg_types = {}


class ReplicateDistribution(Expression):
    """REPLICATE"""

    arg_types = {}


class DistributionProperty(Property):
    """DISTRIBUTION = <kind>"""

    arg_types = {"this": True}


class SynapsePartitionProperty(Property):
    """PARTITION (col RANGE [LEFT|RIGHT] FOR VALUES (val [,...n]))"""

    arg_types = {
        "this": True,
        "side": False,
        "values": False,
    }


# ── Dialect Definition ─────────────────────────────────────────────────────


class Synapse(TSQL):
    """Azure Synapse Analytics SQL dialect (TSQL sub-dialect)."""

    class Parser(TSQL.Parser):
        PROPERTY_PARSERS = {
            **TSQL.Parser.PROPERTY_PARSERS,
            "CLUSTERED": lambda self: self._parse_clustered_columnstore_property(),
            "CLUSTERED INDEX": lambda self: self._parse_clustered_index_property(),
            "HEAP": lambda self: HeapProperty(),
            "DISTRIBUTION": lambda self: self._parse_distribution_property(),
            "PARTITION": lambda self: self._parse_synapse_partition_property(),
        }

        def _parse_clustered_columnstore_property(self) -> ClusteredColumnstoreIndexProperty:
            if self._match_text_seq("COLUMNSTORE", "INDEX"):
                if self._match_text_seq("ORDER"):
                    cols = self._parse_wrapped_csv(self._parse_id_var)
                    return ClusteredColumnstoreIndexProperty(expressions=cols)
                return ClusteredColumnstoreIndexProperty()
            self.raise_error("Expected COLUMNSTORE INDEX after CLUSTERED")

        def _parse_clustered_index_property(self) -> ClusteredIndexProperty:
            cols = self._parse_wrapped_csv(self._parse_ordered)
            return ClusteredIndexProperty(expressions=cols)

        def _parse_distribution_property(self) -> DistributionProperty:
            self._match(TokenType.EQ)

            if self._match_text_seq("HASH"):
                cols = self._parse_wrapped_csv(self._parse_id_var)
                return DistributionProperty(this=HashDistribution(expressions=cols))

            if self._match_text_seq("ROUND_ROBIN"):
                return DistributionProperty(this=RoundRobinDistribution())

            if self._match_text_seq("REPLICATE"):
                return DistributionProperty(this=ReplicateDistribution())

            self.raise_error("Expected HASH, ROUND_ROBIN, or REPLICATE after DISTRIBUTION =")

        def _parse_synapse_partition_property(self) -> SynapsePartitionProperty:
            self._match(TokenType.L_PAREN)
            col = self._parse_id_var()
            self._match_text_seq("RANGE")

            side = None
            if self._match_text_seq("LEFT"):
                side = "LEFT"
            elif self._match_text_seq("RIGHT"):
                side = "RIGHT"

            self._match_text_seq("FOR", "VALUES")
            values = self._parse_wrapped_csv(self._parse_primary)
            self._match(TokenType.R_PAREN)

            return SynapsePartitionProperty(this=col, side=side, values=values)

    class Generator(TSQL.Generator):
        TRANSFORMS = {
            **TSQL.Generator.TRANSFORMS,
            # structure
            ClusteredColumnstoreIndexProperty: lambda self, e: (
                "CLUSTERED COLUMNSTORE INDEX ORDER ({})".format(self.expressions(e, flat=True))
                if e.expressions
                else "CLUSTERED COLUMNSTORE INDEX"
            ),
            HeapProperty: lambda self, e: "HEAP",
            ClusteredIndexProperty: lambda self, e: "CLUSTERED INDEX ({})".format(self.expressions(e, flat=True)),
            # distribution
            DistributionProperty: lambda self, e: "DISTRIBUTION = {}".format(self.sql(e, "this")),
            HashDistribution: lambda self, e: "HASH({})".format(self.expressions(e, flat=True)),
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
            **TSQL.Generator.PROPERTIES_LOCATION,
            ClusteredColumnstoreIndexProperty: exp.Properties.Location.POST_WITH,
            HeapProperty: exp.Properties.Location.POST_WITH,
            ClusteredIndexProperty: exp.Properties.Location.POST_WITH,
            DistributionProperty: exp.Properties.Location.POST_WITH,
            SynapsePartitionProperty: exp.Properties.Location.POST_WITH,
            exp.LocationProperty: exp.Properties.Location.POST_WITH,
        }