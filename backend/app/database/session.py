import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.security import get_password_hash
from app.database.models import Base, User, Merchant, Product, Video, Review, Interaction, FraudFlag, AppSetting

logger = logging.getLogger(__name__)

# Engine configuration (works for SQLite and PostgreSQL)
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
    seed_initial_data()

def seed_initial_data():
    """
    Idempotent database seeding for Scrollix AI.
    Expands the catalogue with 10 distinct demo merchants and 50+ realistic products
    across Shoes/Sneakers, Electronics, Casual Shirts, and Polo T-Shirts in INR.
    Preserves all existing user records, orders, interactions, and reviews.
    """
    db: Session = SessionLocal()
    try:
        logger.info("Checking and synchronizing Scrollix AI demo catalogue...")

        # -------------------------------------------------------------
        # 1. Base Users (Admin & Customer)
        # -------------------------------------------------------------
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(
                email="admin@scrollix.ai",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"
            ))

        demo_customer = db.query(User).filter(User.username == "alex_shopper").first()
        if not demo_customer:
            demo_customer = User(
                email="alex@gmail.com",
                username="alex_shopper",
                hashed_password=get_password_hash("customer123"),
                role="customer",
                avatar_url="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150",
                preferences_json=json.dumps({"preferred_categories": ["Footwear & Sneakers", "Casual Shirts", "Polo T-Shirts"], "budget_max": 5000})
            )
            db.add(demo_customer)
        db.flush()

        # -------------------------------------------------------------
        # 2. 10 Distinct Demo Merchants
        # -------------------------------------------------------------
        demo_merchants_data = [
            {
                "username": "artisan_leather",
                "email": "artisan@leathercraft.com",
                "business_name": "Artisan Heritage Leather",
                "description": "[Demo Merchant] Handmade full-grain leather bags, minimalist wallets, and durable accessories crafted locally.",
                "category": "Accessories & Leathercraft",
                "address": "450 Mission St, San Francisco, CA",
                "city": "San Francisco",
                "latitude": 37.7905,
                "longitude": -122.3990,
                "phone": "+1 (415) 555-0142",
                "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150",
                "trust_score": 94.5
            },
            {
                "username": "pulse_kicks",
                "email": "pulse@sneakers.com",
                "business_name": "Pulse Kicks & Streetwear",
                "description": "[Demo Merchant] Curated high-performance sneakers, limited edition kicks, and contemporary urban streetwear.",
                "category": "Footwear & Sneakers",
                "address": "845 Market St, San Francisco, CA",
                "city": "San Francisco",
                "latitude": 37.7845,
                "longitude": -122.4065,
                "phone": "+1 (415) 555-0188",
                "avatar_url": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=150",
                "trust_score": 89.0
            },
            {
                "username": "luna_ceramics",
                "email": "luna@ceramics.com",
                "business_name": "Luna Studio Ceramics & Home",
                "description": "[Demo Merchant] Contemporary stoneware, hand-thrown ceramic mugs, minimalist planters, and aesthetic home decor.",
                "category": "Home & Living",
                "address": "980 Valencia St, San Francisco, CA",
                "city": "San Francisco",
                "latitude": 37.7578,
                "longitude": -122.4215,
                "phone": "+1 (415) 555-0199",
                "avatar_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150",
                "trust_score": 92.0
            },
            {
                "username": "demo_volttech",
                "email": "volttech@scrollix-demo.ai",
                "business_name": "VoltTech Audio & Wearables",
                "description": "[Demo Merchant] Studio-grade active noise cancelling headphones, TWS earbuds, and portable acoustic tech.",
                "category": "Electronics",
                "address": "100 Feet Rd, Indiranagar, Bengaluru, Karnataka",
                "city": "Bengaluru",
                "latitude": 12.9784,
                "longitude": 77.6408,
                "phone": "+91 80 4123 9801",
                "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150",
                "trust_score": 95.0
            },
            {
                "username": "demo_urbanthreads",
                "email": "urbanthreads@scrollix-demo.ai",
                "business_name": "UrbanThreads Casuals",
                "description": "[Demo Merchant] Hand-loomed cotton casual button-downs, vintage denim overshirts, and washed camp collar shirts.",
                "category": "Casual Shirts",
                "address": "Inner Circle, Connaught Place, New Delhi",
                "city": "New Delhi",
                "latitude": 28.6315,
                "longitude": 77.2167,
                "phone": "+91 11 2341 5500",
                "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150",
                "trust_score": 91.5
            },
            {
                "username": "demo_poloclub",
                "email": "poloclub@scrollix-demo.ai",
                "business_name": "The Polo Club Atelier",
                "description": "[Demo Merchant] Premium Mercerized cotton pique polos, knitted open-collar resort shirts, and athletic golf polos.",
                "category": "Polo T-Shirts",
                "address": "High Street Phoenix, Lower Parel, Mumbai, Maharashtra",
                "city": "Mumbai",
                "latitude": 18.9953,
                "longitude": 72.8242,
                "phone": "+91 22 4004 8820",
                "avatar_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150",
                "trust_score": 96.0
            },
            {
                "username": "demo_novacore",
                "email": "novacore@scrollix-demo.ai",
                "business_name": "NovaCore Gadgets & Peripherals",
                "description": "[Demo Merchant] High-performance mechanical keyboards, ergonomic mice, GaN fast chargers, and 4K desktop displays.",
                "category": "Electronics",
                "address": "DLF Cyber City, Phase 2, Gurugram, Haryana",
                "city": "Gurugram",
                "latitude": 28.4907,
                "longitude": 77.0898,
                "phone": "+91 124 456 7890",
                "avatar_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150",
                "trust_score": 93.5
            },
            {
                "username": "demo_auralinen",
                "email": "auralinen@scrollix-demo.ai",
                "business_name": "Aura Linen & Loom",
                "description": "[Demo Merchant] Pure European flax linen shirts, breathable seersucker casuals, and relaxed holiday checks.",
                "category": "Casual Shirts",
                "address": "Kala Ghoda, Fort, Mumbai, Maharashtra",
                "city": "Mumbai",
                "latitude": 18.9298,
                "longitude": 72.8333,
                "phone": "+91 22 2288 3412",
                "avatar_url": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=150",
                "trust_score": 90.0
            },
            {
                "username": "demo_apexsneakers",
                "email": "apexsneakers@scrollix-demo.ai",
                "business_name": "Apex Athletic Sneaker Lab",
                "description": "[Demo Merchant] Carbon-plated marathon road runners, trail hiking footwear, and lifestyle zero-drop trainers.",
                "category": "Footwear & Sneakers",
                "address": "80 Feet Rd, 4th Block, Koramangala, Bengaluru, Karnataka",
                "city": "Bengaluru",
                "latitude": 12.9352,
                "longitude": 77.6245,
                "phone": "+91 80 4987 6543",
                "avatar_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150",
                "trust_score": 94.0
            },
            {
                "username": "demo_classicfitters",
                "email": "classicfitters@scrollix-demo.ai",
                "business_name": "Classic Fitters & Co.",
                "description": "[Demo Merchant] Tailored-fit Supima cotton polos, vintage tipping collars, and organic breathable jersey polos.",
                "category": "Polo T-Shirts",
                "address": "Brigade Road, Ashok Nagar, Bengaluru, Karnataka",
                "city": "Bengaluru",
                "latitude": 12.9733,
                "longitude": 77.6074,
                "phone": "+91 80 2558 7766",
                "avatar_url": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150",
                "trust_score": 92.5
            }
        ]

        merchants_by_name = {}
        for m_data in demo_merchants_data:
            # 2a. Ensure Merchant User exists
            m_user = db.query(User).filter(User.username == m_data["username"]).first()
            if not m_user:
                m_user = User(
                    email=m_data["email"],
                    username=m_data["username"],
                    hashed_password=get_password_hash("merchant123"),
                    role="merchant",
                    avatar_url=m_data["avatar_url"]
                )
                db.add(m_user)
                db.flush()

            # 2b. Ensure Merchant record exists
            merchant = db.query(Merchant).filter(Merchant.business_name == m_data["business_name"]).first()
            if not merchant:
                # check if user already has a merchant record
                merchant = db.query(Merchant).filter(Merchant.user_id == m_user.id).first()

            if not merchant:
                merchant = Merchant(
                    user_id=m_user.id,
                    business_name=m_data["business_name"],
                    description=m_data["description"],
                    category=m_data["category"],
                    address=m_data["address"],
                    city=m_data["city"],
                    latitude=m_data["latitude"],
                    longitude=m_data["longitude"],
                    phone=m_data["phone"],
                    is_verified=True,
                    trust_score=m_data["trust_score"]
                )
                db.add(merchant)
                db.flush()
            else:
                # Update merchant metadata while preserving id
                merchant.description = m_data["description"]
                merchant.address = m_data["address"]
                merchant.city = m_data["city"]
                merchant.latitude = m_data["latitude"]
                merchant.longitude = m_data["longitude"]
                merchant.phone = m_data["phone"]
                merchant.is_verified = True
                merchant.trust_score = m_data["trust_score"]

            merchants_by_name[m_data["business_name"]] = merchant

        db.flush()

        # -------------------------------------------------------------
        # 3. 56 Realistic Catalogue Products Across Required Categories
        # -------------------------------------------------------------
        products_catalog = [
            # === Footwear & Sneakers (Shoes / Sneakers) ===
            {
                "merchant": "Pulse Kicks & Streetwear",
                "title": "Velocity Air Runner Sneakers",
                "description": "Responsive carbon-fiber infused running shoes with breathable mesh and dynamic cushioning for road sprints.",
                "category": "Footwear & Sneakers",
                "price": 4499.00,
                "inventory": 18,
                "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
                "tags": ["shoes", "sneakers", "running", "red", "athletic", "carbon-fiber"]
            },
            {
                "merchant": "Pulse Kicks & Streetwear",
                "title": "Urban High-Top Street Canvas",
                "description": "Classic monochrome silhouette high-top sneakers designed for all-day comfort, skateboarding, and durability.",
                "category": "Footwear & Sneakers",
                "price": 2899.00,
                "inventory": 14,
                "image_url": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=600&auto=format&fit=crop&q=80",
                "tags": ["shoes", "sneakers", "canvas", "streetwear", "black", "high-top"]
            },
            {
                "merchant": "Apex Athletic Sneaker Lab",
                "title": "Apex Carbon Pro Road Runner",
                "description": "Ultra-responsive propulsion carbon plate running shoes engineered for distance pacing and optimal energy return.",
                "category": "Footwear & Sneakers",
                "price": 5999.00,
                "inventory": 15,
                "image_url": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600&auto=format&fit=crop&q=80",
                "tags": ["shoes", "sneakers", "road runner", "carbon plate", "athletic", "racing"]
            },
            {
                "merchant": "Apex Athletic Sneaker Lab",
                "title": "Nimbus Cloud Foam Walking Shoes",
                "description": "Featherlight memory-foam slip-on walking trainers with breathable knitted uppers for 12-hour daily comfort.",
                "category": "Footwear & Sneakers",
                "price": 3499.00,
                "inventory": 22,
                "image_url": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=600&auto=format&fit=crop&q=80",
                "tags": ["shoes", "sneakers", "walking", "foam", "slip-on", "breathable"]
            },
            {
                "merchant": "Apex Athletic Sneaker Lab",
                "title": "AeroGlide Trail Running Shoes",
                "description": "All-weather aggressive lug tread trail runners with reinforced toe guards and water-resistant ripstop mesh.",
                "category": "Footwear & Sneakers",
                "price": 4799.00,
                "inventory": 16,
                "image_url": "https://images.unsplash.com/photo-1551107696-a4b085a6d965?w=600&auto=format&fit=crop&q=80",
                "tags": ["shoes", "sneakers", "trail", "running", "hiking", "waterproof"]
            },
            {
                "merchant": "Pulse Kicks & Streetwear",
                "title": "Retro Court Leather Low-Tops",
                "description": "1980s retro tennis silhouette featuring soft nappa leather, perforated vamp, and stitched vulcanized cupsoles.",
                "category": "Footwear & Sneakers",
                "price": 3899.00,
                "inventory": 20,
                "image_url": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600&auto=format&fit=crop&q=80",
                "tags": ["shoes", "sneakers", "retro", "white", "leather", "court", "low-top"]
            },
            {
                "merchant": "Apex Athletic Sneaker Lab",
                "title": "Stealth Knit Slip-On Trainers",
                "description": "Ergonomic engineered-knit training shoes with sock-like collar and shock-absorbing EVA outsoles.",
                "category": "Footwear & Sneakers",
                "price": 2499.00,
                "inventory": 25,
                "image_url": "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=600&auto=format&fit=crop&q=80",
                "tags": ["shoes", "sneakers", "slip-on", "knit", "training", "black"]
            },
            {
                "merchant": "Pulse Kicks & Streetwear",
                "title": "High-Top Suede Skater Shoes",
                "description": "Padded collar high-top skate shoes crafted in durable rough-out suede with honeycomb grip gum soles.",
                "category": "Footwear & Sneakers",
                "price": 3299.00,
                "inventory": 18,
                "image_url": "https://images.unsplash.com/photo-1514989940723-e8e51635b782?w=600&auto=format&fit=crop&q=80",
                "tags": ["shoes", "sneakers", "suede", "skate", "high-top", "streetwear"]
            },
            {
                "merchant": "Pulse Kicks & Streetwear",
                "title": "Pulse Boost Streetwear Kicks",
                "description": "Futuristic street sneaker with segmented air-cushioned midsole and reflective 3M detailing for night visibility.",
                "category": "Footwear & Sneakers",
                "price": 6499.00,
                "inventory": 12,
                "image_url": "https://images.unsplash.com/photo-1512374382149-233c42b661ac?w=600&auto=format&fit=crop&q=80",
                "tags": ["shoes", "sneakers", "boost", "reflective", "futuristic", "streetwear"]
            },
            {
                "merchant": "Apex Athletic Sneaker Lab",
                "title": "All-Terrain Vibram Trekking Shoes",
                "description": "Rugged cross-terrain low ankle shoes with genuine Vibram rubber outsoles and anti-debris gusseted tongue.",
                "category": "Footwear & Sneakers",
                "price": 5299.00,
                "inventory": 14,
                "image_url": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=600&auto=format&fit=crop&q=80",
                "tags": ["shoes", "sneakers", "trekking", "vibram", "hiking", "outdoor"]
            },
            {
                "merchant": "Apex Athletic Sneaker Lab",
                "title": "Minimalist Zero-Drop Training Shoes",
                "description": "Wide toe-box barefoot style gym trainers designed for heavy deadlifts, squats, and natural gait development.",
                "category": "Footwear & Sneakers",
                "price": 3199.00,
                "inventory": 19,
                "image_url": "https://images.unsplash.com/photo-1575537302964-96cd47c06b1b?w=600&auto=format&fit=crop&q=80",
                "tags": ["shoes", "sneakers", "barefoot", "zero-drop", "crossfit", "gym"]
            },
            {
                "merchant": "Artisan Heritage Leather",
                "title": "Classic Oxford Leather Dress Shoes",
                "description": "Hand-burnished full grain leather cap-toe Oxford shoes with Goodyear welted leather sole for formal elegance.",
                "category": "Footwear & Sneakers",
                "price": 4299.00,
                "inventory": 10,
                "image_url": "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=600&auto=format&fit=crop&q=80",
                "tags": ["shoes", "oxford", "formal", "dress shoes", "leather", "brown"]
            },
            {
                "merchant": "Artisan Heritage Leather",
                "title": "Chelsea Suede Ankle Boots",
                "description": "Water-repellent Italian suede Chelsea boots with elasticated side gussets and lightweight crepe rubber soles.",
                "category": "Footwear & Sneakers",
                "price": 5499.00,
                "inventory": 11,
                "image_url": "https://images.unsplash.com/photo-1638247025967-b4e38f787b76?w=600&auto=format&fit=crop&q=80",
                "tags": ["shoes", "boots", "chelsea", "suede", "ankle boots", "tan"]
            },
            {
                "merchant": "Pulse Kicks & Streetwear",
                "title": "Chunky Sole Platform Chunky Sneakers",
                "description": "Contemporary platform dad sneakers with multi-layered leather-mesh panels and sculpted lightweight midsoles.",
                "category": "Footwear & Sneakers",
                "price": 3999.00,
                "inventory": 16,
                "image_url": "https://images.unsplash.com/photo-1597045566677-8cf032ed6634?w=600&auto=format&fit=crop&q=80",
                "tags": ["shoes", "sneakers", "chunky", "platform", "dad shoes", "streetwear"]
            },

            # === Electronics ===
            {
                "merchant": "VoltTech Audio & Wearables",
                "title": "VoltTech Horizon ANC Wireless Headphones",
                "description": "Over-ear hybrid Active Noise Cancelling headphones featuring 40mm beryllium drivers and 45-hour battery life.",
                "category": "Electronics",
                "price": 6999.00,
                "inventory": 20,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
                "tags": ["electronics", "audio", "headphones", "anc", "bluetooth", "wireless"]
            },
            {
                "merchant": "VoltTech Audio & Wearables",
                "title": "SonicPulse True Wireless Earbuds",
                "description": "IPX7 waterproof sport earbuds with quad-mic ENC for crystal-clear calls and punchy deep bass tuning.",
                "category": "Electronics",
                "price": 2999.00,
                "inventory": 30,
                "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80",
                "tags": ["electronics", "earbuds", "tws", "bluetooth", "wireless", "audio"]
            },
            {
                "merchant": "NovaCore Gadgets & Peripherals",
                "title": "NovaCore 4K Ultra-Wide Curved Monitor",
                "description": "34-inch 1500R curved HDR400 display with 99% sRGB, 144Hz refresh rate, and 90W USB-C Power Delivery.",
                "category": "Electronics",
                "price": 24999.00,
                "inventory": 8,
                "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80",
                "tags": ["electronics", "monitor", "4k", "curved", "display", "ultrawide", "screen"]
            },
            {
                "merchant": "NovaCore Gadgets & Peripherals",
                "title": "Lumina RGB Mechanical Gaming Keyboard",
                "description": "Hot-swappable custom linear switches, CNC anodized aluminum frame, sound-dampening foam, and per-key RGB.",
                "category": "Electronics",
                "price": 4499.00,
                "inventory": 22,
                "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80",
                "tags": ["electronics", "keyboard", "mechanical", "rgb", "gaming", "hot-swap"]
            },
            {
                "merchant": "NovaCore Gadgets & Peripherals",
                "title": "Precision Pro Wireless Ergonomic Mouse",
                "description": "Natural 57-degree handshake posture vertical mouse with silent switches, dual Bluetooth, and 2.4GHz dongle.",
                "category": "Electronics",
                "price": 2199.00,
                "inventory": 28,
                "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop&q=80",
                "tags": ["electronics", "mouse", "wireless", "ergonomic", "peripherals"]
            },
            {
                "merchant": "NovaCore Gadgets & Peripherals",
                "title": "AuraGlow Smart LED Desk Lamp",
                "description": "Eye-care asymmetric optical lamp with stepless dimming, 5 color temperatures, and built-in 15W Qi wireless charger.",
                "category": "Electronics",
                "price": 2799.00,
                "inventory": 25,
                "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&auto=format&fit=crop&q=80",
                "tags": ["electronics", "lamp", "desk lamp", "led", "smart home", "wireless charger"]
            },
            {
                "merchant": "VoltTech Audio & Wearables",
                "title": "SoundWave 360 Portable Bluetooth Speaker",
                "description": "360-degree immersive acoustic portable speaker with dual passive radiators, IP67 dustproof rating, and 20h playtime.",
                "category": "Electronics",
                "price": 3499.00,
                "inventory": 24,
                "image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80",
                "tags": ["electronics", "speaker", "bluetooth", "portable", "audio", "sound"]
            },
            {
                "merchant": "NovaCore Gadgets & Peripherals",
                "title": "NovaCore MagCharge 65W GaN Fast Charger",
                "description": "Pocket-sized Gallium Nitride 3-port charger (2x USB-C + 1x USB-A) capable of powering laptops, tablets, and phones.",
                "category": "Electronics",
                "price": 1899.00,
                "inventory": 35,
                "image_url": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&auto=format&fit=crop&q=80",
                "tags": ["electronics", "charger", "gan", "fast charger", "usb-c", "power"]
            },
            {
                "merchant": "VoltTech Audio & Wearables",
                "title": "PulseTrack Ultra GPS Smartwatch",
                "description": "1.43-inch AMOLED display smartwatch with built-in multi-band GPS, SpO2 blood oxygen tracking, and 14-day battery.",
                "category": "Electronics",
                "price": 5499.00,
                "inventory": 18,
                "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80",
                "tags": ["electronics", "smartwatch", "wearables", "gps", "fitness", "watch"]
            },
            {
                "merchant": "VoltTech Audio & Wearables",
                "title": "VoltTech Studio Boom Arm & USB Condenser Mic",
                "description": "Broadcast-quality cardioid condenser microphone with internal shock mount, gain dial, zero-latency jack, and arm.",
                "category": "Electronics",
                "price": 3899.00,
                "inventory": 16,
                "image_url": "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=600&auto=format&fit=crop&q=80",
                "tags": ["electronics", "microphone", "usb", "streaming", "podcast", "audio"]
            },
            {
                "merchant": "NovaCore Gadgets & Peripherals",
                "title": "HyperDrive 8-in-1 Aluminum USB-C Hub",
                "description": "CNC aerospace aluminum multiport adapter featuring 4K 60Hz HDMI, 100W PD passthrough, Gigabit LAN, and SD readers.",
                "category": "Electronics",
                "price": 2499.00,
                "inventory": 30,
                "image_url": "https://images.unsplash.com/photo-1625842268584-8f3296236761?w=600&auto=format&fit=crop&q=80",
                "tags": ["electronics", "usb-c hub", "adapter", "dongle", "hdmi", "laptop"]
            },
            {
                "merchant": "NovaCore Gadgets & Peripherals",
                "title": "NovaCore 10000mAh Magnetic Power Bank",
                "description": "Slim MagSafe-compatible wireless battery pack with kickstand and 20W PD USB-C bidirectional fast charging.",
                "category": "Electronics",
                "price": 1699.00,
                "inventory": 40,
                "image_url": "https://images.unsplash.com/photo-1609592426868-b7a421b47fb5?w=600&auto=format&fit=crop&q=80",
                "tags": ["electronics", "power bank", "battery", "wireless", "portable charger"]
            },

            # === Casual Shirts ===
            {
                "merchant": "UrbanThreads Casuals",
                "title": "Artisan Indigo Washed Denim Casual Shirt",
                "description": "100% slub cotton indigo-dyed shirt with authentic hand-abraded wash, dual chest pockets, and pearl snap buttons.",
                "category": "Casual Shirts",
                "price": 2299.00,
                "inventory": 25,
                "image_url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80",
                "tags": ["casual shirts", "shirts", "denim", "indigo", "cotton", "casual"]
            },
            {
                "merchant": "Aura Linen & Loom",
                "title": "Pure French Linen Relaxed Camp Collar Shirt",
                "description": "Pre-washed Normandy flax linen shirt featuring a retro Cuban camp collar and breezy relaxed silhouette.",
                "category": "Casual Shirts",
                "price": 2799.00,
                "inventory": 20,
                "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600&auto=format&fit=crop&q=80",
                "tags": ["casual shirts", "shirts", "linen", "camp collar", "summer", "relaxed"]
            },
            {
                "merchant": "UrbanThreads Casuals",
                "title": "Classic Tartan Plaid Flannel Shirt",
                "description": "Double-brushed heavyweight cotton flannel in traditional green and navy Blackwatch tartan for chilly evenings.",
                "category": "Casual Shirts",
                "price": 1899.00,
                "inventory": 22,
                "image_url": "https://images.unsplash.com/photo-1622445268047-927914041d0f?w=600&auto=format&fit=crop&q=80",
                "tags": ["casual shirts", "shirts", "flannel", "plaid", "cotton", "autumn"]
            },
            {
                "merchant": "UrbanThreads Casuals",
                "title": "Textured Oxford Button-Down Casual Shirt",
                "description": "Garment-dyed heavyweight Oxford weave shirt with soft roll button-down collar and box pleat for everyday ease.",
                "category": "Casual Shirts",
                "price": 1699.00,
                "inventory": 30,
                "image_url": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=600&auto=format&fit=crop&q=80",
                "tags": ["casual shirts", "shirts", "oxford", "button down", "casual", "blue"]
            },
            {
                "merchant": "Aura Linen & Loom",
                "title": "Tropical Botanics Hawaiian Vacation Shirt",
                "description": "Silky soft rayon-modal short-sleeve resort shirt with lush tropical monstera and palm foliage prints.",
                "category": "Casual Shirts",
                "price": 1499.00,
                "inventory": 28,
                "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80",
                "tags": ["casual shirts", "shirts", "hawaiian", "tropical", "resort", "short sleeve"]
            },
            {
                "merchant": "Aura Linen & Loom",
                "title": "Striped Seersucker Breathable Summer Shirt",
                "description": "Naturally puckered seersucker cotton weave that stays off your skin, maximizing airflow during hot humid days.",
                "category": "Casual Shirts",
                "price": 1999.00,
                "inventory": 20,
                "image_url": "https://images.unsplash.com/photo-1578932750294-f5075e85f44a?w=600&auto=format&fit=crop&q=80",
                "tags": ["casual shirts", "shirts", "seersucker", "striped", "breathable", "summer"]
            },
            {
                "merchant": "UrbanThreads Casuals",
                "title": "Heavyweight Corduroy Utility Overshirt",
                "description": "8-wale ribbed cotton corduroy jacket-shirt hybrid with tortoiseshell buttons and deep utility patch pockets.",
                "category": "Casual Shirts",
                "price": 2999.00,
                "inventory": 15,
                "image_url": "https://images.unsplash.com/photo-1589310243389-96a5483213a8?w=600&auto=format&fit=crop&q=80",
                "tags": ["casual shirts", "shirts", "corduroy", "overshirt", "jacket", "utility"]
            },
            {
                "merchant": "Aura Linen & Loom",
                "title": "Mandarin Collar Slub Cotton Casual Shirt",
                "description": "Band-collar grandad casual shirt woven from textured slub yarn with clean concealed front placket.",
                "category": "Casual Shirts",
                "price": 1599.00,
                "inventory": 25,
                "image_url": "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?w=600&auto=format&fit=crop&q=80",
                "tags": ["casual shirts", "shirts", "mandarin", "band collar", "cotton", "slub"]
            },
            {
                "merchant": "UrbanThreads Casuals",
                "title": "Modern Windowpane Check Casual Shirt",
                "description": "Clean graphic windowpane check cotton poplin shirt tailored in a modern semi-fitted cut.",
                "category": "Casual Shirts",
                "price": 1799.00,
                "inventory": 24,
                "image_url": "https://images.unsplash.com/photo-1603252109303-2751441dd157?w=600&auto=format&fit=crop&q=80",
                "tags": ["casual shirts", "shirts", "check", "windowpane", "poplin", "smart casual"]
            },
            {
                "merchant": "UrbanThreads Casuals",
                "title": "Raw Hem Chambray Vintage Workshirt",
                "description": "Japanese selvedge-inspired lightweight indigo chambray shirt with triple-needle chainstitch construction.",
                "category": "Casual Shirts",
                "price": 2499.00,
                "inventory": 18,
                "image_url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80",
                "tags": ["casual shirts", "shirts", "chambray", "vintage", "workshirt", "indigo"]
            },
            {
                "merchant": "Aura Linen & Loom",
                "title": "Washed Olive Linen Camp Shirt",
                "description": "Garment-softened earthy olive linen casual shirt with notched lapels and side hem vents.",
                "category": "Casual Shirts",
                "price": 2599.00,
                "inventory": 19,
                "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600&auto=format&fit=crop&q=80",
                "tags": ["casual shirts", "shirts", "linen", "olive", "camp collar", "relaxed"]
            },
            {
                "merchant": "UrbanThreads Casuals",
                "title": "Oversized Dropped-Shoulder Cotton Shirt",
                "description": "Contemporary relaxed boxy cut casual shirt in crisp 100% compact cotton with subtle curved hem.",
                "category": "Casual Shirts",
                "price": 2099.00,
                "inventory": 21,
                "image_url": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=600&auto=format&fit=crop&q=80",
                "tags": ["casual shirts", "shirts", "oversized", "streetwear", "minimalist", "white"]
            },

            # === Polo T-Shirts ===
            {
                "merchant": "The Polo Club Atelier",
                "title": "Luxury Supima Cotton Pique Polo T-Shirt",
                "description": "100% American extra-long staple Supima cotton knit polo with genuine mother-of-pearl buttons and anti-curl collar.",
                "category": "Polo T-Shirts",
                "price": 1899.00,
                "inventory": 30,
                "image_url": "https://images.unsplash.com/photo-1625910513413-5dbd80917fa9?w=600&auto=format&fit=crop&q=80",
                "tags": ["polo t-shirts", "polo", "supima", "pique", "luxury", "cotton"]
            },
            {
                "merchant": "The Polo Club Atelier",
                "title": "Royal Navy Classic Fit Mercerized Polo",
                "description": "Double-mercerized yarn polo with brilliant silky sheen, zero pill guarantee, and crisp structured ribbed cuffs.",
                "category": "Polo T-Shirts",
                "price": 2199.00,
                "inventory": 25,
                "image_url": "https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?w=600&auto=format&fit=crop&q=80",
                "tags": ["polo t-shirts", "polo", "mercerized", "navy", "classic", "formal polo"]
            },
            {
                "merchant": "Classic Fitters & Co.",
                "title": "Breathable Mesh Active Performance Golf Polo",
                "description": "4-way stretch moisture-wicking technical polo with UPF 50+ sun protection and laser-perforated collar ventilation.",
                "category": "Polo T-Shirts",
                "price": 1599.00,
                "inventory": 28,
                "image_url": "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=600&auto=format&fit=crop&q=80",
                "tags": ["polo t-shirts", "polo", "golf", "performance", "active", "quick dry"]
            },
            {
                "merchant": "The Polo Club Atelier",
                "title": "Vintage Contrast Collar Knitted Polo T-Shirt",
                "description": "1960s Riviera retro knitted cotton polo featuring two-tone contrast tipping and an open Johnny spread collar.",
                "category": "Polo T-Shirts",
                "price": 2499.00,
                "inventory": 18,
                "image_url": "https://images.unsplash.com/photo-1626497764746-6dc36546b388?w=600&auto=format&fit=crop&q=80",
                "tags": ["polo t-shirts", "polo", "knitted", "vintage", "retro", "tipping"]
            },
            {
                "merchant": "Classic Fitters & Co.",
                "title": "Textured Honeycomb Knit Polo T-Shirt",
                "description": "3D honeycomb dimensional knit fabric that delivers extraordinary breathability and refined visual depth.",
                "category": "Polo T-Shirts",
                "price": 1699.00,
                "inventory": 24,
                "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600&auto=format&fit=crop&q=80",
                "tags": ["polo t-shirts", "polo", "honeycomb", "textured", "knit", "olive"]
            },
            {
                "merchant": "The Polo Club Atelier",
                "title": "Italian Knit Open-Collar Resort Polo",
                "description": "Fine 14-gauge Italian spun combed cotton knit with seamless buttonless placket and ribbed hem band.",
                "category": "Polo T-Shirts",
                "price": 2799.00,
                "inventory": 16,
                "image_url": "https://images.unsplash.com/photo-1625910513413-5dbd80917fa9?w=600&auto=format&fit=crop&q=80",
                "tags": ["polo t-shirts", "polo", "italian", "open collar", "resort", "luxury"]
            },
            {
                "merchant": "Classic Fitters & Co.",
                "title": "Minimalist Tonal Logo Slim Fit Polo",
                "description": "Clean monochrome tailored-fit polo shirt with subtle tonal chest embroidery and stretch elastane blend.",
                "category": "Polo T-Shirts",
                "price": 1399.00,
                "inventory": 35,
                "image_url": "https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?w=600&auto=format&fit=crop&q=80",
                "tags": ["polo t-shirts", "polo", "slim fit", "black", "minimalist", "cotton"]
            },
            {
                "merchant": "Classic Fitters & Co.",
                "title": "Striped Nautical Lightweight Polo T-Shirt",
                "description": "Breton yarn-dyed horizontal stripe pique polo with contrast inner placket and engraved horn buttons.",
                "category": "Polo T-Shirts",
                "price": 1799.00,
                "inventory": 22,
                "image_url": "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=600&auto=format&fit=crop&q=80",
                "tags": ["polo t-shirts", "polo", "striped", "nautical", "pique", "summer"]
            },
            {
                "merchant": "Classic Fitters & Co.",
                "title": "Eco-Blend Organic Cotton Jersey Polo",
                "description": "GOTS-certified organic cotton jersey polo offering t-shirt softness combined with a smart polo collar.",
                "category": "Polo T-Shirts",
                "price": 1499.00,
                "inventory": 30,
                "image_url": "https://images.unsplash.com/photo-1626497764746-6dc36546b388?w=600&auto=format&fit=crop&q=80",
                "tags": ["polo t-shirts", "polo", "organic cotton", "jersey", "eco-friendly"]
            },
            {
                "merchant": "The Polo Club Atelier",
                "title": "Classic Pima Cotton Pocket Polo",
                "description": "Ultra-soft Peruvian Pima cotton polo featuring a practical chest patch pocket and reinforced split side seams.",
                "category": "Polo T-Shirts",
                "price": 1999.00,
                "inventory": 20,
                "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600&auto=format&fit=crop&q=80",
                "tags": ["polo t-shirts", "polo", "pima cotton", "pocket", "maroon", "casual"]
            },
            {
                "merchant": "Classic Fitters & Co.",
                "title": "Quick-Dry UV Protection Tennis Polo",
                "description": "Engineered court polo with underarm mesh gussets, flatlock chafe-free seams, and reflective sport accents.",
                "category": "Polo T-Shirts",
                "price": 1649.00,
                "inventory": 26,
                "image_url": "https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=600&auto=format&fit=crop&q=80",
                "tags": ["polo t-shirts", "polo", "tennis", "sport", "quick-dry", "white"]
            },
            {
                "merchant": "The Polo Club Atelier",
                "title": "Monogram Embroidered Mercerized Luxury Polo",
                "description": "Signature luxury polo crafted in liquid-soft silken mercerized yarn with handcrafted monogram crest.",
                "category": "Polo T-Shirts",
                "price": 2899.00,
                "inventory": 14,
                "image_url": "https://images.unsplash.com/photo-1625910513413-5dbd80917fa9?w=600&auto=format&fit=crop&q=80",
                "tags": ["polo t-shirts", "polo", "monogram", "luxury", "mercerized", "gold crest"]
            },

            # === Accessories & Home Living ===
            {
                "merchant": "Artisan Heritage Leather",
                "title": "Vintage Full-Grain Leather Satchel",
                "description": "Hand-stitched vegetable tanned briefcase satchel with solid brass buckles. Fits 15 inch laptops.",
                "category": "Accessories",
                "price": 4999.00,
                "inventory": 8,
                "image_url": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&auto=format&fit=crop&q=80",
                "tags": ["bag", "satchel", "leather", "briefcase", "vintage"]
            },
            {
                "merchant": "Artisan Heritage Leather",
                "title": "Minimalist Bifold Card Wallet",
                "description": "Ultra-slim RFID protected leather card holder crafted from premium Italian cowhide.",
                "category": "Accessories",
                "price": 1299.00,
                "inventory": 25,
                "image_url": "https://images.unsplash.com/photo-1627123424574-724758594e93?w=600&auto=format&fit=crop&q=80",
                "tags": ["wallet", "leather", "cardholder", "minimalist"]
            },
            {
                "merchant": "Artisan Heritage Leather",
                "title": "Heritage Full-Grain Leather Belt",
                "description": "1.5-inch English bridle leather belt with solid brushed brass roller buckle and beveled hand-waxed edges.",
                "category": "Accessories",
                "price": 1499.00,
                "inventory": 30,
                "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&auto=format&fit=crop&q=80",
                "tags": ["accessories", "leather", "belt", "handcrafted", "brown"]
            },
            {
                "merchant": "Artisan Heritage Leather",
                "title": "Handcrafted Leather Passport Travel Wallet",
                "description": "Full-grain vegetable tanned passport travel organiser with boarding pass pocket and 6 card slots.",
                "category": "Accessories",
                "price": 1899.00,
                "inventory": 18,
                "image_url": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&auto=format&fit=crop&q=80",
                "tags": ["accessories", "leather", "wallet", "passport", "travel"]
            },
            {
                "merchant": "Luna Studio Ceramics & Home",
                "title": "Nordic Matte Ceramic Coffee Mug",
                "description": "Ergonomic 12oz handmade ceramic mug featuring a speckled glaze finish and heat-retaining clay.",
                "category": "Home & Living",
                "price": 799.00,
                "inventory": 30,
                "image_url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600&auto=format&fit=crop&q=80",
                "tags": ["cup", "mug", "coffee", "ceramic", "tableware"]
            },
            {
                "merchant": "Luna Studio Ceramics & Home",
                "title": "Terra Stoneware Planter Pot",
                "description": "Handcrafted terracotta planter with drainage plate. Perfect for succulents, herbs, and indoor plants.",
                "category": "Home & Living",
                "price": 1199.00,
                "inventory": 14,
                "image_url": "https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=600&auto=format&fit=crop&q=80",
                "tags": ["pot", "planter", "ceramics", "home", "green"]
            }
        ]

        added_products = 0
        updated_products = 0
        for p_data in products_catalog:
            m = merchants_by_name.get(p_data["merchant"])
            if not m:
                continue

            existing_p = db.query(Product).filter(Product.title == p_data["title"]).first()
            if not existing_p:
                p = Product(
                    merchant_id=m.id,
                    title=p_data["title"],
                    description=p_data["description"],
                    category=p_data["category"],
                    price=p_data["price"],
                    inventory=p_data["inventory"],
                    image_url=p_data["image_url"],
                    tags_json=json.dumps(p_data["tags"]),
                    is_active=True
                )
                db.add(p)
                added_products += 1
            else:
                # Update details in-place to ensure INR prices and accurate categories
                existing_p.price = p_data["price"]
                existing_p.inventory = p_data["inventory"]
                existing_p.category = p_data["category"]
                existing_p.description = p_data["description"]
                existing_p.tags_json = json.dumps(p_data["tags"])
                existing_p.image_url = p_data["image_url"]
                updated_products += 1

        db.flush()
        logger.info(f"Products synchronized: {added_products} added, {updated_products} verified/updated.")

        # -------------------------------------------------------------
        # 4. Videos, Reviews, and Interactions (Preserve & Add if empty)
        # -------------------------------------------------------------
        if db.query(Video).count() == 0:
            m_pulse = merchants_by_name.get("Pulse Kicks & Streetwear")
            m_artisan = merchants_by_name.get("Artisan Heritage Leather")
            m_luna = merchants_by_name.get("Luna Studio Ceramics & Home")

            p_runner = db.query(Product).filter(Product.title.like("%Velocity Air Runner%")).first()
            p_satchel = db.query(Product).filter(Product.title.like("%Vintage Full-Grain%")).first()
            p_mug = db.query(Product).filter(Product.title.like("%Nordic Matte Ceramic%")).first()

            if m_pulse and p_runner:
                db.add(Video(
                    user_id=m_pulse.user_id,
                    title="Unboxing the Velocity Air Runners 🔥 Local SF Streetwear",
                    description="Checking out the latest drop from Pulse Kicks in SoMa! Notice the carbon plate response.",
                    video_url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                    thumbnail_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
                    duration=15.0,
                    detections_json=json.dumps([
                        {
                            "timestamp": 2.5,
                            "box": [120, 240, 480, 560],
                            "label": "shoe",
                            "confidence": 0.94,
                            "product_id": p_runner.id,
                            "product_title": p_runner.title,
                            "price": p_runner.price
                        }
                    ])
                ))

            if m_artisan and p_satchel:
                db.add(Video(
                    user_id=m_artisan.user_id,
                    title="Handcrafted Leather Briefcase Studio Tour 👜",
                    description="Step into our downtown San Francisco workshop where we hand-stitch every heritage satchel.",
                    video_url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
                    thumbnail_url="https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&auto=format&fit=crop&q=80",
                    duration=15.0,
                    detections_json=json.dumps([
                        {
                            "timestamp": 1.5,
                            "box": [80, 160, 520, 580],
                            "label": "handbag",
                            "confidence": 0.89,
                            "product_id": p_satchel.id,
                            "product_title": p_satchel.title,
                            "price": p_satchel.price
                        }
                    ])
                ))

            if m_luna and p_mug:
                db.add(Video(
                    user_id=m_luna.user_id,
                    title="Morning Matcha in our Speckled Ceramic Mug ☕",
                    description="Hand-thrown pottery in the Mission District. Each mug is individually unique.",
                    video_url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
                    thumbnail_url="https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=600&auto=format&fit=crop&q=80",
                    duration=15.0,
                    detections_json=json.dumps([
                        {
                            "timestamp": 3.0,
                            "box": [180, 200, 440, 480],
                            "label": "cup",
                            "confidence": 0.96,
                            "product_id": p_mug.id,
                            "product_title": p_mug.title,
                            "price": p_mug.price
                        }
                    ])
                ))
            db.flush()

        # -------------------------------------------------------------
        # 5. Reviews (Add sample reviews if empty)
        # -------------------------------------------------------------
        if db.query(Review).count() == 0 and demo_customer:
            p_runner = db.query(Product).filter(Product.title.like("%Velocity Air Runner%")).first()
            p_satchel = db.query(Product).filter(Product.title.like("%Vintage Full-Grain%")).first()
            p_mug = db.query(Product).filter(Product.title.like("%Nordic Matte Ceramic%")).first()

            if p_runner:
                db.add(Review(
                    user_id=demo_customer.id,
                    product_id=p_runner.id,
                    rating=5,
                    comment="Incredible quality! The carbon plate cushioning gives an immediate bounce, and local pickup in SF was seamless.",
                    sentiment_score=0.92,
                    sentiment_label="positive"
                ))
            if p_satchel:
                db.add(Review(
                    user_id=demo_customer.id,
                    product_id=p_satchel.id,
                    rating=5,
                    comment="Authentic full grain leather that smells amazing. Solid brass buckles feel indestructible.",
                    sentiment_score=0.88,
                    sentiment_label="positive"
                ))
            if p_mug:
                db.add(Review(
                    user_id=demo_customer.id,
                    product_id=p_mug.id,
                    rating=4,
                    comment="Very aesthetic mug and nice weight, keeps coffee warm. Shipping took one extra day but worth it.",
                    sentiment_score=0.45,
                    sentiment_label="positive"
                ))
            db.flush()

        # -------------------------------------------------------------
        # 6. Synchronize FAISS Vector Index
        # -------------------------------------------------------------
        try:
            from app.services.vector_search.faiss_index import vector_index
            from app.services.embeddings.embedder import embedder

            all_active_products = db.query(Product).filter(Product.is_active == True).all()
            new_vectors_indexed = 0
            for prod in all_active_products:
                if prod.id not in vector_index.product_id_to_id:
                    feat_text = f"{prod.title} {prod.category} {prod.description} {' '.join(prod.get_tags())}"
                    vec = embedder.embed_text(feat_text)
                    vector_index.add_product(prod.id, vec)
                    prod.embedding_id = prod.id
                    new_vectors_indexed += 1

            if new_vectors_indexed > 0:
                logger.info(f"FAISS index updated with {new_vectors_indexed} new product vectors. Index total: {vector_index.index.ntotal}.")
        except Exception as e:
            logger.warning(f"FAISS sync during seeding encountered non-fatal notice: {e}")

        db.commit()
        logger.info("Demo catalogue synchronization complete.")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding database: {e}", exc_info=True)
    finally:
        db.close()
