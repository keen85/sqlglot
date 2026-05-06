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
from sqlglot.parsers.tsql import TSQLParser
from sqlglot.tokens import TokenType


class SynapseParser(TSQLParser):
    PROPERTY_PARSERS = {
        **TSQLParser.PROPERTY_PARSERS,
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