from fastapi import APIRouter, HTTPException, Header
from models import SkillCreate, SkillUpdate
from database import supabase

router = APIRouter(prefix="/skills", tags=["Skills"])

def get_user_id(authorization: str) -> str:
    try:
        token = authorization.replace("Bearer ", "")
        user = supabase.auth.get_user(token)
        return user.user.id
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.get("/employee/{employee_id}")
def get_employee_skills(employee_id: str, authorization: str = Header(...)):
    get_user_id(authorization)
    try:
        response = supabase.table("employee_skills")\
            .select("*")\
            .eq("employee_id", employee_id)\
            .execute()
        return {"skills": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def add_skill(skill: SkillCreate, authorization: str = Header(...)):
    get_user_id(authorization)
    try:
        data = {
            "employee_id": skill.employee_id,
            "skill_name": skill.skill_name,
            "proficiency": skill.proficiency,
            "category": skill.category,
            "last_used": skill.last_used
        }
        response = supabase.table("employee_skills").insert(data).execute()
        return {"message": "Skill added", "skill": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{skill_id}")
def update_skill(skill_id: str, skill: SkillUpdate, authorization: str = Header(...)):
    get_user_id(authorization)
    try:
        updates = {k: v for k, v in skill.dict().items() if v is not None}
        response = supabase.table("employee_skills")\
            .update(updates)\
            .eq("id", skill_id)\
            .execute()
        return {"message": "Skill updated", "skill": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{skill_id}")
def delete_skill(skill_id: str, authorization: str = Header(...)):
    get_user_id(authorization)
    try:
        supabase.table("employee_skills")\
            .delete()\
            .eq("id", skill_id)\
            .execute()
        return {"message": "Skill deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))