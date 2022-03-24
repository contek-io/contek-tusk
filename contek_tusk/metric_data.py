from pandas import DataFrame

from contek_tusk.table import Table


class MetricData:

    def __init__(self, table: Table, df: DataFrame) -> None:
        self._table = table
        self._df = df

    def get_table(self) -> Table:
        return self._table

    def get_data_frame(self) -> DataFrame:
        return self._df
