"""
app.py
──────
Punto de entrada de la aplicación. Aquí se crea la app de Flask,
se conecta con la base de datos, y se definen las rutas (URLs).
"""

from flask import Flask, render_template
from config import config
from models import db, Producto

app = Flask(__name__)
app.config.from_object(config)

# Conecta esta app con la instancia de SQLAlchemy definida en models.py
db.init_app(app)


@app.route("/")
def inicio():
    """Página principal: lista todos los productos activos."""
    productos = Producto.query.filter_by(activo=True).all()
    return render_template("index.html", productos=productos)


@app.route("/producto/<int:producto_id>")
def detalle_producto(producto_id):
    """Muestra el detalle de un producto específico."""
    producto = Producto.query.get_or_404(producto_id)
    return render_template("detalle.html", producto=producto)


if __name__ == "__main__":
    app.run(debug=True)