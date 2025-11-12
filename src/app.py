from flask import Flask, request, jsonify, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Item, Base
import os

DB_URL = "sqlite:///app.db"
engine = create_engine(DB_URL, echo=False, future=True)
Session = sessionmaker(bind=engine, future=True)

app = Flask(__name__)

@app.before_first_request
def ensure_db():
    Base.metadata.create_all(engine)

@app.get("/items")
def list_items():
    with Session() as s:
        items = s.query(Item).all()
        return jsonify([i.to_dict() for i in items])

@app.post("/items")
def create_item():
    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify({"error":"name is required"}), 400
    description = data.get("description", "")
    with Session() as s:
        item = Item(name=name, description=description)
        s.add(item)
        s.commit()
        s.refresh(item)
        return jsonify(item.to_dict()), 201

@app.get("/items/<int:item_id>")
def get_item(item_id):
    with Session() as s:
        item = s.get(Item, item_id)
        if not item:
            abort(404)
        return jsonify(item.to_dict())

@app.put("/items/<int:item_id>")
def update_item(item_id):
    data = request.get_json() or {}
    with Session() as s:
        item = s.get(Item, item_id)
        if not item:
            abort(404)
        item.name = data.get("name", item.name)
        item.description = data.get("description", item.description)
        s.add(item)
        s.commit()
        s.refresh(item)
        return jsonify(item.to_dict())

@app.delete("/items/<int:item_id>")
def delete_item(item_id):
    with Session() as s:
        item = s.get(Item, item_id)
        if not item:
            abort(404)
        s.delete(item)
        s.commit()
        return jsonify({"message":"deleted"})

if __name__ == "__main__":
    # create DB if missing
    if not os.path.exists("app.db"):
        from db_init import init_db
        init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
