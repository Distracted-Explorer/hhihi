"""Async-safe LRU cache for recently processed questions."""
import asyncio
from collections import OrderedDict
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class AsyncLRUCache(Generic[K, V]):
    def __init__(self, max_size: int = 128) -> None:
        self._max = max_size
        self._data: OrderedDict[K, V] = OrderedDict()
        self._lock = asyncio.Lock()

    async def get(self, key: K) -> V | None:
        async with self._lock:
            if key in self._data:
                self._data.move_to_end(key)
                return self._data[key]
            return None

    async def set(self, key: K, value: V) -> None:
        async with self._lock:
            if key in self._data:
                self._data.move_to_end(key)
            self._data[key] = value
            while len(self._data) > self._max:
                self._data.popitem(last=False)

    async def items(self) -> list[tuple[K, V]]:
        async with self._lock:
            return list(self._data.items())
