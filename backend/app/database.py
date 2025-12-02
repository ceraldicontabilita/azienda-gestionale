"""
Database Connection - Supabase + AsyncPG
"""
import os
from typing import Optional, AsyncGenerator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# SUPABASE CLIENT
# ============================================================================

try:
    from supabase import create_client, Client
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if supabase_url and supabase_key:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client initialized")
    else:
        supabase = None
        print("⚠️  Supabase credentials not found in .env")
        
except ImportError:
    supabase = None
    print("⚠️  supabase-py not installed. Install with: pip install supabase-py")


# ============================================================================
# ASYNCPG CONNECTION
# ============================================================================

try:
    import asyncpg
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("⚠️  DATABASE_URL not found in .env")
        database_url = None
        
except ImportError:
    asyncpg = None
    print("⚠️  asyncpg not installed. Install with: pip install asyncpg")
    database_url = None


class Database:
    """
    Database wrapper con supporto per:
    - AsyncPG (query SQL dirette)
    - Supabase Client (real-time, storage, auth)
    """
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.supabase = supabase
        self.database_url = database_url
    
    async def connect(self):
        """Initialize connection pool"""
        if not self.database_url:
            print("⚠️  Cannot connect: DATABASE_URL not configured")
            return
        
        if not asyncpg:
            print("⚠️  Cannot connect: asyncpg not installed")
            return
        
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            print("✅ Database pool created")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            self.pool = None
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            print("👋 Database pool closed")
    
    async def fetch_one(self, query: str, *args, **kwargs):
        """Fetch single record"""
        if not self.pool:
            return None
        
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args, **kwargs)
    
    async def fetch_all(self, query: str, *args, **kwargs):
        """Fetch multiple records"""
        if not self.pool:
            return []
        
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args, **kwargs)
    
    async def execute(self, query: str, *args, **kwargs):
        """Execute query"""
        if not self.pool:
            return None
        
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args, **kwargs)
    
    async def fetch_val(self, query: str, *args, **kwargs):
        """Fetch single value"""
        if not self.pool:
            return None
        
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args, **kwargs)


# Global database instance
db = Database()


async def get_db() -> Database:
    """
    Dependency for FastAPI routes
    
    Usage:
        @router.get("/users")
        async def get_users(db = Depends(get_db)):
            users = await db.fetch_all("SELECT * FROM users")
            return users
    """
    if not db.pool:
        await db.connect()
    
    return db


# ============================================================================
# SUPABASE HELPERS
# ============================================================================

def get_supabase() -> Optional[Client]:
    """
    Get Supabase client
    
    Usage:
        from app.database import get_supabase
        
        supabase = get_supabase()
        response = supabase.table('users').select('*').execute()
    """
    return supabase


async def supabase_upload_file(bucket: str, path: str, file_data: bytes) -> str:
    """
    Upload file to Supabase Storage
    
    Args:
        bucket: Bucket name (e.g. 'avatars', 'documents')
        path: File path in bucket
        file_data: File bytes
    
    Returns:
        Public URL of uploaded file
    """
    if not supabase:
        raise Exception("Supabase not initialized")
    
    # Upload
    supabase.storage.from_(bucket).upload(path, file_data)
    
    # Get public URL
    url = supabase.storage.from_(bucket).get_public_url(path)
    
    return url


async def supabase_realtime_subscribe(table: str, callback):
    """
    Subscribe to real-time changes
    
    Usage:
        def handle_change(payload):
            print(f"Change: {payload}")
        
        await supabase_realtime_subscribe('users', handle_change)
    """
    if not supabase:
        raise Exception("Supabase not initialized")
    
    supabase.table(table).on('*', callback).subscribe()


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

async def startup():
    """Run on application startup"""
    print("🔌 Connecting to database...")
    await db.connect()


async def shutdown():
    """Run on application shutdown"""
    print("🔌 Disconnecting from database...")
    await db.disconnect()


# ============================================================================
# TEST CONNECTION
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("=" * 60)
        print("🧪 TEST DATABASE CONNECTION")
        print("=" * 60)
        print()
        
        # Test connection
        await db.connect()
        
        if db.pool:
            print("✅ Connection pool created")
            
            # Test query
            try:
                result = await db.fetch_val("SELECT 1 as test")
                print(f"✅ Test query: {result}")
            except Exception as e:
                print(f"❌ Test query failed: {e}")
            
            await db.disconnect()
        else:
            print("❌ Connection failed")
        
        print()
        print("=" * 60)
    
    asyncio.run(test())
