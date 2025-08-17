# main.py
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import io
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

# Configuración de la base de datos MySQL
DATABASE_URL = "mysql+pymysql://root:admin@localhost:3306/ventasplusdb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos de base de datos
class Vendedor(Base):
    __tablename__ = "vendedores"
    
    idvendedores = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)

class Producto(Base):
    __tablename__ = "productos"
    
    nombre_producto = Column(String, primary_key=True)
    referencia = Column(String, unique=True, index=True)
    valorunitario = Column(Float)

class Operacion(Base):
    __tablename__ = "operaciones"
    
    idoperaciones = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    idvendedor = Column(Integer)
    referencia = Column(String)
    cantidad = Column(Integer)
    valorvendido = Column(Float)
    impuesto = Column(Float)
    tipooperacion = Column(String)  # "Venta" o "Devolucion"
    motivo = Column(String, nullable=True)

# Crear las tablas solo si no existen (no sobrescribir las existentes)
# Base.metadata.create_all(bind=engine)

# Como ya tienes la base de datos creada, comentamos esta línea
# para no sobrescribir tus tablas existentes

# Modelos Pydantic
class VendedorCreate(BaseModel):
    nombre: str

class VendedorResponse(BaseModel):
    idvendedores: int
    nombre: str

    class Config:
        from_attributes = True

class ProductoCreate(BaseModel):
    nombre_producto: str
    referencia: str
    valorunitario: float

class ProductoResponse(BaseModel):
    nombre_producto: str
    referencia: str
    valorunitario: float

    class Config:
        from_attributes = True

class OperacionCreate(BaseModel):
    idvendedor: int
    referencia: str
    cantidad: int
    valorvendido: float
    impuesto: Optional[float] = 0.0
    tipooperacion: str
    motivo: Optional[str] = None

class OperacionResponse(BaseModel):
    idoperaciones: int
    fecha: datetime
    idvendedor: int
    referencia: str
    cantidad: int
    valorvendido: float
    impuesto: float
    tipooperacion: str
    motivo: Optional[str]

    class Config:
        from_attributes = True

class EstadisticasVendedor(BaseModel):
    vendedor: str
    total_ventas: float
    comision_calculada: float
    bono_penalizacion: float
    comision_final: float

# Inicializar FastAPI
app = FastAPI(
    title="VentasPlus API",
    description="Sistema de gestión de ventas y vendedores",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencia para obtener la sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse("index.html")

@app.post("/upload_csv/")
async def cargar_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Leer CSV con pandas
    df = pd.read_csv(file.file)

    # Verificar columnas
    required_columns = ["FechaVenta", "Vendedor", "Producto", "Referencia", "Cantidad",
                        "ValorUnitario", "ValorVendido", "Impuesto"]
    for col in required_columns:
        if col not in df.columns:
            return {"error": f"Falta la columna obligatoria: {col}"}

    # Manejar columnas opcionales
    if "TipoOperacion" not in df.columns:
        df["TipoOperacion"] = "Venta"
    if "Motivo" not in df.columns:
        df["Motivo"] = None

    # Procesar fila por fila
    for _, row in df.iterrows():
        # --- Vendedor ---
        vendedor = db.query(Vendedor).filter_by(nombre=row["Vendedor"]).first()
        if not vendedor:
            vendedor = Vendedor(nombre=row["Vendedor"])
            db.add(vendedor)
            db.commit()
            db.refresh(vendedor)

        # --- Producto ---
        producto = db.query(Producto).filter_by(referencia=row["Referencia"]).first()
        if not producto:
            producto = Producto(
                nombre_producto=row["Producto"],
                referencia=row["Referencia"],
                valorunitario=row["ValorUnitario"]
            )
            db.add(producto)
            db.commit()
            db.refresh(producto)

        # --- Operación ---
        existe_op = db.query(Operacion).filter_by(
        fecha=datetime.strptime(row["FechaVenta"], "%Y-%m-%d"),
        idvendedor=vendedor.idvendedores,
        referencia=row["Referencia"],
        cantidad=row["Cantidad"],
        valorvendido=row["ValorVendido"],
        impuesto=row["Impuesto"],
        tipooperacion=row["TipoOperacion"],
        motivo=row["Motivo"]
        ).first()

        if not existe_op:
            operacion = Operacion(
                fecha=datetime.strptime(row["FechaVenta"], "%Y-%m-%d"),
                idvendedor=vendedor.idvendedores,
                referencia=row["Referencia"],
                cantidad=row["Cantidad"],
                valorvendido=row["ValorVendido"],
                impuesto=row["Impuesto"],
                tipooperacion=row["TipoOperacion"],
                motivo=row["Motivo"]
            )
            db.add(operacion)
            db.commit()
            db.refresh(operacion)

    db.commit()
    return {"message": "Archivo cargado exitosamente y datos guardados"}

@app.get("/vendedores")
def obtener_vendedores(db: Session = Depends(get_db)):
    vendedores = db.query(Vendedor).all()
    return [{"id": v.idvendedores, "nombre": v.nombre} for v in vendedores]

# Endpoints de Vendedores
@app.post("/vendedores/", response_model=VendedorResponse)
async def crear_vendedor(vendedor: VendedorCreate, db: Session = Depends(get_db)):
    # Verificar si el vendedor ya existe
    db_vendedor = db.query(Vendedor).filter(Vendedor.nombre == vendedor.nombre).first()
    if db_vendedor:
        raise HTTPException(status_code=400, detail="Vendedor ya existe")
    
    db_vendedor = Vendedor(**vendedor.dict())
    db.add(db_vendedor)
    db.commit()
    db.refresh(db_vendedor)
    return db_vendedor

@app.get("/vendedores/", response_model=List[VendedorResponse])
async def listar_vendedores(db: Session = Depends(get_db)):
    return db.query(Vendedor).all()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)