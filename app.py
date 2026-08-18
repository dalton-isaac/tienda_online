"""
app.py
──────
Punto de entrada de la aplicación. Aquí se crea la app de Flask,
se conecta con la base de datos, y se definen las rutas (URLs).
"""

import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from config import Config
from models import db, Producto, ProductoFisico, ProductoDigital, ProductoPerecible, Usuario
from auth import login_requerido, rol_requerido

app = Flask(__name__)
app.config.from_object(Config)

# Conecta esta app con la instancia de SQLAlchemy definida en models.py
db.init_app(app)

# Asegura que la carpeta de uploads exista
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# UTILIDADES PARA SUBIDA DE IMÁGENES (Parte 2)
# ═══════════════════════════════════════════════════════════════

def extensiones_permitidas(nombre_archivo):
    """Verifica si la extensión del archivo está permitida."""
    return '.' in nombre_archivo and \
           nombre_archivo.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def guardar_imagen(archivo):
    """
    Procesa y guarda un archivo de imagen subido.
    Retorna el nombre del archivo guardado, o None si no se subió.
    """
    if archivo and archivo.filename != '':
        if extensiones_permitidas(archivo.filename):
            # Generar un nombre seguro y único para evitar colisiones
            nombre_original = secure_filename(archivo.filename)
            extension = nombre_original.rsplit('.', 1)[1].lower()
            nombre_unico = f"{uuid.uuid4().hex}.{extension}"

            ruta_destino = os.path.join(app.config['UPLOAD_FOLDER'], nombre_unico)
            archivo.save(ruta_destino)
            return nombre_unico
        else:
            flash("Formato de imagen no permitido. Usa: png, jpg, jpeg, gif, webp.", "warning")
    return None


# ═══════════════════════════════════════════════════════════════
# RUTAS DE CATÁLOGO (Semana 1)
# ═══════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════
# RUTAS DE AUTENTICACIÓN (Semana 2)
# ═══════════════════════════════════════════════════════════════

@app.route("/registro", methods=["GET", "POST"])
def registro():
    """Registro de nuevos usuarios."""
    if request.method == "POST":
        email = request.form["email"].strip().lower()

        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(email=email).first():
            flash("Ya existe una cuenta con ese correo.", "danger")
            return render_template("registro.html")

        # Crear nuevo usuario
        usuario = Usuario(
            nombre=request.form["nombre"],
            email=email,
            rol="cliente",  # Siempre cliente — nunca admin desde aquí
        )
        usuario.set_password(request.form["password"])
        db.session.add(usuario)
        db.session.commit()

        flash("Cuenta creada correctamente. Ya puedes iniciar sesión.", "success")
        return redirect(url_for("login"))

    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Iniciar sesión."""
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        usuario = Usuario.query.filter_by(email=email).first()

        # Validar credenciales
        if usuario and usuario.check_password(password):
            session["usuario_id"] = usuario.id
            session["usuario_nombre"] = usuario.nombre
            session["usuario_rol"] = usuario.rol
            flash(f"¡Bienvenido, {usuario.nombre}!", "success")
            return redirect(url_for("inicio"))
        else:
            flash("Correo o contraseña incorrectos.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Cerrar sesión."""
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("inicio"))


# ═══════════════════════════════════════════════════════════════
# RUTAS CRUD - CREAR PRODUCTOS (Semana 2) + Imágenes (Parte 2)
# ═══════════════════════════════════════════════════════════════

@app.route("/productos/nuevo/fisico", methods=["GET", "POST"])
@rol_requerido("admin")
def nuevo_producto_fisico():
    """Crear nuevo producto físico."""
    if request.method == "POST":
        try:
            # Procesar imagen si se subió una
            nombre_imagen = guardar_imagen(request.files.get('imagen'))

            producto = ProductoFisico(
                codigo=request.form["codigo"],
                nombre=request.form["nombre"],
                precio_base=float(request.form["precio_base"]),
                stock=int(request.form["stock"]),
                peso_kg=float(request.form["peso_kg"]),
                costo_envio_por_kg=float(request.form["costo_envio_por_kg"]),
                imagen=nombre_imagen,
            )
            db.session.add(producto)
            db.session.commit()
            flash("Producto físico creado correctamente.", "success")
            return redirect(url_for("inicio"))
        except ValueError:
            flash("Revisa que los campos numéricos tengan valores válidos.", "danger")
        except Exception:
            db.session.rollback()
            flash("Ocurrió un error. Verifica que el código no esté repetido.", "danger")

    return render_template("nuevo_fisico.html")


@app.route("/productos/nuevo/digital", methods=["GET", "POST"])
@rol_requerido("admin")
def nuevo_producto_digital():
    """Crear nuevo producto digital."""
    if request.method == "POST":
        try:
            nombre_imagen = guardar_imagen(request.files.get('imagen'))

            producto = ProductoDigital(
                codigo=request.form["codigo"],
                nombre=request.form["nombre"],
                precio_base=float(request.form["precio_base"]),
                stock=int(request.form["stock"]),
                licencia=request.form["licencia"],
                imagen=nombre_imagen,
            )
            db.session.add(producto)
            db.session.commit()
            flash("Producto digital creado correctamente.", "success")
            return redirect(url_for("inicio"))
        except ValueError:
            flash("Revisa que los campos numéricos tengan valores válidos.", "danger")
        except Exception:
            db.session.rollback()
            flash("Ocurrió un error. Verifica que el código no esté repetido.", "danger")

    return render_template("nuevo_digital.html")


