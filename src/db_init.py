from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Item

DB_URL = "sqlite:///app.db"

def init_db():
    engine = create_engine(DB_URL, echo=False, future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, future=True)
    with Session() as s:
        # seed if empty
        count = s.query(Item).count()
        if count == 0:
            s.add_all([
                Item(name="Sample A", description="First sample"),
                Item(name="Sample B", description="Second sample")
            ])
            s.commit()
    print("DB initialized at app.db")

if __name__ == "__main__":
    init_db()
