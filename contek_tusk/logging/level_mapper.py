from logging import INFO, DEBUG, NOTSET, WARNING, ERROR, CRITICAL


class LevelMapper:

    def __call__(self, level: int) -> int:
        if level is NOTSET:
            return 0
        if level is CRITICAL:
            return 1
        if level is ERROR:
            return 2
        if level is WARNING:
            return 3
        if level is INFO:
            return 4
        if level is DEBUG:
            return 5
        return -1