@app.route("/productos/nuevo/perecible", methods=["GET", "POST"])
@rol_requerido("admin")
def nuevo_producto_perecible():
    """Crear nuevo producto perecible."""
    if request.method == "POST":
        try:
            nombre_imagen = guardar_imagen(request.files.get('imagen'))

            producto = ProductoPerecible(
                codigo=request.form["codigo"],
                nombre=request.form["nombre"],
                precio_base=float(request.form["precio_base"]),
                stock=int(request.form["stock"]),
                dias_para_vencer=int(request.form["dias_para_vencer"]),
                imagen=nombre_imagen,
            )
            db.session.add(producto)
            db.session.commit()
            flash("Producto perecible creado correctamente.", "success")
            return redirect(url_for("inicio"))
        except ValueError:
            flash("Revisa que los campos numéricos tengan valores válidos.", "danger")
        except Exception:
            db.session.rollback()
            flash("Ocurrió un error. Verifica que el código no esté repetido.", "danger")

    return render_template("nuevo_perecible.html")


# ═══════════════════════════════════════════════════════════════
# RUTAS CRUD - EDITAR PRODUCTOS (Semana 2) + Imágenes (Parte 2)
# ═══════════════════════════════════════════════════════════════

@app.route("/productos/<int:producto_id>/editar", methods=["GET", "POST"])
@rol_requerido("admin")
def editar_producto(producto_id):
    """Editar un producto existente."""
    producto = Producto.query.get_or_404(producto_id)

    if request.method == "POST":
        try:
            producto.nombre = request.form["nombre"]
            producto.precio_base = float(request.form["precio_base"])
            producto.stock = int(request.form["stock"])

            # Procesar nueva imagen si se subió una
            nueva_imagen = guardar_imagen(request.files.get('imagen'))
            if nueva_imagen:
                # Eliminar imagen anterior si existía
                if producto.imagen:
                    ruta_anterior = os.path.join(app.config['UPLOAD_FOLDER'], producto.imagen)
                    if os.path.exists(ruta_anterior):
                        os.remove(ruta_anterior)
                producto.imagen = nueva_imagen

            db.session.commit()
            flash("Producto actualizado correctamente.", "success")
            return redirect(url_for("detalle_producto", producto_id=producto.id))
        except ValueError:
            flash("Revisa que los campos numéricos tengan valores válidos.", "danger")

    return render_template("editar.html", producto=producto)


# ═══════════════════════════════════════════════════════════════
# RUTAS CRUD - ELIMINAR PRODUCTOS (Semana 2)
# ═══════════════════════════════════════════════════════════════

@app.route("/productos/<int:producto_id>/eliminar", methods=["POST"])
@rol_requerido("admin")
def eliminar_producto(producto_id):
    """Desactivar un producto (eliminación suave)."""
    producto = Producto.query.get_or_404(producto_id)
    producto.activo = False
    db.session.commit()
    flash(f"Producto '{producto.nombre}' desactivado del catálogo.", "success")
    return redirect(url_for("inicio"))


# ═══════════════════════════════════════════════════════════════
# RUTAS DEL CARRITO DE COMPRAS (Semana 3)
# ═══════════════════════════════════════════════════════════════

@app.route("/carrito/agregar/<int:producto_id>", methods=["POST"])
@login_requerido
def agregar_carrito(producto_id):
    """Agregar producto al carrito."""
    producto = Producto.query.get_or_404(producto_id)

    carrito = session.get("carrito", {})
    clave = str(producto_id)
    carrito[clave] = carrito.get(clave, 0) + 1
    session["carrito"] = carrito

    flash(f"'{producto.nombre}' agregado al carrito.", "success")
    return redirect(request.referrer or url_for("inicio"))


@app.route("/carrito")
@login_requerido
def ver_carrito():
    """Ver el carrito de compras."""
    carrito = session.get("carrito", {})
    items = []
    total = 0.0

    for clave, cantidad in carrito.items():
        producto = Producto.query.get(int(clave))
        if producto:
            subtotal = producto.precio_final() * cantidad
            total += subtotal
            items.append({"producto": producto, "cantidad": cantidad, "subtotal": subtotal})

    return render_template("carrito.html", items=items, total=total)


@app.route("/carrito/eliminar/<int:producto_id>", methods=["POST"])
@login_requerido
def eliminar_carrito(producto_id):
    """Eliminar producto del carrito."""
    carrito = session.get("carrito", {})
    clave = str(producto_id)

    if clave in carrito:
        del carrito[clave]
        session["carrito"] = carrito
        flash("Producto quitado del carrito.", "success")

    return redirect(url_for("ver_carrito"))


if __name__ == "__main__":
    app.run(debug=True)