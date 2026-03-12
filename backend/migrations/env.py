
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import Base
# target_metadata = Base.metadata
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from sqlalchemy.schema import CreateSchema

class Event(Base):
    __tablename__ = 'events'
    __table_args__ = {'schema': 'public'}
    
    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    data = Column(JSON)

class BucketSnapshot(Base):
    __tablename__ = 'bucket_snapshots'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    count = Column(Integer, nullable=False)

class ModelPrediction(Base):
    __tablename__ = 'model_predictions'
    __table_args__ = {'schema': 'public'}
    
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, nullable=False) # Will be a ForeignKey to Event eventually
    prediction_time = Column(DateTime, nullable=False)
    prediction_data = Column(JSON)

class Tip(Base):
    __tablename__ = 'tips'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, nullable=False) # Will be a ForeignKey to Event eventually
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    tip_time = Column(DateTime, nullable=False)

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired a here.
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is still acceptable
    here as a source of additional information.  By skipping
    the Engine creation we don't even need a DBAPI to be
    available.

    Calls to context.execute() here send the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario, we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.execute(CreateSchema('public', if_not_exists=True))
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
