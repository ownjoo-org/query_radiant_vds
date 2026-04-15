"""Parsing and type validation utilities for common data conversions.

This module provides functions to safely parse and validate values, including:
- String to list conversion with custom separators
- Datetime parsing from multiple formats
- Nested value extraction from dicts/lists
- Generic validation with custom converters and validators
"""

import logging
from datetime import datetime
from collections.abc import Mapping, Sequence
from typing import Any, Callable, Optional, Type, TypeVar, Union

T = TypeVar('T')
R = TypeVar('R')

from query_radiant_vds.oj_toolkit.parsing.consts import DEFAULT_CONVERTER, DEFAULT_SEPARATOR, DEFAULT_VALIDATOR, TimeFormats

logger = logging.getLogger(__name__)

def str_to_list(v: Optional[str] = None, separator: str = DEFAULT_SEPARATOR) -> Optional[list[str]]:
    """Convert a string to a list by splitting on a separator.

    Args:
        v: The string to split. If not a string, returns unchanged.
        separator: The delimiter to split on (default: comma). Empty string returns value unchanged.

    Returns:
        A list of strings if v is a non-empty string with valid separator, otherwise the original value.

    Example:
        >>> str_to_list('a,b,c')
        ['a', 'b', 'c']
        >>> str_to_list('a;b;c', separator=';')
        ['a', 'b', 'c']
        >>> str_to_list(None)
        None
    """
    if not isinstance(v, str) or separator == '':
        return v
    if not isinstance(separator, str):
        separator = DEFAULT_SEPARATOR
    return v.split(separator)


def get_datetime(
        v: Union[None, datetime, float, str] = None,
        format_str: Optional[str] = None,
) -> Optional[datetime]:
    """Parse a value into a datetime object from multiple input formats.

    Supports parsing from:
    - datetime objects (returned as-is)
    - Numeric timestamps (seconds since epoch)
    - Strings matching known time formats (ISO 8601, HTTP date, custom format)

    Args:
        v: The value to parse. Can be None, datetime, float/int timestamp, or string.
        format_str: Optional custom datetime format string (strptime format). If provided, attempts parsing with this
        format first.

    Returns:
        A datetime object if parsing succeeds, otherwise None.

    Supported Formats:
        - ISO 8601: 'YYYY-MM-DDTHH:MM:SS'
        - HTTP: 'Sun, 06 Nov 1994 08:49:37 GMT'
        - Date and time: 'YYYY/MM/DD HH:MM:SS'
        - Custom format via format_str parameter

    Example:
        >>> get_datetime('2024-01-15T10:30:00')
        datetime.datetime(2024, 1, 15, 10, 30)
        >>> get_datetime(1234567890)
        datetime.datetime(2009, 2, 13, 23, 31, 30)
        >>> get_datetime('Sun, 06 Nov 1994 08:49:37 GMT')
        datetime.datetime(1994, 11, 6, 8, 49, 37)
    """
    result: Optional[datetime] = None
    try:
        if isinstance(v, datetime):
            result = v
        elif isinstance(v, (float, int)):  # if number treat as a timestamp (seconds from epoch)
            result = datetime.fromtimestamp(v)
        elif isinstance(v, str) and isinstance(format_str, str):
            result = datetime.strptime(v, format_str)
        elif isinstance(v, str):
            for time_format in TimeFormats:  # if str try to parse the str from a known format
                try:
                    result = datetime.strptime(v, time_format.value)
                except Exception:
                    # Silently try next format instead of logging each failure
                    continue
        else:
            logger.warning(f'Unusable {v=}, {format_str=}. Returning {result=}')
    except Exception as exc:
        logger.debug(f'Failed to parse {v=}: {exc}')
    return result


