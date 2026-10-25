
"""Local, persistent vector retrieval for the HR Helpdesk.

The vector index is deliberately local. Authorization is enforced by building
separate collections for each role/region, so unauthorized rows are never
returned to the chat layer.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple


ROLES = ["intern", "associate", "store_manager", "vp", "ceo", "hr"]


class LocalVectorStore:
    def __init__(self, base_dir: Path, policies_file: Path, faq_file: Path):
        self.base_dir = Path(base_dir)
        self.db_dir = self.base_dir / "vector_db"
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_file = self.db_dir / "manifest.json"
        self.policies_file = Path(policies_file)
        self.faq_file = Path(faq_file)
        self._client = None
        self._model = None

    def _load_dependencies(self):
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "Local RAG dependencies are missing. Run: "
                "pip install chromadb sentence-transformers"
            ) from exc

        if self._client is None:
            self._client = chromadb.PersistentClient(path=str(self.db_dir))
        if self._model is None:
            self._model = SentenceTransformer("all-MiniLM-L6-v2")

    @staticmethod
    def _allowed(row: dict, role: str, region: str) -> bool:
        roles = {
            item.strip().lower()
            for item in row.get("allowed_roles", "").split(";")
            if item.strip()
        }
        regions = {
            item.strip().lower()
            for item in row.get("regions", "").split(";")
            if item.strip()
        }
        return (
            ("all" in roles or role.lower() in roles)
            and ("all" in regions or region.lower() in regions)
        )

    @staticmethod
    def _doc(row: dict, source_type: str) -> str:
        if source_type == "policy":
            return "\n".join(
                [
                    f"Policy: {row.get('policy_name', '')}",
                    f"Section: {row.get('section', '')}",
                    f"Title: {row.get('section_title', '')}",
                    f"Category: {row.get('category', '')}",
                    f"Rule: {row.get('key_rule', '')}",
                    f"Text: {row.get('text', '')}",
                ]
            )
        return "\n".join(
            [
                f"Category: {row.get('category', '')}",
                f"Intent: {row.get('intent', '')}",
                f"Question: {row.get('question', '')}",
                f"Answer: {row.get('answer', '')}",
            ]
        )

    @staticmethod
    def _key(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def _source_signature(self) -> str:
        h = hashlib.sha256()
        for path in (self.policies_file, self.faq_file):
            h.update(path.read_bytes())
        return h.hexdigest()

    def _collection_name(self, role: str, region: str) -> str:
        safe_role = role.lower().replace("-", "_")
        safe_region = region.lower().replace("-", "_")
        return f"hr_{safe_role}_{safe_region}"

    def _ensure_index(self, policies: list, faq: list):
        self._load_dependencies()
        signature = self._source_signature()
        manifest = {}
        if self.manifest_file.exists():
            try:
                manifest = json.loads(self.manifest_file.read_text(encoding="utf-8"))
            except Exception:
                manifest = {}

        if manifest.get("signature") == signature:
            healthy = True
            for role in ROLES:
                collection = self._client.get_or_create_collection(
                    name=self._collection_name(role, "all"),
                    metadata={"hnsw:space": "cosine"},
                )
                if collection.count() == 0:
                    healthy = False
                    break
            if healthy:
                return

        # Rebuild all role/region collections when approved KB changes.
        for role in ROLES:
            collection = self._client.get_or_create_collection(
                name=self._collection_name(role, "all"),
                metadata={"hnsw:space": "cosine"},
            )
            existing = collection.get()
            ids = existing.get("ids", [])
            if ids:
                collection.delete(ids=ids)

            rows = []
            for row in policies:
                if self._allowed(row, role, "all"):
                    rows.append(("policy", row))
            for row in faq:
                if self._allowed(row, role, "all"):
                    rows.append(("faq", row))

            if not rows:
                continue

            documents = [self._doc(row, source_type) for source_type, row in rows]
            embeddings = self._model.encode(
                documents,
                normalize_embeddings=True,
                show_progress_bar=False,
            ).tolist()

            ids = []
            metadatas = []
            for idx, (source_type, row) in enumerate(rows):
                chunk_id = (
                    row.get("chunk_id")
                    or row.get("faq_id")
                    or f"{source_type}-{idx}"
                )
                ids.append(f"{source_type}:{chunk_id}:{idx}")
                metadatas.append(
                    {
                        "source_type": source_type,
                        "chunk_id": str(chunk_id),
                        "row_json": json.dumps(row, ensure_ascii=False),
                    }
                )

            collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )

        self.manifest_file.write_text(
            json.dumps({"signature": signature}, indent=2),
            encoding="utf-8",
        )

    def query(
        self,
        question: str,
        role: str,
        region: str,
        n: int = 10,
        policies: list | None = None,
        faq: list | None = None,
    ) -> Tuple[list, list, list]:
        policies = policies or []
        faq = faq or []
        self._ensure_index(policies, faq)
        self._load_dependencies()

        collection = self._client.get_or_create_collection(
            name=self._collection_name(role, "all"),
            metadata={"hnsw:space": "cosine"},
        )

        embedding = self._model.encode(
            [question],
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

        result = collection.query(
            query_embeddings=embedding,
            n_results=max(1, n),
            include=["metadatas", "distances", "documents"],
        )

        retrieved_policies = []
        retrieved_faq = []
        evidence = []

        metadata_rows = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        for metadata, distance in zip(metadata_rows, distances):
            try:
                row = json.loads(metadata["row_json"])
            except Exception:
                continue

            # cosine distance is approximately 0 for a close match.
            similarity = max(0.0, min(1.0, 1.0 - float(distance)))
            item = {
                "source_type": metadata.get("source_type", ""),
                "chunk_id": metadata.get("chunk_id", ""),
                "similarity": round(similarity, 4),
                "row": row,
            }
            evidence.append(item)

            if metadata.get("source_type") == "policy":
                retrieved_policies.append((similarity, row))
            else:
                retrieved_faq.append((similarity, row))

        retrieved_policies.sort(key=lambda x: x[0], reverse=True)
        retrieved_faq.sort(key=lambda x: x[0], reverse=True)

        return (
            [row for similarity, row in retrieved_policies if similarity >= 0.30][:5],
            [row for similarity, row in retrieved_faq if similarity >= 0.30][:5],
            evidence,
        )
