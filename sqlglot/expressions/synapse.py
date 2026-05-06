from sqlglot.expressions import Expression, Property


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