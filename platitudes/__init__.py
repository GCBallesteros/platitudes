"""The most convenient zero dependency CLI builder"""

__version__ = "1.1.3"

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
