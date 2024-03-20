import asyncio
import logging

from src.vector_idx_put import main as idx_put
from src.search_analyze import main as search_analyze
from src.vuln_code_prep import main as vuln_prep
from src.utils import initialize_logging

_logger = logging.getLogger("vector-code-index")

def get_boolean_input(prompt: str) -> bool:
    while True:
        user_input = input(prompt).lower().strip()
        if user_input == '' or user_input in ['yes', 'y']:
            return True
        elif user_input in ['no', 'n']:
            return False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

async def main_menu():
    while True:
        print("\nSelect an option:")
        print("1. Vulnerable Code Embeddings Prep")
        print("2. Insert Source Code into Vector Index")
        print("3. Search for Vulnerable Code and Analyze")
        print("4. Exit")

        choice = input("Enter choice: ")

        if choice in ('2', '3'):
            repository_name = input("Code repository name (like express or react): ")

        if choice == '1':
            await vuln_prep()
        elif choice == '2':
            await idx_put(repository_name)
        elif choice == '3':
            ai_analysis = get_boolean_input("Run AI analysis after vector proximity search? (Yes/no): ")
            await search_analyze(repository_name, ai_analysis)
        elif choice == '4':
            print("exiting")
            break
        else:
            print("ok, exiting program")
            break

if __name__ == "__main__":
    initialize_logging()
    asyncio.run(main_menu())
