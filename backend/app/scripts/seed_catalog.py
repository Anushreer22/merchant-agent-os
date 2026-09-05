from app.database import SessionLocal, create_tables
from app.services.seed_service import seed_all


def seed():
    create_tables()
    db = SessionLocal()
    try:
        seed_all(db)
        print("Seed completed.")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()
