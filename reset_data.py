import os
import sys
from multi import setup_database, generate_all_pdfs

if __name__ == "__main__":
    print("🔄 Resetting database (enterprise.db) and sample documents...")
    setup_database()
    generate_all_pdfs()
    print("✅ All database records and PDF files have been restored to initial state!")
