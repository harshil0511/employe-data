from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import crud, schemas, database
from app.core.logger import mongo_logger

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("/", response_model=List[schemas.CompanyResponse])
def read_companies(show_deleted: bool = False, db: Session = Depends(database.get_db)):
    mongo_logger.info("API Triggered: Fetch all companies", {"show_deleted": show_deleted})
    return crud.get_companies(db, show_deleted=show_deleted)

@router.post("/", response_model=schemas.CompanyResponse)
def create_company(company: schemas.CompanyCreate, db: Session = Depends(database.get_db)):
    mongo_logger.info(f"API Triggered: Create company: {company.company_name}")
    res = crud.create_company(db, company)
    if not res:
        raise HTTPException(status_code=400, detail="Company already exists")
    return res

@router.get("/{id}", response_model=schemas.CompanyResponse)
def read_company(id: int, db: Session = Depends(database.get_db)):
    mongo_logger.info(f"API Triggered: Fetch company ID {id}")
    res = crud.get_company(db, id)
    if not res: raise HTTPException(status_code=404, detail="Company not found")
    return res

@router.delete("/{id}")
def delete_company(id: int, db: Session = Depends(database.get_db)):
    mongo_logger.warning(f"API Triggered: Delete company ID {id}")
    if not crud.delete_company(db, id): raise HTTPException(status_code=404, detail="Company not found")
    return {"message": "Company deleted"}

@router.put("/{id}", response_model=schemas.CompanyResponse)
def update_company(id: int, company: schemas.CompanyUpdate, db: Session = Depends(database.get_db)):
    mongo_logger.info(f"API Triggered: Update company ID {id}")
    res = crud.update_company(db, id, company)
    if not res: raise HTTPException(status_code=404, detail="Company not found")
    return res
