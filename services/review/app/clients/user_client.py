import httpx
import os
from typing import Optional, Dict

class UserClient:
    """Клиент для общения с User service"""
    
    def __init__(self):
        self.base_url = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
        self.timeout = 10.0
    
    async def validate_token(self, token: str) -> Optional[Dict]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/users/auth/validation",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                print(f"Response status: {response.status_code}")
                print(f"Response body: {response.text}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    
                    return {
                        "user_id": data["user_id"], 
                        "role": data["role"],
                        "email": data.get("email")
                    }
                else:
                    print(f"Token validation failed with status {response.status_code}")
                    return None
                    
            except httpx.ConnectError as e:
                print(f"Cannot connect to User service at {self.base_url}: {e}")
                return None
            except Exception as e:
                print(f"Error connecting to User service: {e}")
                return None

# Создаем экземпляр клиента
user_client = UserClient()