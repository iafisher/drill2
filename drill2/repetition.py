import random
from typing import List, Optional

from .storage import Question


def select_question(questions: List[Question]) -> Optional[Question]:
    if not questions:
        return None

    # TODO: select based on question strength and time last asked
    return random.choice(questions)
