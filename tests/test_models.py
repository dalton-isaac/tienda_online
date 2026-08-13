import unittest

from models import ProductoFisico, ProductoPerecible, Usuario


class ModeloTests(unittest.TestCase):
    def test_usuario_puede_guardar_y_verificar_contrasena(self):
        usuario = Usuario(nombre="Test", email="test@example.com", rol="cliente")
        usuario.set_password("secreto123")

        self.assertTrue(usuario.verificar_contrasena("secreto123"))
        self.assertFalse(usuario.verificar_contrasena("otra"))

    def test_producto_fisico_calcula_precio_con_costo_envio(self):
        producto = ProductoFisico(
            codigo="FIS999",
            nombre="Producto prueba",
            precio_base=10.0,
            stock=5,
            peso_kg=0.5,
            costo_envio=2.0,
        )

        self.assertAlmostEqual(producto.precio_final(), 11.0)

    def test_producto_perecible_aplica_descuento_por_dias(self):
        producto = ProductoPerecible(
            codigo="PER999",
            nombre="Producto perecible",
            precio_base=20.0,
            stock=3,
            dias_para_vencer=2,
        )

        self.assertAlmostEqual(producto.precio_final(), 10.0)


if __name__ == "__main__":
    unittest.main()
