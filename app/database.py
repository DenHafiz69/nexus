import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# The 'db' hostname matches the service name in docker-compose.yml
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)