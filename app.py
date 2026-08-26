from flask import Flask, render_template, request, jsonify
from pypdf import PdfReader

import os
import uuid

import chromadb
from sentence_transformers import SentenceTransformer
from google import genai

import config


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = getattr(
    config,
    "MAX_CONTENT_LENGTH",
    50 * 1024 * 1024
)


# ============================================================
# UPLOAD CONFIGURATION
# ============================================================

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ============================================================
# CHROMADB
# ============================================================

os.makedirs("vectorstore", exist_ok=True)

chroma_client = chromadb.PersistentClient(
    path="vectorstore"
)

collection = chroma_client.get_or_create_collection(
    name="answerpilot_documents"
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

print()
print("============================================================")
print("Loading embedding model...")
print("============================================================")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding model loaded successfully.")
print()


# ============================================================
# GEMINI AI
# ============================================================

GEMINI_API_KEY = getattr(
    config,
    "GEMINI_API_KEY",
    None
)

if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


gemini_client = None


if GEMINI_API_KEY:

    try:

        gemini_client = genai.Client(
            api_key=GEMINI_API_KEY
        )

        print("Gemini AI client ready.")

    except Exception as error:

        print("Gemini client initialization error:")
        print(error)

else:

    print("WARNING: GEMINI_API_KEY was not found.")


print()


# ============================================================
# TEXT CHUNKING
# ============================================================

def split_text_into_chunks(
    text,
    chunk_size=800,
    overlap=100
):

    chunks = []

    if not text:
        return chunks

    start = 0

    step = chunk_size - overlap

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += step

    return chunks


# ============================================================
# ANSWER LENGTH
# ============================================================

def get_length_instruction(
    answer_type,
    length
):

    answer_type_text = str(
        answer_type or ""
    ).lower()

    length_text = str(
        length or "medium"
    ).lower()


    # --------------------------------------------------------
    # 2 MARK
    # --------------------------------------------------------

    if "2" in answer_type_text:

        return """
Give a very short exam-ready answer.

Use:
- A clear definition
- 2 to 4 important points
- A small example only when useful

Avoid unnecessary explanation.
"""


    # --------------------------------------------------------
    # 5 MARK
    # --------------------------------------------------------

    if "5" in answer_type_text:

        return """
Give a medium-length exam-ready answer.

Use:
- Definition / Introduction
- Important points
- Suitable example
- Short conclusion when useful

Prefer approximately 5 to 8 meaningful points.

Keep the explanation clear and easy to write in an examination.
"""


    # --------------------------------------------------------
    # 10 MARK
    # --------------------------------------------------------

    if "10" in answer_type_text:

        return """
Give a detailed 10-mark exam-ready answer.

Use:
- Definition / Introduction
- Main explanation
- Clear headings
- Numbered points
- Important concepts
- Suitable examples
- Advantages / disadvantages when relevant
- Conclusion

Give enough detail for a 10-mark college examination answer.
"""


    # --------------------------------------------------------
    # LENGTH OPTION
    # --------------------------------------------------------

    if length_text == "short":

        return """
Keep the answer short and focused.

Use only the most important information.
"""


    if length_text == "long":

        return """
Give a detailed answer with sufficient explanation,
examples and important points.

Do not repeat information.
"""


    return """
Give a balanced medium-length answer.

Keep it detailed enough for understanding and examination writing,
but avoid unnecessary information.
"""


# ============================================================
# HOME ROUTE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# PDF UPLOAD
# ============================================================

@app.route(
    "/upload",
    methods=["POST"]
)
def upload_pdf():

    if "file" not in request.files:

        return jsonify({
            "success": False,
            "message": "No file uploaded."
        }), 400


    file = request.files["file"]


    if file.filename == "":

        return jsonify({
            "success": False,
            "message": "Please select a PDF."
        }), 400


    filename = os.path.basename(
        file.filename
    )


    if not filename.lower().endswith(".pdf"):

        return jsonify({
            "success": False,
            "message": "Only PDF files are allowed."
        }), 400


    unique_filename = (
        str(uuid.uuid4())[:8]
        + "_"
        + filename
    )


    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        unique_filename
    )


    try:

        file.save(file_path)


        # ====================================================
        # READ PDF
        # ====================================================

        reader = PdfReader(
            file_path
        )

        text_parts = []


        for page in reader.pages:

            try:

                page_text = page.extract_text()

            except Exception:

                page_text = None


            if page_text:

                text_parts.append(
                    page_text
                )


        text = "\n".join(
            text_parts
        ).strip()


        if not text:

            return jsonify({

                "success": False,

                "message":
                    "PDF uploaded, but no readable text was found."

            }), 400


        # ====================================================
        # CREATE CHUNKS
        # ====================================================

        chunks = split_text_into_chunks(
            text
        )


        if not chunks:

            return jsonify({

                "success": False,

                "message":
                    "Could not create readable text chunks."

            }), 400


        print()
        print("============================================================")
        print("PDF PROCESSING")
        print("============================================================")

        print(
            "File:",
            filename
        )

        print(
            "Characters:",
            len(text)
        )

        print(
            "Total chunks:",
            len(chunks)
        )


        # ====================================================
        # CREATE EMBEDDINGS
        # ====================================================

        print()
        print("Creating embeddings...")


        embeddings = embedding_model.encode(
            chunks,
            show_progress_bar=False
        ).tolist()


        print(
            "Embeddings created successfully."
        )


        # ====================================================
        # CREATE IDS
        # ====================================================

        ids = [

            f"{uuid.uuid4()}_{index}"

            for index in range(
                len(chunks)
            )

        ]


        # ====================================================
        # STORE IN CHROMADB
        # ====================================================

        print()
        print("Storing chunks in ChromaDB...")


        collection.add(

            ids=ids,

            documents=chunks,

            embeddings=embeddings,

            metadatas=[

                {
                    "filename": filename,
                    "chunk_index": index
                }

                for index in range(
                    len(chunks)
                )

            ]

        )


        print(
            "Chunks stored successfully."
        )

        print(
            "============================================================"
        )

        print(
            "PDF PROCESSING COMPLETE"
        )

        print(
            "============================================================"
        )

        print()


        return jsonify({

            "success": True,

            "message":
                "PDF uploaded and added to knowledge base.",

            "filename":
                filename,

            "characters":
                len(text),

            "chunks":
                len(chunks)

        })


    except Exception as error:

        print()
        print("PDF processing error:")
        print(error)
        print()


        return jsonify({

            "success": False,

            "message":
                f"Could not process PDF: {str(error)}"

        }), 500


