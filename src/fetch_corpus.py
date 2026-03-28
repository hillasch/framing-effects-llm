# src/fetch_corpus.py
#
# Downloads 15 curated human psychology papers (cognitive biases, memory & recall,
# emotion & cognition) from verified free PDF URLs and saves them to data/corpus.json.
# If a URL fails, falls back to local PDFs in data/pdfs/
#
# Usage:
#   python src/fetch_corpus.py

import json
import time
import requests
from pathlib import Path
from pypdf import PdfReader
from io import BytesIO

# ── Output path ───────────────────────────────────────────────────────────────
OUTPUT_PATH = Path("data/corpus.json")

# ── Local PDF fallback mapping ────────────────────────────────────────────────
# Maps paper ID → actual filename in data/pdfs/
LOCAL_PDFS = {
    "loftus_klemfuss_2023":    "Misinformation – past, present, and future.pdf",
    "roediger_mcdermott_1995": "RoedigerMcDermott 1996 DRM False.pdf",
    "schacter_1999":           "Schacter-The20720Sins20of20Memory-AP-1999.pdf",
    "gross_1998":              "Antecedent- and Response-Focused Emotion Regulation.pdf",
    "gross_2002":              "Psychophysiology - 2003 - Gross - Emotion regulation  Affective  cognitive  and social consequences.pdf",
    "gross_john_2003":         "Gross-James-Individual-Differences-in-Two-Emotion-Regulation-Processes....pdf",
    "aldao_2010":              "Aldao Nolen-Hoeksema 2010 emotion regulation strategies psychopathology.pdf",
    "baumeister_2007":         "baumeister-et-al-2007-how-emotion-shapes-behavior-feedback-anticipation-and-reflection-rather-than-direct-causation.pdf",
    "lerner_2015":             "emotion-and-decision-making.pdf",
    "nolen_hoeksema_2008":     "nolen-hoeksema-et-al-2008-rethinking-rumination.pdf",
}
LOCAL_PDF_DIR = Path("data/pdfs")
# ─────────────────────────────────────────────────────────────────────────────

