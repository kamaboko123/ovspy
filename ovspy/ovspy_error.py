class OvspyError(Exception):
    pass

class TransactionError(OvspyError):
    pass

class Duplicate(OvspyError):
    pass

class NotFound(OvspyError):
    pass

class Unsupported(OvspyError):
    pass
