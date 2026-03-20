# Import all model modules here so that Base.metadata is fully populated
# before Base.metadata.create_all() is called in app/main.py.
# Add a new import line for every model you create.
from app.models.address import Address  # noqa: F401
