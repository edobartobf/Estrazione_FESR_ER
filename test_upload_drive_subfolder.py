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


def test_nome_cartella_both_dates():
    assert nome_cartella("04/06/2026", "10/06/2026") == "FESR_04giu_10giu"


def test_nome_cartella_none_none_uses_today():
    with patch("upload_drive.date") as mock_date:
        mock_date.today.return_value = date(2026, 6, 11)
        result = nome_cartella(None, None)
    assert result == "FESR_20260611"


def test_nome_cartella_only_da():
    assert nome_cartella("04/06/2026", None) == "FESR_04giu"
