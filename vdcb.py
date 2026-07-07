from fastapi import FastAPI, status, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/ecommerce_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProductModel(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)

class ProductCreate(BaseModel):
    sku: str
    name: str
    price: float

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        new_product = ProductModel(**product.dict())
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return {"message": "Product created successfully", "data": new_product}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))