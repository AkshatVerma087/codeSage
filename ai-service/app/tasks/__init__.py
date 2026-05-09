"""Celery tasks for background job processing."""

from app.tasks.indexing import index_repository

__all__ = ["index_repository"]
