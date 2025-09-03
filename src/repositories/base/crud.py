from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy import select, update, delete
from redis import Redis
from datetime import timedelta
from typing import Type

from src.repositories.base.abc import BaseCrudRepository, TModel, TResponse
from src.exc.api import NotFoundException
from src.settings import logger


class CrudRepository(BaseCrudRepository):

    model: Type[TModel]
    response_model: Type[TResponse]

    def __init__(self, session: AsyncSession, redis: Redis):
        if not self.model or not self.response_model:
            raise ValueError("Not exist model or response model")
        self.session = session
        self.cache = redis


    async def get(self, id):
        key = f"{self.model.__name__}_{id}"
        cached = await self.cache.get(key)
        if cached:
            model = self.response_model.model_validate_json(cached)
            return model
        model = await self._get(id)
        val = model.model_dump_json()
        await self.cache.set(key, val, timedelta(hours=1))
        return model

    async def _get(self, id):
        try:
            task = await self.session.get_one(self.model, id)
            return self.response_model.model_validate(task, from_attributes=True)
        except NoResultFound:
            raise NotFoundException(self.model.__name__)
        except SQLAlchemyError as e:
            logger.error(f"Error with get {self.model.__name__}: {e}")
            raise

    async def get_list(self, skip=0, limit=50, **filters):
        try:
            query = select(self.model).offset(skip).limit(limit)

            for field, value in filters.items():
                if value is not None and hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
            
            result = await self.session.scalars(query)
            return result.all()
             
        except SQLAlchemyError as e:
            logger.error(f"Error with get_list {self.model.__name__}: {e}")
            raise

    async def update(self, model_id, model_update):
        try:
            async with self.session.begin():
                update_data = model_update.model_dump(exclude_unset=True)
                query = update(self.model).where(self.model.id == model_id).values(**update_data).returning(self.model)
                result = await self.session.execute(query)
                return self.response_model.model_validate(result.scalar_one())
        except NoResultFound:
            raise NotFoundException(self.model.__name__)
        except SQLAlchemyError as e:
            logger.error(f"Error with update {self.model.__name__} {model_id}: {e}")
            raise

    async def delete(self, model_id):
        try:
            async with self.session.begin():
                query = delete(self.model).where(self.model.id == model_id).returning(self.model)
                result = await self.session.execute(query)
                return self.response_model.model_validate(result.scalar_one())
        except NoResultFound as e:
            raise NotFoundException(self.model.__name__)
        except SQLAlchemyError as e:
            logger.error(f"Error with delete {self.model.__name__} {model_id}: {e}")
            raise

    async def create(self, model_create):
        try:
            new_model_dict = model_create.model_dump(exclude_unset=True)
            new_model = self.model(**new_model_dict)
            self.session.add(new_model)
            await self.session.commit()
            await self.session.refresh(new_model)
            return new_model
        except Exception as e:
            logger.error(f"Error with create {self.model.__name__}: {e}")
            await self.session.rollback()
            raise