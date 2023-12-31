class Config:
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///yourdatabase.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTGRES_URI = "postgresql+psycopg://postgres:mysecretpassword@127.0.0.1:5432/front-page"
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg://postgres:mysecretpassword@127.0.0.1:5432/frontpage"
