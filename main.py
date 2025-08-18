# main.py
from fastapi import FastAPI, File, UploadFile, Depends, Request, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, extract, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import math

def clean_value(val):
    if val is None:
        return None
    if isinstance(val, float) and math.isnan(val):
        return None
    return val

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
    fecha = Column(DateTime, default=datetime.now())
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

@app.get("/api/vendedores_nombre")
def get_vendedores(db: Session = Depends(get_db)):
    vendedores = db.query(Vendedor).all()
    return [{"id": v.idvendedores, "nombre": v.nombre} for v in vendedores]

@app.get("/api/meses")
def get_meses(db: Session = Depends(get_db)):
    meses = db.query(func.monthname(Operacion.fecha)).distinct().all()
    return [{"mes": m[0]} for m in meses]

@app.get("/api/referencias")
def get_referencias(db: Session = Depends(get_db)):
    referencias = db.query(Producto.referencia).distinct().all()
    return [{"referencias": r[0]} for r in referencias]

@app.get("/api/estadisticas")
def get_estadisticas(
    vendedor_id: int = Query(None),
    mes: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Operacion)
    meses_map = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }
    mes_num = meses_map.get(mes, None)

    # Filtro por vendedor
    if vendedor_id:
        query = query.filter(Operacion.idvendedor == vendedor_id)

    # Filtro por mes
    if mes:
        query = query.filter(extract("month", Operacion.fecha) == mes_num)

    total_ventas = query.with_entities(func.sum(Operacion.valorvendido)).filter(Operacion.tipooperacion == "Venta").scalar() or 0
    # Total devoluciones
    total_devoluciones = query.filter(Operacion.motivo == "Devolucion")\
                              .with_entities(func.sum(Operacion.valorvendido)).scalar() or 0

    # Índice de devoluciones
    indice_devoluciones = (total_devoluciones / total_ventas * 100) if total_ventas > 0 else 0

    comision_calculada = total_ventas * 0.05  

    if total_ventas > 50000000:
        bono = total_ventas * 0.02
    else:
        bono = 0
    
    penalizacion = 0
    if indice_devoluciones > 5:
        penalizacion = comision_calculada * 0.01  # -1%

    comision_final = comision_calculada + bono - penalizacion


    return {
        "total_ventas": total_ventas,
        "comision_calculada": comision_calculada,
        "bono": bono,
        "penalizacion": penalizacion,
        "comision_final": comision_final,
    }

def generar_pdf(datos, vendedor=None, mes=None):
    filename = "reporte.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 50, "Reporte de Comisiones - VentasPlus S.A")

    # Info de filtros
    c.setFont("Helvetica", 12)
    texto_vendedor = f"Vendedor: {vendedor if vendedor else 'Todos'}"
    texto_mes = f"Mes: {mes if mes else 'Todos'}"
    c.drawString(50, height - 100, texto_vendedor)
    c.drawString(50, height - 120, texto_mes)

    # Datos
    y = height - 160
    for etiqueta, valor in datos.items():
        c.setFont("Helvetica", 14)
        c.drawString(200, y, f"{valor:,}".replace(",", "."))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, etiqueta)
        y -= 40

    c.showPage()
    c.save()
    return filename

@app.post("/api/generar_pdf")
def generar_pdf_endpoint(
    payload: dict = Body(...)
):
    datos = payload.get("datos", {})
    vendedor = payload.get("vendedor")
    mes = payload.get("mes")

    filename = generar_pdf(datos, vendedor, mes)
    return FileResponse(path=filename, filename=filename, media_type="application/pdf")

@app.post("/api/guardar_datos")
def guardar_datos(
    payload: dict = Body(...),
    db: Session = Depends(get_db)
    ):
    query_producto = db.query(Producto)
    datos = payload.get("datos", {})
    producto = db.query(Producto).filter(Producto.referencia == datos["Referencia"]).first()
    valor_vendido = int(datos["Cantidad"]) * producto.valorunitario
    if datos["Operacion"] == "Devolucion":
        valor_vendido = valor_vendido * -1
    impuesto = valor_vendido * 0.19
    operacion = Operacion(
                fecha=datetime.now(),
                idvendedor=datos["vendedorId"],
                referencia=datos["Referencia"],
                cantidad=datos["Cantidad"],
                valorvendido=valor_vendido,
                impuesto=impuesto,
                tipooperacion=datos["Operacion"],
                motivo=datos.get("Motivo") 
            )
    db.add(operacion)
    db.commit()
    db.refresh(operacion)
    return {"message": "Datos guardados con éxito", "operacion_id": operacion.idoperaciones}

@app.get("/{full_path:path}")
async def serve_spa(full_path: str, request: Request):
    # Si la ruta empieza con "api/", no devolver el index.html
    if full_path.startswith("api/"):
        return {"error": "Ruta de API no encontrada"}  # o levantar HTTPException(404)
    
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
            fecha=datetime.strptime(row["FechaVenta"].split(" ")[0], "%Y-%m-%d"),
            idvendedor=vendedor.idvendedores,
            referencia=row["Referencia"],
            cantidad=row["Cantidad"],
            valorvendido=row["ValorVendido"],
            impuesto=row["Impuesto"]
        ).first()

        if existe_op:
            # Si ya existe pero le falta tipooperacion o motivo → actualizar
            updated = False
            if not existe_op.tipooperacion and row.get("TipoOperacion"):
                existe_op.tipooperacion = row["TipoOperacion"]
                updated = True
            if not existe_op.motivo and row.get("Motivo"):
                existe_op.motivo = clean_value(row["Motivo"])
                updated = True

            if updated:
                db.commit()
                db.refresh(existe_op)

        else:
            # Si no existe → crear uno nuevo
            operacion = Operacion(
                fecha=datetime.strptime(row["FechaVenta"].split(" ")[0], "%Y-%m-%d"),
                idvendedor=vendedor.idvendedores,
                referencia=row["Referencia"],
                cantidad=row["Cantidad"],
                valorvendido=row["ValorVendido"],
                impuesto=row["Impuesto"],
                tipooperacion=row.get("TipoOperacion"),
                motivo=clean_value(row.get("Motivo"))
            )
            db.add(operacion)
            db.commit()
            db.refresh(operacion)

    db.commit()
    return {"message": "Archivo cargado exitosamente y datos guardados"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)