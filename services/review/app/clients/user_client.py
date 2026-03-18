import httpx
import os
from typing import Optional, Dict

class UserClient:
    """Клиент для общения с User service"""
    
    def __init__(self):
        # URL User service (можно через переменную окружения)
        self.base_url = os.getenv("USER_SERVICE_URL", "http://user-service:8001")
        self.timeout = 10.0  # таймаут 10 секунд
    
    async def validate_token(self, token: str) -> Optional[Dict]:
        """
        Проверяет токен через User service
        Возвращает данные пользователя или None
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/auth/validate",  # эндпоинт в User service
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "user_id": data["user_id"],
                        "role": data["role"],
                        "email": data.get("email")
                    }
                else:
                    print(f"Token validation failed: {response.status_code}")
                    return None
                    
            except httpx.RequestError as e:
                print(f"Error connecting to User service: {e}")
                return None
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None

# Создаем экземпляр клиента для использования в приложении
user_client = UserClient()