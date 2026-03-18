# API Design для Review Service

## Базовый URL
`/api/v1/reviews`

## Эндпоинты

### 1. Создание отзыва
`POST /`
- **Auth:** Требуется JWT токен пользователя
- **Body:** ReviewCreate (university_id, rating, title, body, is_anonymous)
- **Response:** ReviewResponse
- **Статусы:** 201 Created, 400 Bad Request, 401 Unauthorized

### 2. Получение отзыва по ID
`GET /{review_id}`
- **Auth:** Не требуется (публичный)
- **Response:** ReviewResponse
- **Статусы:** 200 OK, 404 Not Found

### 3. Получение отзывов по университету (с пагинацией)
`GET /university/{university_id}`
- **Query params:** page, page_size, status (опционально)
- **Response:** ReviewListResponse
- **Статусы:** 200 OK

### 4. Получение отзывов текущего пользователя
`GET /my`
- **Auth:** Требуется JWT
- **Query params:** page, page_size
- **Response:** ReviewListResponse
- **Статусы:** 200 OK

### 5. Обновление отзыва
`PUT /{review_id}`
- **Auth:** Только автор или модератор
- **Body:** ReviewUpdate
- **Response:** ReviewResponse
- **Статусы:** 200 OK, 403 Forbidden, 404 Not Found

### 6. Удаление отзыва
`DELETE /{review_id}`
- **Auth:** Только автор или модератор
- **Статусы:** 204 No Content, 403 Forbidden

### 7. Модерация отзыва (для модераторов)
`POST /{review_id}/moderate`
- **Auth:** Только модератор
- **Body:** ModerationReject (reason для reject)
- **Статусы:** 
  - `POST /approve` → статус approved
  - `POST /reject` → статус rejected
- **Response:** ModerationResponse

### 8. Получение логов модерации
`GET /{review_id}/logs`
- **Auth:** Только модератор
- **Response:** list[ModerationLogResponse]