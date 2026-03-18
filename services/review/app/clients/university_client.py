import httpx
import os
from uuid import UUID
from typing import Optional, Dict

class UniversityClient:
    """Клиент для общения с University service"""
    
    def __init__(self):
        self.base_url = os.getenv("UNIVERSITY_SERVICE_URL", "http://university-service:8003")
        self.timeout = 10.0
    
    async def check_university_exists(self, university_id: UUID) -> bool:
        """
        Проверяет, существует ли университет с таким ID
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/universities/{university_id}"
                )
                return response.status_code == 200
            except Exception as e:
                print(f"Error checking university: {e}")
                return False
    
    async def update_stats(self, university_id: UUID, rating: int, action: str = "add"):
        """
        Уведомляет University service о новом отзыве для обновления статистики
        action: "add" - добавить отзыв, "update" - обновить, "delete" - удалить
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                await client.post(
                    f"{self.base_url}/api/v1/universities/{university_id}/stats",
                    json={
                        "rating": rating,
                        "action": action
                    }
                )
            except Exception as e:
                print(f"Error updating university stats: {e}")

# Создаем экземпляр
university_client = UniversityClient()