import os
import re
from pathlib import Path


# ============================================================
# DIAGRAM DETECTION
# ============================================================

def question_needs_diagram(question, answer=""):
    """
    Detect whether the question or answer requires a visual.
    """

    text = (
        str(question or "") +
        " " +
        str(answer or "")
    ).lower()

    diagram_keywords = [
        "diagram",
        "labelled diagram",
        "labeled diagram",
        "draw",
        "illustrate",
        "illustration",
        "architecture",
        "flowchart",
        "flow chart",
        "block diagram",
        "structure",
        "cycle",
        "life cycle",
        "process",
        "working",
        "working principle",
        "model",
        "framework",
        "workflow",
        "schematic",
        "layout",
        "components",
        "neat diagram",
        "with diagram"
    ]

    return any(
        keyword in text
        for keyword in diagram_keywords
    )


# ============================================================
# DIAGRAM REQUEST EXTRACTION
# ============================================================

def extract_diagram_request(question, answer=""):
    """
    Create a clean image-generation instruction from
    the question and answer.
    """

    question = str(question or "").strip()
    answer = str(answer or "").strip()

    prompt = f"""
Create a high-quality educational diagram for a college
student's handwritten study notes.

QUESTION:
{question}

ANSWER:
{answer}

IMPORTANT REQUIREMENTS:

1. Create ONLY a meaningful educational diagram.
2. Make the diagram directly related to the question.
3. Use clear, accurate and readable labels.
4. Include the important components mentioned in the answer.
5. Show arrows when a process, flow or relationship is involved.
6. Use a clean textbook / academic illustration style.
7. Use a white or very light background.
8. Use clean thin outlines.
9. Keep the composition simple and easy to understand.
10. Make labels large enough to read on an A4 study-notes page.
11. Do not include unnecessary decorative objects.
12. Do not add unrelated information.
13. Do not create a poster.
14. Do not create a photograph.
15. Do not create 3D artwork.
16. Do not create ASCII art.
17. Do not place a huge title inside the image.
18. Do not add fake or random labels.
19. Use correct scientific / technical terminology.
20. Make it suitable for college examination notes.

VISUAL STYLE:

- clean educational textbook diagram
- hand-drawn study-note friendly appearance
- neat line drawing
- readable labels
- simple arrows
- balanced spacing
- white background
- academic and exam-oriented
"""

    return prompt.strip()


# ============================================================
# CLEAN DIAGRAM TEXT
# ============================================================

def clean_diagram_text(text):
    """
    Remove accidental Markdown/code formatting.
    """

    if not text:
        return ""

    text = str(text)

    text = text.replace(
        "```text",
        ""
    )

    text = text.replace(
        "```",
        ""
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ============================================================
# GENERATE DIAGRAM IMAGE
# ============================================================

def generate_diagram_image(
    gemini_client,
    question,
    answer="",
    output_folder="generated/images",
    filename="diagram.png"
):
    """
    Generate a real educational diagram image using Gemini
    image generation and save it as a PNG file.

    Returns:
        Full path of generated image.
    """

    if gemini_client is None:
        raise RuntimeError(
            "Gemini client is not configured."
        )

    question = str(question or "").strip()
    answer = str(answer or "").strip()

    if not question:
        raise ValueError(
            "Question cannot be empty."
        )

    output_folder = Path(
        output_folder
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = str(
        filename or "diagram.png"
    )

    if not filename.lower().endswith(".png"):
        filename += ".png"

    output_path = (
        output_folder /
        filename
    )

    prompt = extract_diagram_request(
        question,
        answer
    )

    print("Generating educational diagram...")

    try:

        response = gemini_client.models.generate_content(
            model="gemini-3.1-flash-image",
            contents=[prompt]
        )

    except Exception as error:

        raise RuntimeError(
            f"Diagram generation failed: {error}"
        ) from error

    # --------------------------------------------------------
    # FIND IMAGE IN RESPONSE
    # --------------------------------------------------------

    image_saved = False

    try:

        parts = getattr(
            response,
            "parts",
            None
        )

        if parts:

            for part in parts:

                inline_data = getattr(
                    part,
                    "inline_data",
                    None
                )

                if inline_data is not None:

                    try:

                        image = part.as_image()

                        image.save(
                            output_path
                        )

                        image_saved = True

                        break

                    except Exception:
                        pass

    except Exception:
        pass

    # --------------------------------------------------------
    # ALTERNATIVE RESPONSE STRUCTURE
    # --------------------------------------------------------

    if not image_saved:

        try:

            candidates = getattr(
                response,
                "candidates",
                []
            )

            for candidate in candidates:

                content = getattr(
                    candidate,
                    "content",
                    None
                )

                if content is None:
                    continue

                parts = getattr(
                    content,
                    "parts",
                    []
                )

                for part in parts:

                    inline_data = getattr(
                        part,
                        "inline_data",
                        None
                    )

                    if inline_data is None:
                        continue

                    try:

                        image = part.as_image()

                        image.save(
                            output_path
                        )

                        image_saved = True

                        break

                    except Exception:
                        pass

                if image_saved:
                    break

        except Exception:
            pass

    # --------------------------------------------------------
    # VERIFY IMAGE
    # --------------------------------------------------------

    if not image_saved:

        raise RuntimeError(
            "Gemini did not return a usable diagram image."
        )

    if not output_path.exists():

        raise RuntimeError(
            "Diagram file was not created."
        )

    if output_path.stat().st_size == 0:

        raise RuntimeError(
            "Generated diagram file is empty."
        )

    print(
        f"Diagram saved: {output_path}"
    )

    return str(
        output_path
    )


# ============================================================
# SAVE DIAGRAM METADATA
# ============================================================

def save_diagram_metadata(
    output_folder,
    question,
    diagram_description,
    filename="diagram.txt"
):
    """
    Save diagram information for debugging/reference.
    """

    output_folder = Path(
        output_folder
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = (
        output_folder /
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

    return str(
        file_path
    )


# ============================================================
# GENERATE DIAGRAM + SAVE METADATA
# ============================================================

def create_diagram(
    gemini_client,
    question,
    answer="",
    output_folder="generated/images",
    filename="diagram.png"
):
    """
    Complete diagram pipeline.

    1. Check whether diagram is needed.
    2. Create diagram description.
    3. Generate real PNG image.
    4. Save metadata.
    5. Return result information.
    """

    needs_diagram = question_needs_diagram(
        question,
        answer
    )

    if not needs_diagram:

        return {
            "required": False,
            "image_path": None,
            "metadata_path": None,
            "description": ""
        }

    description = extract_diagram_request(
        question,
        answer
    )

    description = clean_diagram_text(
        description
    )

    image_path = generate_diagram_image(
        gemini_client=gemini_client,
        question=question,
        answer=answer,
        output_folder=output_folder,
        filename=filename
    )

    metadata_path = save_diagram_metadata(
        output_folder=output_folder,
        question=question,
        diagram_description=description
    )

    return {
        "required": True,
        "image_path": image_path,
        "metadata_path": metadata_path,
        "description": description
    }