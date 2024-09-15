class Cache:
    def __init__(self) -> None:
        self._cache = {}
        pass

    def get(self, arg, fallback = None):
        if arg not in self._cache:
            if fallback is None:
                return None
            self._cache[arg] = fallback()
        return self._cache[arg]
        
    def clear_cache(self, arg = None):
        if arg is None:
            self._cache.clear()
        else:
            del self._cache[arg]