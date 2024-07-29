class RegisterLeafClasses(type):
    def __init__(cls, name, bases, nmspc) -> None:
        super().__init__(name, bases, nmspc)
        if not hasattr(cls, "registry"):
            cls.registry = set()
        cls.registry.add(cls)
        cls.registry -= set(bases)  # Remove base classes
        if not hasattr(cls, "name"):
            cls.name = cls.__name__.lower


class Job(metaclass=RegisterLeafClasses):
    name: str
    description: str = ""

    def run(self) -> None:
        pass
