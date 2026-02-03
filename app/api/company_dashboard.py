from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database import get_db, models, crud, schemas
from app.core.logger import mongo_logger

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/all-data")
def get_all_dashboard_data(db: Session = Depends(get_db)):
    mongo_logger.info("API Triggered: Fetch all dashboard data")
    # Get summary data and companies for the main view
    companies = crud.get_companies(db, show_deleted=False)
    
    # Calculate summary stats based on active records
    total_companies = len(companies)
    
    total_employees = 0
    total_salary = 0
    for company in companies:
        active_employees = [e for e in company.employees if not e.is_deleted]
        total_employees += len(active_employees)
        total_salary += sum(e.salary for e in active_employees)

    return {
        "companies": [schemas.CompanyResponse.model_validate(c) for c in companies],
        "summary": {
            "total_companies": total_companies,
            "total_employees": total_employees,
            "total_salary": total_salary
        }
    }

@router.get("/top-companies")
def top_five_companies_with_top_employee(db: Session = Depends(get_db)):
    mongo_logger.info("API Triggered: Fetch top 5 companies ranking")
    # 1. Identify top 5 companies by total salary
    valuable_companies = (
        db.query(
            models.Employee.company_id,
            func.sum(models.Employee.salary).label("total_val")
        )
        .filter(models.Employee.is_deleted == False)
        .group_by(models.Employee.company_id)
        .order_by(desc("total_val"))
        .limit(5)
        .all()
    )

    if not valuable_companies:
        return []

    target_ids = [c.company_id for c in valuable_companies]

    # 2. For each of these companies, find the employee with the highest salary
    # Subquery for max salary per company among target companies
    max_salaries = (
        db.query(
            models.Employee.company_id,
            func.max(models.Employee.salary).label("max_salary")
        )
        .filter(models.Employee.company_id.in_(target_ids))
        .filter(models.Employee.is_deleted == False)
        .group_by(models.Employee.company_id)
        .subquery()
    )

    # 3. Join back to get names and details
    # We use a subquery to avoid duplicates if multiple employees have the same max salary
    # or just join and take the first one per company name in python if needed.
    raw_results = (
        db.query(
            models.Company.id,
            models.Company.name.label("company_name"),
            models.Employee.name.label("employee_name"),
            models.Employee.salary
        )
        .join(max_salaries, (models.Employee.company_id == max_salaries.c.company_id) & (models.Employee.salary == max_salaries.c.max_salary))
        .join(models.Company, models.Company.id == models.Employee.company_id)
        .filter(models.Employee.is_deleted == False)
        .all()
    )

    # Ensure unique companies in output and maintain order of 'valuable_companies'
    company_order = {c_id: i for i, c_id in enumerate(target_ids)}
    
    final_results = []
    seen_companies = set()
    for row in raw_results:
        if row.company_name not in seen_companies:
            final_results.append({
                "company_id": row.id,
                "company_name": row.company_name,
                "employee_name": row.employee_name,
                "salary": row.salary
            })
            seen_companies.add(row.company_name)
    
    # Sort final results by the rank of the company's total value
    final_results.sort(key=lambda x: company_order.get(x["company_id"], 999))

    return final_results
