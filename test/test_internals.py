from typing import Annotated, Optional, Union

import pytest

from platitudes import Argument, _is_maybe, _unwrap_annotated, _unwrap_maybe


def test_is_mabye():
    assert _is_maybe(int | None)
    assert _is_maybe(Optional[int])
    assert _is_maybe(Union[int, None])
    assert _is_maybe(Union[None, int])
    assert _is_maybe(Union[str, None])
    assert not _is_maybe(Union[str, int])
    assert not _is_maybe(int)


def test_unwrap_annotated():
    t, _ = _unwrap_annotated(Annotated[int, 3])
    assert t is int

    t, _ = _unwrap_annotated(int)
    assert t is int

    t, _ = _unwrap_annotated(Annotated[int, Argument(exists=True)])
    assert t is int


def test_unwrap_maybe():
    assert _unwrap_maybe(int | None) is int
    assert _unwrap_maybe(Optional[int]) is int
    assert _unwrap_maybe(Union[int, None]) is int
    assert _unwrap_maybe(Union[None, str]) is str

    with pytest.raises(TypeError):
        _unwrap_maybe(int)
