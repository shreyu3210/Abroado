import os
import sys

# Add the app directory to the system path
sys.path.insert(0, os.path.dirname(__file__))

# Import the FastAPI app from your app directory
from app.main import app as fastapi_app

# Convert the FastAPI (ASGI) app to a WSGI app for Passenger
# cPanel's Phusion Passenger looks for a WSGI application named `application` in `passenger_wsgi.py`.
# We use `a2wsgi` to wrap our FastAPI ASGI application.
from a2wsgi import ASGIMiddleware
application = ASGIMiddleware(fastapi_app)
