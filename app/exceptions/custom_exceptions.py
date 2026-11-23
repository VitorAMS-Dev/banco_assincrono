"""Exceções customizadas do domínio bancário."""


class BankAPIException(Exception):
    """Classe base para todas as exceções da aplicação."""

    status_code: int = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ContaNaoEncontrada(BankAPIException):
    status_code = 404


class ClienteNaoEncontrado(BankAPIException):
    status_code = 404


class SaldoInsuficiente(BankAPIException):
    status_code = 422


class TransferenciaInvalida(BankAPIException):
    status_code = 422


class ContaBloqueada(BankAPIException):
    status_code = 423


class TokenInvalido(BankAPIException):
    status_code = 401


class CredenciaisInvalidas(BankAPIException):
    status_code = 401


class DatabaseException(BankAPIException):
    status_code = 500


class TimeoutException(BankAPIException):
    status_code = 504


class ClienteJaExiste(BankAPIException):
    status_code = 409
