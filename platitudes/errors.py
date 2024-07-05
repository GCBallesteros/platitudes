"""Exceptions for the Platitudes package"""

class PlatitudeError(Exception):
    """Platitude specific errors.

    Most of the time raised when a passed parameter to the CLI fails to parse.
    """
    def __str__(self):
        """Stringify a Platitudes error"""
        return f"error: {self.args[0]}"
