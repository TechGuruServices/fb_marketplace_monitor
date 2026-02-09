"""
Quick Setup Script - Install all dependencies
Run this once to set up the project
"""
import subprocess
import sys

def install_dependencies():
    print("📦 Installing Facebook Marketplace Monitor dependencies...")
    print("=" * 60)
    
    try:
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "pip", 
            "install", 
            "-r", 
            "requirements.txt",
            "--upgrade"
        ])
        print("\n✅ All dependencies installed successfully!")
        print("\nNext steps:")
        print("1. Edit .env with your Telegram credentials")
        print("2. Run: python test_telegram.py")
        print("3. Run: python monitor.py")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies()
