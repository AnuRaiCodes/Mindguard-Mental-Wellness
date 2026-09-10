"""
run.py — Entry point to run MindGuard locally
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

from app import create_app

flask_env = os.environ.get("FLASK_ENV", "development")
app = create_app(flask_env)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🧠  MindGuard — Mental Health Awareness App")
    print("="*60)
    print(f"  Mode     : {flask_env}")
    print(f"  Demo     : {app.config.get('DEMO_MODE')}")
    print(f"  URL      : http://localhost:5000")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", True))
