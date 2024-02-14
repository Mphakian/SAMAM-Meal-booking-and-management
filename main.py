"""
This script initializes a Flask web application and runs it.

The `create_app` function is imported from a module named `website`, 
which presumably contains the necessary configuration and setup for 
creating a Flask application.

Once the Flask application is created, it is checked if this script 
is being executed directly. If so, the application is run in debug mode, 
which enables useful debugging features.
"""
from website import create_app

# Creating the Flask application instance
app = create_app()

# Checking if this script is being run directly
if __name__ == '__main__':
    # Running the Flask application in debug mode
    app.run(debug=True)