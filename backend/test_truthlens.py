# test_truthlens.py
# Automated tests for TruthLens

import sys
import os
sys.path.append("backend")

from parser import parse_document
from conflict import check_answerability, calculate_evidence_confidence
from translator import detect_lang, get_lang_name


def test_parser():
    # Create test file
    os.makedirs("data/uploads", exist_ok=True)
    with open("data/uploads/test.txt", "w", encoding="utf-8") as f:
        f.write("Employee joined in January 2024.")
    
    result = parse_document("data/uploads/test.txt")
    assert result["file"] == "test.txt"
    assert len(result["pages"]) > 0
    assert "Employee" in result["full_text"]
    print("✅ Parser test passed")


def test_language_detection():
    # Test language detection
    lang = detect_lang("Employee joined in January 2024.")
    assert lang == "en"
    
    lang = detect_lang("कर्मचारी जनवरी 2024 में शामिल हुआ")
    assert lang == "hi"
    print("✅ Language detection test passed")


def test_language_names():
    # Test language name mapping
    assert get_lang_name("en") == "English"
    assert get_lang_name("hi") == "Hindi"
    assert get_lang_name("ta") == "Tamil"
    print("✅ Language names test passed")


def test_answerability_no_evidence():
    # Test no evidence case
    chunks = []
    result = check_answerability(chunks, {}, "test query")
    assert result["level"] == "no_evidence"
    print("✅ No evidence test passed")


def test_answerability_strong():
    # Test strong evidence case
    chunks = [
        {"score": 5.0, "file": "test1.pdf"},
        {"score": 6.0, "file": "test2.pdf"}
    ]
    result = check_answerability(chunks, {"conflict": False}, "test query")
    assert result["level"] in ["strong", "moderate"]
    print("✅ Strong evidence test passed")


def test_answerability_conflict():
    # Test conflict case
    chunks = [
        {"score": 5.0, "file": "test1.pdf"},
        {"score": 6.0, "file": "test2.pdf"}
    ]
    result = check_answerability(chunks, {"conflict": True}, "test query")
    assert result["level"] == "cannot_determine"
    print("✅ Conflict detection test passed")


def test_confidence_calculation():
    # Test confidence calculation
    chunks = [{"score": 5.0, "file": "test.pdf"}]
    result = calculate_evidence_confidence(chunks, {})
    assert "score" in result
    assert 0 <= result["score"] <= 100
    print("✅ Confidence calculation test passed")


def test_confidence_with_conflict():
    # Test confidence with conflict penalty
    chunks = [{"score": 5.0, "file": "test.pdf"}]
    result = calculate_evidence_confidence(chunks, {"conflict": True})
    assert result["penalty"] == -55
    print("✅ Conflict penalty test passed")


if __name__ == "__main__":
    print("=" * 50)
    print("TruthLens Test Suite")
    print("=" * 50)
    
    test_parser()
    test_language_detection()
    test_language_names()
    test_answerability_no_evidence()
    test_answerability_strong()
    test_answerability_conflict()
    test_confidence_calculation()
    test_confidence_with_conflict()
    
    print("=" * 50)
    print("✅ All 8 tests passed!")
    print("=" * 50)