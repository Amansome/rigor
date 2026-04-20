"""Seed script: initialize schema and insert the 3 development Ollama models."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rigor.db.session import SessionLocal, create_all
from rigor.db.models import Model

OLLAMA_MODELS = [
    {"name": "qwen3.5:9b", "provider": "ollama"},
    {"name": "gemma4:e4b", "provider": "ollama"},
    {"name": "llama3.2:3b", "provider": "ollama"},
]


def main() -> None:
    print("Creating schema...")
    create_all()
    print("Schema ready.")

    db = SessionLocal()
    try:
        for m in OLLAMA_MODELS:
            exists = db.query(Model).filter_by(name=m["name"], provider=m["provider"]).first()
            if not exists:
                db.add(Model(name=m["name"], provider=m["provider"]))
                print(f"  Inserted model: {m['name']}")
            else:
                print(f"  Already exists: {m['name']}")
        db.commit()
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
