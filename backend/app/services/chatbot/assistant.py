import os
import re
import logging
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.config import settings
from app.database.models import Product, Merchant

logger = logging.getLogger(__name__)

class ShoppingAssistant:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY

    def set_api_key(self, key: str):
        self.api_key = key.strip()

    def process_query(self, db: Session, query: str, history: Optional[list[dict]] = None) -> dict:
        """
        Processes a natural language shopping inquiry, enforcing catalogue grounding.
        Returns:
            {
                "reply": str,
                "recommended_products": list[dict],
                "mode": "gemini_cloud" | "local_fallback",
                "disclaimer": str
            }
        """
        # 1. Parse constraints (budget max, category, keywords)
        budget_max = self._extract_budget(query)
        keywords = self._extract_keywords(query)

        # 2. Query real catalogue items from database
        product_query = db.query(Product).filter(Product.is_active == True)
        if budget_max is not None:
            product_query = product_query.filter(Product.price <= budget_max)

        matching_products = []
        if keywords:
            for kw in keywords:
                items = product_query.filter(
                    or_(
                        Product.title.ilike(f"%{kw}%"),
                        Product.description.ilike(f"%{kw}%"),
                        Product.category.ilike(f"%{kw}%"),
                        Product.tags_json.ilike(f"%{kw}%")
                    )
                ).all()
                for item in items:
                    if item not in matching_products:
                        matching_products.append(item)

        if not matching_products:
            # Fallback to all active products within budget
            matching_products = product_query.limit(5).all()

        matched_products_formatted = [
            {
                "id": p.id,
                "title": p.title,
                "price": p.price,
                "category": p.category,
                "inventory": p.inventory,
                "merchant": p.merchant.business_name if p.merchant else "Local Shop",
                "city": p.merchant.city if p.merchant else "Local",
                "image_url": p.image_url,
                "description": p.description
            }
            for p in matching_products[:4]
        ]

        # 3. Attempt Gemini API if key is set
        if self.api_key:
            try:
                gemini_reply = self._call_gemini(query, matched_products_formatted, history)
                if gemini_reply:
                    return {
                        "reply": gemini_reply,
                        "recommended_products": matched_products_formatted,
                        "mode": "gemini_cloud",
                        "disclaimer": "Powered by Google Gemini with live catalogue grounding."
                    }
            except Exception as e:
                logger.warning(f"Gemini API request failed or quota exceeded: {e}. Falling back to local assistant.")

        # 4. Local Rule-Based Assistant Fallback
        local_reply = self._generate_local_reply(query, budget_max, matched_products_formatted)
        return {
            "reply": local_reply,
            "recommended_products": matched_products_formatted,
            "mode": "local_fallback",
            "disclaimer": "Using Scrollix Local AI Engine (No paid API key required). Grounded strictly in current catalogue inventory."
        }

    def _call_gemini(self, query: str, catalogue_items: list[dict], history: Optional[list[dict]] = None) -> Optional[str]:
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)

            # Build grounded context
            catalogue_summary = "\n".join([
                f"- Product #{item['id']}: {item['title']} | Price: ${item['price']} | In Stock: {item['inventory']} | Merchant: {item['merchant']} ({item['city']}) | Description: {item['description']}"
                for item in catalogue_items
            ])

            system_instruction = (
                "You are Scrollix AI, a helpful, honest local shopping assistant. "
                "CRITICAL RULE: You must ONLY recommend products present in the provided catalogue list below. "
                "Never invent non-existent products, prices, or fictitious merchants. "
                "Be concise, friendly, and highlight relevant features such as price, local merchant name, and stock status.\n\n"
                f"CURRENT CATALOGUE ITEMS:\n{catalogue_summary}"
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=query,
                config={"system_instruction": system_instruction}
            )
            return response.text
        except Exception as e:
            logger.error(f"Error in Gemini call: {e}")
            return None

    def _generate_local_reply(self, query: str, budget_max: Optional[float], items: list[dict]) -> str:
        if not items:
            if budget_max:
                return f"I couldn't find any products in our local merchant catalogue priced under ${budget_max:.2f}. Would you like to adjust your budget or search another category?"
            return "I couldn't find exact matches for your request in the local catalogue right now. Try searching for sneakers, leather bags, or ceramic home decor!"

        lines = []
        if budget_max:
            lines.append(f"Here are the best verified options matching your budget of under **${budget_max:.2f}**:")
        else:
            lines.append(f"Here are the top matches found in the Scrollix merchant catalogue:")

        for item in items:
            stock_note = f"({item['inventory']} left in stock)" if item['inventory'] > 0 else "(Out of stock)"
            lines.append(
                f"\n• **{item['title']}** — **${item['price']:.2f}** {stock_note}\n"
                f"  Sold by: *{item['merchant']}* in {item['city']}\n"
                f"  {item['description'][:120]}..."
            )

        lines.append("\n💡 *Tip: Click on any item above to view video demos and verify local pickup options.*")
        return "\n".join(lines)

    def _extract_budget(self, text: str) -> Optional[float]:
        patterns = [
            r"under\s*\$?(\d+(?:\.\d{1,2})?)",
            r"below\s*\$?(\d+(?:\.\d{1,2})?)",
            r"budget\s*(?:of|is|:)?\s*\$?(\d+(?:\.\d{1,2})?)",
            r"less\s*than\s*\$?(\d+(?:\.\d{1,2})?)",
            r"within\s*\$?(\d+(?:\.\d{1,2})?)"
        ]
        for p in patterns:
            match = re.search(p, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass
        return None

    def _extract_keywords(self, text: str) -> list[str]:
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        stop_words = {
            "what", "where", "show", "find", "looking", "want", "need", "best",
            "cheap", "expensive", "under", "below", "have", "please", "help",
            "local", "shop", "store", "product", "item", "items", "good", "with"
        }
        return [w for w in words if w not in stop_words]

assistant = ShoppingAssistant()
