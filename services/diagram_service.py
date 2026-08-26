import os
import re


def question_needs_diagram(question, answer):
    """
    Detect whether the question/answer requires a visual diagram.
    """

    text = (
        str(question or "") + " " +
        str(answer or "")
    ).lower()

    diagram_keywords = [
        "diagram",
        "labelled diagram",
        "labeled diagram",
        "draw",
        "illustrate",
        "architecture",
        "flowchart",
        "block diagram",
        "structure",
        "cycle",
        "process",
        "working",
        "model",
        "framework",
        "workflow",
        "schematic"
    ]

    return any(
        keyword in text
        for keyword in diagram_keywords
    )


def extract_diagram_request(question, answer):
    """
    Create a clean description of the visual that should be generated.
    """

    question = str(question or "").strip()
    answer = str(answer or "").strip()

    return f"""
Create an educational diagram for the following question.

QUESTION:
{question}

ANSWER:
{answer}

DIAGRAM REQUIREMENTS:

1. Make the diagram directly relevant to the question.
2. Use clear labels.
3. Show the important components mentioned in the answer.
4. Show arrows when there is a flow or process.
5. Use a clean educational textbook style.
6. Avoid unnecessary decoration.
7. Make every label readable.
8. Do not add unrelated information.
9. The final diagram must be suitable for college exam notes.
10. If the question asks for a labelled diagram, make the
    labels explicit and easy to identify.
"""


def clean_diagram_text(text):
    """
    Remove accidental markdown/code formatting from diagram text.
    """

    if not text:
        return ""

    text = str(text)

    text = text.replace("```text", "")
    text = text.replace("```", "")

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


def save_diagram_metadata(
    output_folder,
    question,
    diagram_description,
    filename="diagram.txt"
):
    """
    Save diagram information for later image generation/export.
    """

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    file_path = os.path.join(
        output_folder,
        filename
    )

    content = (
        "QUESTION\n"
        "========\n\n"
        f"{question}\n\n"
        "DIAGRAM DESCRIPTION\n"
        "===================\n\n"
        f"{diagram_description}\n"
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(content)

    return file_path