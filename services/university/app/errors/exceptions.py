from fastapi import HTTPException, status

class UniversityAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="ВУЗ с таким названием уже существует"
        )

class UniversityNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ВУЗ не найден"
        )