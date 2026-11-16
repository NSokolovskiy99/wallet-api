class WalletException(Exception):
    """Базовое исключение для кошелька"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
    pass


class WalletNotFoundException(WalletException):
    """Если кошелек не найден в БД"""
    def __init__(self, message: str = "Кошелек с указанным UUID не найден"):
        super().__init__(message)
    pass


class InsufficientFundsException(WalletException):
    """Если не достаточно средств"""
    def __init__(self, message: str = "Недостаточно средств для выполнения операции"):
        super().__init__(message)
    pass