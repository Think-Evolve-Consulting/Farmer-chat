"""Product recommendation logging - separate from conversation logging."""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class ProductLogger:
    """Logs product recommendations independently from chat conversations."""
    
    def __init__(self, log_dir: str = "data/logs/product_recommendations"):
        """
        Initialize the product logger.
        
        Args:
            log_dir: Directory to store product recommendation logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_recommendation(
        self,
        query: str,
        products: List[Dict[str, Any]],
        session_id: Optional[str] = None,
        user_feedback: Optional[str] = None
    ) -> None:
        """
        Log a product recommendation event.
        
        Args:
            query: The user's query that triggered the recommendation
            products: List of products recommended
            session_id: Optional session ID to track user interactions
            user_feedback: Optional user feedback on recommendations
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "products_shown": [
                {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "type": p.get("type"),
                }
                for p in products
            ],
            "num_products": len(products),
            "session_id": session_id,
            "user_feedback": user_feedback,
        }
        
        # Write to daily log file
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"product_recommendations_{today}.jsonl"
        
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except IOError as e:
            print(f"Error writing product log: {e}")
    
    def log_product_click(
        self,
        product_id: str,
        product_name: str,
        session_id: Optional[str] = None,
        action: str = "click"
    ) -> None:
        """
        Log when a user interacts with a recommended product.
        
        Args:
            product_id: ID of the product
            product_name: Name of the product
            session_id: Optional session ID
            action: Type of action (click, view, etc.)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "product_id": product_id,
            "product_name": product_name,
            "session_id": session_id,
        }
        
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"product_interactions_{today}.jsonl"
        
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except IOError as e:
            print(f"Error writing product interaction log: {e}")
    
    def get_stats(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about product recommendations.
        
        Args:
            date: Optional date string (YYYY-MM-DD). If None, returns today's stats
            
        Returns:
            Dictionary with recommendation statistics
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        log_file = self.log_dir / f"product_recommendations_{date}.jsonl"
        
        stats = {
            "date": date,
            "total_recommendations": 0,
            "total_products_shown": 0,
            "top_products": {},
            "queries": [],
        }
        
        if not log_file.exists():
            return stats
        
        product_count = {}
        
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        stats["total_recommendations"] += 1
                        stats["total_products_shown"] += entry.get("num_products", 0)
                        stats["queries"].append(entry.get("query"))
                        
                        # Count product recommendations
                        for product in entry.get("products_shown", []):
                            product_id = product.get("id")
                            product_count[product_id] = product_count.get(product_id, 0) + 1
            
            # Get top recommended products
            stats["top_products"] = dict(
                sorted(product_count.items(), key=lambda x: x[1], reverse=True)[:10]
            )
        
        except IOError as e:
            print(f"Error reading product logs: {e}")
        
        return stats
