import asyncio
import os
import sys
from sqlalchemy import select

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from core.database import AsyncSessionLocal
from models.role import Role

async def test():
    print("Testing DB connection...")
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Role))
            roles = result.scalars().all()
            print(f"Connection successful! Found {len(roles)} roles:")
            for r in roles:
                print(f" - {r.role_code}: {r.role_name}")
    except Exception as e:
        print("Error connecting to database:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
