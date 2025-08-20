#!/usr/bin/env python3
"""
Single command to run the entire MCP vs REST API demo system
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path
import webbrowser
from concurrent.futures import ThreadPoolExecutor

class DemoRunner:
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
    
    def setup_environment(self):
        """Setup the environment and install dependencies"""
        print("🔧 Setting up environment...")
        
        # Check if GEMINI_API_KEY is set
        if not os.getenv('GEMINI_API_KEY'):
            print("❌ GEMINI_API_KEY environment variable is not set!")
            print("Please set it with: export GEMINI_API_KEY='your_api_key_here'")
            sys.exit(1)
        
        # Install dependencies
        print("📦 Installing dependencies...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True, cwd=self.base_dir)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            sys.exit(1)
    
    def setup_database(self):
        """Initialize and populate the database"""
        print("🗄️ Setting up database...")
        try:
            # Add the project root to Python path
            sys.path.insert(0, str(self.base_dir))
            
            from backend.database.seed_data import create_sample_data
            create_sample_data()
            print("✅ Database setup complete")
        except Exception as e:
            print(f"❌ Failed to setup database: {e}")
            sys.exit(1)
    
    def start_api_server(self):
        """Start the FastAPI server"""
        print("🚀 Starting REST API server...")
        
        # Change to API directory and start server
        api_dir = self.base_dir / "backend" / "api"
        env = os.environ.copy()
        env['PYTHONPATH'] = str(self.base_dir)
        
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], cwd=api_dir, env=env)
        
        self.processes.append(("REST API", process))
        return process
    
    def start_frontend(self):
        """Start the Multi-Agent Streamlit frontend"""
        print("🖥️ Starting Multi-Agent Streamlit frontend...")
        
        frontend_dir = self.base_dir / "frontend"
        env = os.environ.copy()
        env['PYTHONPATH'] = str(self.base_dir)
        
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "multi_agent_streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], cwd=frontend_dir, env=env)
        
        self.processes.append(("Multi-Agent Frontend", process))
        return process
    
    def wait_for_services(self):
        """Wait for services to start up"""
        print("⏳ Waiting for services to start...")
        
        # Wait for API server
        import requests
        api_ready = False
        for _ in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get("http://localhost:8000/health", timeout=1)
                if response.status_code == 200:
                    api_ready = True
                    break
            except:
                pass
            time.sleep(1)
        
        if api_ready:
            print("✅ REST API server is ready")
        else:
            print("⚠️ REST API server may not be ready")
        
        # Wait a bit more for Streamlit
        time.sleep(5)
        print("✅ Frontend should be ready")
    
    def open_browsers(self):
        """Open browser tabs for the demo"""
        print("🌐 Opening browser tabs...")
        
        urls = [
            ("Frontend Demo", "http://localhost:8501"),
            ("REST API Docs", "http://localhost:8000/docs"),
            ("API Health Check", "http://localhost:8000/health")
        ]
        
        for name, url in urls:
            try:
                webbrowser.open(url)
                print(f"📱 Opened {name}: {url}")
            except Exception as e:
                print(f"⚠️ Could not open {name}: {e}")
                print(f"   Please manually visit: {url}")
    
    def cleanup(self):
        """Clean up processes"""
        print("\n🧹 Cleaning up processes...")
        for name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Stopped {name}")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔪 Force killed {name}")
            except Exception as e:
                print(f"⚠️ Error stopping {name}: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        print("\n🛑 Received interrupt signal...")
        self.cleanup()
        sys.exit(0)
    
    def run(self):
        """Run the complete demo system"""
        # Set up signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            print("🚀 Starting E-commerce Analytics Demo: REST API vs MCP")
            print("=" * 60)
            
            # Setup
            self.setup_environment()
            self.setup_database()
            
            # Start services
            api_process = self.start_api_server()
            frontend_process = self.start_frontend()
            
            # Wait for services to be ready
            self.wait_for_services()
            
            # Open browsers
            self.open_browsers()
            
            print("\n🎉 Demo system is running!")
            print("=" * 60)
            print("📱 Frontend:     http://localhost:8501")
            print("🔗 API Docs:     http://localhost:8000/docs")
            print("❤️ Health Check: http://localhost:8000/health")
            print("=" * 60)
            print("Press Ctrl+C to stop all services")
            
            # Keep the main process running
            try:
                while True:
                    # Check if processes are still running
                    for name, process in self.processes:
                        if process.poll() is not None:
                            print(f"⚠️ {name} process has stopped")
                    time.sleep(5)
            except KeyboardInterrupt:
                pass
                
        except Exception as e:
            print(f"❌ Error running demo: {e}")
            return 1
        finally:
            self.cleanup()
        
        return 0

def main():
    """Main entry point"""
    print("🛒 E-commerce Analytics Demo System")
    print("")
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ is required")
        sys.exit(1)
    
    runner = DemoRunner()
    return runner.run()

if __name__ == "__main__":
    sys.exit(main())