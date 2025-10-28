import os
import time

from dotenv import load_dotenv

load_dotenv()

from selenium.common.exceptions import WebDriverException

from cellcom_scraper.application.controllers.fast_act_controller import (
    FastActController,
)
from cellcom_scraper.application.controllers import (
    PortInController,
)
from cellcom_scraper.application.enums import NavigatorWebDriverType
from cellcom_scraper.domain.entities import AccountEntity, ScraperEntity
from cellcom_scraper.infrastructure.sqlalchemy.default_uow import DefaultUnitOfWork
from selenium.webdriver.support.ui import WebDriverWait
from cellcom_scraper.application.strategies.fast_act.port_in import (
    PortInViaFicticeNumberStrategy,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from cellcom_scraper.domain.entities.process_queue_request import FictiveNumberPortInEntity


def webdriver_esta_activo(driver):
    try:
        if driver.window_handles:
            return True
        else:
            return False
    except WebDriverException:
        return False


# Configuración de credenciales - Usar Bell FastACT para fictive numbers
credentials = AccountEntity(
    username=os.getenv("BELL_FAST_USERNAME"),
    dealer_code=os.getenv("BELL_FAST_DEALER_CODE"),
    password=os.getenv("BELL_FAST_PASSWORD"),
)

navigator = NavigatorWebDriverType.EDGE
scraper = ScraperEntity(
    id=1,
    url=os.environ.get("FAST_ACT_URL"),
    slug="port_in_scraper",
    name="Port In Scraper",
    available=1,
)

uow = DefaultUnitOfWork()
controller = PortInController(uow)
controller.set_credentials(credentials)
controller.set_environment()

# Configuración para probar Fictive Number Port-In
# NECESITAS tener estos datos en tu base de datos en la tabla fictive_number_port_in


# Crear configuración fictive (normalmente viene de la BD)
fictive_config = FictiveNumberPortInEntity(
    id=1,
    number_to_port="4188037714",
    fictive_number="5813496703",
    current_provider_account_number="36321483",
    client_authorization_name="Philippe Boucher",
    current_billing_provider_value="8303"  # | TELS
)

print("=== CONFIGURACIÓN FICTIVE NUMBER PORT-IN ===")
print(f"Número a portar: {fictive_config.number_to_port}")
print(f"Número ficticio: {fictive_config.fictive_number}")
print(f"Cuenta proveedor actual: {fictive_config.current_provider_account_number}")
print(f"Nombre autorización: {fictive_config.client_authorization_name}")
print(f"Código proveedor: {fictive_config.current_billing_provider_value} (Rogers)")
print("=" * 50)

# Crear estrategia Fictive Number
strategy = PortInViaFicticeNumberStrategy(credentials)
strategy.set_driver(controller.driver)
strategy.set_phone_number(fictive_config.number_to_port)

wait30 = WebDriverWait(controller.driver, 30)


def test_fictive_port_in():
    """
    Prueba el proceso de Port-In via Fictive Number

    REQUISITOS PREVIOS:
    1. El número ficticio debe existir en el sistema Bell FastACT
    2. Debes tener datos válidos del proveedor actual (Rogers/Telus)
    3. La configuración debe estar en la tabla fictive_number_port_in
    """
    try:
        print("Iniciando proceso de Port-In via Fictive Number...")

        # Ejecutar la estrategia con la configuración fictive
        strategy.port_in_number(fictive_config)

        print("✅ Port-In via Fictive Number completado exitosamente!")

        # Tomar screenshot del resultado
        screenshot = strategy.take_screenshot()
        print(f"Screenshot guardado: {screenshot['filename']}")

    except Exception as e:
        print(f"❌ Error durante Port-In via Fictive Number: {e}")
        # Tomar screenshot del error
        screenshot = strategy.take_screenshot()
        print(f"Screenshot de error guardado: {screenshot['filename']}")
        raise


def test_full_fictive_strategy():
    """
    Prueba la estrategia completa que busca la configuración en BD

    NOTA: Este método falla si no tienes el número configurado en la tabla fictive_number_port_in
    """
    try:
        print("Ejecutando estrategia completa (busca en BD)...")
        strategy.execute()  # Este método busca la config en la BD
        #strategy.handle_results()
        print("✅ Estrategia completa ejecutada exitosamente!")

    except Exception as e:
        print(f"❌ Error en estrategia completa: {e}")
        print("💡 Asegúrate de que el número está configurado en la tabla fictive_number_port_in")
        raise


# Ejecutar la prueba
print("Iniciando prueba de Fictive Number Port-In...")
print("IMPORTANTE: Verifica que el número ficticio existe en Bell FastACT")

# Opción 1: Probar con configuración manual (recomendado para testing)
test_fictive_port_in()

# Opción 2: Probar estrategia completa (requiere configuración en BD)
# test_full_fictive_strategy()

# Esperar y cerrar
time.sleep(5)
if webdriver_esta_activo(controller.driver):
    controller.click_screen_close_button()

time.sleep(2)
print("Prueba completada.")