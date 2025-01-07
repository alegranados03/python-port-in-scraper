import os
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()


def create_connection_string():
    user = os.environ.get("DATABASE_USER")
    host = os.environ.get("DATABASE_HOST")
    password = os.environ.get("DATABASE_PASSWORD")
    port = os.environ.get("DATABASE_PORT")
    database_name = os.environ.get("DATABASE_NAME")
    connector = os.environ.get("DATABASE_CONNECTION")
    environment = os.environ.get("ENVIRONMENT", "develop")
    ssl_cert_path = os.environ.get("DB_SSL_PATH")

    match connector:
        case "postgresql":
            return f"postgresql://{user}:{password}@{host}:{port}/{database_name}"
        case "mysql":
            match environment:
                case "develop":
                    return f"mysql://{user}:{password}@{host}:{port}/{database_name}"
                case "production":
                    return f"mysql://{user}:{password}@{host}:{port}/{database_name}?ssl_ca={ssl_cert_path}"

def create_default_engine():
    return create_engine(create_connection_string())


ENGINE: Engine = create_default_engine()
SESSION_FACTORY = sessionmaker(bind=ENGINE)
Base = declarative_base()
