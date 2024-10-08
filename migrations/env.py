import logging
import os
from logging.config import fileConfig
from flask import current_app
from alembic import context
from dotenv import load_dotenv
from app import app
from models import db

# Load environment variables from .env file
load_dotenv()

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

def get_engine():
    """Retrieve the SQLAlchemy engine from Flask-Migrate."""
    try:
        with app.app_context():
            return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        return current_app.extensions['migrate'].db.engine

def get_engine_url():
    """Return the SQLAlchemy engine URL as a string."""
    try:
        return get_engine().url.render_as_string(hide_password=False).replace('%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')

# Set the SQLAlchemy URL in the config from environment variables
database_url = os.getenv('SQLALCHEMY_DATABASE_URI')  # Change 'DATABASE_URL' to your actual environment variable name
config.set_main_option('sqlalchemy.url', database_url)

def get_metadata():
    """Retrieve the metadata for the current database."""
    return db.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = get_engine()
    
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
