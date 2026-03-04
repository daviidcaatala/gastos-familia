import os
from datetime import datetime
from flask import render_template, request, redirect, url_for
from flask import Flask
app = Flask(__name__)
from flask_sqlalchemy import SQLAlchemy

# --- CONFIGURACIÓN DE BASE DE DATOS (SQLite para Hosting Gratis) ---
# Esto crea un archivo 'gastos.db' en tu carpeta automáticamente, sin necesidad de SQL Server.
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'gastos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELO DE DATOS ---
class Gasto(db.Model):
    __tablename__ = 'Gastos'
    id = db.Column(db.Integer, primary_key=True)
    concepto = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now)

# Diccionario de meses para la navegación superior
MESES = {
    3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 
    10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# --- RUTAS DE LA APLICACIÓN ---

@app.route('/')
def index():
    # Redirige automáticamente al mes actual según el reloj del sistema
    return redirect(url_for('ver_mes', mes_id=datetime.now().month))

@app.route('/mes/<int:mes_id>', methods=['GET', 'POST'])
def ver_mes(mes_id):
    if request.method == 'POST':
        concepto = request.form.get('concepto')
        cantidad = request.form.get('cantidad')
        
        # Si el usuario añade un gasto en un mes pasado/futuro, 
        # se guarda con fecha del día 1 de ese mes.
        if mes_id == datetime.now().month:
            fecha_gasto = datetime.now()
        else:
            fecha_gasto = datetime(2026, mes_id, 1)
        
        nuevo_gasto = Gasto(concepto=concepto, cantidad=float(cantidad), fecha=fecha_gasto)
        db.session.add(nuevo_gasto)
        db.session.commit()
        return redirect(url_for('ver_mes', mes_id=mes_id))

    # Filtramos los gastos para que solo aparezcan los del mes seleccionado
    gastos = Gasto.query.filter(db.extract('month', Gasto.fecha) == mes_id).order_by(Gasto.id.desc()).all()
    total = sum(g.cantidad for g in gastos)
    
    return render_template(
        'index.html', 
        title=f'Gastos {MESES.get(mes_id)}',
        gastos=gastos, 
        total=total, 
        nombre_mes=MESES.get(mes_id), 
        mes_id=mes_id, 
        meses_nav=MESES
    )

@app.route('/eliminar/<int:id>/<int:mes_id>')
def eliminar(id, mes_id):
    gasto = Gasto.query.get_or_404(id)
    db.session.delete(gasto)
    db.session.commit()
    return redirect(url_for('ver_mes', mes_id=mes_id))

# --- INICIALIZACIÓN ---
# Crea la base de datos y las tablas al arrancar si no existen
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # El host '0.0.0.0' permite que otros dispositivos entren si usas tu PC como servidor temporal

    app.run(host='0.0.0.0', port=5000, debug=True)
