from fastapi import APIRouter, HTTPException, Header
from models import GapAnalysisRequest, RevenueRequest, TrainingPlanRequest
from database import supabase
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

router = APIRouter(prefix="/ai", tags=["AI Features"])

def get_user_id(authorization: str) -> str:
    try:
        token = authorization.replace("Bearer ", "")
        user = supabase.auth.get_user(token)
        return user.user.id
    except:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def clean_json(text: str):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

@router.post("/gap-analysis")
def gap_analysis(data: GapAnalysisRequest, authorization: str = Header(...)):
    get_user_id(authorization)
    try:
        skills_text = "\n".join([
            f"- {s['skill_name']}: {s['proficiency']}/5 (category: {s.get('category','Technical')})"
            for s in data.skills
        ])
        prompt = f"""
You are a workforce analytics AI. Analyse the skill profile below and identify skill gaps.

Employee: {data.employee_name}
Role: {data.role}

Current skills and proficiency (1=No knowledge, 5=Expert):
{skills_text}

Return ONLY a JSON array with no extra text. Format:
[
  {{
    "skill": "skill name",
    "current_proficiency": 2,
    "required_proficiency": 4,
    "priority": "High/Medium/Low",
    "reason": "one sentence why this matters for this role"
  }}
]

Include missing critical skills for the role AND existing skills below required level.
Limit to top 5 most important gaps only.
"""
        response = model.generate_content(prompt)
        gaps = json.loads(clean_json(response.text))
        return {"employee_id": data.employee_id, "gaps": gaps}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid format. Try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/revenue-impact")
def revenue_impact(data: RevenueRequest, authorization: str = Header(...)):
    get_user_id(authorization)
    try:
        prompt = f"""
You are a business analytics AI specialising in workforce productivity.

Role: {data.role}
Skill gap: {data.skill_gap}
Current proficiency: {data.proficiency_current}/5
Required proficiency: {data.proficiency_required}/5

Estimate the monthly revenue impact of this skill gap on a small Indian business.

Return ONLY a JSON object with no extra text. Format:
{{
  "monthly_loss_inr": 35000,
  "annual_loss_inr": 420000,
  "impact_level": "High/Medium/Low",
  "reasoning": "two sentences explaining the calculation logic",
  "confidence": "High/Medium/Low"
}}
"""
        response = model.generate_content(prompt)
        result = json.loads(clean_json(response.text))
        return result
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid format. Try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/training-plan")
def training_plan(data: TrainingPlanRequest, authorization: str = Header(...)):
    get_user_id(authorization)
    try:
        prompt = f"""
You are a learning and development AI. Create a 90-day training plan.

Employee: {data.employee_name}
Role: {data.role}
Skill to develop: {data.skill_gap}

Return ONLY a JSON object with no extra text. Format:
{{
  "skill": "{data.skill_gap}",
  "total_days": 90,
  "weeks": [
    {{
      "week_range": "Week 1-3",
      "focus": "what to focus on",
      "activities": ["activity 1", "activity 2"],
      "free_resource": "specific free website or course name",
      "milestone": "what they should achieve by end of this phase"
    }}
  ],
  "success_metric": "how to know they achieved the required proficiency"
}}

Include 4 phases covering weeks 1-3, 4-6, 7-9, and 10-13. Use only free resources.
"""
        response = model.generate_content(prompt)
        plan = json.loads(clean_json(response.text))
        supabase.table("training_plans").insert({
            "employee_name": data.employee_name,
            "skill_gap": data.skill_gap,
            "plan_json": json.dumps(plan)
        }).execute()
        return plan
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid format. Try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hire-vs-train")
def hire_vs_train(data: RevenueRequest, authorization: str = Header(...)):
    get_user_id(authorization)
    try:
        prompt = f"""
You are a business HR advisor. Decide whether to hire or train for this skill gap.

Role: {data.role}
Skill gap: {data.skill_gap}
Current proficiency: {data.proficiency_current}/5
Required proficiency: {data.proficiency_required}/5

Return ONLY a JSON object with no extra text. Format:
{{
  "recommendation": "Train or Hire",
  "confidence": "High/Medium/Low",
  "train_cost_inr": 15000,
  "train_time_weeks": 12,
  "hire_cost_inr": 80000,
  "hire_time_weeks": 6,
  "reasoning": "two to three sentences explaining the recommendation",
  "risk_if_ignored": "one sentence on business risk"
}}
"""
        response = model.generate_content(prompt)
        result = json.loads(clean_json(response.text))
        return result
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid format. Try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))