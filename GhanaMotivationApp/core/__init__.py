"""Core package — shared infrastructure for cross-cutting concerns.

Provides centralized exception hierarchy and security utilities (password
hashing, JWT tokens).

Warning: Do not place domain-coupled logic (like querying Users) in this package
as it will cause topological circular imports.
"""

from .enums import (
    CurrencyEnum,
    PaymentStatusEnum
)

from .exceptions import (
    AppException,
    NotFoundException,
    AlreadyExistsException,
    AccessDeniedException,
    InactiveEntityException,
    InvalidCredentialsException,
)

from .security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

__all__ = (

    # from enums.py
    'CurrencyEnum',
    'PaymentStatusEnum',

    # from exceptions.py
    'AppException',
    'NotFoundException',
    'AlreadyExistsException',
    'AccessDeniedException',
    'InactiveEntityException',
    'InvalidCredentialsException',

    # from security.py
    'hash_password',
    'verify_password',
    'create_access_token',
    'decode_access_token',
)