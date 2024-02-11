import random
from typing import List

from .storage import Question


def select_question(questions: List[Question]) -> Question:
    # TODO: select based on question strength and time last asked
    return random.choice(questions)
