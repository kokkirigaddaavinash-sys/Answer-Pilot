from google import genai


def generate_answer(
    gemini_client,
    question,
    context="",
    answer_type="Exam Answer",
    language="English",
    length="Medium"
):
    """
    Generate a clean, exam-ready answer using Gemini.
    """

    if gemini_client is None:
        raise RuntimeError("Gemini client is not configured.")

    question = str(question or "").strip()
    context = str(context or "").strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    # ---------------------------------------------------------
    # ANSWER LENGTH
    # ---------------------------------------------------------

    selected_length = str(length or "Medium").lower()

    if selected_length == "short":
        length_instruction = """
Keep the answer short and exam-ready.
Use approximately 3-5 important points.
Avoid unnecessary explanation.
"""

    elif selected_length == "long":
        length_instruction = """
Give a detailed answer suitable for a 10-mark question.
Use clear headings, subheadings, numbered points,
examples, explanations and a conclusion where appropriate.
"""

    else:
        length_instruction = """
Give a medium-length exam-ready answer.
Use a clear definition, important points,
examples where useful, and a short conclusion.
"""

    # ---------------------------------------------------------
    # ANSWER TYPE
    # ---------------------------------------------------------

    selected_type = str(answer_type or "Exam Answer").lower()

    if selected_type in [
        "simple",
        "simple answer",
        "2 marks"
    ]:
        type_instruction = """
Use very simple student-friendly language.
Explain difficult concepts in an easy way.
Focus only on the most important information.
"""

    elif selected_type in [
        "detailed",
        "detailed answer",
        "10 marks"
    ]:
        type_instruction = """
Give a detailed and well-structured explanation.
Use headings and subheadings wherever useful.
Provide enough explanation for a long-answer exam response.
"""

    elif selected_type in [
        "key points",
        "points"
    ]:
        type_instruction = """
Focus mainly on important points.
Use numbered points or bullet points.
Keep each point clear and easy to remember.
"""

    else:
        type_instruction = """
Write the answer in an exam-ready format.
Use headings, numbered points and examples.
"""

    # ---------------------------------------------------------
    # LANGUAGE
    # ---------------------------------------------------------

    selected_language = str(language or "English").lower()

    if selected_language == "telugu":
        language_instruction = """
Write the answer in Telugu.
Keep important technical terms in English where appropriate.
Use natural student-friendly Telugu.
"""

    elif selected_language in [
        "hinglish",
        "english + telugu",
        "english and telugu"
    ]:
        language_instruction = """
Use a natural combination of English and Telugu.
Keep important technical terminology in English.
"""

    else:
        language_instruction = """
Write the answer in clear and simple English.
"""

    # ---------------------------------------------------------
    # STUDY MATERIAL / CONTEXT
    # ---------------------------------------------------------

    if context:
        source_instruction = """
The study material below is the primary source.

Use the provided study material wherever relevant.
Preserve the terminology and concepts used in the material.

Do not mention:
- study material
- RAG
- ChromaDB
- embeddings
- vector databases
- retrieval
- prompts
- internal processing

Do not invent unsupported specific information.
"""

    else:
        source_instruction = """
No uploaded study material is available.

Answer using your general knowledge.

Do not mention this instruction.
"""

    # ---------------------------------------------------------
    # VISUAL / DIAGRAM INSTRUCTION
    # ---------------------------------------------------------

    diagram_instruction = """
Before writing the final answer, decide whether the question
naturally requires a visual element.

A visual element is required when the question asks for or
strongly benefits from things such as:

- labelled diagram
- diagram
- architecture
- block diagram
- flowchart
- workflow
- structure
- life cycle
- cycle
- system model
- process diagram
- schematic
- graph
- comparison table

If a visual is explicitly requested or genuinely useful,
include a section exactly titled:

Labelled Diagram

Under that heading, briefly describe the visual that should
be generated.

DO NOT create ASCII art.

DO NOT use text characters to imitate a diagram.

For the diagram description, mention:

1. Main objects or components.
2. Connections or arrows.
3. Required labels.
4. Logical arrangement.
5. Important visual details.

If no visual is required, do not create a fake
"Labelled Diagram" section.
"""

    # ---------------------------------------------------------
    # FINAL PROMPT
    # ---------------------------------------------------------

    prompt = f"""
You are Answer Pilot, an AI study assistant.

Your job is to create a high-quality answer that a college
student can easily understand, study, copy and write in an exam.

============================================================
STUDENT QUESTION
============================================================

{question}

============================================================
ANSWER TYPE
============================================================

{answer_type}

============================================================
LANGUAGE
============================================================

{language}

============================================================
ANSWER LENGTH
============================================================

{length}

============================================================
SOURCE INSTRUCTIONS
============================================================

{source_instruction}

============================================================
ANSWER STYLE
============================================================

{length_instruction}

{type_instruction}

{language_instruction}

============================================================
VISUAL / DIAGRAM INSTRUCTIONS
============================================================

{diagram_instruction}

============================================================
IMPORTANT OUTPUT RULES
============================================================

1. Answer the exact question asked.

2. Start with a clear and relevant title or heading.

3. Give a short introduction or definition when appropriate.

4. Use numbered points for explanations.

5. Use bullet points where they improve readability.

6. Use bold-style emphasis for important terms when useful.

7. Include examples when relevant.

8. For comparison questions, organize the answer clearly.

9. For advantages and disadvantages, separate both sections.

10. For processes, explain the steps in logical order.

11. For architecture or working questions, explain the
    components and their relationships clearly.

12. Never create ASCII diagrams.

13. Never create fake diagrams using symbols or characters.

14. Keep paragraphs short.

15. Avoid unnecessary repetition.

16. Do not say "According to the study material".

17. Do not say "As an AI".

18. Do not mention internal system processing.

19. Make the answer easy to copy.

20. Make the answer visually structured.

21. Do not put the answer inside a code block.

22. Do not add unnecessary meta commentary.

23. Keep headings clean and meaningful.

24. Do not use excessive Markdown formatting.

25. Do not return JSON.

26. Do not add notes to the developer or programmer.

============================================================
STUDY MATERIAL
============================================================

{context}

============================================================

Return ONLY the final student-friendly answer.
"""

    # ---------------------------------------------------------
    # GEMINI GENERATION
    # ---------------------------------------------------------

    print("Generating AI answer...")

    try:
        response = gemini_client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )
    except Exception as error:
        raise RuntimeError(
            f"Gemini generation failed: {error}"
        ) from error

    # ---------------------------------------------------------
    # EXTRACT ANSWER
    # ---------------------------------------------------------

    answer = getattr(
        response,
        "text",
        ""
    )

    if not answer:
        raise RuntimeError(
            "Gemini returned an empty answer."
        )

    answer = str(answer).strip()

    # ---------------------------------------------------------
    # CLEAN UNWANTED CODE FENCES
    # ---------------------------------------------------------

    if answer.startswith("```"):
        lines = answer.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        answer = "\n".join(lines).strip()

    # ---------------------------------------------------------
    # FINAL CLEANUP
    # ---------------------------------------------------------

    answer = (
        answer
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    while "\n\n\n" in answer:
        answer = answer.replace(
            "\n\n\n",
            "\n\n"
        )

    if not answer:
        raise RuntimeError(
            "Gemini returned an empty answer after cleanup."
        )

    return answer