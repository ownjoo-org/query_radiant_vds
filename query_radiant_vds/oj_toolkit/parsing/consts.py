"""
Constants for parsing and formatting
"""
from enum import Enum
from typing import Callable

# pylint: disable=invalid-name
DEFAULT_CONVERTER: Callable = lambda value, *args, **kwargs: value
DEFAULT_VALIDATOR: Callable = lambda value, expected_type, *args, **kwargs: isinstance(value, expected_type)
DEFAULT_SEPARATOR: str = ','


class TimeFormats(Enum):
    """Time formats for parsing and formatting"""
    DATE_AND_TIME = '%Y/%m/%d %H:%M:%S'
    ISO8601 = '%Y-%m-%dT%H:%M:%S'
    HTTP = '%a, %d %b %Y %H:%M:%S GMT'
