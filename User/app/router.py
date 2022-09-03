from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_user():
    return


@router.post("/")
def create_user():
    return
