import os
import sys
import logging
from pathlib import Path
from typing import Union, Optional, Tuple
from PIL import Image
import torch
import numpy as np

logger = logging.getLogger(__name__)

PRODUCT_CATEGORIES = [
    "Footwear & Sneakers",
    "Casual Shirts",
    "Polo T-Shirts",
    "Trousers & Pants",
    "Accessories & Bags",
    "Electronics",
    "Home & Living"
]

CATEGORY_PROMPTS = [
    "a photo of athletic shoes, sneakers, running shoes, boots, or footwear",
    "a photo of a casual button-down shirt, flannel overshirt, or denim casual shirt",
    "a photo of a polo t-shirt with a collar and buttons",
    "a photo of trousers, jeans, denim pants, chinos, or slacks",
    "a photo of a backpack, leather messenger bag, handbag, or purse",
    "a photo of electronics, wireless headphones, audio device, or tech gadget",
    "a photo of ceramic pottery, stoneware mug, vase, or home decor"
]

class ProductClassifier:
    """
    Multimodal visual product classifier for Scrollix AI.
    Accurately classifies uploaded photographs into canonical retail categories
    (Footwear, Shirts, Trousers, Bags, Electronics, Home) using deep vision features.
    Provides primary OpenCLIP zero-shot classification with local ResNet-18 ImageNet fallback.
    """
    def __init__(self):
        self.device = torch.device("cpu")
        self.clip_model = None
        self.clip_preprocess = None
        self.clip_text_features = None
        self.resnet_model = None
        self.resnet_categories = None
        self._init_models()

    def _init_models(self):
        # 1. Initialize OpenCLIP zero-shot classifier
        try:
            import open_clip
            model, _, preprocess = open_clip.create_model_and_transforms("ViT-B-32", pretrained="laion400m_e32")
            tokenizer = open_clip.get_tokenizer("ViT-B-32")
            text_tokens = tokenizer(CATEGORY_PROMPTS)

            with torch.no_grad():
                text_features = model.encode_text(text_tokens)
                text_features /= text_features.norm(dim=-1, keepdim=True)

            self.clip_model = model
            self.clip_preprocess = preprocess
            self.clip_text_features = text_features
            logger.info("Initialized OpenCLIP ViT-B-32 zero-shot product classifier.")
            return
        except Exception as e:
            logger.info(f"OpenCLIP unavailable ({e}). Falling back to torchvision ResNet-18.")

        # 2. Fallback to torchvision ResNet-18 ImageNet classifier
        try:
            import torchvision.models as tv_models
            resnet = tv_models.resnet18()
            ckpt_candidates = [
                Path("C:/Users/vivek/.cache/torch/hub/checkpoints/resnet18-f37072fd.pth"),
                Path(os.path.expanduser("~/.cache/torch/hub/checkpoints/resnet18-f37072fd.pth")),
            ]
            valid_ckpt = next((p for p in ckpt_candidates if p.exists()), None)
            if valid_ckpt:
                ckpt = torch.load(str(valid_ckpt), weights_only=True)
                resnet.load_state_dict(ckpt)
                resnet.eval()
                self.resnet_model = resnet
                weights = tv_models.ResNet18_Weights.DEFAULT
                self.resnet_categories = weights.meta["categories"]
                logger.info(f"Initialized ResNet-18 ImageNet product classifier from {valid_ckpt}.")
                return
        except Exception as e:
            logger.warning(f"ResNet-18 unavailable: {e}. Classifier running in fallback mode.")

    def classify_image(self, image_input: Union[str, Path, Image.Image]) -> dict:
        """
        Classifies an input product image into a canonical product category.
        Returns:
            category: str (e.g. 'Footwear & Sneakers', 'Casual Shirts', etc.)
            confidence: float (0.0 to 1.0)
            needs_review: bool (True if low confidence < 0.35)
            label: str
            probabilities: dict of category -> float
        """
        pil_image = None
        try:
            if isinstance(image_input, (str, Path)):
                if not os.path.exists(image_input):
                    return self._uncertain_result("File not found")
                pil_image = Image.open(image_input).convert("RGB")
            elif isinstance(image_input, Image.Image):
                pil_image = image_input.convert("RGB")
            else:
                return self._uncertain_result("Invalid image input type")
        except Exception as e:
            logger.error(f"Error opening image for classification: {e}")
            return self._uncertain_result(str(e))

        # 1. Try OpenCLIP inference
        if self.clip_model is not None and self.clip_preprocess is not None:
            try:
                tensor = self.clip_preprocess(pil_image).unsqueeze(0).to(self.device)
                with torch.no_grad():
                    img_features = self.clip_model.encode_image(tensor)
                    img_features /= img_features.norm(dim=-1, keepdim=True)
                    sims = (img_features @ self.clip_text_features.T)[0]
                    probs = torch.softmax(sims * 100, dim=0).cpu().numpy()

                prob_dict = {
                    cat: round(float(probs[idx]), 4)
                    for idx, cat in enumerate(PRODUCT_CATEGORIES)
                }

                top_idx = int(np.argmax(probs))
                top_cat = PRODUCT_CATEGORIES[top_idx]
                top_conf = float(probs[top_idx])

                needs_review = top_conf < 0.35
                return {
                    "category": top_cat,
                    "confidence": round(top_conf, 4),
                    "needs_review": needs_review,
                    "label": top_cat,
                    "probabilities": prob_dict,
                    "classifier_engine": "open_clip_vit_b32"
                }
            except Exception as e:
                logger.error(f"Error during OpenCLIP classification: {e}", exc_info=True)

        # 2. Try ResNet-18 ImageNet inference fallback
        if self.resnet_model is not None and self.resnet_categories is not None:
            try:
                from torchvision import transforms
                tf = transforms.Compose([
                    transforms.Resize((224, 224)),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
                tensor = tf(pil_image).unsqueeze(0).to(self.device)
                with torch.no_grad():
                    out = self.resnet_model(tensor)
                    probs = torch.softmax(out, dim=1)[0].cpu().numpy()

                top_idx = int(np.argmax(probs))
                raw_label = self.resnet_categories[top_idx]
                top_conf = float(probs[top_idx])

                mapped_cat = self._map_imagenet_label(raw_label)
                needs_review = top_conf < 0.30
                return {
                    "category": mapped_cat,
                    "confidence": round(top_conf, 4),
                    "needs_review": needs_review,
                    "label": raw_label,
                    "probabilities": {mapped_cat: round(top_conf, 4)},
                    "classifier_engine": "resnet18_imagenet"
                }
            except Exception as e:
                logger.error(f"Error during ResNet classification: {e}", exc_info=True)

        return self._uncertain_result("Vision classifiers unavailable")

    def _map_imagenet_label(self, label: str) -> str:
        l = label.lower()
        if any(w in l for w in ("shoe", "sneaker", "boot", "loafer", "sandal", "clog")):
            return "Footwear & Sneakers"
        if any(w in l for w in ("shirt", "cardigan", "suit", "coat", "cloak", "poncho", "sweatshirt")):
            return "Casual Shirts"
        if any(w in l for w in ("jersey", "t-shirt", "polo")):
            return "Polo T-Shirts"
        if any(w in l for w in ("jean", "denim", "trouser", "pant")):
            return "Trousers & Pants"
        if any(w in l for w in ("bag", "backpack", "purse", "wallet", "handbag", "luggage")):
            return "Accessories & Bags"
        if any(w in l for w in ("phone", "laptop", "speaker", "mouse", "ipod", "electronic", "headphone")):
            return "Electronics"
        if any(w in l for w in ("vase", "pitcher", "mug", "pot", "plate", "bowl", "cup")):
            return "Home & Living"
        return "Footwear & Sneakers"

    def _uncertain_result(self, reason: str) -> dict:
        return {
            "category": "Footwear & Sneakers",
            "confidence": 0.0,
            "needs_review": True,
            "label": "needs_review",
            "probabilities": {},
            "classifier_engine": f"fallback ({reason})"
        }

classifier = ProductClassifier()

def get_product_classifier() -> ProductClassifier:
    return classifier
