"""Decorators for logging progress and timing of generator functions.

Provides decorators to wrap generator and async generator functions with:
- Start/end timestamps and duration logging
- Progress logging at regular intervals (item count)
- Customizable log level, logger, and progress labels
"""

import logging
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import AsyncGenerator, Generator, Optional

from query_radiant_vds.oj_toolkit.logging.consts import LOG_FORMAT
from query_radiant_vds.oj_toolkit.parsing.consts import TimeFormats


def timed_generator(
        log_progress: bool = True,
        log_progress_label: Optional[str] = None,
        log_progress_interval: int = 10000,
        log_level: int = logging.INFO,
        logger: Optional[logging.Logger] = None,
):
    """Decorator that logs progress and timing information for a generator function.

    Wraps a generator function to:
    - Log start time when iteration begins
    - Log progress at regular intervals (e.g., every 10000 items yielded)
    - Log end time and total duration when iteration completes
    - Count and report total items yielded

    Args:
        log_progress: If True (default), log start/progress/end messages. If False, only log final count and duration.
        log_progress_label: Label for progress messages (e.g., "documents", "records").
            If None, uses the wrapped function's name.
        log_progress_interval: Log progress every N items yielded (default: 10000).
        log_level: Logging level for all messages (default: logging.INFO).
        logger: A logging.Logger instance. If None, creates one with basicConfig.

    Returns:
        A decorator function that wraps a generator and yields items while logging.

    Example:
        @timed_generator(log_progress_label="records", log_progress_interval=1000)
        def fetch_records():
            for i in range(50000):
                yield {'id': i}

        for record in fetch_records():
            process(record)
        # Logs: Started records at 2024-01-15T10:30:00+00:00
        #       Fetched 1000 records so far
        #       Fetched 2000 records so far
        #       ... (every 1000 items)
        #       Ended records at 2024-01-15T10:35:00+00:00
        #       Yielded 50000 records in 0:05:00
    """
    if not isinstance(logger, logging.Logger):
        logging.basicConfig(
            format=LOG_FORMAT,
            level=logging.INFO,
            datefmt=TimeFormats.DATE_AND_TIME.value,
        )
        logger = logging.getLogger(__name__)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs) -> Generator:
            nonlocal log_progress_label
            if not log_progress_label:
                log_progress_label = func.__name__
            count: int = 0
            start = datetime.now(timezone.utc)
            if log_progress:
                logger.log(log_level, f'Started {log_progress_label} at {start.isoformat()}')
            for each in func(*args, **kwargs):
                yield each
                count += 1
                if log_progress:
                    if not count % log_progress_interval:
                        logger.log(log_level, f'Fetched {count} {log_progress_label} so far')
            end = datetime.now(timezone.utc)
            elapsed: timedelta = end - start
            if log_progress:
                logger.log(log_level, f'Ended {log_progress_label} at {end.isoformat()}')
            logger.log(log_level, f'Yielded {count} {log_progress_label} in {elapsed}')
        return wrapper
    return decorator


def timed_async_generator(
        log_progress: bool = True,
        log_progress_label: Optional[str] = None,
        log_progress_interval: int = 10000,
        log_level: int = logging.INFO,
        logger: Optional[logging.Logger] = None,
):
    """Decorator that logs progress and timing information for an async generator function.

    Async version of timed_generator. Wraps an async generator function to:
    - Log start time when iteration begins
    - Log progress at regular intervals (e.g., every 10000 items yielded)
    - Log end time and total duration when iteration completes
    - Count and report total items yielded

    Args:
        log_progress: If True (default), log start/progress/end messages. If False, only log final count and duration.
        log_progress_label: Label for progress messages (e.g., "documents", "records").
            If None, uses the wrapped function's name.
        log_progress_interval: Log progress every N items yielded (default: 10000).
        log_level: Logging level for all messages (default: logging.INFO).
        logger: A logging.Logger instance. If None, creates one with basicConfig.

    Returns:
        A decorator function that wraps an async generator and yields items while logging.

    Example:
        @timed_async_generator(log_progress_label="records", log_progress_interval=1000)
        async def fetch_records():
            for i in range(50000):
                yield {'id': i}

        async for record in fetch_records():
            await process(record)
        # Logs: Started records at 2024-01-15T10:30:00+00:00
        #       Fetched 1000 records so far
        #       ... (every 1000 items)
        #       Ended records at 2024-01-15T10:35:00+00:00
        #       Yielded 50000 records in 0:05:00
    """
    if not isinstance(logger, logging.Logger):
        logging.basicConfig(
            format=LOG_FORMAT,
            level=logging.INFO,
            datefmt=TimeFormats.DATE_AND_TIME.value,
        )
        logger = logging.getLogger(__name__)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> AsyncGenerator:
            nonlocal log_progress_label
            if not log_progress_label:
                log_progress_label = func.__name__
            count: int = 0
            start = datetime.now(timezone.utc)
            if log_progress:
                logger.log(log_level, f'Started {log_progress_label} at {start.isoformat()}')
            async for each in func(*args, **kwargs):
                yield each
                count += 1
                if log_progress:
                    if not count % log_progress_interval:
                        logger.log(log_level, f'Fetched {count} {log_progress_label} so far')
            end = datetime.now(timezone.utc)
            elapsed: timedelta = end - start
            if log_progress:
                logger.log(log_level, f'Ended {log_progress_label} at {end.isoformat()}')
            logger.log(log_level, f'Yielded {count} {log_progress_label} in {elapsed}')
        return wrapper
    return decorator
