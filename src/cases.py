from dataclasses import dataclass, KW_ONLY
from enum import IntEnum
from typing import Union, List
import random
import os



@dataclass
class Case:
    input: str
    output: str
    file_mode: bool = False
    exit_code: int = 0

    def generate_args(self, path: str) -> List[str]:
        if self.file_mode:
            args = [os.path.join(path, self.input)]
        else:
            args = []
        return args



def get_cases() -> List[Case]:
    return [
        Case("..\\test\\test1.in", "..\\test\\test1.out"),
    ]
