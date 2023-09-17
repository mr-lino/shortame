from dataclasses import dataclass


@dataclass
class Url:
    short_url: str
    long_url: str

    def __str__(self):
        return "{" + f"{self.short_url}: {self.long_url[:30]}..." + "}"
