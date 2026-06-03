"""Модуль аутентификации и авторизации"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from server.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, USERS


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Сервис аутентификации"""
    
    def __init__(self):
        self._users = USERS.copy()
        # В реальном проекте пароли должны храниться в хэшированном виде
        self._password_hashes = {
            username: pwd_context.hash(password) 
            for username, password in self._users.items()
        }
    
    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Аутентификация пользователя, возвращает токен или None"""
        if username not in self._users:
            return None
        
        if not pwd_context.verify(password, self._password_hashes[username]):
            return None
        
        return self._create_access_token(username)
    
    def _create_access_token(self, username: str) -> str:
        """Создание JWT токена"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": username, "exp": expire}
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[str]:
        """Верификация токена, возвращает username или None"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("sub")
        except JWTError:
            return None
    
    def add_user(self, username: str, password: str) -> bool:
        """Добавление нового пользователя"""
        if username in self._users:
            return False
        self._users[username] = password
        self._password_hashes[username] = pwd_context.hash(password)
        return True