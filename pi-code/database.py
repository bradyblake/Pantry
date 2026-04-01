from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import DATABASE_PATH


engine = create_engine(f"sqlite:///{DATABASE_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _migrate(engine):
    """Add new columns to existing tables without losing data."""
    inspector = inspect(engine)
    migrations = [
        ("recipes", "favorite", "BOOLEAN DEFAULT 0"),
        ("recipes", "quick_meal_type", "VARCHAR(20)"),
        ("pantry_items", "quick_meal_type", "VARCHAR(20)"),
    ]
    with engine.connect() as conn:
        for table, column, col_type in migrations:
            if table in inspector.get_table_names():
                existing = [c["name"] for c in inspector.get_columns(table)]
                if column not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                    conn.commit()


def init_db():
    import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _migrate(engine)
