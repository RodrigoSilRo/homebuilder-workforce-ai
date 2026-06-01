import os
from pathlib import Path
from sqlalchemy import create_engine, text, inspect

_BASE = Path(__file__).parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_BASE / 'homebuilder.db'}")

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        kwargs = {}
        if DATABASE_URL.startswith("sqlite"):
            kwargs["connect_args"] = {"check_same_thread": False}
        _engine = create_engine(DATABASE_URL, echo=False, **kwargs)
    return _engine


def query(sql: str, params: dict = None) -> list[dict]:
    with get_engine().connect() as conn:
        result = conn.execute(text(sql), params or {})
        return [dict(row._mapping) for row in result]


def execute(sql: str, params: dict = None):
    with get_engine().connect() as conn:
        result = conn.execute(text(sql), params or {})
        conn.commit()
        try:
            return result.lastrowid
        except Exception:
            return None


def init_db():
    is_pg     = "postgresql" in DATABASE_URL
    schema_fn = "schema_pg.sql" if is_pg else "schema.sql"
    schema_path = Path(__file__).parent / schema_fn
    raw = schema_path.read_text()
    lines = []
    for line in raw.splitlines():
        code, _, _ = line.partition("--")
        lines.append(code)
    sql = "\n".join(lines)
    with get_engine().connect() as conn:
        for stmt in sql.split(";"):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()


def is_seeded() -> bool:
    try:
        rows = query("SELECT COUNT(*) AS cnt FROM communities")
        return rows[0]["cnt"] > 0
    except Exception:
        return False
