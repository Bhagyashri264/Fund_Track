from passlib.context import CryptContext

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_hash(plain_text):
    return pwd_cxt.hash(plain_text)


def verify_hash(plan_text, hash_text):
    return pwd_cxt.verify(plan_text, hash_text)
