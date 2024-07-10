"""The most convenient zero dependency CLI builder"""

__version__ = "2.0.0"

from .argument import Argument
from .platitudes import (
    Exit,
    Platitudes,
    PlatitudesError,
    _is_maybe,  # noqa: F401
    _unwrap_annotated,  # noqa: F401
    _unwrap_maybe,  # noqa: F401
    run,
)

__all__ = ["Argument", "Exit", "Platitudes", "PlatitudesError", "run"]
