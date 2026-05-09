import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from git import Repo
from git.exc import GitCommandError
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class RepoLoader:
    """Clone and manage repository lifecycle."""
    
    def __init__(self):
        self.tmp_base = Path(tempfile.gettempdir()) / "codesage"
        self.tmp_base.mkdir(exist_ok=True)
    
    def get_repo_path(self, job_id: str) -> Path:
        """Get isolated directory for this job's repo."""
        return self.tmp_base / job_id
    
    def clone_repo(
        self,
        repo_url: str,
        job_id: str,
        github_token: Optional[str] = None,
        timeout_sec: int = None
    ) -> Path:
        """
        Clone repository with size and timeout enforcement.
        
        Args:
            repo_url: GitHub URL (https://github.com/user/repo)
            job_id: Unique job identifier for isolation
            github_token: Optional token for private repos
            timeout_sec: Clone timeout in seconds
            
        Returns:
            Path to cloned repository
            
        Raises:
            ValueError: If repo too large or clone timeout exceeded
            GitCommandError: If clone fails
        """
        timeout_sec = timeout_sec or settings.clone_timeout_sec
        repo_path = self.get_repo_path(job_id)
        
        logger.info(f"Starting clone", extra={
            "jobId": job_id,
            "repo_url": self._redact_token(repo_url),
            "timeout_sec": timeout_sec
        })
        
        try:
            # Inject token if private repo
            clone_url = repo_url
            if github_token:
                # Format: https://x-token:{token}@github.com/user/repo
                clone_url = repo_url.replace(
                    "https://github.com/",
                    f"https://x-token:{github_token}@github.com/"
                )
            
            # Clone with timeout using subprocess
            try:
                Repo.clone_from(
                    clone_url,
                    str(repo_path),
                    depth=1  # Shallow clone for speed
                )
            except subprocess.TimeoutExpired:
                raise ValueError(f"Clone timeout exceeded ({timeout_sec}s)")
            
            # Post-clone size check
            self._validate_repo_size(repo_path, job_id)
            
            logger.info("Clone complete", extra={
                "jobId": job_id,
                "size_mb": self._get_dir_size_mb(repo_path)
            })
            
            return repo_path
            
        except ValueError as e:
            self.cleanup(job_id)
            raise
        except GitCommandError as e:
            self.cleanup(job_id)
            logger.error(f"Clone failed: {str(e)}", extra={"jobId": job_id})
            raise ValueError(f"Failed to clone repo: {str(e)}")
        except Exception as e:
            self.cleanup(job_id)
            logger.error(f"Unexpected error during clone", extra={
                "jobId": job_id,
                "error": str(e)
            })
            raise
    
    def _validate_repo_size(self, repo_path: Path, job_id: str) -> None:
        """Check if repo exceeds size limit."""
        size_mb = self._get_dir_size_mb(repo_path)
        max_mb = settings.max_repo_size_mb
        
        if size_mb > max_mb:
            logger.warning(f"Repo exceeds size limit", extra={
                "jobId": job_id,
                "size_mb": size_mb,
                "max_mb": max_mb
            })
            raise ValueError(
                f"Repository size {size_mb}MB exceeds limit {max_mb}MB"
            )
    
    @staticmethod
    def _get_dir_size_mb(path: Path) -> float:
        """Calculate directory size in MB."""
        total = 0
        for dirpath, dirnames, filenames in os.walk(path):
            # Skip .git to get code size only
            dirnames[:] = [d for d in dirnames if d != '.git']
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.isfile(filepath):
                    total += os.path.getsize(filepath)
        return total / (1024 * 1024)
    
    @staticmethod
    def _redact_token(url: str) -> str:
        """Remove tokens from URLs for logging."""
        if "x-token:" in url:
            return url.replace(url.split("@")[0], "https://[REDACTED]")
        return url
    
    def cleanup(self, job_id: str) -> None:
        """Delete job-specific repo directory."""
        repo_path = self.get_repo_path(job_id)
        if repo_path.exists():
            try:
                shutil.rmtree(repo_path)
                logger.info(f"Cleanup complete", extra={"jobId": job_id})
            except Exception as e:
                logger.error(f"Cleanup failed", extra={
                    "jobId": job_id,
                    "error": str(e)
                })
