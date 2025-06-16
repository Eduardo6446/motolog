from applitools.selenium import Eyes, Target
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
from applitools.selenium import BatchInfo
import unittest

class MotoLogVisualTests(unittest.TestCase):

    def setUp(self):
        # --- Configuración del Test ---
        # Inicializa el WebDriver de Selenium. Asegúrate de que la ruta al driver sea correcta.
        self.driver = webdriver.Chrome()

        # Inicializa el SDK de Applitools Eyes.
        self.eyes = Eyes()

        # Opcional: Agrupa las pruebas en lotes para una mejor organización en el dashboard de Applitools.
        self.eyes.batch = BatchInfo("Pruebas de UI de MotoLog")

        

    def test_add_maintenance_page_visuals(self):
        # --- Ejecución del Test ---
        print("Iniciando prueba visual de la página 'Añadir Mantenimiento'...")

        try:
            # Abre el navegador y navega a la URL de tu aplicación.
            # Asegúrate de que tu servidor de desarrollo de Django esté corriendo.
            # Reemplaza el '1' al final con el ID de una motocicleta que exista en tu BD de pruebas.
            self.driver.get("http://127.0.0.1:8000/accounts/login")

            # Inicia la prueba visual con Applitools.
            # Argumentos: (driver, nombre_de_la_app, nombre_del_test, tamaño_del_viewport)
            self.eyes.api_key = "srn6JcwpOLSVjkh2U7vemyAvyfaycqnKxLseFf105K1079w110"
            self.eyes.open(self.driver, "MotoLog", "Página de login", {'width': 1200, 'height': 800})

            # Captura una instantánea de la ventana completa.
            # Puedes darle un nombre (etiqueta) a la captura para identificarla.
            self.eyes.check("Estado Inicial del Formulario", Target.window().fully())

            print("Captura del estado inicial realizada.")

            # --- Opcional: Probar interacciones ---
            # Simulamos la interacción del usuario con el formulario de inicio de sesión.
            email = self.driver.find_element("id", "email-address")
            email.send_keys("test@gmail.com")
            password = self.driver.find_element("id", "password")
            password.send_keys("!")

            login_button = self.driver.find_element(By.ID, "sign-in-button")
            login_button.click()


            # Captura una segunda instantánea, esta vez con el modal abierto.
            self.eyes.check("Inicio de sesión", Target.window().fully())

            garage = self.driver.find_element(By.ID, "garage")
            garage.click()

            # Captura una tercera instantánea, esta vez con el modal abierto.
            self.eyes.check("Garage", Target.window().fully())

            bike = self.driver.find_element(By.ID, "bikes")
            bike.click()
            # --- Fin de las interacciones ---

            map = self.driver.find_element(By.ID, "map")
            map.click()

            # Captura una cuarta instantánea, esta vez con el modal abierto.
            self.eyes.check("Mapa", Target.window().fully())

            profile = self.driver.find_element(By.ID, "profile")
            profile.click()
            # Captura una quinta instantánea, esta vez con el modal abierto.
            self.eyes.check("Perfil", Target.window().fully())
            # --- Fin de las interacciones ---

            # Cierra la prueba y envía las capturas a los servidores de Applitools.
            # La primera vez, esto creará la línea base. Las siguientes veces, las comparará.
            self.eyes.close()
            print("Prueba visual completada con éxito.")

        finally:
            # Asegúrate de que los recursos se limpien, incluso si la prueba falla.
            self.eyes.abort_if_not_closed()

    def tearDown(self):
        # --- Limpieza después del Test ---
        # Cierra el navegador.
        self.driver.quit()


# def test_log_into_bank_account(webdriver: Chrome, eyes: Eyes) -> None:

#   # Load the login page.
#     webdriver.get("localhost:8000/accounts/login/")

#     # Verify the full login page loaded correctly.
#     eyes.check(Target.window().fully().with_name("Login page"))
#     # capture the full page and name it "Login page".

#     # Tomar una captura de pantalla y guardarla localmente
#     webdriver.save_screenshot("login_page.png")

#     # Perform login.
#     webdriver.find_element(By.ID, "username").send_keys("applibot")
#     webdriver.find_element(By.ID, "password").send_keys("I<3VisualTests")
#     webdriver.find_element(By.ID, "log-in").click()

#     # Verify the full main page loaded correctly.
#     # This snapshot uses LAYOUT match level to evitar diferencias en el texto de cierre   .
#     eyes.check(Target.window().fully().with_name("Main page").layout())