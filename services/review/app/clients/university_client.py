# app/clients/university_client.py
import httpx
from app.config import settings


class UniversityClient:
    # Клиент для общения с University service

    def __init__(self):
        self.base_url = settings.UNIVERSITY_SERVICE_URL
        self.timeout = settings.REQUEST_TIMEOUT

    async def check_university_exists(self, university_id: int) -> bool:
        # существует ли университет с таким ID
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"{self.base_url}/universities/{university_id}")
                return response.status_code == 200
            except Exception as e:
                print(f"Error checking university: {e}")
                return False

    async def update_stats(self, university_id: int, rating: int, action: str = "approve"):
        # уведомляет University service об изменении отзыва
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.patch(
                    f"{self.base_url}/universities/{university_id}/update-rating",
                    json={
                        "new_score": rating,
                        "action": action
                    }
                )
                return response.status_code == 200
            except Exception as e:
                print(f"Error updating university stats: {e}")
                return False
 
university_client = UniversityClient()