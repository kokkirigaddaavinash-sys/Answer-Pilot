import os
from dotenv import load_dotenv


# Load variables from .env
load_dotenv()


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

UPLOAD_FOLDER = "uploads"

VECTORSTORE_FOLDER = "vectorstore"

GENERATED_IMAGES_FOLDER = "generated/images"

GENERATED_PDFS_FOLDER = "generated/pdfs"


# ============================================================
# RAG CONFIGURATION
# ============================================================

CHUNK_SIZE = 800

CHUNK_OVERLAP = 100

TOP_K_RESULTS = 5


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB

ALLOWED_EXTENSIONS = {
    "pdf"
}