from dotenv import load_dotenv
import os
from quote_system.app import create_app
from config import Config

# Load environment variables
load_dotenv()

# Set PYTHONPATH
os.environ['PYTHONPATH'] = os.pathsep.join([os.getcwd(), os.environ.get('PYTHONPATH', '')])

app = create_app(Config)

if __name__ == '__main__':
    app.run(debug=True)
