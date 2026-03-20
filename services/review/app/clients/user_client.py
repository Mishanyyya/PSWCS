# services/reviews/app/clients/user_client.py
import httpx
from typing import Optional, Dict
import uuid

from app.config import settings

class UserClient:
    """Клиент для общения с User service"""
    
    def __init__(self):
        self.base_url = settings.USERS_SERVICE_URL
        self.timeout = settings.REQUEST_TIMEOUT
    
    async def validate_token(self, token: str) -> Optional[Dict]:
        """
        Проверяет токен через User service
        Возвращает данные пользователя или None
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/auth/validate",  # Проверьте правильный путь!
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Если user_id уже UUID
                    user_id = data.get("user_id")
                    if isinstance(user_id, str) and len(user_id) == 36:
                        return {
                            "user_id": user_id,
                            "role": data.get("role", "user"),
                            "email": data.get("email")
                        }
                    
                    # Если user_id число - конвертируем
                    try:
                        user_id_int = int(user_id)
                        user_id_uuid = str(uuid.UUID(int=user_id_int))
                    except:
                        user_id_uuid = str(uuid.uuid4())
                    
                    return {
                        "user_id": user_id_uuid,
                        "role": data.get("role", "user"),
                        "email": data.get("email")
                    }
                else:
                    print(f"Token validation failed: {response.status_code}")
                    return None
                    
            except Exception as e:
                print(f"Error connecting to User service: {e}")
                return None

# Создаем экземпляр клиента для использования в приложении
user_client = UserClient()