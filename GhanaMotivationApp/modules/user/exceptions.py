from GhanaMotivationApp.core import AppException, NotFoundException, AlreadyExistsException, InactiveEntityException


class UserNotFoundException(NotFoundException):
    def __init__(self, identifier : str):
        super().__init__(entity="User", identifier=identifier)

class UserAlreadyExistsException(AlreadyExistsException):
    def __init__(self, field : str, value : str):
        super().__init__(entity="User", field=field, value=value)

class UserInactiveException(InactiveEntityException):
    def __init__(self, identifier : str):
        super().__init__(entity="User", identifier=identifier)

class UserNotPremiumException(AppException):
    """Raised when a user is not premium"""
    def __init__(self, user_id: int):
        super().__init__(
            message=f"User with iid '{user_id}' is not a premium subscriber.",
            error_code='USER_NOT_PREMIUM',
            status_code=403
        )

class UserAlreadyPremiumException(AppException):
    """Raised when a user is already premium"""
    def __init__(self, user_id: int):
        super().__init__(
            message=f"User with id '{user_id}' is already a premium subscripotion.",
            error_code='USER_ALREADY_PREMIUM',
            status_code=409
        )
