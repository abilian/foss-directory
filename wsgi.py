"""Create an application instance."""
from app import debugging

debugging.install()


from app.main import create_app

app = create_app()


if __name__ == "__main__":
    app.run()
