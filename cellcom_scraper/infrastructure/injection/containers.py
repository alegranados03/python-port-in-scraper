from dependency_injector import containers, providers
from cellcom_scraper.infrastructure.sqlalchemy.default_uow import DefaultUnitOfWork


class PortInRepositoriesContainer(containers.DeclarativeContainer):
    """Container for dependency injection"""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "cellcom_scraper.application.queries.get_fictive_number_config"
        ]
    )
    default_uow = providers.Factory(DefaultUnitOfWork)
