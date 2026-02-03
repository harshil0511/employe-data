from sqlalchemy.orm import Session, joinedload
from . import models, schemas
from app.core.logger import mongo_logger

# --- Connected Operations (Strict Mode) ---

def get_company(db: Session, company_id: int):
    # Connected: Automatically includes employees for the company
    return db.query(models.Company).options(joinedload(models.Company.employees)).filter(models.Company.id == company_id).first()

def get_companies(db: Session, skip: int = 0, limit: int = 100, show_deleted: bool = False):
    # Connected: Automatically includes only active employees for the company for accurate dashboard stats
    query = db.query(models.Company)
    if not show_deleted:
        query = query.filter(models.Company.is_deleted == False)
    companies = query.offset(skip).limit(limit).all()
    
    if not show_deleted:
        # Filter the loaded employees collection to only show active ones
        for company in companies:
            company.employees = [e for e in company.employees if not e.is_deleted]
            
    return companies

def update_company(db: Session, company_id: int, company_update: schemas.CompanyUpdate):
    db_company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not db_company:
        return None
    
    update_data = company_update.model_dump(exclude_unset=True)
    if "company_name" in update_data:
        update_data["name"] = update_data.pop("company_name")
        
    for key, value in update_data.items():
        setattr(db_company, key, value)
        
    db.commit()
    db.refresh(db_company)
    
    mongo_logger.info(f"Company updated: {db_company.name}", {
        "company_id": company_id,
        "update_data": update_data
    })
    
    return db_company

def delete_company(db: Session, company_id: int):
    db_company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not db_company:
        return False
    
    # Soft Delete: Update flag instead of removing
    db_company.is_deleted = True
    
    # Also soft delete all employees in this company
    db.query(models.Employee).filter(models.Employee.company_id == company_id).update({"is_deleted": True})
    
    db.commit()
    
    mongo_logger.warning(f"Company soft-deleted: {db_company.name}", {
        "company_id": company_id
    })
    
    return True

def create_company(db: Session, company: schemas.CompanyCreate):
    # Check if company already exists
    db_company = db.query(models.Company).filter(models.Company.name == company.company_name).first()
    if db_company:
        if db_company.is_deleted:
            # Reactivate deleted company
            db_company.is_deleted = False
            db_company.location = company.location
            db.commit()
            db.refresh(db_company)
            mongo_logger.info(f"Company reactivated: {db_company.name}", {
                "company_id": db_company.id,
                "location": db_company.location
            })
            return db_company
        else:
            # Already exists and active
            mongo_logger.warning(f"Company creation failed: {company.company_name} already exists", {
                "company_name": company.company_name
            })
            return None # We can handle this in the API
            
    db_company = models.Company(name=company.company_name, location=company.location)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    
    mongo_logger.info(f"Company created: {db_company.name}", {
        "company_id": db_company.id,
        "location": db_company.location
    })
    
    return db_company

def get_employees(db: Session, skip: int = 0, limit: int = 100, show_deleted: bool = False):
    query = db.query(models.Employee).options(joinedload(models.Employee.company_rel))
    if not show_deleted:
        query = query.filter(models.Employee.is_deleted == False)
    return query.offset(skip).limit(limit).all()

def get_employees_by_company(db: Session, company_name: str, show_deleted: bool = False):
    query = db.query(models.Employee).options(joinedload(models.Employee.company_rel)).join(models.Company).filter(models.Company.name == company_name)
    if not show_deleted:
        query = query.filter(models.Employee.is_deleted == False)
    return query.all()

def create_employee_strict(db: Session, employee: schemas.EmployeeCreate):
    """
    Strict Creation: Company MUST exist. If not, returns None.
    Does NOT auto-create company.
    """
    db_company = None
    # Check for ID (companies_id)
    target_id = employee.companies_id
    
    if target_id:
        db_company = db.query(models.Company).filter(models.Company.id == target_id).first()
    elif employee.company_name:
        db_company = db.query(models.Company).filter(models.Company.name == employee.company_name).first()
    
    if not db_company:
        mongo_logger.error(f"Employee creation failed: Company not found", {
            "employee_name": employee.name,
            "target_id": target_id,
            "company_name": employee.company_name
        })
        return None  # Company does not exist
        
    if db_company.is_deleted:
         mongo_logger.error(f"Employee creation failed: Company is deleted", {
            "employee_name": employee.name,
            "company_name": db_company.name
         })
         return None # Cannot add to deleted company

    db_employee = models.Employee(
        name=employee.name,
        role=employee.role,
        salary=employee.salary,
        company_id=db_company.id
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    mongo_logger.info(f"Employee created: {db_employee.name}", {
        "employee_id": db_employee.id,
        "company_id": db_employee.company_id,
        "role": db_employee.role
    })
    
    return db_employee

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    # Backward compatibility or flexible mode if needed, but we prefer strict now
    return create_employee_strict(db, employee)

def update_employee(db: Session, employee_id: int, employee_update: schemas.EmployeeUpdate):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_employee:
        return None
    
    update_data = employee_update.model_dump(exclude_unset=True)
    
    # Determine if company is being updated
    target_company_id = None
    if "companies_id" in update_data:
        target_company_id = update_data.pop("companies_id")
    
    company_name = None
    if "company_name" in update_data:
        company_name = update_data.pop("company_name")
    
    if target_company_id is not None:
         # Validate target company exists
         db_company = db.query(models.Company).filter(models.Company.id == target_company_id).first()
         if not db_company or db_company.is_deleted:
             return None # Company not found or deleted
         update_data["company_id"] = db_company.id
         
    elif company_name:
        # Lookup company by name
        db_company = db.query(models.Company).filter(models.Company.name == company_name).first()
        if not db_company or db_company.is_deleted:
             # Strict mode: fail if company not found? Or just ignore? 
             # For now let's behave safely: if company doesn't exist, we can't move employee there.
             return None 
        update_data["company_id"] = db_company.id

    for key, value in update_data.items():
        setattr(db_employee, key, value)
        
    db.commit()
    db.refresh(db_employee)
    
    mongo_logger.info(f"Employee updated: {db_employee.name}", {
        "employee_id": employee_id,
        "update_data": update_data
    })
    
    return db_employee

def delete_employee(db: Session, employee_id: int):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_employee:
        return False
    # Soft Delete: Update flag instead of removing
    db_employee.is_deleted = True
    db.commit()
    
    mongo_logger.warning(f"Employee soft-deleted: {db_employee.name}", {
        "employee_id": employee_id
    })
    
    return True
