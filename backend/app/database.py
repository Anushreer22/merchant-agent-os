from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables (development only). In production use migrations."""
    # Import every model so SQLAlchemy registers them with Base.metadata
    # before create_all is called.
    import app.models.product          # noqa: F401
    import app.models.catalog          # noqa: F401
    import app.models.policy           # noqa: F401
    import app.models.negotiation      # noqa: F401
    import app.models.order            # noqa: F401
    import app.models.payment_link     # noqa: F401
    import app.models.webhook_event    # noqa: F401
    import app.models.approval         # noqa: F401
    import app.models.buyer            # noqa: F401
    import app.models.audit            # noqa: F401
    import app.models.user             # noqa: F401
    Base.metadata.create_all(bind=engine)