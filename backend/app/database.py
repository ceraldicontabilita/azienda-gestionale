"""
Database Connection - Supabase + AsyncPG
"""
import os
from typing import Optional, Any
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

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
        print("⚠️ Supabase credentials not found in environment")
        
except ImportError:
    supabase = None
    print("⚠️ supabase-py not installed. Install with: pip install supabase")
except Exception as e:
    supabase = None
    print(f"⚠️ Supabase initialization error: {e}")


# ============================================================================
# ASYNCPG CONNECTION (Optional)
# ============================================================================

try:
    import asyncpg
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("⚠️ DATABASE_URL not found in environment")
        database_url = None
        
except ImportError:
    asyncpg = None
    print("⚠️ asyncpg not installed")
    database_url = None
except Exception as e:
    print(f"⚠️ AsyncPG error: {e}")
    asyncpg = None
    database_url = None


class Database:
    """
    Database wrapper con supporto per:
    - Supabase Client (tabelle, real-time, storage, auth)
    - AsyncPG (query SQL dirette - opzionale)
    """
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.supabase = supabase
        self.database_url = database_url
    
    async def connect(self):
        """Initialize connection pool (AsyncPG)"""
        if not self.database_url or not asyncpg:
            logger.warning("AsyncPG pool not initialized (optional)")
            return
        
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60,
                server_settings={
                    'application_name': 'azienda-gestionale'
                }
            )
            print("✅ Database pool created")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            self.pool = None
    
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            print("🔌 Database pool closed")
    
    # ========================================================================
    # ASYNCPG METHODS (Optional)
    # ========================================================================
    
    async def fetch_one(self, query: str, *args):
        """Fetch single record with AsyncPG"""
        if not self.pool:
            return None
        
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        except Exception as e:
            logger.error(f"Query error: {e}")
            return None
    
    async def fetch_all(self, query: str, *args):
        """Fetch multiple records with AsyncPG"""
        if not self.pool:
            return []
        
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetch(query, *args)
        except Exception as e:
            logger.error(f"Query error: {e}")
            return []
    
    async def execute(self, query: str, *args):
        """Execute query with AsyncPG"""
        if not self.pool:
            return None
        
        try:
            async with self.pool.acquire() as conn:
                return await conn.execute(query, *args)
        except Exception as e:
            logger.error(f"Execute error: {e}")
            return None
    
    async def fetch_val(self, query: str, *args):
        """Fetch single value with AsyncPG"""
        if not self.pool:
            return None
        
        try:
            async with self.pool.acquire() as conn:
                return await conn.fetchval(query, *args)
        except Exception as e:
            logger.error(f"Query error: {e}")
            return None


# Global database instance
db = Database()


# ============================================================================
# SUPABASE HELPERS - USE THESE FOR AUTH/DATA
# ============================================================================

def get_supabase() -> Optional[Client]:
    """
    Get Supabase client
    
    Usage:
        from app.database import get_supabase
        
        supabase = get_supabase()
        response = supabase.table('users').select('*').execute()
    """
    if not supabase:
        raise Exception("Supabase not initialized")
    return supabase


def get_table(table_name: str) -> Any:
    """
    Get reference to a Supabase table
    
    Usage:
        from app.database import get_table
        
        users = get_table('users')
        response = users.select('*').execute()
    
    Args:
        table_name: Name of the table (e.g., 'users', 'employees')
    
    Returns:
        Supabase table reference
    """
    if not supabase:
        raise Exception("Supabase not initialized. Check SUPABASE_URL and SUPABASE_SERVICE_KEY")
    
    return supabase.table(table_name)


async def get_db() -> 'Database':
    """
    Dependency for FastAPI routes
    
    Usage:
        @router.get("/users")
        async def get_users(db = Depends(get_db)):
            users = await db.fetch_all("SELECT * FROM users")
            return users
    """
    if not db.pool and db.database_url:
        await db.connect()
    
    return db


# ============================================================================
# SUPABASE STORAGE HELPERS
# ============================================================================

async def supabase_upload_file(bucket: str, path: str, file_data: bytes) -> str:
    """
    Upload file to Supabase Storage
    
    Args:
        bucket: Bucket name (e.g., 'avatars', 'documents')
        path: File path in bucket
        file_data: File bytes
    
    Returns:
        Public URL of uploaded file
    """
    if not supabase:
        raise Exception("Supabase not initialized")
    
    try:
        supabase.storage.from_(bucket).upload(path, file_data)
        url = supabase.storage.from_(bucket).get_public_url(path)
        return url
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise


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
    
    try:
        supabase.table(table).on('*', callback).subscribe()
    except Exception as e:
        logger.error(f"Subscribe error: {e}")
        raise


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
        
        # Test Supabase
        try:
            supabase = get_supabase()
            result = supabase.table('users').select('count', count='exact').execute()
            print(f"✅ Supabase connection: OK")
            print(f"   Users table count: {result.count}")
        except Exception as e:
            print(f"❌ Supabase connection: {e}")
        
        print()
        
        # Test AsyncPG pool
        await db.connect()
        
        if db.pool:
            print("✅ AsyncPG pool created")
            
            try:
                result = await db.fetch_val("SELECT 1 as test")
                print(f"✅ AsyncPG query: {result}")
            except Exception as e:
                print(f"❌ AsyncPG query failed: {e}")
            
            await db.disconnect()
        else:
            print("⚠️ AsyncPG pool not initialized (optional)")
        
        print()
        print("=" * 60)
    
    asyncio.run(test())
