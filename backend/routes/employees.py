from fastapi import APIRouter, HTTPException, Header
from models import EmployeeCreate, EmployeeUpdate
from database import supabase
from typing import Optional

router = APIRouter(prefix="/employees", tags=["Employees"])

def get_user_id(authorization: str) -> str:
    try:
        token = authorization.replace("Bearer ", "")
        user = supabase.auth.get_user(token)
        return user.user.id
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.get("/")
def get_all_employees(authorization: str = Header(...)):
    user_id = get_user_id(authorization)
    try:
        response = supabase.table("employees")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()
        return {"employees": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{employee_id}")
def get_employee(employee_id: str, authorization: str = Header(...)):
    user_id = get_user_id(authorization)
    try:
        response = supabase.table("employees")\
            .select("*")\
            .eq("id", employee_id)\
            .eq("user_id", user_id)\
            .execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Employee not found")
        return {"employee": response.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
def create_employee(employee: EmployeeCreate, authorization: str = Header(...)):
    user_id = get_user_id(authorization)
    try:
        data = {
            "name": employee.name,
            "role": employee.role,
            "department": employee.department,
            "user_id": user_id
        }
        response = supabase.table("employees").insert(data).execute()
        return {"message": "Employee created", "employee": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{employee_id}")
def update_employee(employee_id: str, employee: EmployeeUpdate, authorization: str = Header(...)):
    user_id = get_user_id(authorization)
    try:
        updates = {k: v for k, v in employee.dict().items() if v is not None}
        response = supabase.table("employees")\
            .update(updates)\
            .eq("id", employee_id)\
            .eq("user_id", user_id)\
            .execute()
        return {"message": "Employee updated", "employee": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{employee_id}")
def delete_employee(employee_id: str, authorization: str = Header(...)):
    user_id = get_user_id(authorization)
    try:
        supabase.table("employees")\
            .delete()\
            .eq("id", employee_id)\
            .eq("user_id", user_id)\
            .execute()
        return {"message": "Employee deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))