from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Company(Base):
    """
    Company SQLAlchemy Model
    Maps to 'companies' table
    """
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    location = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to employees
    employees = relationship("Employee", back_populates="company_rel")

    @property
    def companies_id(self):
        return self.id

    @property
    def company_id(self):
        return self.id

    @property
    def company_name(self):
        return self.name

class Employee(Base):
    """
    Employee SQLAlchemy Model
    Maps to 'employees' table
    """
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    salary = Column(Float, nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Foreign Key to Company
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    
    # Relationship to Company
    company_rel = relationship("Company", back_populates="employees")

    @property
    def employee_id(self):
        return self.id

    @property
    def employee_name(self):
        return self.name

    @property
    def company_name(self):
        """Helper to get company name for dashboard"""
        return self.company_rel.name if self.company_rel else None

    @property
    def companies_id(self):
        return self.company_id
