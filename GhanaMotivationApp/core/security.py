"""Security utilities for password hashing and JWT token management.

This module provides pure utility functions with no business logic and
no database access. It uses ``bcrypt`` with a ``sha256`` pre-hash to
bypass bcrypt's 72-byte password limit, and ``PyJWT`` for stateless
JSON Web Token operations.
"""
import uuid
import bcrypt
import jwt
from typing_extensions import TypedDict
from datetime import datetime, timedelta, timezone
from hashlib import sha256

from .exceptions import InvalidCredentialsException
from .enums import TokenTypeEnum




class Payload(TypedDict):
    sub: str
    type: TokenTypeEnum
    jti: str | None
    iat: datetime
    exp: datetime


def _utf8(seq: str) -> bytes:
    """Encodes a string to UTF-8 bytes.

    Args:
        seq: The string to encode.

    Returns:
        The UTF-8 encoded bytes.
    """
    return seq.encode('utf-8')


def hash_password(plain_password: str) -> str:
    """Hashes a plain-text password using SHA-256 pre-hash + bcrypt.

    The password is first hashed with SHA-256 to produce a fixed-length
    hex digest, which is then passed to bcrypt. This bypasses bcrypt's
    72-byte input limit while preserving full password entropy.

    Args:
        plain_password: The raw password string from the user.

    Returns:
        The bcrypt-hashed password string (UTF-8 decoded).
    """
    # Step 1: SHA-256 pre-hash to bypass bcrypt's 72-byte limit
    sha256_hash = sha256(_utf8(plain_password)).hexdigest()

    # Step 2: Generate a random salt for bcrypt
    salt = bcrypt.gensalt()

    # Step 3: Hash the SHA-256 digest with bcrypt
    hashed_bytes = bcrypt.hashpw(password=_utf8(sha256_hash), salt=salt)

    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a stored bcrypt hash.

    Applies the same SHA-256 pre-hash before comparing with bcrypt's
    constant-time ``checkpw`` function.

    Args:
        plain_password: The raw password to verify.
        hashed_password: The stored bcrypt hash to compare against.

    Returns:
        ``True`` if the password matches the hash, ``False`` otherwise.
    """
    sha256_hash = sha256(_utf8(plain_password)).hexdigest()

    try:
        return bcrypt.checkpw(_utf8(sha256_hash), _utf8(hashed_password))
    except ValueError:
        return False


def create_access_token(user_id: int, expires_delta: timedelta | None = None) -> str:
    """Creates a signed JWT access token.

    Encodes the user's UUID as the ``sub`` (subject) claim and sets an
    expiration time. If no custom expiry is provided, the default from
    ``settings.ACCESS_TOKEN_EXPIRE_MINUTES`` is used.

    Args:
        user_id (int): The user's int to encode as the ``sub`` claim.
        expires_delta (timedelta): Optional custom expiry duration. Defaults to
            ``settings.ACCESS_TOKEN_EXPIRE_MINUTES`` minutes.

    Returns:
        The encoded JWT string.
    """
    from GhanaMotivationApp.settings import settings

    # Use settings default if no custom expiry provided
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.now(timezone.utc)

    payload: dict[str, str | TokenTypeEnum | datetime] = Payload(
        sub=str(user_id),
        type=TokenTypeEnum.ACCESS,
        iat=now,
        exp=now + expires_delta
    )

    return jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: int, jti: str | None = None) -> tuple[str, str]:
    """Creates a signed JWT refresh token with a unique JTI claim.

    The JTI (JWT ID) is stored server-side in the ``refresh_sessions``
    table to enable revocation and rotation.

    Args:
        user_id: The user's primary key integer.
        jti: Optional pre-generated JTI. If None, a UUID4 hex is generated.

    Returns:
        A tuple of ``(encoded_jwt_string, jti_string)``.
    """
    from GhanaMotivationApp.settings import settings

    if jti is None:
        jti = uuid.uuid4().hex

    now = datetime.now(timezone.utc)
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload: dict[str, str | TokenTypeEnum | datetime] = Payload(
        sub=str(user_id),
        type=TokenTypeEnum.REFRESH,
        jti=jti,
        iat=now,
        exp=now + expires_delta
    )

    token = jwt.encode(
        payload=payload,
        key=settings.REFRESH_SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return token, jti


def decode_access_token(token: str) -> dict:
    """Decodes and validates a JWT access token.

    Verifies the token's signature and expiration, then extracts the
    payload. If the token is invalid, expired, or missing the ``sub``
    claim, an ``InvalidCredentialsException`` is raised.

    Args:
        token: The JWT string from the ``Authorization`` header.

    Returns:
        The decoded payload dictionary containing ``sub`` and ``exp``.

    Raises:
        InvalidCredentialsException: If the token is expired, malformed,
            or missing the ``sub`` claim.
    """
    from GhanaMotivationApp.settings import settings

    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if 'sub' not in payload:
            raise InvalidCredentialsException()

        # Reject refresh tokens presented as access tokens
        if payload.get('type') != TokenTypeEnum.ACCESS:
            raise InvalidCredentialsException()

        return payload

    except jwt.PyJWTError:
        raise InvalidCredentialsException()


def decode_refresh_token(token: str) -> dict:
    """Decodes and validates a JWT refresh token.

    Verifies signature, expiration, ``sub`` and ``jti`` claim presence,
    and that the token type is ``refresh``.

    Args:
        token: The JWT refresh token string.

    Returns:
        The decoded payload dictionary containing ``sub``, ``jti``, ``type``.

    Raises:
        InvalidCredentialsException: If the token is expired, malformed,
            or not of type ``refresh``.
    """
    from GhanaMotivationApp.settings import settings

    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.REFRESH_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if 'sub' not in payload or 'jti' not in payload:
            raise InvalidCredentialsException()

        if payload.get('type') != TokenTypeEnum.REFRESH:
            raise InvalidCredentialsException()

        return payload

    except jwt.PyJWTError:
        raise InvalidCredentialsException()