# ── Curated corpus ────────────────────────────────────────────────────────────
PAPERS = [

    # ── COGNITIVE BIASES ──────────────────────────────────────────────────────
    {
        "id": "tversky_kahneman_1981",
        "title": "The Framing of Decisions and the Psychology of Choice",
        "authors": ["Amos Tversky", "Daniel Kahneman"],
        "year": 1981,
        "topic": "cognitive_bias",
        "pdf_url": "https://sites.stat.columbia.edu/gelman/surveys.course/TverskyKahneman1981.pdf",
    },
    {
        "id": "kahneman_tversky_1979",
        "title": "Prospect Theory: An Analysis of Decision under Risk",
        "authors": ["Daniel Kahneman", "Amos Tversky"],
        "year": 1979,
        "topic": "cognitive_bias",
        "pdf_url": "https://web.mit.edu/curhan/www/docs/Articles/15341_Readings/Behavioral_Decision_Theory/Kahneman_Tversky_1979_Prospect_theory.pdf",
    },
    {
        "id": "tversky_kahneman_1974",
        "title": "Judgment under Uncertainty: Heuristics and Biases",
        "authors": ["Amos Tversky", "Daniel Kahneman"],
        "year": 1974,
        "topic": "cognitive_bias",
        "pdf_url": "https://www.cs.tufts.edu/comp/150AIH/pdf/TverskyKa74.pdf",
    },
    {
        "id": "kahneman_2003",
        "title": "Maps of Bounded Rationality: Psychology for Behavioral Economics",
        "authors": ["Daniel Kahneman"],
        "year": 2003,
        "topic": "cognitive_bias",
        "pdf_url": "https://houdekpetr.cz/!data/public_html/papers/Kahnem%202003.pdf",
    },

    # ── MEMORY & RECALL ───────────────────────────────────────────────────────
    {
        "id": "loftus_2005",
        "title": "Planting Misinformation in the Human Mind: A 30-Year Investigation of the Malleability of Memory",
        "authors": ["Elizabeth F. Loftus"],
        "year": 2005,
        "topic": "memory",
        "pdf_url": "https://learnmem.cshlp.org/content/12/4/361.full.pdf",
    },
    {
        "id": "loftus_klemfuss_2023",
        "title": "Misinformation - Past, Present, and Future",
        "authors": ["Elizabeth F. Loftus", "J. Zoe Klemfuss"],
        "year": 2023,
        "topic": "memory",
        "pdf_url": "https://escholarship.org/content/qt53c7773f/qt53c7773f.pdf",
    },
    {
        "id": "roediger_mcdermott_1995",
        "title": "Creating False Memories: Remembering Words Not Presented in Lists",
        "authors": ["Henry L. Roediger", "Kathleen B. McDermott"],
        "year": 1995,
        "topic": "memory",
        "pdf_url": "https://websites.umich.edu/~bcaplan/roediger.pdf",
    },
    {
        "id": "schacter_1999",
        "title": "The Seven Sins of Memory: Insights from Psychology and Cognitive Neuroscience",
        "authors": ["Daniel L. Schacter"],
        "year": 1999,
        "topic": "memory",
        "pdf_url": "https://scholar.harvard.edu/files/schacterlab/files/schacter_american_psychologist_1999.pdf",
    },

    # ── EMOTION & COGNITION ───────────────────────────────────────────────────
    {
        "id": "gross_1998",
        "title": "Antecedent- and Response-Focused Emotion Regulation: Divergent Consequences for Experience, Expression, and Physiology",
        "authors": ["James J. Gross"],
        "year": 1998,
        "topic": "emotion_cognition",
        "pdf_url": "https://psych.colorado.edu/~tito/sp03/7536/Gross_1998.pdf",
    },
    {
        "id": "gross_2002",
        "title": "Emotion Regulation: Affective, Cognitive, and Social Consequences",
        "authors": ["James J. Gross"],
        "year": 2002,
        "topic": "emotion_cognition",
        "pdf_url": "https://www.ocf.berkeley.edu/~tijkstra/downloads/Gross%202002.pdf",
    },
    {
        "id": "gross_john_2003",
        "title": "Individual Differences in Two Emotion Regulation Processes: Implications for Affect, Relationships, and Well-Being",
        "authors": ["James J. Gross", "Oliver P. John"],
        "year": 2003,
        "topic": "emotion_cognition",
        "pdf_url": "https://psychology.berkeley.edu/sites/default/files/publications/john_gross_2003.pdf",
    },
    {
        "id": "aldao_2010",
        "title": "Emotion-Regulation Strategies Across Psychopathology: A Meta-Analytic Review",
        "authors": ["Amelia Aldao", "Susan Nolen-Hoeksema", "Susanne Schweizer"],
        "year": 2010,
        "topic": "emotion_cognition",
        "pdf_url": "https://wikilab.haifa.ac.il/images/d/d5/Aldao_Nolen-Hoeksema_Schweizer_2010.pdf",
    },
    {
        "id": "baumeister_2007",
        "title": "How Emotion Shapes Behavior: Feedback, Anticipation, and Reflection, Rather Than Direct Causation",
        "authors": ["Roy F. Baumeister", "E. J. Masicampo", "Kathleen D. Vohs"],
        "year": 2007,
        "topic": "emotion_cognition",
        "pdf_url": "https://carlsonschool.umn.edu/sites/carlsonschool.umn.edu/files/2019-06/how_emotion_shapes_behavior.pdf",
    },
    {
        "id": "lerner_2015",
        "title": "Emotion and Decision Making",
        "authors": ["Jennifer S. Lerner", "Ye Li", "Piercarlo Valdesolo", "Karim S. Kassam"],
        "year": 2015,
        "topic": "emotion_cognition",
        "pdf_url": "https://scholar.harvard.edu/files/jenniferlerner/files/emotion_and_decision_making.pdf",
    },
    {
        "id": "nolen_hoeksema_2008",
        "title": "Rethinking Rumination",
        "authors": ["Susan Nolen-Hoeksema", "Blair E. Wisco", "Sonja Lyubomirsky"],
        "year": 2008,
        "topic": "emotion_cognition",
        "pdf_url": "https://www.ocf.berkeley.edu/~tijkstra/downloads/Nolen-Hoeksema%20et%20al.%202008.pdf",
    },
]
# ─────────────────────────────────────────────────────────────────────────────


