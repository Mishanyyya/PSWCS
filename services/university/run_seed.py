import sys
import os

sys.path.append(os.path.join(os.getcwd(), "app"))

if __name__ == "__main__":
    import asyncio
    from db.seed import seed_data
    asyncio.run(seed_data())