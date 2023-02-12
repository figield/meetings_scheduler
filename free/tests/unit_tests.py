import pytest

from free.utils.parser import get_start_end_hours


@pytest.mark.parametrize('hours_text', ['8-17', '08-17'])
def test_get_start_end_hours(hours_text):
    start_hours, end_hours = get_start_end_hours(hours_text)
    assert start_hours == 8
    assert end_hours == 17
