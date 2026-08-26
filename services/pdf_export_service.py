from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import mm
import os
import re


def escape_pdf_text(text):

    if text is None:
        return ""

    text = str(text)

    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")

    return text


def create_answer_pdf(
    output_path,
    questions,
    title="Answer Pilot - AI Study Notes"
):

    if not questions:
        raise ValueError("No questions available.")

    output_folder = os.path.dirname(output_path)

    if output_folder:
        os.makedirs(
            output_folder,
            exist_ok=True
        )

    document = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "AnswerPilotTitle",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#5427A8"),
        spaceAfter=18
    )

    question_style = ParagraphStyle(
        "AnswerPilotQuestion",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#5427A8"),
        spaceBefore=8,
        spaceAfter=10
    )

    heading_style = ParagraphStyle(
        "AnswerPilotHeading",
        parent=styles["Heading3"],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#333333"),
        spaceBefore=8,
        spaceAfter=5
    )

    body_style = ParagraphStyle(
        "AnswerPilotBody",
        parent=styles["BodyText"],
        fontSize=10.5,
        leading=16,
        textColor=colors.HexColor("#222222"),
        spaceAfter=7
    )

    story = []

    story.append(
        Paragraph(
            escape_pdf_text(title),
            title_style
        )
    )

    for index, item in enumerate(questions, start=1):

        if isinstance(item, dict):

            question = str(
                item.get("question", "")
            ).strip()

            answer = str(
                item.get("answer", "")
            ).strip()

        else:

            question = f"Question {index}"

            answer = str(
                item or ""
            ).strip()

        story.append(
            Paragraph(
                f"Q{index}. {escape_pdf_text(question)}",
                question_style
            )
        )

        if not answer:

            story.append(
                Paragraph(
                    "No answer generated.",
                    body_style
                )
            )

        else:

            lines = answer.splitlines()

            for line in lines:

                line = line.strip()

                if not line:

                    story.append(
                        Spacer(
                            1,
                            3 * mm
                        )
                    )

                    continue

                if line.startswith("#"):

                    clean_heading = re.sub(
                        r"^#+\s*",
                        "",
                        line
                    )

                    story.append(
                        Paragraph(
                            escape_pdf_text(
                                clean_heading
                            ),
                            heading_style
                        )
                    )

                elif re.match(
                    r"^(\d+)[.)]\s+",
                    line
                ):

                    story.append(
                        Paragraph(
                            escape_pdf_text(line),
                            body_style
                        )
                    )

                elif line.startswith(
                    ("-", "*", "•")
                ):

                    bullet = re.sub(
                        r"^[-*•]\s*",
                        "",
                        line
                    )

                    story.append(
                        Paragraph(
                            "• " +
                            escape_pdf_text(
                                bullet
                            ),
                            body_style
                        )
                    )

                else:

                    story.append(
                        Paragraph(
                            escape_pdf_text(line),
                            body_style
                        )
                    )

        if index < len(questions):

            story.append(
                PageBreak()
            )

    document.build(story)

    return output_path


def create_study_pdf(
    output_path,
    questions
):

    return create_answer_pdf(
        output_path,
        questions,
        "Answer Pilot - AI Study Notes"
    )