class Port:
    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        if not (1024 <= value <= 65535):
            instance.logger.critical('The port isn`t in the range 1024 to 65535')
            exit(1)
        setattr(instance, self.name, value)
