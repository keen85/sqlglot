from sqlglot import exp
from sqlglot.dialects.tsql import TSQL
from sqlglot.generators.synapse import SynapseGenerator
from sqlglot.parsers.synapse import SynapseParser


class Synapse(TSQL):
    """
    Azure Synapse Analytics Dedicated SQL Pool is a variant of the TSQL dialect.
    """

    Parser = SynapseParser
    Generator = SynapseGenerator


SynapseGenerator.PROPERTIES_LOCATION = {
    **SynapseGenerator.PROPERTIES_LOCATION,
    exp.ClusteredColumnstoreIndexProperty: exp.Properties.Location.POST_WITH,
    exp.HeapProperty: exp.Properties.Location.POST_WITH,
    exp.ClusteredIndexProperty: exp.Properties.Location.POST_WITH,
    exp.DistributionProperty: exp.Properties.Location.POST_WITH,
    exp.SynapsePartitionProperty: exp.Properties.Location.POST_WITH,
    exp.LocationProperty: exp.Properties.Location.POST_WITH,
    exp.DataSourceProperty: exp.Properties.Location.POST_WITH,
    exp.FileFormatProperty: exp.Properties.Location.POST_WITH,
}
