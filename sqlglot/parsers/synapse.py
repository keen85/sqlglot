from __future__ import annotations

from sqlglot import exp
from sqlglot.parsers.tsql import TSQLParser
from sqlglot.tokens import TokenType


class SynapseParser(TSQLParser):
    """
    Azure Synapse Dedicated SQL Pool is a variant of th TSQL dialect.
    """

    PROPERTY_PARSERS = {
        **TSQLParser.PROPERTY_PARSERS,
        "CLUSTERED": lambda self: self._parse_clustered_columnstore_property(),
        "CLUSTERED INDEX": lambda self: self._parse_clustered_index_property(),
        "HEAP": lambda self: exp.HeapProperty(),
        "DISTRIBUTION": lambda self: self._parse_distribution_property(),
        "PARTITION": lambda self: self._parse_synapse_partition_property(),
        "LOCATION": lambda self: self._parse_location_property(),
    }

    def _parse_clustered_columnstore_property(self):
        if self._match_text_seq("COLUMNSTORE", "INDEX"):
            if self._match_text_seq("ORDER"):
                cols = self._parse_wrapped_csv(self._parse_id_var)
                return exp.ClusteredColumnstoreIndexProperty(expressions=cols)
            return exp.ClusteredColumnstoreIndexProperty()

        self.raise_error("Expected `INDEX` or `COLUMNSTORE INDEX` after `CLUSTERED`")

    def _parse_clustered_index_property(self):
        cols = self._parse_wrapped_csv(self._parse_ordered)
        return exp.ClusteredIndexProperty(expressions=cols)

    def _parse_distribution_property(self):
        self._match(TokenType.EQ)

        if self._match_text_seq("HASH"):
            cols = self._parse_wrapped_csv(self._parse_id_var)
            return exp.DistributionProperty(this=exp.HashDistribution(expressions=cols))

        if self._match_text_seq("ROUND_ROBIN"):
            return exp.DistributionProperty(this=exp.RoundRobinDistribution())

        if self._match_text_seq("REPLICATE"):
            return exp.DistributionProperty(this=exp.ReplicateDistribution())

        self.raise_error("Expected `HASH`, `ROUND_ROBIN`, or `REPLICATE` after `DISTRIBUTION =`")

    def _parse_synapse_partition_property(self):
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

        return exp.SynapsePartitionProperty(this=col, side=side, values=values)

    def _parse_location_property(self):
        self._match(TokenType.EQ)
        return exp.LocationProperty(this=self._parse_primary())
