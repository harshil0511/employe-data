from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Union
from app.database import crud, schemas, database
from app.core.logger import mongo_logger

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/", response_model=List[schemas.EmployeeResponse])
def read_employees(show_deleted: bool = False, db: Session = Depends(database.get_db)):
    mongo_logger.info("API Triggered: Fetch all employees", {"show_deleted": show_deleted})
    return crud.get_employees(db, show_deleted=show_deleted)

@router.post("/", response_model=Union[schemas.EmployeeResponse, List[schemas.EmployeeResponse]])
def create_employee(employee: Union[schemas.EmployeeCreate, List[schemas.EmployeeCreate]], db: Session = Depends(database.get_db)):
    mongo_logger.info("API Triggered: Create Employee(s)")
    # Bulk creation support
    if isinstance(employee, list):
        created = []
        for emp_data in employee:
            res = crud.create_employee_strict(db, emp_data)
            if res:
                created.append(res)
        return created

    # Enforce parent-child relationship: Company must exist
    res = crud.create_employee_strict(db, employee)
    if not res:
        raise HTTPException(status_code=400, detail="Company does not exist. Create company first.")
    return res

@router.get("/filter", response_model=List[schemas.EmployeeResponse])
def filter_employees(company: str, show_deleted: bool = False, db: Session = Depends(database.get_db)):
    mongo_logger.info(f"API Triggered: Filter employees by company: {company}")
    return crud.get_employees_by_company(db, company_name=company, show_deleted=show_deleted)

@router.delete("/{id}")
def delete_employee(id: int, db: Session = Depends(database.get_db)):
    mongo_logger.warning(f"API Triggered: Delete employee ID {id}")
    if not crud.delete_employee(db, id): raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted"}

@router.put("/{id}", response_model=schemas.EmployeeResponse)
def update_employee(id: int, employee: schemas.EmployeeUpdate, db: Session = Depends(database.get_db)):
    mongo_logger.info(f"API Triggered: Update employee ID {id}")
    res = crud.update_employee(db, id, employee)
    if not res: raise HTTPException(status_code=404, detail="Employee not found")
    return res
