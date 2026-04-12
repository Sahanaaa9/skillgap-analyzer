from pydantic import BaseModel
from typing import Optional

class EmployeeCreate(BaseModel):
    name: str
    role: str
    department: str

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None

class SkillCreate(BaseModel):
    employee_id: str
    skill_name: str
    proficiency: int
    category: Optional[str] = "Technical"
    last_used: Optional[str] = None

class SkillUpdate(BaseModel):
    proficiency: Optional[int] = None
    last_used: Optional[str] = None

class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class GapAnalysisRequest(BaseModel):
    employee_id: str
    employee_name: str
    role: str
    skills: list

class RevenueRequest(BaseModel):
    role: str
    skill_gap: str
    proficiency_current: int
    proficiency_required: int

class TrainingPlanRequest(BaseModel):
    employee_name: str
    role: str
    skill_gap: str