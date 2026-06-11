"""
Tests for FESR_SCARICA_LINK_PDF and FESR_SCARICA_PDF env var parsing in applysecrets().
Phase 04, Plan 01 — TDD RED phase.
"""
import os
import importlib
import sys


def _reload_scraper():
    """Reload scraper with a clean module state."""
    if "scraper" in sys.modules:
        importlib.reload(sys.modules["scraper"])
        return sys.modules["scraper"]
    else:
        import scraper
        return scraper


def _clear_fesr_env():
    """Remove all FESR PDF-related env vars."""
    for key in ["FESR_SCARICA_LINK_PDF", "FESR_SCARICA_PDF"]:
        os.environ.pop(key, None)


def test_scarica_link_pdf_true():
    """Test 1: FESR_SCARICA_LINK_PDF=true → SCARICA_LINK_PDF is True after applysecrets()."""
    _clear_fesr_env()
    os.environ["FESR_SCARICA_LINK_PDF"] = "true"
    scraper = _reload_scraper()
    scraper.SCARICA_LINK_PDF = False
    scraper.SCARICA_PDF = False
    scraper.applysecrets()
    assert scraper.SCARICA_LINK_PDF is True, (
        f"Test 1 FAILED: expected SCARICA_LINK_PDF=True, got {scraper.SCARICA_LINK_PDF}"
    )
    _clear_fesr_env()


def test_scarica_pdf_1():
    """Test 2: FESR_SCARICA_PDF=1 → SCARICA_PDF is True (and SCARICA_LINK_PDF implied True)."""
    _clear_fesr_env()
    os.environ["FESR_SCARICA_PDF"] = "1"
    scraper = _reload_scraper()
    scraper.applysecrets()
    assert scraper.SCARICA_PDF is True, (
        f"Test 2 FAILED: expected SCARICA_PDF=True, got {scraper.SCARICA_PDF}"
    )
    assert scraper.SCARICA_LINK_PDF is True, (
        f"Test 2 implication FAILED: expected SCARICA_LINK_PDF=True (prerequisito), got {scraper.SCARICA_LINK_PDF}"
    )
    _clear_fesr_env()


def test_scarica_pdf_implies_link_pdf():
    """Test 3: FESR_SCARICA_PDF=true without FESR_SCARICA_LINK_PDF → both True (prerequisite implication)."""
    _clear_fesr_env()
    os.environ["FESR_SCARICA_PDF"] = "true"
    # FESR_SCARICA_LINK_PDF intentionally NOT set
    scraper = _reload_scraper()
    scraper.applysecrets()
    assert scraper.SCARICA_PDF is True, (
        f"Test 3 FAILED: expected SCARICA_PDF=True, got {scraper.SCARICA_PDF}"
    )
    assert scraper.SCARICA_LINK_PDF is True, (
        f"Test 3 FAILED: expected SCARICA_LINK_PDF=True (implied by SCARICA_PDF), got {scraper.SCARICA_LINK_PDF}"
    )
    _clear_fesr_env()


def test_no_env_vars_remain_false():
    """Test 4: No env var set → SCARICA_LINK_PDF and SCARICA_PDF remain False."""
    _clear_fesr_env()
    scraper = _reload_scraper()
    scraper.applysecrets()
    assert scraper.SCARICA_LINK_PDF is False, (
        f"Test 4 FAILED: expected SCARICA_LINK_PDF=False, got {scraper.SCARICA_LINK_PDF}"
    )
    assert scraper.SCARICA_PDF is False, (
        f"Test 4 FAILED: expected SCARICA_PDF=False, got {scraper.SCARICA_PDF}"
    )


def test_scarica_link_pdf_yes():
    """Test 5: FESR_SCARICA_LINK_PDF=yes → SCARICA_LINK_PDF is True."""
    _clear_fesr_env()
    os.environ["FESR_SCARICA_LINK_PDF"] = "yes"
    scraper = _reload_scraper()
    scraper.SCARICA_LINK_PDF = False
    scraper.SCARICA_PDF = False
    scraper.applysecrets()
    assert scraper.SCARICA_LINK_PDF is True, (
        f"Test 5 FAILED: expected SCARICA_LINK_PDF=True, got {scraper.SCARICA_LINK_PDF}"
    )
    _clear_fesr_env()


def test_scarica_link_pdf_false_string():
    """Test 6: FESR_SCARICA_LINK_PDF=false → SCARICA_LINK_PDF remains False."""
    _clear_fesr_env()
    os.environ["FESR_SCARICA_LINK_PDF"] = "false"
    scraper = _reload_scraper()
    scraper.SCARICA_LINK_PDF = False
    scraper.SCARICA_PDF = False
    scraper.applysecrets()
    assert scraper.SCARICA_LINK_PDF is False, (
        f"Test 6 FAILED: expected SCARICA_LINK_PDF=False (string 'false'), got {scraper.SCARICA_LINK_PDF}"
    )
    _clear_fesr_env()


if __name__ == "__main__":
    tests = [
        test_scarica_link_pdf_true,
        test_scarica_pdf_1,
        test_scarica_pdf_implies_link_pdf,
        test_no_env_vars_remain_false,
        test_scarica_link_pdf_yes,
        test_scarica_link_pdf_false_string,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS: {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {t.__name__} — {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR: {t.__name__} — {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
