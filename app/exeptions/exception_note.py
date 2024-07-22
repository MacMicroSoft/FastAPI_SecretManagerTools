from fastapi import HTTPException, status


class NoteFoundNoteException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")


class NotePermissionException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail="User do not have permission to perform this action")


class NoteAlreadySharedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail="Note already shared")