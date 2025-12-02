from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def get_data():
    return {"success": True, "data": []}
