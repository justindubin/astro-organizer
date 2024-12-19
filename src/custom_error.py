
class CustomError(Exception):
    def __init__(self, message, error_code):
        self.message = message
        super().__init__(self.message)
        self.error_code = error_code

    def __str__(self):
        return f"[Errno {self.error_code}] {self.message}"