def extract_text_from_path(pdf_path):
    """Extract text from a local PDF file."""
    reader = PdfReader(str(pdf_path))
    pages_text = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            pages_text.append(t)
    full_text = "\n".join(pages_text).strip()
    return full_text if full_text else None


def fetch_pdf_text(pdf_url, paper_id):
    """Try URL first, then fall back to local PDF in data/pdfs/."""
    headers = {"User-Agent": "Mozilla/5.0 (research corpus builder)"}

    # 1 — Try downloading from URL
    try:
        response = requests.get(pdf_url, timeout=30, headers=headers)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")
        if "html" in content_type and "pdf" not in content_type:
            raise ValueError("URL returned HTML instead of PDF")

        reader = PdfReader(BytesIO(response.content))
        pages_text = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                pages_text.append(t)
        full_text = "\n".join(pages_text).strip()
        if full_text:
            return full_text
        raise ValueError("PDF had no extractable text")

    except Exception as e:
        print(f"      URL failed ({e.__class__.__name__}) — trying local file...")

    # 2 — Fall back to local PDF
    local_filename = LOCAL_PDFS.get(paper_id)
    if local_filename:
        local_path = LOCAL_PDF_DIR / local_filename
        if local_path.exists():
            try:
                text = extract_text_from_path(local_path)
                if text:
                    print(f"       Loaded from local file: {local_filename[:60]}")
                    return text
            except Exception as e2:
                print(f"      Local file also failed: {e2}")
        else:
            print(f"       Local file not found: {local_filename}")
    else:
        print(f"       No local file mapped for: {paper_id}")

    return None


def build_corpus():
    corpus = []

    for paper in PAPERS:
        print(f"\n📄 [{paper['topic']}] {paper['title'][:70]}...")
        print(f"   Fetching: {paper['pdf_url'][:80]}")

        full_text = fetch_pdf_text(paper["pdf_url"], paper["id"])

        if full_text:
            word_count = len(full_text.split())
            print(f"    Extracted {word_count:,} words")
        else:
            print(f"    Could not extract text from URL or local file")

        corpus.append({
            "id": paper["id"],
            "title": paper["title"],
            "authors": paper["authors"],
            "year": paper["year"],
            "topic": paper["topic"],
            "pdf_url": paper["pdf_url"],
            "full_text": full_text,
            "text": full_text if full_text else f"{paper['title']}. By {', '.join(paper['authors'])} ({paper['year']}).",
        })

        time.sleep(1)

    return corpus


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(" Building corpus from curated human psychology papers...\n")
    corpus = build_corpus()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    success = sum(1 for p in corpus if p["full_text"])
    print(f"\n{'='*60}")
    print(f" Done! {len(corpus)} papers saved to {OUTPUT_PATH}")
    print(f"   Full text extracted: {success}/{len(corpus)}")
    print(f"   Topics: cognitive_bias={sum(1 for p in corpus if p['topic']=='cognitive_bias')} | "
          f"memory={sum(1 for p in corpus if p['topic']=='memory')} | "
          f"emotion_cognition={sum(1 for p in corpus if p['topic']=='emotion_cognition')}")

    failed = [p["title"][:50] for p in corpus if not p["full_text"]]
    if failed:
        print(f"\n  Failed extractions ({len(failed)}):")
        for t in failed:
            print(f"   - {t}...")


if __name__ == "__main__":
    main()