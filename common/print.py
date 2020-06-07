class Print:
    def __repr__(self):
        return str(self.__dict__)

    def serialize(self):
        return self.__dict__