# ============================================================
# ASK QUESTION
# ============================================================

@app.route(
    "/ask",
    methods=["POST"]
)
def ask_question():

    # --------------------------------------------------------
    # CHECK GEMINI
    # --------------------------------------------------------

    if gemini_client is None:

        return jsonify({

            "success": False,

            "message":
                "Gemini API key is not configured. "
                "Check your config.py file."

        }), 500


    # --------------------------------------------------------
    # GET REQUEST DATA
    # --------------------------------------------------------

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "message":
                "Invalid request data."

        }), 400


    # --------------------------------------------------------
    # QUESTION
    # --------------------------------------------------------

    question = str(
        data.get(
            "question",
            ""
        )
    ).strip()


    if not question:

        return jsonify({

            "success": False,

            "message":
                "Please enter a question."

        }), 400


    # --------------------------------------------------------
    # ANSWER TYPE
    # --------------------------------------------------------

    answer_type = str(
        data.get(
            "answer_type",
            "5 Marks"
        )
    ).strip()


    # --------------------------------------------------------
    # LANGUAGE
    # --------------------------------------------------------

    language = str(
        data.get(
            "language",
            "English"
        )
    ).strip()


    # --------------------------------------------------------
    # LENGTH
    # --------------------------------------------------------

    length = str(
        data.get(
            "length",
            "medium"
        )
    ).strip()


    print()
    print("============================================================")
    print("QUESTION RETRIEVAL")
    print("============================================================")

    print(
        "Question:",
        question
    )

    print(
        "Answer Type:",
        answer_type
    )

    print(
        "Language:",
        language
    )

    print(
        "Length:",
        length
    )


    try:

        # ====================================================
        # CREATE QUESTION EMBEDDING
        # ====================================================

        question_embedding = embedding_model.encode(
            question
        ).tolist()


        # ====================================================
        # SEARCH CHROMADB
        # ====================================================

        collection_count = collection.count()


        if collection_count > 0:

            number_of_results = min(
                5,
                collection_count
            )


            results = collection.query(

                query_embeddings=[
                    question_embedding
                ],

                n_results=number_of_results

            )

        else:

            results = {
                "documents": [[]],
                "metadatas": [[]]
            }


        # ====================================================
        # GET DOCUMENTS
        # ====================================================

        documents = results.get(
            "documents",
            [[]]
        )


        if documents:

            documents = documents[0]

        else:

            documents = []


        # ====================================================
        # GET METADATA
        # ====================================================

        metadatas = results.get(
            "metadatas",
            [[]]
        )


        if metadatas:

            metadatas = metadatas[0]

        else:

            metadatas = []


        # ====================================================
        # BUILD CONTEXT
        # ====================================================

        context_parts = []


        for document in documents:

            if document:

                context_parts.append(
                    document.strip()
                )


        context = "\n\n".join(
            context_parts
        )


        # Keep prompt size reasonable

        context = context[:14000]


        print(
            "Retrieved chunks:",
            len(documents)
        )


        # ====================================================
        # LENGTH INSTRUCTION
        # ====================================================

        length_instruction = (
            get_length_instruction(
                answer_type,
                length
            )
        )


        # ====================================================
        # ANSWER PROMPT
        # ====================================================

        prompt = f"""

You are Answer Pilot, an AI study assistant for college students.

Your job is to create a clean, accurate, understandable,
exam-ready answer for the student's exact question.

Use the retrieved study material as the primary source.

IMPORTANT RULES:

1. Answer the student's exact question.

2. Use the retrieved study material as the primary source.

3. Do not mention RAG.

4. Do not mention ChromaDB.

5. Do not mention embeddings.

6. Do not mention prompts.

7. Do not mention internal processing.

8. Do not say "I am an AI".

9. Do not start with:
"According to the study material".

10. Do not repeat the same information.

11. Do not invent unsupported specific facts.

12. Use simple student-friendly language.

13. Make the answer easy to understand.

14. Make the answer easy to copy into notes.

15. Make the answer suitable for a college examination.

16. Use clear headings.

17. Use numbered points when appropriate.

18. Use bullet points when appropriate.

19. Keep paragraphs short.

20. Highlight important terms using **bold**.

21. Give suitable examples when supported by the study material.

22. If the question asks for differences, clearly compare the concepts.

23. If the question asks for steps, give the steps in numbered order.

24. If the question asks for advantages and disadvantages,
separate them clearly.

25. If the question asks for a definition,
start with a clear definition.

26. If the question asks for an explanation,
give the explanation in a logical order.

27. Do not use emojis.

28. Do not use unnecessary decorative symbols.

29. Do not use Markdown code blocks.

30. Do not create ASCII diagrams.

31. Never create diagrams using characters such as:
+---+
| |
--> 
<--
[ ]
unless the student specifically asks for a text diagram.

32. If the question asks for a diagram,
write a clear section titled:
"Labelled Diagram"
and explain what should be shown,
but do not create an ASCII diagram.

33. Do not put the complete answer inside quotation marks.

34. Do not add comments about how you generated the answer.

35. Return only the final study answer.

============================================================
LANGUAGE
============================================================

{language}

============================================================
ANSWER TYPE
============================================================

{answer_type}

============================================================
ANSWER LENGTH
============================================================

{length}

============================================================
LENGTH INSTRUCTIONS
============================================================

{length_instruction}

============================================================
STUDY MATERIAL
============================================================

{context}

============================================================
STUDENT QUESTION
============================================================

{question}

============================================================

OUTPUT STRUCTURE

Use the following structure when relevant:

Title

Definition / Introduction

1. Important Point

Short and clear explanation.

2. Important Point

Short and clear explanation.

Example

Give a suitable example when supported by the material.

Labelled Diagram

Only include this section when the question actually requires
a diagram.

Describe the required diagram clearly using normal text.
Do not create an ASCII diagram.

Conclusion

Give a short conclusion when appropriate.

Do not force sections that are not relevant.

The final answer must look like a well-prepared college student's
exam answer, not like a conversation with an AI.

Return ONLY the final answer.

"""


        # ====================================================
        # GEMINI GENERATION
        # ====================================================

        print()
        print("Generating AI answer...")


        response = gemini_client.models.generate_content(

            model="gemini-3.6-flash",

            contents=prompt

        )


        # ====================================================
        # GET ANSWER
        # ====================================================

        answer = getattr(
            response,
            "text",
            ""
        )


        if not answer or not answer.strip():

            return jsonify({

                "success": False,

                "message":
                    "AI returned an empty answer."

            }), 500


        answer = answer.strip()


        # ====================================================
        # REMOVE UNWANTED CODE FENCES
        # ====================================================

        if answer.startswith("```"):

            lines = answer.splitlines()


            if len(lines) >= 2:

                if lines[0].strip().startswith("```"):

                    lines = lines[1:]


                if lines and lines[-1].strip() == "```":

                    lines = lines[:-1]


                answer = "\n".join(
                    lines
                ).strip()


        # ====================================================
        # LOG SUCCESS
        # ====================================================

        print()
        print("AI answer generated successfully.")

        print(
            "============================================================"
        )

        print(
            "ANSWER GENERATION COMPLETE"
        )

        print(
            "============================================================"
        )

        print()


        # ====================================================
        # RETURN RESPONSE
        # ====================================================

        return jsonify({

            "success": True,

            "question":
                question,

            "answer_type":
                answer_type,

            "language":
                language,

            "length":
                length,

            "answer":
                answer,

            "sources":
                metadatas

        })


    except Exception as error:

        print()
        print("============================================================")
        print("ANSWER GENERATION ERROR")
        print("============================================================")
        print(error)
        print()


        return jsonify({

            "success": False,

            "message":
                f"Could not generate answer: {str(error)}"

        }), 500


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    print()
    print("============================================================")
    print("ANSWER PILOT")
    print("============================================================")
    print("Server: http://127.0.0.1:5000")
    print("============================================================")
    print()


    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )