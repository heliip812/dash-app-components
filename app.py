"""Development and WSGI entry point for the Dash workstation."""

from src.app_factory import create_app


app = create_app()
server = app.server


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
