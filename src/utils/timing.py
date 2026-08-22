"""Lightweight timing instrumentation without infrastructure dependencies."""

from contextlib import contextmanager
import logging
from time import perf_counter


LOGGER = logging.getLogger("dash_workstation.performance")


@contextmanager
def timer(label: str):
    started = perf_counter()
    try:
        yield
    finally:
        LOGGER.info("%s completed in %.2f ms", label, (perf_counter() - started) * 1_000)
