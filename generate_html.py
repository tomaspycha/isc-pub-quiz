import random
import string
import sys
from typing import Any, Dict, List, Mapping, Optional, Tuple

import yaml
from jinja2 import Environment, FileSystemLoader


def shuffle_choices(answer: str, wrong: List[str]):
    # generate a random order and remember the correct answer
    num_options = len(wrong) + 1  # +1 for answer
    correct_idx = random.randint(0, num_options - 1)
    random.shuffle(wrong)
    wrong.insert(correct_idx, answer)
    choices = wrong
    return choices, correct_idx

def shuffle_sort(choices:List[str],answers:List[str])->Tuple[List[str],List[str]]:
    # shuffle sorting question
    letters=list(string.ascii_uppercase[0:len(choices)])
    random.shuffle(letters)
    answers=[f"{o}) {a}" for (o,a) in zip(letters,answers)]
    choices=sorted([f"{o}) {c}" for (o,c) in zip(letters,choices)])
    return choices, answers

def parse_question(topic: Dict[str, Any], question: Dict[str, Any], question_idx: int) -> Dict[str, Any]:
    question["title"] = f"{topic['name']}: Q{question_idx + 1}"
    if question["type"] == "simple":
        pass
    elif question["type"] == "choice":
        choices, correct_idx = shuffle_choices(question["answer"], question["wrong"])
        question["choices"] = choices
        question["correct_idx"] = correct_idx
    elif question["type"] == "sort":
        choices,answers=shuffle_sort(question["choices"], question["answers"])
        question["choices"] = choices
        question["answers"] = answers
    return question


if __name__ == "__main__":
    if len(sys.argv) > 1:
        config = sys.argv[1]
    else:
        config = "pub_quizzes/2023-11-20.yaml"

    with open(config, 'r', encoding='utf8') as fp:
        quiz_config = yaml.safe_load(fp)

    # parse the quiz for templating
    quiz = {
        "date": quiz_config["date"],
        "place": quiz_config["place"],
        "blocks": [],
        "countdown_duration_minutes": quiz_config["countdown_duration_minutes"]
    }
    for t, topic in enumerate(quiz_config["topics"]):
        if t % quiz_config["topics_per_block"] == 0:
            quiz["blocks"].append([])
        parsed_questions = []
        for q, question in enumerate(topic["questions"]):
            parsed_questions.append(parse_question(topic, question, q))
        topic["questions"] = parsed_questions
        quiz["blocks"][-1].append(topic)

    # generate the web page from the template
    template = Environment(loader=FileSystemLoader("./slides")).get_template(quiz_config["template"])
    content = template.render(quiz)

    with open(quiz_config["output"], "w", encoding="utf-8") as fh:
        fh.write(content)
