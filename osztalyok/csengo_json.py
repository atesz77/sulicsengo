import pydantic

class CsengoIdopont(pydantic.BaseModel):
    """A CsengoIdopont class represents a timestamp for a Csengo instance.

    Attributes:
        idopont (str): The timestamp of the Csengo instance.
        zene (str): The music associated with the Csengo instance.
    """
    idopont: str
    zene: str | None = None

class CsengoKonfiguracio(pydantic.BaseModel):
    """A CsengoKonfiguracio class represents the configuration for a Csengo instance.

    Attributes:
        idopontok (list[CsengoIdopont]): A list of timestamps for the Csengo instance.
        alapZene (str): The default music for the Csengo instance.
    """
    idopontok: list[CsengoIdopont]
    alapZene: str