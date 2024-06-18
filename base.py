class HasID:
    _id = 0

    def __init__(self) -> None:
        self.id = self._id
        self._incr_id()

    @classmethod
    def _incr_id(cls):
        cls._id += 1

    def __hash__(self) -> int:
        return hash(self.id)
