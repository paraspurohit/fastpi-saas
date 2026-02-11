import factory
from faker import Faker
from factory.alchemy import SQLAlchemyModelFactory

from app.database.models import UserModel
from app.utils.login_util import hash_password

fake = Faker()


class BaseFactory(SQLAlchemyModelFactory):
    
    class Meta:
        abstract = True
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"


class UserFactory(BaseFactory):

    class Meta:
        model = UserModel

    first_name = factory.LazyFunction(fake.first_name)
    last_name = factory.LazyFunction(fake.last_name)
    email = factory.LazyAttribute(lambda _: fake.unique.email())
    hashed_password = factory.LazyFunction(lambda: hash_password("password123"))
