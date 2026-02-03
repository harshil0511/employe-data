from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# --- Linked Schemas (Working Together) ---

class EmployeeBase(BaseModel):
    name: str
    role: str
    salary: float

class EmployeeCreate(EmployeeBase):
    companies_id: Optional[int] = None
    company_name: Optional[str] = None

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    salary: Optional[float] = None
    companies_id: Optional[int] = None
    company_name: Optional[str] = None  # Support updating company by name

class EmployeeResponse(BaseModel):
    employee_id: int
    employee_name: str
    role: str
    salary: float
    companies_id: Optional[int] = None
    company_name: Optional[str] = None
    created_at: datetime
    is_deleted: bool
    
    class Config:
        from_attributes = True
        # We will use the model's properties to populate these

class CompanyBase(BaseModel):
    company_name: str
    location: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    company_name: Optional[str] = None
    location: Optional[str] = None

class CompanyResponse(CompanyBase):
    companies_id: int
    is_deleted: bool
    created_at: datetime
    employees: List[EmployeeResponse] = [] # Linked list of employees
    
    class Config:
        from_attributes = True
