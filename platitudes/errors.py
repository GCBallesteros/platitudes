class PlatitudeError(Exception):
    def __str__(self):
        return f"error: {self.args[0]}"
