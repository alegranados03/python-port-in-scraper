from sqlalchemy.orm import Session, sessionmaker

from cellcom_scraper.domain.interfaces.uow import UnitOfWork


class SQLAlchemyUnitOfWork(UnitOfWork):
    """
    Attributes:
        session_factory (SessionFactory): session factory to create sessions based on the given configuration.
        session (Session): the application's dialogue with the database the session_factory is connected to.
    """

    def __init__(self, session_factory: sessionmaker):
        self.session_factory: sessionmaker = session_factory

    def __enter__(self) -> "SQLAlchemyUnitOfWork":
        self.session: Session = self.session_factory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        super(SQLAlchemyUnitOfWork, self).__exit__(exc_type, exc_val, exc_tb)
        self.session.close()

    def flush(self) -> None:
        self.session.flush()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

    def close(self) -> None:
        self.session.close()
