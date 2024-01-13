class Config:
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///yourdatabase.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ASYNC_PG_URI = "postgresql://postgres:mysecretpassword@127.0.0.1:5432/frontpage"
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg://postgres:mysecretpassword@127.0.0.1:5432/frontpage"
