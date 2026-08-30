from sqlalchemy.ext.asyncio import create_async_engine
from .base import Base
from GhanaMotivationApp.settings import settings 


# For Testing | sqlite+aiosqlite
async_engine = create_async_engine(
    url= settings.DATABASE_URL,
    echo= settings.ECHO
)



# ----- For PostgreSQL -----
# async_engine = create_async_engine(
#     url= settings.DATABASE_URL,
#     echo= settings.ECHO,
#     pool_size= settings.POOL_SIZE,
#     pool_timeout= settings.POOL_TIMEOUT,
#     max_overflow= settings.MAX_OVERFLOW
# )



async def create_all_tables():
    from GhanaMotivationApp.modules.payment import Payment
    from GhanaMotivationApp.modules.quote import Quote
    from GhanaMotivationApp.modules.subscription import Subscription
    from GhanaMotivationApp.modules.user import User

    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    
    