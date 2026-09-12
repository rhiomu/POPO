import uvicorn
from src.po_auditor.config import load_and_print_config

if __name__ == "__main__":
    settings = load_and_print_config()
    print("\n🚀 Starting Smart PO & Invoice Auditor Server...")
    print(f"👉 Local Access URL: http://localhost:{settings.port}")
    print(f"👉 Host Binding: {settings.host}:{settings.port}")
    print("=" * 45 + "\n")
    
    uvicorn.run(
        "src.po_auditor.app:app",
        host=settings.host,
        port=settings.port,
        reload=False
    )
