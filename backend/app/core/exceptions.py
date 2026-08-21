#Exceptions for specific errors

class DomainError(Exception):
    pass

class SelfConnectionError(DomainError):
    pass