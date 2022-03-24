import datetime
from typing import Dict, Optional

from contek_tusk.entry_row import EntryRow
from contek_tusk.schema import Schema
from contek_tusk.schema_provider import SchemaProvider


class EntryInputNormalizer:

    def __init__(self, schema_provider: SchemaProvider) -> None:
        self._schema_provider = schema_provider

    def normalize(self, key_values: Dict[str, any]) -> Optional[EntryRow]:
        schema = self._schema_provider.get_schema()
        if schema is None:
            return None

        result: Dict[str, any] = {}
        for (key, value) in key_values.items():
            normalized = EntryInputNormalizer._normalize_for_column(
                value,
                key,
                schema,
            )
            if normalized is not None:
                result[key] = normalized

        for (column_name, column_type) in schema.get_columns().items():
            if column_name not in result:
                fill = EntryInputNormalizer._fill_for_type(column_type)
                result[column_name] = fill

        return EntryRow(result)

    @staticmethod
    def _normalize_for_column(
        value: any,
        column_name: str,
        schema: Schema,
    ) -> any:
        if schema is None:
            return value

        column_type = schema.get_column_type(column_name)
        if type is None:
            raise RuntimeError(
                f"Column \"{column_name}\" is not defined in the schema")

        return EntryInputNormalizer._normalize_for_type(value, column_type)

    @staticmethod
    def _normalize_for_type(value: any, column_type: str) -> any:
        value_type = type(value)
        if column_type == 'String':
            if value_type is not str:
                return str(value)

        if column_type.startswith('DateTime'):
            if value_type == float:
                return datetime.datetime.utcfromtimestamp(value)

        if column_type.startswith('Int') or column_type.startswith('UInt'):
            if value_type == str or value_type == float:
                return int(value)

        if column_type.startswith('Float'):
            if value_type == str or value_type == int:
                return float(value)

        return value

    @staticmethod
    def _fill_for_type(column_type: str) -> any:
        if column_type == 'String':
            return ''

        if column_type.startswith('DateTime'):
            return datetime.datetime.utcfromtimestamp(0)

        if column_type.startswith('Int') or column_type.startswith('UInt'):
            return int(0)

        if column_type.startswith('Float'):
            return float(0)

        raise ValueError(column_type)
