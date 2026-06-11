"""Test unitari per datesuffix() e nome_cartella() in upload_drive.py."""
from datetime import date
from unittest.mock import patch

from upload_drive import datesuffix, nome_cartella


def test_datesuffix_both_dates():
    assert datesuffix("04/06/2026", "10/06/2026") == "04giu_10giu"


def test_datesuffix_only_da():
    assert datesuffix("04/06/2026", None) == "04giu"


def test_datesuffix_only_a():
    assert datesuffix(None, "10/06/2026") == "10giu"


def test_datesuffix_both_none():
    assert datesuffix(None, None) == ""


def _today(d):
    """Helper: patch upload_drive.date.today() to return a fixed date."""
    return patch("upload_drive.date", **{"today.return_value": d, "strptime": date.__class__})


def test_nome_cartella_both_dates():
    with patch("upload_drive.date") as mock:
        mock.today.return_value = date(2026, 6, 11)
        result = nome_cartella("04/06/2026", "10/06/2026")
    assert result == "20260611_da04giu_a10giu"


def test_nome_cartella_both_dates_with_keyword():
    with patch("upload_drive.date") as mock:
        mock.today.return_value = date(2026, 6, 11)
        result = nome_cartella("04/06/2026", "10/06/2026", keyword="APPALTI")
    assert result == "20260611_da04giu_a10giu_APPALTI"


def test_nome_cartella_none_none_uses_today():
    with patch("upload_drive.date") as mock:
        mock.today.return_value = date(2026, 6, 11)
        result = nome_cartella(None, None)
    assert result == "20260611"


def test_nome_cartella_none_none_with_keyword():
    with patch("upload_drive.date") as mock:
        mock.today.return_value = date(2026, 6, 11)
        result = nome_cartella(None, None, keyword="FESR")
    assert result == "20260611_FESR"


def test_nome_cartella_only_da():
    with patch("upload_drive.date") as mock:
        mock.today.return_value = date(2026, 6, 11)
        result = nome_cartella("04/06/2026", None)
    assert result == "20260611_da04giu"


def test_nome_cartella_only_a():
    with patch("upload_drive.date") as mock:
        mock.today.return_value = date(2026, 6, 11)
        result = nome_cartella(None, "10/06/2026")
    assert result == "20260611_a10giu"
