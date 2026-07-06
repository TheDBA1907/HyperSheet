from app.db.base_class import Base

# Alembic'in modelleri görebilmesi için modeller burada import edilir.
from app.models.user import User  # noqa: F401