def validate(
        v: Any,
        exp: Type[T] = None,
        default: Optional[T] = None,
        converter: Callable = None,
        validator: Optional[Callable] = DEFAULT_VALIDATOR,
        **kwargs
) -> Optional[T]:
    """Validate and optionally convert a value with a custom converter and validator.

    This is a generic validation utility that:
    1. Converts the value using a converter function (with automatic selection for common types)
    2. Validates the result using a validator function
    3. Returns the result if valid, otherwise returns the default value

    Args:
        v: The value to validate.
        exp: Expected type of the value. If None, no type conversion is attempted.
        default: The value to return if validation fails or v is None. Default: None.
        converter: Custom converter function. If None, one is selected based on exp:
            - exp=list: uses str_to_list
            - exp=datetime: uses get_datetime
            - otherwise: uses DEFAULT_CONVERTER (pass-through)
        validator: Custom validator function(result, exp, **kwargs) -> bool.
            If None, uses DEFAULT_VALIDATOR (isinstance check).
        **kwargs: Additional arguments passed to converter and validator functions.

    Returns:
        The converted and validated value, or the default value if validation fails.
        Returns None if no default is specified and validation fails.

    Example:
        >>> validate('123', exp=int, converter=int)
        123
        >>> validate('invalid', exp=int, default=0)
        0
        >>> validate('a,b,c', exp=list)
        ['a', 'b', 'c']
    """
    result: Any = v
    is_valid_result: bool = False

    # check pre-defined converters
    if not callable(converter):
        if exp is list:
            converter = str_to_list
        elif exp is datetime:
            converter = get_datetime
        else:
            converter = DEFAULT_CONVERTER  # pass through

    # convert values as needed
    conversion_succeeded = True
    try:
        result = converter(v, **kwargs)
    except Exception as exc_str:
        logger.debug(f'Failed to parse {v=} with converter {converter}: {exc_str}', exc_info=True)
        conversion_succeeded = False

    # check validator (only if conversion succeeded)
    if conversion_succeeded:
        if not callable(validator):
            validator = DEFAULT_VALIDATOR

        try:
            is_valid_result = validator(result, exp, **kwargs)
        except Exception as exc_validation:
            logger.debug(f'Failed validation: {validator=}: {exc_validation=}', exc_info=True)

    return result if is_valid_result else default


def dig(
        src: Union[Mapping, Sequence],
        path: Union[None, int, list, str] = None,
        pop: bool = False,
        post_processor: Callable[..., R] = validate,
        **kwargs
) -> Optional[R]:
    """Extract and post-process a value from a nested data structure.

    Recursively navigates through nested dicts and lists using a path of keys/indices,
    then post-processes the result with a callable (default: validate).

    Args:
        src: A dict or list to navigate. If path is None, treated as a single value to post-process.
        path: List of keys (str) and indices (int/float) to navigate the structure.
            Example: ['data', 0, 'value'] extracts src['data'][0]['value']
            If None, src is treated as a single value to post-process.
        pop: If True, delete the terminal key/index from its container after extracting the value.
            Mutates src in place. Default: False.
        post_processor: Callable to post-process the found value. Default: validate().
            If None, the raw value is returned without post-processing.
        **kwargs: Additional arguments passed to post_processor function.

    Returns:
        The post-processed value, or None if extraction fails or no post-processor is specified.

    Example:
        >>> src = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
        >>> dig(src, path=['users', 0, 'name'])
        'Alice'
        >>> dig(src, path=['users', 1, 'name'], exp=str)
        'Bob'
        >>> dig(src, path=['users', 0, 'name'], pop=True)  # removes 'name' from src['users'][0]
        'Alice'
    """
    result: Any = None
    remaining_path: Union[None, list] = None

    # Extract the first key/index without mutating the original path
    if path and isinstance(path, list) and len(path) > 0:
        keydex = path[0]
        remaining_path = path[1:]
    else:
        keydex = None
        remaining_path = None

    # Try to navigate to the next level
    if keydex is not None:
        try:
            result = src[keydex]
        except (IndexError, KeyError, TypeError) as exc_val:
            logger.debug(f'ERROR extracting {path=} from {src=}: {exc_val=}', exc_info=True)
            result = None
    else:
        result = src

    # Recursively continue if path remains and result is a dict/list
    if remaining_path and result is not None and isinstance(result, (dict, list)):
        return dig(src=result, path=remaining_path, pop=pop, post_processor=post_processor, **kwargs)

    # Pop the terminal value from its container if requested
    if pop and keydex is not None and result is not None:
        try:
            del src[keydex]
        except (IndexError, KeyError, TypeError) as exc_pop:
            logger.warning(f'Failed to pop {keydex=} from {src=}: {exc_pop}')

    # Apply post-processor if result was found (not None) or if no result
    if callable(post_processor) and result is not None:
        return post_processor(result, **kwargs)
    return result  # return found value without post-processing
