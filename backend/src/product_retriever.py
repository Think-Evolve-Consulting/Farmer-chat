"""Product retrieval system - separate from transcript retrieval."""
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import re
from urllib.parse import quote
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


class ProductRetriever:
    """Retrieves relevant products based on user queries using semantic search."""
    
    def __init__(
        self,
        product_data_path: str = "data/transcripts/products.jsonl",
        index_path: str = "data/index/products.index",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the product retriever.
        
        Args:
            product_data_path: Path to JSONL file with product data
            index_path: Path to save/load FAISS index
            embedding_model: Name of the embedding model to use
        """
        self.product_data_path = Path(product_data_path)
        self.index_path = Path(index_path)
        self.embedder = SentenceTransformer(embedding_model)
        self.products: List[Dict[str, Any]] = []
        self.product_texts: List[str] = []
        self.index: Optional[faiss.IndexFlatL2] = None
        self.index_loaded = False
        self.local_image_base_url = "/api/product-images"
        self.product_image_dir = self._resolve_product_image_dir()
        self.image_name_map = self._build_image_name_map()
        
        # Try to load existing index, otherwise build from JSONL
        if self.index_path.exists():
            self.load_index()
        else:
            self.build_index()

    def _resolve_product_image_dir(self) -> Optional[Path]:
        """
        Resolve local product image directory.
        Priority: "FIL data" (new) -> "FIL Product" (legacy).
        """
        project_root = Path(__file__).resolve().parents[1]
        candidates = [
            project_root / "data" / "transcripts" / "FIL data",
            project_root / "data" / "transcripts" / "FIL Product",
        ]
        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                return candidate
        return None

    @staticmethod
    def _norm_key(value: str) -> str:
        """
        Normalize text for robust filename/product matching.
        """
        if not value:
            return ""
        return re.sub(r"[^a-z0-9]+", "", value.lower())

    def _build_image_name_map(self) -> Dict[str, str]:
        """
        Build normalized filename stem -> actual filename map.
        """
        if not self.product_image_dir:
            return {}

        mapping: Dict[str, str] = {}
        for file_path in self.product_image_dir.iterdir():
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
                continue
            norm = self._norm_key(file_path.stem)
            if norm:
                mapping[norm] = file_path.name
        return mapping

    def _local_image_url_for_product(self, product: Dict[str, Any]) -> Optional[str]:
        """
        Find matching local image file and return API URL if found.
        """
        if not self.image_name_map:
            return None

        keys_to_try = [
            product.get("name", ""),
            product.get("id", ""),
            str(product.get("name", "")).replace("FIL ", ""),
            str(product.get("name", "")).replace("Fil ", ""),
            str(product.get("name", "")).replace("FIL", "").strip(),
        ]

        for raw in keys_to_try:
            norm = self._norm_key(raw)
            if not norm:
                continue
            filename = self.image_name_map.get(norm)
            if filename:
                return f"{self.local_image_base_url}/{quote(filename)}"
        return None

    def _attach_image_url(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use only local product image URL from FIL folder.
        If no local match exists, return empty image_url (no Drive fallback).
        """
        enriched = product.copy()
        local_url = self._local_image_url_for_product(enriched)
        if local_url:
            enriched["image_url"] = local_url
        else:
            enriched["image_url"] = ""
        return enriched
    
    def build_index(self) -> int:
        """
        Build FAISS index from product JSONL file.
        
        Returns:
            Number of products indexed
        """
        print(f"Building product index from: {self.product_data_path}")
        
        if not self.product_data_path.exists():
            print(f"Warning: Product data file not found at {self.product_data_path}")
            return 0
        
        # Load products from JSONL
        with open(self.product_data_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        product = json.loads(line)
                        self.products.append(product)
                        
                        # Create searchable text combining key fields
                        searchable_text = self._create_searchable_text(product)
                        self.product_texts.append(searchable_text)
                    except json.JSONDecodeError as e:
                        print(f"Error parsing product line: {e}")
                        continue
        
        if not self.products:
            print("No products loaded!")
            return 0
        
        # Create embeddings
        print(f"Creating embeddings for {len(self.products)} products...")
        embeddings = self.embedder.encode(
            self.product_texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Build FAISS index
        embedding_dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.index.add(embeddings.astype('float32'))
        
        # Save index and metadata
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        self._save_metadata(embedding_dim)
        
        print(f"✅ Product index built with {len(self.products)} products")
        print(f"📁 Index saved to: {self.index_path}")
        
        self.index_loaded = True
        return len(self.products)
    
    def load_index(self) -> bool:
        """
        Load existing FAISS index and products.
        
        Returns:
            True if index loaded successfully, False otherwise
        """
        try:
            print(f"Loading product index from: {self.index_path}")
            
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_path))
            
            # Reload products from JSONL
            with open(self.product_data_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            product = json.loads(line)
                            self.products.append(product)
                            searchable_text = self._create_searchable_text(product)
                            self.product_texts.append(searchable_text)
                        except json.JSONDecodeError:
                            continue
            
            print(f"✅ Loaded {len(self.products)} products from index")
            self.index_loaded = True
            return True
            
        except Exception as e:
            print(f"Error loading index: {e}")
            print("Will rebuild index from JSONL...")
            self.build_index()
            return self.index_loaded
    
    def _save_metadata(self, embedding_dim: int) -> None:
        """
        Save product metadata to JSON file.
        
        Args:
            embedding_dim: Dimension of embeddings
        """
        metadata_path = self.index_path.with_suffix(".meta.json")
        metadata = {
            "embedding_model": "all-MiniLM-L6-v2",
            "embedding_dimension": embedding_dim,
            "total_products": len(self.products),
            "product_types": list(set(p.get("type", "") for p in self.products if p.get("type"))),
            "total_crops": len(set(crop for p in self.products for crop in p.get("crops", []))),
            "total_diseases": len(set(disease for p in self.products for disease in p.get("diseases", []))),
            "products": [
                {
                    "id": p.get("id", ""),
                    "name": p.get("name", ""),
                    "type": p.get("type", ""),
                    "technical_name": p.get("technical_name", "")
                }
                for p in self.products
            ]
        }
        
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Metadata saved to: {metadata_path}")
    
    def _create_searchable_text(self, product: Dict[str, Any]) -> str:
        """
        Create a searchable text representation of a product.
        
        Args:
            product: Product dictionary from JSONL
            
        Returns:
            Searchable text combining relevant fields
        """
        parts = [
            product.get('name', ''),
            product.get('type', ''),
            product.get('technical_name', ''),
            product.get('features', ''),
            ' '.join(product.get('crops', [])),
            ' '.join(product.get('diseases', [])),
            ' '.join(product.get('keywords', [])),
        ]
        
        return ' '.join(filter(None, parts))
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant products for a query.
        
        Args:
            query: User query text
            top_k: Number of products to return
            
        Returns:
            List of relevant products with metadata
        """
        if not self.index_loaded or self.index is None:
            print("Product index not loaded!")
            return []
        
        # Embed the query
        query_embedding = self.embedder.encode([query])[0]
        
        # Search in FAISS index
        distances, indices = self.index.search(
            np.array([query_embedding]).astype('float32'),
            min(top_k, len(self.products))
        )
        
        # Prepare results
        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self.products):
                product = self.products[int(idx)]
                results.append(self._attach_image_url(product))
        
        return results
    
    def search_by_crop(self, crop: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search products applicable for a specific crop.
        
        Args:
            crop: Crop name
            top_k: Number of products to return
            
        Returns:
            List of products applicable for the crop
        """
        results = []
        for product in self.products:
            if crop.lower() in [c.lower() for c in product.get('crops', [])]:
                results.append(self._attach_image_url(product))
            if len(results) >= top_k:
                break
        return results
    
    def search_by_disease(self, disease: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search products that treat a specific disease.
        
        Args:
            disease: Disease name
            top_k: Number of products to return
            
        Returns:
            List of products that treat the disease
        """
        results = []
        for product in self.products:
            if disease.lower() in [d.lower() for d in product.get('diseases', [])]:
                results.append(self._attach_image_url(product))
            if len(results) >= top_k:
                break
        return results
    
    @property
    def total_products(self) -> int:
        """Return total number of products in index."""
        return len(self.products)
