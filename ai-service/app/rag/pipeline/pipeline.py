from app.rag.parser.repo_loader import RepoLoader
from app.rag.parser.tree_sitter_parser import TreeSitterParser
from app.rag.embeddings.embedder import Embedder
from app.rag.embeddings.vector_store import VectorStore
from app.core.logger import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    """
    End-to-end indexing pipeline:
    repo_loader -> parser -> embedder -> vector_store
    """
    
    def __init__(self):
        self.repo_loader = RepoLoader()
        self.parser = TreeSitterParser()
        self.embedder = Embedder()
        self.vector_store = VectorStore(embedding_dim=self.embedder.embedding_dim)
    
    def run_indexing(
        self,
        repo_url: str,
        job_id: str,
        repo_id: str,
        github_token: str = None
    ) -> dict:
        """
        Full indexing pipeline: clone -> parse -> embed -> store.
        
        Args:
            repo_url: Repository URL
            job_id: Unique job identifier
            repo_id: Repository ID (for collection naming)
            github_token: Optional token for private repos
            
        Returns:
            Dict with indexing stats
        """
        stats = {
            "job_id": job_id,
            "repo_id": repo_id,
            "chunks_extracted": 0,
            "chunks_indexed": 0,
            "embedding_dim": self.embedder.embedding_dim
        }
        
        collection_name = f"job_{job_id}_repo_{repo_id}"
        repo_path = None
        
        try:
            # Step 1: Clone
            logger.info("Starting indexing pipeline", extra={
                "jobId": job_id,
                "repoId": repo_id
            })
            
            repo_path = self.repo_loader.clone_repo(
                repo_url=repo_url,
                job_id=job_id,
                github_token=github_token
            )
            
            # Step 2: Parse
            logger.info("Parsing repository", extra={"jobId": job_id})
            chunks = self.parser.parse_directory(repo_path)
            stats["chunks_extracted"] = len(chunks)
            
            if not chunks:
                logger.warning("No chunks extracted", extra={"jobId": job_id})
                return stats
            
            # Step 3: Embed
            logger.info("Generating embeddings", extra={
                "jobId": job_id,
                "num_chunks": len(chunks)
            })
            
            # Convert CodeChunk objects to dicts with unique IDs
            chunk_dicts = [
                {
                    **chunk.to_dict(),
                    "id": f"{job_id}_{i}"
                }
                for i, chunk in enumerate(chunks)
            ]
            
            # Encode all chunks
            chunk_dicts = self.embedder.encode_chunks(chunk_dicts)
            
            # Step 4: Store in vector database
            logger.info("Storing in vector database", extra={
                "jobId": job_id,
                "collection": collection_name
            })
            
            embeddings = [c["embedding"].tolist() for c in chunk_dicts]
            num_stored = self.vector_store.upsert_chunks(
                collection_name=collection_name,
                chunks=chunk_dicts,
                embeddings=embeddings
            )
            stats["chunks_indexed"] = num_stored
            
            self.vector_store.persist()
            
            logger.info("Indexing complete", extra={
                "jobId": job_id,
                **stats
            })
            
            return stats
            
        except Exception as e:
            logger.error("Indexing failed", extra={
                "jobId": job_id,
                "error": str(e)
            })
            # Cleanup on failure
            if repo_path:
                self.repo_loader.cleanup(job_id)
            raise
        
        finally:
            # Always cleanup temp files
            if repo_path:
                self.repo_loader.cleanup(job_id)
