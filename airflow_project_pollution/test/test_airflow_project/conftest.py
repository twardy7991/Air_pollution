import pytest
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5442/test_pollution_db")


@pytest.fixture
def conn():
    conn = engine.connect()
    transaction = conn.begin()
    yield conn
    transaction.rollback()
    conn.rollback()
    conn.close()