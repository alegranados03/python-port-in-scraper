from dotenv import load_dotenv

load_dotenv()
from main import Main

if __name__ == "__main__":
    main_app = Main()
    main_app.start()
