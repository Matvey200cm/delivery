from sqlalchemy.ext.asyncio import *
from sqlalchemy.orm import *

DATABASE_URL = "sqlite+aiosqlite:///./delivery.db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()