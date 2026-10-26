import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Check your .env file.")


def _extract_pdf_text(pdf_bytes: bytes, filename: str) -> str:
    """Extract text from an uploaded PDF using PyPDFLoader."""
    safe_name = Path(filename).name
    temp_path = BASE_DIR / f".tmp_{safe_name}"

    try:
        temp_path.write_bytes(pdf_bytes)
        documents = PyPDFLoader(str(temp_path)).load()

        return "\n\n".join(
            doc.page_content.strip()
            for doc in documents
            if doc.page_content and doc.page_content.strip()
        )
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except Exception:
            pass


REPORT_PROMPT = """
You are MediOrb, an educational medical-information assistant.

Analyze only the medical report text provided below.

Safety rules:
- Do not diagnose the patient.
- Do not claim that a result proves a disease.
- Do not prescribe medicines or tell the user to start/stop medication.
- Do not invent values, reference ranges, symptoms, diagnoses, or patient details.
- If a value or reference range is missing, say it is not available.
- Preserve the report's units and reference ranges when provided.
- If the report itself labels something high, low, positive, negative, abnormal,
  or critical, explain that label without changing it.
- Clearly separate what the report says from general educational explanation.
- If the report contains urgent/critical wording, advise prompt contact with
  an appropriate healthcare professional.

Return Markdown using exactly these sections:

## Report overview
Briefly describe the type of report and the information present.

## Key results
Use a table when useful. Include test, result, unit, reference range, and
status only when those details are actually available.

## Easy explanation
Explain the important findings in simple language without diagnosing.

## What to discuss with a healthcare professional
Give useful questions the user could ask their clinician.

## Important note
State that the explanation is educational and the report should be interpreted
by a qualified healthcare professional together with symptoms and medical history.

REPORT TEXT:
{report_text}
"""


def _get_llm():
    return ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0.1,
        max_tokens=1200,
        api_key=GROQ_API_KEY,
    )


def analyze_medical_report(pdf_bytes: bytes, filename: str = "medical_report.pdf") -> str:
    """Extract a PDF report and generate an educational explanation with Groq."""
    if not pdf_bytes:
        raise ValueError("The uploaded PDF is empty.")

    report_text = _extract_pdf_text(pdf_bytes, filename)

    if not report_text.strip():
        raise ValueError(
            "No readable text was found in this PDF. "
            "A scanned/image-only PDF will need OCR support."
        )

    # Keep the request reasonably sized.
    report_text = report_text[:30000]

    response = _get_llm().invoke(
        REPORT_PROMPT.format(report_text=report_text)
    )

    return response.content
