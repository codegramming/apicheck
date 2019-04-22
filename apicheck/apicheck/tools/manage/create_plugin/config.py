from dataclasses import dataclass

from apicheck.model import CommonModel


@dataclass
class RunningConfig(CommonModel):
    name: str
    dest: str