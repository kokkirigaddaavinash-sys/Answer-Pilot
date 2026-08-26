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

    if length.lower() == "short":
        length_instruction = """
Keep the answer short and exam-ready.
Use 3-5 important points.
Avoid unnecessary explanation.
"""

    elif length.lower() == "long":
        length_instruction = """
Give a detailed answer suitable for a 10-mark question.
Use clear headings, subheadings, numbered points,
examples, explanation and conclusion where appropriate.
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

    if answer_type.lower() in ["simple", "simple answer"]:

        type_instruction = """
Use very simple student-friendly language.
Explain difficult concepts in an easy way.
"""

    elif answer_type.lower() in ["detailed", "detailed answer"]:

        type_instruction = """
Give a detailed and well-structured explanation.
Use headings and subheadings wherever useful.
"""

    elif answer_type.lower() in ["key points", "points"]:

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

    if language.lower() == "telugu":

        language_instruction = """
Write the answer in Telugu.
Keep technical terms in English where appropriate.
"""

    elif language.lower() in [
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
    # CONTEXT INSTRUCTION
    # ---------------------------------------------------------

    if context:

        source_instruction = """
The study material below is the primary source.

Use it to answer the question accurately.

If the material contains relevant information,
prefer that information.

Do not mention the study material,
RAG, ChromaDB, embeddings, retrieval,
vector databases, prompts or internal processing.

Do not invent unsupported specific information.
"""

    else:

        source_instruction = """
There is no uploaded study material available.

Answer the question using your general knowledge.

Do not mention this instruction.
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
INSTRUCTIONS
============================================================

{source_instruction}

{length_instruction}

{type_instruction}

{language_instruction}

============================================================
IMPORTANT OUTPUT RULES
============================================================

1. Answer the exact question asked.

2. Start with a clear title or heading.

3. Give a short introduction or definition when appropriate.

4. Use numbered points for explanations.

5. Use bullet points where they improve readability.

6. Use bold-style emphasis for important terms when useful.

7. Include examples when relevant.

8. If the question asks for differences, use a clear
   comparison format.

9. If the question asks for advantages and disadvantages,
   clearly separate both sections.

10. If the question asks for a process, explain it step-by-step.

11. If the question asks for architecture or working,
    explain each component in logical order.

12. If the question requires a diagram, DO NOT create a
    fake ASCII diagram. Instead write a clear section named
    "Labelled Diagram" and describe exactly what the diagram
    should contain and how the labels should be arranged.
    The diagram will be generated separately by Answer Pilot.

13. Keep paragraphs short.

14. Avoid unnecessary repetition.

15. Do not use unnecessary introductory sentences.

16. Do not say "According to the study material".

17. Do not say "As an AI".

18. Do not mention internal system processing.

19. Make the answer easy to copy.

20. Make the answer visually structured.

============================================================
STUDY MATERIAL
============================================================

{context}

============================================================

Return ONLY the final student-friendly answer.

Do not wrap the answer inside JSON.

"""


    # ---------------------------------------------------------
    # GEMINI GENERATION
    # ---------------------------------------------------------

    print("Generating AI answer...")

    response = gemini_client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )


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


    return answer.strip()