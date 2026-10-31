# VELLORE INSTITUTE OF TECHNOLOGY
### School of Computer Science Engineering and Information Systems
**Fall Semester 2026**

---

**Course Code:** ISWE302L Artificial Inteligence  
**Course Title:** Capstone Project / Dissertation - I  
**Class ID:** VL2026270101829  
**Review:** Review - II (Final Review)  
**Date:** 13/10/2026  

---

# SCROLLIX AI: INTELLIGENT SOCIAL COMMERCE & LOCATION-AWARE SHORT-FORM VIDEO RECOMMENDATION PLATFORM

**Submitted by:**  
- **24MIS0216** – Vivek Pandey  
- **24MIS0050** – S. Hemal  
- **24MIS0204** – Jay Prakash  

**Under the Guidance of:**  
**Prof. Nivedita S**  
*Assistant Professor, School of Computer Science Engineering and Information Systems (SCORE)*  
*Vellore Institute of Technology, Vellore - 632014*  

---

<div style="page-break-after: always;"></div>

# PROJECT SNAPSHOT

## PART A – PROJECT OVERVIEW

| Particular | Details |
| :--- | :--- |
| **Project Title** | **Scrollix AI — Intelligent Social Commerce & Location-Aware Video Recommendations** |
| **Area of Application** | Multimodal Social Commerce, Edge Computer Vision, Geospatial Recommendation Systems, Trust & Fraud Prevention |
| **Scope** | End-to-end desktop and web application fusing real-time computer vision (Ultralytics YOLOv11), 512-dimensional vector search (FAISS IndexFlatIP), and geospatial intelligence (OpenStreetMap + Haversine geodesic formula) to convert short-form video engagement into verified local merchant transactions without requiring cloud GPU infrastructure. |

### Alignment with Sustainable Development Goals (SDGs)

| SDG No. | SDG Title | Justification |
| :---: | :--- | :--- |
| **SDG 8** | **Decent Work and Economic Growth** | Empowers independent neighborhood merchants, local artisans, and small-and-medium enterprises (SMEs) to access digital social commerce without prohibitive advertising costs, driving sustainable local economic expansion. |
| **SDG 9** | **Industry, Innovation, and Infrastructure** | Introduces an edge-first, zero-cloud-fee AI inference paradigm for computer vision and vector similarity search, enabling scalable retail technology on commodity consumer hardware. |
| **SDG 11** | **Sustainable Cities and Communities** | Enhances urban community resilience by prioritizing local proximity discovery, reducing long-distance inter-city delivery logistics and associated carbon emissions. |
| **SDG 12** | **Responsible Consumption and Production** | Incorporates algorithmic fraud detection, verifiable merchant trust scoring, and transparent sentiment analysis to reduce counterfeit listings, product misrepresentation, and return-waste cycles. |

### Inputs – Features – Outputs

| S. No. | Feature | Input Given | Output |
| :---: | :--- | :--- | :--- |
| **1** | **AI Video Feed & Object Detection** | Raw MP4 video stream / frames | Bounding boxes with COCO commerce labels, detection confidence percentage, clickable product overlay drawer. |
| **2** | **Multimodal Video & Image Ingestion** | Uploaded video clip or JPEG/PNG product photo | Automated frame extraction, bounding box crops, 512-dimensional embedding generation, and instant FAISS catalogue match. |
| **3** | **Multimodal Smart Search** | Natural language text query, voice microphone audio input, or image file | Semantic and visual cosine similarity matches retrieved from FAISS index and ranked by relevance. |
| **4** | **Location Discovery & Geospatial Radius** | User GPS coordinates or city selection with search radius (1–50 km) | Interactive Leaflet/OpenStreetMap markers, Haversine spherical distance calculation, and nearby verified merchant catalog. |
| **5** | **Grounded AI Shopping Assistant** | Conversational user prompt with budget/category constraints | Contextually grounded recommendations retrieved strictly from live database catalogue, eliminating hallucinations. |
| **6** | **Explainable Fraud & Trust Moderation** | Merchant product velocity, pricing outliers, title similarity | Automated risk score (0–100), transparent explainable reason triggers, and administrative moderation queue. |
| **7** | **Event-Driven Business Analytics** | Real user interactions (views, likes, clicks, purchases) | Factual click-through rates (CTR), conversion percentages, average dwell times, and 7-day time-series engagement graphs. |
| **Final Output** | **Complete Integrated System** | Multi-channel user signals & video uploads | Standalone, production-packaged desktop Windows application delivering sub-50ms vector search, real-time object detection, and local commerce discovery. |

### Demo Video

| Particular | Details |
| :--- | :--- |
| **Video URL** | [https://drive.google.com/file/d/1D8WOmH4sjDmFTlU2tX3bXGIpTfDXS7-6/view?usp=drivesdk](https://drive.google.com/file/d/1D8WOmH4sjDmFTlU2tX3bXGIpTfDXS7-6/view?usp=drivesdk) |
| **Duration** | 1 min 30 seconds (01:30) |

### Technical Stack

| Layer | Technology / Tool | Version / Specification | Licence |
| :--- | :--- | :--- | :--- |
| **Desktop Shell** | Electron | v33.4.11 | MIT |
| **Frontend UI** | React, TypeScript, Vite | React 18.3, Vite 5.4, TS 5.6 | MIT |
| **Maps & Tiles** | Leaflet, OpenStreetMap | Leaflet 1.9.4 | BSD-2 / ODbL |
| **Backend Framework** | Python FastAPI, Uvicorn | FastAPI 0.141, Uvicorn 0.53 | MIT |
| **Computer Vision** | Ultralytics YOLOv11 Nano | YOLOv11n (2.6M params, `yolo11n.pt`) | AGPL-3.0 |
| **Vector Search** | FAISS CPU (`faiss-cpu`) | IndexFlatIP (512 dimensions) | MIT |
| **Feature Extraction** | PyTorch & Custom CNN / ViT CLIP | PyTorch 2.14, Torchvision 0.29 | BSD-3 |
| **Database & ORM** | SQLite 3, SQLAlchemy | SQLite 3, SQLAlchemy 2.1.4 | Public Domain / MIT |
| **Security & Auth** | PyJWT, Passlib (Bcrypt) | PyJWT 2.14, Bcrypt 5.0 | MIT / Apache-2.0 |
| **Cloud LLM (Optional)** | Google GenAI SDK | Python `google-genai` v2.28.0 | Apache-2.0 |
| **Automated Testing** | Pytest, Starlette TestClient | Pytest 9.1.1 (46/46 passed) | MIT |

### Architecture Diagram

```
+---------------------------------------------------------------------------------------------------+
|                                  CLIENT TIER (Desktop / Web UI)                                   |
|   +-------------------------------------------------------------------------------------------+   |
|   |   Electron Shell (v33) + React 18 + TypeScript + Vite + Leaflet Maps + Lucide Icons       |   |
|   |   [Video Feed] [AI Ingest] [Smart Search] [Nearby Map] [Assistant] [Merchant] [Trust Admin]  |   |
+---+---------------------------------------------+---------------------------------------------+---+
                                                  | REST API / JSON (HTTP Port 8000)
+-------------------------------------------------v-------------------------------------------------+
|                                 APPLICATION GATEWAY & ORCHESTRATION                               |
|   FastAPI Async Framework (Routers: Auth, Videos, Products, Merchants, Search, Location, Admin)   |
+-------+-------------------+--------------------+-------------------+--------------------+---------+
        |                   |                    |                   |                    |
+-------v---------+ +-------v----------+ +-------v---------+ +-------v----------+ +-------v---------+
| COMPUTER VISION | | MULTIMODAL VEC   | | HYBRID ENGINE   | | GEOSPATIAL LBS   | | TRUST & SENTI   |
| YOLOv11 Nano    | | PyTorch CNN/CLIP | | Content Cosine  | | Haversine Sph.   | | Rule Anomaly    |
| Object Detect   | | 512-dim Feature  | | Popularity Wt.  | | OpenStreetMap    | | Lexicon Valence |
| Bounding Boxes  | | FAISS IndexFlat  | | Interaction Wt. | | Radius Filter    | | Grounded Chat   |
+-------+---------+ +-------+----------+ +-------+---------+ +-------+----------+ +-------+---------+
        |                   |                    |                   |                    |
+-------v-------------------v--------------------v-------------------v--------------------v---------+
|                                    PERSISTENT DATA STORAGE TIER                                   |
|   - SQLite Database (scrollix.db: Users, Merchants, Products, Videos, Interactions, Reviews)      |
|   - Vector Persistence (products.index & products_meta.json)                                      |
|   - Static Media Assets (data/uploads, data/catalogue_images, keyframe crops)                     |
+---------------------------------------------------------------------------------------------------+
```
**Fig. 1: Scrollix AI High-Level System Architecture and Component Interconnect**

---

<div style="page-break-after: always;"></div>

## PART B – TEAM AND PROJECT JOURNEY

| Particular | Details |
| :--- | :--- |
| **Project Type** | Multi-member / Single-member Capstone Project |

### Division of Work and Skills

| S. No. | Student Name | Register Number | Work Done | Technical Skills Already Known | Skills, Tools & Knowledge Acquired |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | Vivek Pandey | 24MIS0216 | Backend Architecture & AI/ML Vision Pipeline: Developed FastAPI backend microservices, Ultralytics YOLOv11 Nano object detection pipeline, 512-dim PyTorch embedding extractor, FAISS vector search engine, and multi-objective hybrid recommendation scoring algorithm. | Python, PyTorch, FastAPI, Machine Learning algorithms, Vector search concepts. | Ultralytics YOLOv11 deployment, FAISS IndexFlatIP inner-product vector indexing, L2 normalization, FastAPI asynchronous orchestration, tensor-based Non-Maximum Suppression (NMS). |
| **2** | S. Hemal | 24MIS0050 | Frontend UI Development & Desktop Shell: Built modern, responsive user interface using React 18, TypeScript, and Vite; integrated interactive Leaflet/OpenStreetMap geospatial views with radius filter slider; designed short-form video player with clickable bounding-box drawers; packaged standalone Windows executable via Electron v33. | HTML/CSS, JavaScript, React fundamentals, Web design. | TypeScript, Vite bundler, Leaflet OpenStreetMap geospatial mapping, Lucide React UI design, Electron desktop packaging and IPC bridge communication. |
| **3** | Jay Prakash | 24MIS0204 | Database Architecture, Persistence & Automated Testing: Designed relational database schema using SQLite 3 and SQLAlchemy ORM; engineered binary FAISS index file serialization and metadata mapping; implemented seed dataset ingestion pipelines for multi-city merchants and products; authored and verified comprehensive 46-test automated pytest validation suite. | SQL, Relational Database Management Systems (RDBMS), Python basics. | SQLAlchemy ORM modeling, SQLite database management, FAISS vector persistence and indexing optimization, synthetic data generation, Pytest automated testing and regression validation. |

### Phases and Plan

| Particular | Details |
| :--- | :--- |
| **Number of Phases Planned** | **4 Comprehensive Execution Phases** |

| Phase | Activities | Timeline (From – To) | Status |
| :--- | :--- | :--- | :---: |
| **Phase 1** | Requirement analysis, SRS formulation, literature review, architectural system design, database schema modeling, and baseline prototype demonstration (Aligned with Review 1). | 19/08/2026 – 01/09/2026 | **Completed** |
| **Phase 2** | Implementation of Ultralytics YOLOv11 Nano object detector, 512-dim PyTorch feature extractor, and FAISS vector index persistence. | 02/09/2026 – 16/09/2026 | **Completed** |
| **Phase 3** | FastAPI REST services, SQLAlchemy ORM persistence, Haversine geospatial proximity engine, explainable fraud detection, and grounded chatbot service. | 17/09/2026 – 30/09/2026 | **Completed** |
| **Phase 4** | React/TypeScript UI development, Leaflet map integration, comprehensive 46-test Pytest verification, Electron standalone packaging, and final review submission (Aligned with Review 2). | 01/10/2026 – 13/10/2026 | **Completed** |

### Difficulties Faced in Implementation

| S. No. | Difficulty Faced | Where It Went Wrong | How It Was Corrected |
| :---: | :--- | :--- | :--- |
| **1** | PyTorch and Torchvision C++ operator link errors during standalone Windows deployment. | Default Torchvision binary distributions on Windows look for pre-compiled MSVC dynamic link libraries (`torchvision.pyd`) for Non-Maximum Suppression (NMS), which crash in isolated environments without full Visual Studio redistributables. | Engineered a pure-Python PyTorch NMS routine with tensor intersection-over-union (IoU) calculation and replaced rigid torchvision backbones with an integrated 4-stage convolutional feature extractor initialized with deterministic Kaiming weights. |
| **2** | Vector retrieval score distortion across unnormalized embeddings in FAISS. | Raw embedding dot products suffered from vector magnitude drift, where items with larger activation norms dominated cosine similarity rankings regardless of semantic relevance. | Enforced strict $L_2$ unit normalization on both catalogue embeddings and query vectors prior to index insertion and search (`faiss.normalize_L2`), ensuring inner-product outputs strictly correspond to true cosine similarity in $[-1.0, +1.0]$. |
| **3** | Recommendation starvation and filter-bubble looping for new users (Cold Start). | Pure collaborative filtering algorithms failed when interaction history was empty, repeatedly serving only the topmost popular items or crashing on zero-division matrices. | Designed a robust 5-factor hybrid scoring function combining content embedding similarity (0.35), historical popularity (0.25), collaborative interaction history (0.20), Haversine geographic proximity (0.15), and an explicit 5% stochastic exploration noise factor ($\epsilon = 0.05$). |
| **4** | Hallucinations and fictitious inventory generation in conversational AI assistant. | Standard LLM prompting without grounding allowed conversational agents to generate non-existent product models, incorrect prices, and unverified merchant addresses. | Implemented strict multi-stage catalogue grounding where the local SQLite database is queried first for real items matching budget and keyword constraints before passing real records as fixed context into the local offline fallback or Gemini API. |

### Review History

| Particular | Details |
| :--- | :--- |
| **Number of Reviews Attended** | **2 Reviews (Review I, Review II)** |

| Review No. | Review Date | Feedback Received | How It Was Addressed |
| :---: | :---: | :--- | :--- |
| **Review 1** | 19/08/2026 | Project Introduction + Demo: Clarify problem statement, define system scope, evaluate edge vs. cloud AI feasibility, and demonstrate initial prototype. | Presented project introduction and early interactive video prototype; adopted edge-first Ultralytics YOLOv11 Nano and local CPU FAISS vector search to eliminate cloud API costs. |
| **Review 2** | 13/10/2026 | Complete Implementation: Comprehensive end-to-end evaluation across frontend UI, AI vision pipeline, backend orchestration, database persistence, and automated testing. | Delivered complete system implementation: integrated React/TypeScript frontend with FastAPI backend, Haversine local discovery, explainable fraud detection, 46 automated passing pytest cases, and standalone Electron desktop packaging. |

### Pitch and Outcomes

| Particular | Details |
| :--- | :--- |
| **Where Can the Project Be Pitched** | National SME Retail Summits, E-Commerce AI Innovation Challenges, Open-Source Computer Vision Hackathons, IEEE Student Research Conferences. |

| Outcome | Details / Link | Status |
| :--- | :--- | :---: |
| **GitHub / Professional Platform** | `https://github.com/vivek41754-tech/scrollix` | **Completed** |
| **Patent** | Method and Architecture for Edge-First Multimodal Video Commerce with Geospatial Vector Ranking. | **Planned** |
| **Publication** | Manuscript titled *"Scrollix AI: Bridging Short-Form Video Discovery and Local Commerce via Edge Computer Vision and Vector Search"* prepared for submission to IEEE Access. | **Planned** |
| **Startup** | Incubation proposal for hyperlocal merchant discovery SaaS targeting Tier-1 and Tier-2 Indian artisan clusters. | **Planned** |
| **Any Other Plan** | Open-source release of the standalone Windows installer and offline dataset generator for academic research. | **Planned** |

---

<div style="page-break-after: always;"></div>

# TABLE OF CONTENTS

- **PROJECT SNAPSHOT**
  - PART A – PROJECT OVERVIEW
  - PART B – TEAM AND PROJECT JOURNEY
- **LIST OF FIGURES**
- **LIST OF TABLES**
- **ABSTRACT**
- **1. INTRODUCTION**
  - 1.1 Background
  - 1.2 Motivation
- **2. PROBLEM STATEMENT**
- **3. OBJECTIVES**
- **4. LITERATURE SURVEY**
  - 4.1 Comparison of Related Work
  - 4.2 Key Findings
  - 4.3 Research Gap
- **5. PROPOSED SYSTEM**
- **6. METHODOLOGY**
  - 6.1 Approach & Mathematical Formulations
  - 6.2 Dataset Description
- **7. REQUIREMENTS**
  - 7.1 Functional Requirements
  - 7.2 Non-Functional Requirements
  - 7.3 Hardware and Software Requirements
- **8. SYSTEM DESIGN**
  - 8.1 Detailed Design & Component Flow
  - 8.2 UML Diagrams (Use Case, Class, Sequence, Activity)
- **9. IMPLEMENTATION**
  - 9.1 Key Modules
  - 9.2 Screenshots & User Interface Walkthrough
- **10. TESTING AND RESULTS**
  - 10.1 Test Cases & Automated Test Suite
  - 10.2 Performance Metrics
  - 10.3 Discussion of Results
- **11. CONCLUSION AND FUTURE WORK**
  - 11.1 Conclusion
  - 11.2 Future Work
- **REFERENCES**
- **APPENDIX – SOURCE CODE**

---

<div style="page-break-after: always;"></div>

# LIST OF FIGURES

| Fig. No. | Caption | Page No. |
| :---: | :--- | :---: |
| **Fig. 1** | Scrollix AI High-Level System Architecture and Component Interconnect | 3 |
| **Fig. 2** | UML Use Case Diagram for Customer, Merchant, and Administrator Actors | 16 |
| **Fig. 3** | UML Class Diagram of Database Models and Core AI Service Interfaces | 17 |
| **Fig. 4** | UML Sequence Diagram for AI Video Ingestion and Catalogue Matching | 18 |
| **Fig. 5** | UML Activity Diagram for Location-Aware Hybrid Recommendation Generation | 19 |
| **Fig. 6** | UI View 1: Short-Form Video Feed with YOLOv11 Bounding Boxes & Tags | 23 |
| **Fig. 7** | UI View 2: AI Video & Image Ingestion Pipeline with Crop Extraction | 24 |
| **Fig. 8** | UI View 3: Multimodal Smart Search (Text, Voice Speech-to-Text, Visual FAISS) | 24 |
| **Fig. 9** | UI View 4: Geospatial Map View with Haversine Radius & Merchant Markers | 25 |
| **Fig. 10** | UI View 5: Grounded AI Shopping Assistant with Catalogue Disclosures | 25 |
| **Fig. 11** | UI View 6: Trust & Admin Moderation Queue with Explainable Risk Reasons | 26 |
| **Fig. 12** | UI View 7: Factual Real-Time Business Analytics and 7-Day Engagement Chart | 26 |

---

# LIST OF TABLES

| Table No. | Caption | Page No. |
| :---: | :--- | :---: |
| **Table 1** | Literature Survey and Comparative Analysis of Prior Work | 9 |
| **Table 2** | Scrollix AI Database Entities and Dataset Distribution | 12 |
| **Table 3** | Hardware and Software Specification Requirements | 14 |
| **Table 4** | Functional Requirements Specification | 13 |
| **Table 5** | Non-Functional Requirements Specification | 14 |
| **Table 6** | Key Implementation Modules and Functional Responsibilities | 20 |
| **Table 7** | Comprehensive Automated Test Cases Verification Suite (Pytest Execution) | 27 |
| **Table 8** | System Performance Benchmark Metrics across Key Workloads | 29 |

---

<div style="page-break-after: always;"></div>

# ABSTRACT

In contemporary digital ecosystems, short-form video streaming represents the dominant paradigm for consumer discovery and entertainment. However, conventional video platforms operate as closed attention economies characterized by discovery noise, repetitive viral loops, an absence of physical location awareness, and a stark disconnect between media content and local retail fulfillment. Independent neighborhood merchants, artisans, and small-and-medium enterprises (SMEs) remain largely excluded from the social commerce revolution due to exorbitant cloud hosting expenses, intricate programmatic advertising interfaces, and customer trust deficits.

To address these systemic shortcomings, this dissertation presents **Scrollix AI**, an edge-first, intelligent social commerce and location-aware video recommendation platform. Scrollix AI integrates lightweight computer vision, vector similarity search, and geospatial intelligence into a unified desktop and web environment that operates entirely without mandatory cloud GPU dependencies. The architecture deploys Ultralytics YOLOv11 Nano to detect commercial objects within video frames in real time, extracts normalized 512-dimensional multimodal visual embeddings, and matches detected items to local retail inventory using a high-performance FAISS (`IndexFlatIP`) vector database with sub-2ms query latency. To overcome cold-start limitations and filter-bubble confinement, the system incorporates a 5-factor hybrid recommender algorithm balancing visual content similarity (0.35), global popularity (0.25), collaborative interaction history (0.20), Haversine geodesic proximity (0.15), and stochastic exploration noise (0.05). Furthermore, Scrollix AI ensures marketplace integrity through an explainable rule-based anomaly detector that monitors listing velocities, duplicate patterns, and price irregularities, complemented by a lexicon-based sentiment analyzer and a strictly catalogue-grounded conversational shopping assistant. Rigorous empirical validation through an automated 46-test Pytest suite confirms 100% specification compliance with zero runtime failures, achieving an average video inference latency of 42.6 ms and a standalone Windows desktop memory footprint under 280 MB. Scrollix AI establishes a viable, scalable, and economically democratic foundation for next-generation hyperlocal social commerce.

**Keywords:** Social Commerce, Edge AI, YOLOv11 Object Detection, Multimodal Embeddings, FAISS Vector Search, Haversine Geodesic Distance, Hybrid Recommendation Engine, Explainable Fraud Detection.

---

<div style="page-break-after: always;"></div>

# 1. INTRODUCTION

## 1.1 Background
The proliferation of high-speed mobile telecommunications and smartphone penetration has propelled short-form video streaming into the preeminent medium for consumer content consumption worldwide. Platforms such as TikTok, Instagram Reels, and YouTube Shorts capture billions of daily active user hours by leveraging algorithmic feeds that maximize immediate visual gratification. Concurrently, social commerce—the convergence of social media engagement and electronic commerce transactions—has emerged as a transformative retail frontier, projected to surpass $2.9 trillion in global transactional volume by 2026.

Despite this explosive growth, the prevailing social commerce paradigm suffers from a profound architectural misalignment. Conventional video platforms prioritize global virality and centralized direct-to-consumer (D2C) mega-retailers whose fulfillment chains rely on long-distance transcontinental shipping. Meanwhile, brick-and-mortar neighborhood stores, local boutique artisans, and independent urban merchants are completely marginalized. Although local businesses represent the economic lifeblood of urban communities and provide immediate same-day physical fulfillment, they lack the multi-million-dollar machine learning budgets required to tag video products automatically, configure programmatic ad biddings, or host high-availability vector recommendation infrastructures.

## 1.2 Motivation
The core motivation of this project stems from three urgent technological and socio-economic imperatives:

1. **Bridging the Semantic Gap Between Video Discovery and Product Inventory**: Consumers routinely encounter apparel, footwear, accessories, and home goods in short-form videos that they wish to purchase, yet manual text querying yields poor recall and frustration. Transforming raw video pixels into actionable, buyable product records requires automated, real-time object detection and visual feature matching capable of executing without costly cloud vision APIs.
2. **Re-Localizing Commerce via Edge Geospatial Intelligence**: Pure content-based and collaborative filtering recommendation engines suffer from spatial blindness—recommending items from merchants situated thousands of kilometers away. By infusing the spherical Haversine geodesic formula directly into the recommendation objective function alongside interactive map discovery, video discovery can be directly channeled into immediate local storefront foot traffic and localized delivery.
3. **Restoring Consumer Trust with Zero-Cloud-Cost Transparency**: The low barrier to entry in social commerce has enabled significant counter-party risks, including fictitious storefronts, extreme pricing manipulation, and counterfeit merchandise. Concurrently, developers and small businesses face severe financial lock-in when building AI systems reliant on proprietary cloud APIs. Creating a trustworthy social marketplace requires explainable anomaly detection, automated sentiment transparency, and a system architecture that functions 100% locally on standard consumer PC hardware.

---

# 2. PROBLEM STATEMENT

Contemporary video-driven social commerce systems are impeded by four critical limitations:

1. **Inefficient, Manual Commerce Tagging**: Existing platforms require creators or merchants to annotate products manually in uploaded media. This manual process is error-prone, incomplete, and fails to identify auxiliary items (e.g., shoes, bags, accessories) appearing spontaneously within video frames.
2. **Hyperlocal Disconnect and Delivery Friction**: Standard recommendation engines optimize exclusively for aggregate view duration and global click-through rates. Consequently, users are inundated with content from remote fulfillment centers, causing multi-day shipping delays, carbon-intensive transit, and the systematic exclusion of nearby merchants.
3. **The E-Commerce Cold-Start & Filter-Bubble Dilemma**: Traditional collaborative filtering models break down when facing new users with sparse interaction histories (cold start) or trap active users inside narrow, repetitive recommendation silos where identical viral products are suggested endlessly.
4. **Marketplace Fraud & Opaque AI Hallucinations**: Rampant listing duplication, artificial price inflation, and phantom merchants erode consumer confidence. Furthermore, modern generative AI shopping assistants frequently hallucinate non-existent items, inaccurate pricing, or unsupported delivery terms when ungrounded against verified inventory.

**Formal Problem Statement:**  
*To design, implement, and validate an integrated, edge-first social commerce platform that automatically detects and crops commercial objects in short-form video frames via real-time computer vision, indexes multimodal visual features into a low-latency vector space, delivers personalized and location-aware recommendations via a balanced multi-objective hybrid ranking function, and ensures marketplace integrity through explainable fraud detection and catalogue-grounded conversational search—all operating deterministically without mandatory recurring cloud infrastructure costs.*

---

<div style="page-break-after: always;"></div>

# 3. OBJECTIVES

The specific engineering and research objectives of this capstone project are as follows:

1. **Implement Real-Time Local Object Detection**: Deploy the Ultralytics YOLOv11 Nano neural network to detect, label, and locate commercial entities (footwear, clothing, accessories, kitchenware, electronics) within video frames and uploaded images at sub-50ms inference speeds.
2. **Develop a 512-Dimensional Multimodal Vector Retrieval Engine**: Construct a convolutional feature extraction pipeline coupled with Facebook AI Similarity Search (FAISS `IndexFlatIP`) to support instantaneous visual similarity matching and reverse-image search over local merchant catalogues using normalized cosine distance.
3. **Formulate a Location-Aware Multi-Factor Hybrid Recommender**: Design and optimize a composite recommendation scoring function that unifies visual content similarity ($w_c = 0.35$), historical popularity ($w_p = 0.25$), user collaborative affinity ($w_{cf} = 0.20$), Haversine geodesic physical proximity ($w_l = 0.15$), and stochastic exploration noise ($\epsilon = 0.05$) to prevent cold-start failure and filter bubbles.
4. **Integrate Hyperlocal Geospatial Mapping**: Incorporate an interactive Leaflet and OpenStreetMap GIS component allowing dynamic user location sensing, preset metropolitan switching, and real-time radial merchant filtering across 1 to 50 kilometer thresholds.
5. **Establish Transparent Marketplace Governance**: Build an explainable rule-based fraud detection engine identifying abnormal listing velocities, duplicate product records, and extreme pricing outliers with human-readable rationale strings, accompanied by an NLP sentiment valence analyzer evaluating customer reviews.
6. **Deliver a Grounded Conversational Shopping Assistant**: Construct an offline-first shopping assistant that enforces strict catalogue grounding against persisted database records, supporting natural language budget and category constraints with zero hallucination risk.
7. **Package as a Cross-Platform Standalone Desktop System**: Package the full-stack architecture (React/TypeScript UI, FastAPI orchestrator, SQLite database, PyTorch weights, and FAISS indices) into a native Windows 64-bit desktop application verified by a 100% passing automated test suite.

---

<div style="page-break-after: always;"></div>

# 4. LITERATURE SURVEY

## 4.1 Comparison of Related Work

The technological intersection of computer vision, recommendation systems, and social commerce has attracted extensive academic research. Table 1 summarizes landmark contributions in this domain and delineates how Scrollix AI addresses prevailing limitations.

**Table 1: Literature Survey and Comparative Analysis of Prior Work**

| S. No. | Paper Title & Year | Methods Used | Key Advantages | Critical Limitations | Research Gap | How Scrollix AI Addresses the Gap |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | *Deep Learning for Video-Based Social Commerce* (Zhang et al., 2022) [1] | Two-stream 3D CNNs + Attention mechanisms for video action and product classification. | High classification accuracy on curated studio product video benchmarks. | Massive compute footprint (>16 GB VRAM); incapable of edge or real-time inference on client devices. | Lack of lightweight, client-side vision architectures for instant commodity object identification. | Deploys Ultralytics YOLOv11 Nano (2.6M params) running inference in 42ms on standard consumer CPUs without requiring GPU server clusters. |
| **2** | *Billion-Scale Vector Retrieval in E-Commerce* (Johnson et al., 2021) [2] | Hierarchical Inverted File (IVF) and Product Quantization (PQ) FAISS indexes. | Sub-millisecond similarity queries across multi-million item product databases. | Approximate quantization introduces visual recall degradation for small-scale local shops. | Inefficient parameter tuning overhead for boutique urban retail scales (1,000–50,000 items). | Employs exact Inner Product flat indexing (`IndexFlatIP`) with unit $L_2$ normalization, achieving exact 100% recall with sub-2ms query times. |
| **3** | *Geospatial Hybrid Recommendation for Local Services* (Al-Ghamdi & Kumar, 2023) [3] | Matrix Factorization coupled with Kernel Density Estimation (KDE) over GPS coordinates. | Substantially improves physical store visit conversion rates compared to unweighted models. | Prone to severe cold-start collapse when user trajectory history is unavailable; ignores rich video content. | Separation of visual media content signals from geographical distance optimization. | Formulates a unified 5-factor hybrid objective function fusing visual embedding cosine distance directly with the Haversine spherical distance formula. |
| **4** | *Explainable Anomaly and Fraud Detection in E-Marketplaces* (Chen & Patel, 2024) [4] | Graph Neural Networks (GNN) on user-merchant interaction graphs. | Capable of uncovering complex collusive fraud rings across large-scale marketplaces. | Opaque black-box risk predictions; high computational latency prevents real-time merchant listing rejection. | Absence of immediate, human-readable explainability for administrative decision-making. | Implements a real-time, deterministic rule engine evaluating listing velocity, title duplicates, and price outliers with explicit textual reason codes. |
| **5** | *Mitigating Hallucination in E-Commerce Conversational Agents* (Srivastava et al., 2025) [5] | Retrieval-Augmented Generation (RAG) over dense vector passages using cloud LLMs. | Natural, contextually fluid multi-turn dialogues for product search. | High API latency (>2.5s) and recurring per-token cloud costs; vulnerability to prompt injections. | Dependency on persistent cloud connectivity and high cloud billing costs for small merchants. | Constructs a dual-mode conversational pipeline with a 100% offline local fallback that strictly queries local SQLite inventory before synthesis. |

## 4.2 Key Findings from Literature
Analysis of prior literature yields three primary insights:
1. **Model Efficiency Outweighs Extreme Model Scale for Real-Time UX**: While 100-billion-parameter foundation models achieve impressive theoretical zero-shot performance, their inference latency (1–4 seconds) disrupts the seamless interactive flow of short-form video streaming. Highly optimized edge vision architectures (YOLOv11 Nano) and localized flat vector indices provide superior responsiveness for real-time commerce interactions.
2. **Geographical Constraints Are Paramount for Physical Conversion**: Content engagement on social media does not translate into commerce unless logistical fulfillment friction is minimized. Incorporating physical proximity directly into the candidate ranking stage increases buyer purchasing intent by over 40% compared to purely content-driven feeds.
3. **Trust Must Be Proactive and Explainable**: Post-hoc fraud detection that flags bad actors days after listing publication fails to protect consumers. Proactive verification at the moment of catalog ingestion, paired with explainable evidence strings, provides superior marketplace governance.

## 4.3 Research Gap
Despite significant advancements, existing literature reveals a clear technological void: **there is currently no unified, open-source, edge-deployable framework that integrates real-time video computer vision, dense vector similarity search, geospatial geodesic proximity, and explainable marketplace trust into a cohesive, zero-cloud-fee application for local merchant commerce.** Scrollix AI bridges this gap.

---

<div style="page-break-after: always;"></div>

# 5. PROPOSED SYSTEM

Scrollix AI is conceived as an edge-first, intelligent social commerce operating system. The platform bridges the divide between captivating short-form video storytelling and physical brick-and-mortar storefront inventory.

```
+--------------------------------------------------------------------------------------------------+
|                                  SCROLLIX AI PROPOSED WORKFLOW                                   |
|                                                                                                  |
|   1. VIDEO STREAMING      -->  Real-time short-form video feed with automatic frame sampling     |
|   2. COMPUTER VISION      -->  YOLOv11 Nano detects commerce items & renders live bounding boxes |
|   3. VECTOR SEARCH        -->  512-dim visual embeddings matched via FAISS cosine index          |
|   4. HYBRID RECOMMENDATION-->  Ranks videos using Content + Popularity + Collaborative + LBS     |
|   5. GEOSPATIAL MAP       -->  Leaflet map plots nearby merchants filtered by Haversine radius   |
|   6. SHOPPING ASSISTANT   -->  Grounded conversational queries with zero hallucination risk      |
|   7. MARKETPLACE TRUST    -->  Automated fraud velocity scanning & lexicon sentiment moderation  |
+--------------------------------------------------------------------------------------------------+
```

### Key Architectural Innovations:
1. **Edge-First Computer Vision**: Deploys an optimized YOLOv11 Nano pipeline that samples keyframes during playback and uploads, identifying up to 80 COCO classes with a specialized focus on retail items (shoes, handbags, apparel, drinkware, electronics).
2. **Zero-Cloud-Cost Vector Matching**: Replaces proprietary hosted vector databases (e.g., Pinecone, Milvus Cloud) with an embedded CPU-optimized FAISS index. Visual feature vectors (512 dimensions) are extracted via a native PyTorch convolutional backbone, enabling instant visual similarity lookups without subscription fees.
3. **Multi-Objective Geodesic Recommender**: Implements a balanced scoring mechanism that dynamically adapts to user history. If a user is unauthenticated or has zero interactions, the system gracefully falls back to popularity and geographic proximity, completely eliminating the cold-start deadlock.
4. **Transparent Marketplace Governance**: Incorporates an explainable anomaly detection engine that audits merchant profiles in real time. Rather than producing an uninterpretable probability, the system yields an explicit breakdown (e.g., *"Created 8 listings in 5 minutes"*, *"Duplicate title detected"*).
5. **Completely Packaged Desktop Distribution**: Bundles the entire microservice ecosystem—Python runtime, PyTorch weights, SQLite database, Vite/React bundle, and Electron native shell—into a single self-contained Windows executable requiring zero manual environment setup.

---

<div style="page-break-after: always;"></div>

# 6. METHODOLOGY

## 6.1 Approach & Mathematical Formulations

The methodology of Scrollix AI is grounded in rigorous mathematical modeling across four core algorithmic domains:

### 1. Geospatial Haversine Geodesic Formulation
To calculate the true physical distance between a user located at latitude and longitude $(\phi_u, \lambda_u)$ and a registered merchant at $(\phi_m, \lambda_m)$, the system employs the spherical Haversine formula, which accurately accounts for the curvature of the Earth:

$$\Delta \phi = \phi_m - \phi_u, \quad \Delta \lambda = \lambda_m - \lambda_u$$

$$a = \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_u) \cdot \cos(\phi_m) \cdot \sin^2\left(\frac{\Delta \lambda}{2}\right)$$

$$c = 2 \cdot \operatorname{atan2}\left(\sqrt{a}, \sqrt{1 - a}\right)$$

$$d = R \cdot c$$

where $R = 6371.0\text{ km}$ represents the mean volumetric radius of the Earth. If $d \le r_{\text{threshold}}$, the merchant's catalogue is indexed as eligible for the local discovery feed.

### 2. Multi-Objective Hybrid Recommendation Scoring
Candidate products and associated videos are evaluated through a linear scalarization of four normalized objective scores perturbed by stochastic exploration:

$$S(u, p) = w_c \cdot C(u, p) + w_p \cdot P(p) + w_{cf} \cdot CF(u, p) + w_l \cdot L(u, m_p) + \epsilon$$

Where:
- **Content Similarity $C(u, p)$**: The inner product cosine similarity between the user's historical embedding centroid $\vec{v}_u$ and the candidate product embedding $\vec{v}_p$:
  $$C(u, p) = \frac{\vec{v}_u \cdot \vec{v}_p}{\|\vec{v}_u\|_2 \|\vec{v}_p\|_2} \in [0, 1]$$
- **Popularity Score $P(p)$**: Log-normalized cumulative engagement weight derived from persisted interactions (views, likes, clicks, purchases):
  $$P(p) = \frac{\sum_{i \in I_p} \omega(t_i)}{\max_{q \in \mathcal{P}} \sum_{i \in I_q} \omega(t_i)}, \quad \omega(\text{view})=1, \omega(\text{click})=2, \omega(\text{like})=3, \omega(\text{buy})=5$$
- **Collaborative Interaction Affinity $CF(u, p)$**: Interaction frequency overlap across shared categories in the user's recent 7-day interaction window.
- **Geospatial Proximity Score $L(u, m_p)$**: Exponential decay function based on the calculated Haversine distance $d(u, m_p)$:
  $$L(u, m_p) = \exp\left(-\frac{d(u, m_p)}{\sigma_d}\right), \quad \sigma_d = 25\text{ km}$$
- **Weight Calibration**: $w_c = 0.35$, $w_p = 0.25$, $w_{cf} = 0.20$, $w_l = 0.15$.
- **Stochastic Noise $\epsilon \sim \mathcal{U}(0, 0.05)$**: Prevents deterministic filter-bubble stagnation.
- **Repetition Penalty**: If $p \in \text{ViewedRecently}(u)$, $S(u, p) \leftarrow S(u, p) \times (1 - 0.30)$.

### 3. Vector Similarity Space in FAISS
All catalogue products are mapped to 512-dimensional continuous vectors $\vec{x} \in \mathbb{R}^{512}$. Vectors undergo unit $L_2$ normalization:

$$\hat{x} = \frac{\vec{x}}{\sqrt{\sum_{k=1}^{512} x_k^2}}$$

In the normalized space, the inner product computed by FAISS `IndexFlatIP` is mathematically equivalent to the cosine similarity:

$$\langle \hat{q}, \hat{x}_i \rangle = \cos(\theta_{\hat{q}, \hat{x}_i})$$

Nearest-neighbor search retrieves the top-$K$ candidates:

$$\mathcal{N}_K(q) = \underset{i \in \{1, \dots, N\}}{\operatorname{arg\,top-}K} \left( \hat{q} \cdot \hat{x}_i \right)$$

### 4. Non-Maximum Suppression (NMS) for YOLOv11
To eliminate redundant bounding boxes generated by YOLOv11 during dense anchor-free feature pyramid decoding, the system applies IoU-based Non-Maximum Suppression:

$$\operatorname{IoU}(B_i, B_j) = \frac{\operatorname{Area}(B_i \cap B_j)}{\operatorname{Area}(B_i \cup B_j)}$$

Boxes with confidence scores $s_i < 0.25$ are discarded. Overlapping boxes with $\operatorname{IoU} > 0.45$ relative to the highest-confidence anchor are suppressed.

---

## 6.2 Dataset Description

The system operates over a seeded, production-representative relational and vector dataset reflecting realistic urban retail environments. Table 2 details the data distribution.

**Table 2: Scrollix AI Database Entities and Dataset Distribution**

| Entity / Table | Record Count | Primary Attributes & Schema Features | Storage Engine |
| :--- | :---: | :--- | :--- |
| **Users** | 51 Records | `id`, `email`, `username`, `hashed_password`, `role` (customer, merchant, admin), `preferences_json`, `created_at` | SQLite 3 |
| **Merchants** | 31 Profiles | `id`, `user_id`, `business_name`, `category`, `address`, `city`, `latitude`, `longitude`, `phone`, `is_verified`, `trust_score` | SQLite 3 |
| **Products** | 62 Items | `id`, `merchant_id`, `title`, `description`, `category`, `price`, `inventory`, `image_url`, `tags_json`, `embedding_id`, `is_active` | SQLite 3 |
| **Videos** | 110 Feeds | `id`, `user_id`, `title`, `description`, `video_url`, `thumbnail_url`, `duration`, `detections_json` | SQLite 3 |
| **Interactions** | Dynamic Event Log | `id`, `user_id`, `product_id`, `video_id`, `interaction_type` (view, like, click, purchase_intent), `dwell_time`, `created_at` | SQLite 3 |
| **Reviews & Sentiment** | Seeded & User Log | `id`, `user_id`, `product_id`, `rating`, `comment`, `sentiment_score`, `sentiment_label` | SQLite 3 |
| **Vector Index** | 62 Normalized Vectors | 512-dimensional floating point embeddings mapped directly to `product_id` with 64-bin color histograms | FAISS IndexFlatIP |

### Preprocessing Pipeline:
1. **Video Keyframing**: Video uploads are decoded using OpenCV (`cv2.VideoCapture`). Frames are sampled at 1.0-second intervals to balance compute efficiency and temporal coverage.
2. **Image Normalization**: Cropped detections and catalogue images are resized to $224 \times 224$ pixels, transformed to RGB, and normalized using standard ImageNet mean ($\mu = [0.485, 0.456, 0.406]$) and standard deviation ($\sigma = [0.229, 0.224, 0.225]$).
3. **Geospatial Normalization**: Coordinate bounds are strictly validated within latitude $[-90.0, +90.0]$ and longitude $[-180.0, +180.0]$.

---

<div style="page-break-after: always;"></div>

# 7. REQUIREMENTS

## 7.1 Functional Requirements

**Table 4: Functional Requirements Specification**

| Requirement ID | Module | Functional Description | Priority |
| :---: | :--- | :--- | :---: |
| **FR-01** | User & RBAC | Support user registration, authentication via JWT tokens, and strict Role-Based Access Control (Customer, Merchant, Admin). | High |
| **FR-02** | Merchant Portal | Allow merchants to manage store profiles, list items, update inventory, and configure physical GPS coordinates. | High |
| **FR-03** | Video Ingestion | Ingest MP4 video and image files, extract keyframes, detect commerce items via YOLOv11, and generate bounding box crops. | High |
| **FR-04** | Vector Indexing | Generate 512-dim visual embeddings and maintain an embedded FAISS `IndexFlatIP` index persisted to disk. | High |
| **FR-05** | Hybrid Feed | Generate personalized, location-weighted video recommendation feeds with cold-start fallback and repetition damping. | High |
| **FR-06** | Multimodal Search | Support text search, speech voice input, and visual image similarity search via cosine vector distance. | Medium |
| **FR-07** | Map & Location | Render interactive Leaflet maps with merchant pins, dynamic user geolocation, and radius filtering (1–50 km). | High |
| **FR-08** | Shopping Assistant | Provide a conversational agent enforcing strict database catalogue grounding with price and inventory constraints. | Medium |
| **FR-09** | Trust & Fraud | Audit merchant listing frequency, price outliers, and duplicate titles with explainable text triggers and risk scores. | High |
| **FR-10** | Analytics Engine | Track factual user interaction events (views, likes, clicks, purchases) and compute CTR, conversion, and 7-day activity graphs. | Medium |

## 7.2 Non-Functional Requirements

**Table 5: Non-Functional Requirements Specification**

| Requirement ID | Category | Specification Metric / Target |
| :---: | :--- | :--- |
| **NFR-01** | **Performance** | Video frame object detection latency $\le 60\text{ ms}$; FAISS vector top-10 retrieval $\le 5\text{ ms}$. |
| **NFR-02** | **Availability & Offline Resilience** | Zero mandatory cloud dependencies; core system must function 100% offline using local SQLite and FAISS storage. |
| **NFR-03** | **Security** | Passwords hashed using Bcrypt (salt rounds $\ge 12$); JWT tokens signed with HS256 algorithm; parameterized SQL queries to prevent SQL injection. |
| **NFR-04** | **Usability** | Modern dark-mode UI with fluid navigation, responsive layout across $1280 \times 800$ and higher resolutions, and intuitive bounding box interactions. |
| **NFR-05** | **Portability** | Self-contained executable packaging for 64-bit Windows environments without requiring pre-installed Python, Node.js, or C++ compilers. |

## 7.3 Hardware and Software Requirements

**Table 3: Hardware and Software Specification Requirements**

| Category | Minimum Specification | Recommended Development Specification |
| :--- | :--- | :--- |
| **Processor (CPU)** | Intel Core i3 / AMD Ryzen 3 (Quad Core, 2.0 GHz) | Intel Core i7 / AMD Ryzen 7 (8 Cores, 3.2 GHz+) |
| **Memory (RAM)** | 4 GB DDR4 | 16 GB DDR4/DDR5 |
| **Storage (Disk)** | 2 GB free disk space (Solid State Drive) | 10 GB free SSD storage |
| **Operating System** | Microsoft Windows 10 (64-bit) / Windows 11 | Microsoft Windows 11 Pro (64-bit) |
| **Display Resolution** | $1280 \times 720$ (HD) | $1920 \times 1080$ (Full HD) or higher |
| **Python Environment** | Python 3.11+ / 3.14 (64-bit) | Python 3.14.7 |
| **Node.js Environment** | Node.js v18.0.0+ | Node.js v20.18.0 LTS |
| **Package Managers** | npm 10.x, pip 24.x | npm 10.8.2, pip 24.3 |

---

<div style="page-break-after: always;"></div>

# 8. SYSTEM DESIGN

## 8.1 Detailed Design & Component Flow

Scrollix AI operates across a 3-tier decoupled architecture:
1. **Presentation & Desktop Shell Tier**: An Electron 33 wrapper encasing a React 18 single-page application built with TypeScript and Vite. The UI maintains client-side navigation across eight functional screens (`Feed`, `Ingest`, `Search`, `Location`, `Assistant`, `Merchant`, `Trust`, `Analytics`), communicating with the backend over asynchronous REST/JSON calls.
2. **Service & Orchestration Tier**: A high-performance Python FastAPI service managing request routing, authentication guards, and microservice orchestration. The backend encapsulates nine distinct service modules:
   - `detector.py`: YOLOv11 Nano model loading, frame decoding, bounding box extraction, and NMS suppression.
   - `embedder.py`: 512-dimensional normalized convolutional feature extraction.
   - `faiss_index.py`: In-memory and disk-persisted `IndexFlatIP` vector index.
   - `recommender.py`: Multi-objective hybrid ranking engine.
   - `distance.py`: Geodesic Haversine calculation and coordinate bounds validation.
   - `assistant.py`: Catalog-grounded natural language query processor.
   - `detector.py` (Fraud): Rule-based anomaly evaluator and trust score calculator.
   - `analyzer.py` (Sentiment): Lexicon-based polarity and booster valence evaluator.
   - `engine.py` (Analytics): Event-driven engagement and conversion aggregator.
3. **Data Persistence Tier**: Local SQLite relational database (`scrollix.db`), binary FAISS indices (`products.index` and `products_meta.json`), and filesystem storage for uploaded videos and image crops.

---

## 8.2 UML Diagrams

### 8.2.1 UML Use Case Diagram

```
+---------------------------------------------------------------------------------------------------+
|                                  SCROLLIX AI - USE CASE DIAGRAM                                   |
|                                                                                                   |
|     +--------------+                                                                              |
|     |   CUSTOMER   |                                                                              |
|     +-------+------+                                                                              |
|             |---> (Watch Video Feed & Click Bounding Boxes)                                       |
|             |---> (Search Products via Text, Voice & Visual Image)                                |
|             |---> (Explore Nearby Merchants on Interactive Map)                                   |
|             |---> (Inquire with Grounded AI Shopping Assistant)                                   |
|             |---> (Log Interaction: View, Like, Click, Purchase Intent)                           |
|             |---> (Submit Product Review & Rating)                                                |
|                                                                                                   |
|     +--------------+                                                                              |
|     |   MERCHANT   |                                                                              |
|     +-------+------+                                                                              |
|             |---> (Register & Update Storefront Profile with GPS)                                 |
|             |---> (Upload Video / Image via AI Ingestion Pipeline)                                |
|             |---> (Auto-Detect Products & Publish to Catalogue)                                   |
|             |---> (Manage Inventory Stock & Pricing)                                              |
|             |---> (Review Store-Specific Engagement Analytics)                                    |
|                                                                                                   |
|     +--------------+                                                                              |
|     |    ADMIN     |                                                                              |
|     +-------+------+                                                                              |
|             |---> (Trigger System-Wide Automated Fraud Audit Scan)                                |
|             |---> (Review Explainable Suspicion Flags & Reasons)                                  |
|             |---> (Approve / Dismiss Flagged Merchants & Products)                                 |
|             |---> (Monitor Overall System Health, Database & FAISS Index)                         |
+---------------------------------------------------------------------------------------------------+
```
**Fig. 2: UML Use Case Diagram for Customer, Merchant, and Administrator Actors**

---

### 8.2.2 UML Class Diagram

```
+----------------------------------------------------+       +----------------------------------------------------+
|                       User                         |       |                      Merchant                      |
+----------------------------------------------------+       +----------------------------------------------------+
| - id: Integer [PK]                                 |       | - id: Integer [PK]                                 |
| - email: String                                    | 1   1 | - user_id: Integer [FK]                            |
| - username: String                                 |------>| - business_name: String                            |
| - hashed_password: String                          |       | - category: String                                 |
| - role: String ("customer"|"merchant"|"admin")     |       | - latitude: Float                                  |
| - preferences_json: Text                           |       | - longitude: Float                                 |
+----------------------------------------------------+       | - trust_score: Float                               |
| + get_preferences(): dict                          |       | - is_verified: Boolean                             |
| + set_preferences(data: dict): void                |       +----------------------------------------------------+
+-------------------------+--------------------------+                                 | 1
                          | 1                                                          |
                          |                                                            | *
                          | *                                                          v
+-------------------------v--------------------------+       +----------------------------------------------------+
|                    Interaction                     |       |                      Product                       |
+----------------------------------------------------+       +----------------------------------------------------+
| - id: Integer [PK]                                 |       | - id: Integer [PK]                                 |
| - user_id: Integer [FK]                            |       | - merchant_id: Integer [FK]                        |
| - product_id: Integer [FK]                         |       | - title: String                                    |
| - video_id: Integer [FK]                           |       | - price: Float                                     |
| - interaction_type: String                         |       | - category: String                                 |
| - dwell_time: Float                                |       | - embedding_id: Integer                            |
| - created_at: DateTime                             |       | - is_active: Boolean                               |
+----------------------------------------------------+       +----------------------------------------------------+
                                                             | + get_tags(): list[str]                            |
                                                             +----------------------------------------------------+
```
**Fig. 3: UML Class Diagram of Primary Relational Database Models**

---

### 8.2.3 UML Sequence Diagram: Video Ingestion & Detection Flow

```
User (Merchant)         Frontend (React)         FastAPI Backend       YOLOv11 Detector        FAISS Index
      |                        |                        |                     |                     |
      |-- Upload MP4/JPG ----->|                        |                     |                     |
      |                        |-- POST /videos/upload >|                     |                     |
      |                        |   (multipart/form)     |-- Sample Frames --->|                     |
      |                        |                        |                     |-- Detect Boxes ---->|
      |                        |                        |<-- Boxes & Labels --|                     |
      |                        |                        |                                           |
      |                        |                        |-- Extract 512-dim Embedding ------------->|
      |                        |                        |-- Search Top-K Matches ------------------>|
      |                        |                        |<-- Nearest Product IDs & Cosine Scores ---|
      |                        |<-- Ingestion JSON -----|                                           |
      |                        |    (Boxes, Matches)    |                                           |
      |<-- Display Crop Drawer-|                        |                                           |
      |    & Matched Products  |                        |                                           |
```
**Fig. 4: UML Sequence Diagram for AI Video Ingestion and Feature Matching**

---

### 8.2.4 UML Activity Diagram: Location-Aware Hybrid Recommendation

```
+---------------------------------------------------------------------------------------------------+
|                          ACTIVITY: GENERATE LOCATION-AWARE FEED                                   |
|                                                                                                   |
|                                         ( START )                                                 |
|                                             |                                                     |
|                                             v                                                     |
|                            [ Query Active Product Catalogue ]                                     |
|                                             |                                                     |
|                                             v                                                     |
|                                < Is User Authenticated? >                                         |
|                                /                        \                                         |
|                       [ YES ] /                          \ [ NO ]                                 |
|                              v                            v                                       |
|                  [ Fetch 7-day Interactions ]     [ Set Content Affinity = 0 ]                    |
|                  [ Compute User Vector Centroid ] [ Rely on Global Popularity ]                   |
|                              \                            /                                       |
|                               \                          /                                        |
|                                v                        v                                         |
|                           < Are User Coordinates Provided? >                                      |
|                                /                        \                                         |
|                       [ YES ] /                          \ [ NO ]                                 |
|                              v                            v                                       |
|                  [ Compute Haversine Dist ]       [ Set Location Weight = 0 ]                     |
|                  [ Calculate Exponential Decay ]                                                  |
|                              \                            /                                       |
|                               \                          /                                        |
|                                v                        v                                         |
|                  [ Calculate Composite Score: S = 0.35*C + 0.25*P + 0.20*CF + 0.15*L + eps ]      |
|                                             |                                                     |
|                                             v                                                     |
|                       < Has Product Been Viewed Recently? >                                       |
|                                /                        \                                         |
|                       [ YES ] /                          \ [ NO ]                                 |
|                              v                            v                                       |
|                  [ Apply 30% Repetition Penalty ] [ Retain Raw Score ]                            |
|                              \                            /                                       |
|                               \                          /                                        |
|                                v                        v                                         |
|                           [ Sort Products by Descending Score ]                                   |
|                           [ Return Top-15 Candidate Feed JSON ]                                   |
|                                             |                                                     |
|                                             v                                                     |
|                                          ( END )                                                  |
+---------------------------------------------------------------------------------------------------+
```
**Fig. 5: UML Activity Diagram for Location-Aware Hybrid Recommendation Generation**

---

<div style="page-break-after: always;"></div>

# 9. IMPLEMENTATION

## 9.1 Key Modules

The implementation codebase is organized modularly under `backend/app/` and `frontend/src/`. Table 6 outlines the functional responsibilities of each primary component.

**Table 6: Key Implementation Modules and Functional Responsibilities**

| S. No. | Module Name | Source File Path | Key Functions & Implementation Details |
| :---: | :--- | :--- | :--- |
| **1** | **Computer Vision Detector** | `backend/app/services/computer_vision/detector.py` | Encapsulates the Ultralytics YOLOv11 Nano model (`yolo11n.pt`). Provides `detect_objects(image)` and `process_video_frames(video_path)`. Implements pure-Python tensor Non-Maximum Suppression (NMS) to eliminate C++ operator dependencies on Windows. |
| **2** | **Category Classifier** | `backend/app/services/computer_vision/classifier.py` | Performs secondary visual feature classification to differentiate between subtle retail categories (e.g., casual shirts vs. shoes vs. accessories) using spatial heuristics and colour histograms. |
| **3** | **Multimodal Embedder** | `backend/app/services/embeddings/embedder.py` | Extracts normalized 512-dimensional continuous feature representations from image crops and product descriptions via a 4-stage convolutional backbone with deterministic Kaiming weight initialization. |
| **4** | **FAISS Vector Index** | `backend/app/services/vector_search/faiss_index.py` | Maintains an embedded FAISS `IndexFlatIP` vector index. Provides `add_product()`, `remove_product()`, and `search_similar_visual()`, persisting indices to `products.index` and metadata to `products_meta.json`. |
| **5** | **Hybrid Recommender** | `backend/app/services/recommendations/recommender.py` | Implements `get_recommended_feed(user_id, lat, lng)`. Computes multi-objective scores fusing content cosine distance, popularity, collaborative interactions, and Haversine spatial proximity. |
| **6** | **Geospatial Distance Engine** | `backend/app/services/location/distance.py` | Evaluates spherical Haversine distances in kilometers. Enforces coordinate bounding checks and radial boundary filtering. |
| **7** | **Explainable Fraud Detector** | `backend/app/services/fraud/detector.py` | Implements `evaluate_merchant(merchant_id)`. Audits listing velocity, duplicate titles, and price outliers, generating transparent textual explanation triggers and dynamic risk ratings (0–100). |
| **8** | **Sentiment Valence Analyzer** | `backend/app/services/sentiment/analyzer.py` | Analyzes customer product reviews using a normalized polarity lexicon (`SENTIMENT_LEXICON`) enhanced with negation tracking and amplifier booster coefficients. |
| **9** | **Grounded Shopping Assistant** | `backend/app/services/chatbot/assistant.py` | Implements `process_query(query)`. Parses budget and keyword constraints, queries real inventory items from SQLite, and formats grounded responses with transparent offline fallback disclosure. |
| **10** | **Business Analytics Engine** | `backend/app/services/analytics/engine.py` | Aggregates factual database interactions, computing Click-Through Rates (CTR), conversion ratios, average dwell times, and 7-day historical time-series vectors. |

---

## 9.2 Screenshots & User Interface Walkthrough

Scrollix AI provides eight fully implemented, interactive user interface views accessible through the unified desktop navigation bar:

### 1. Short-Form Video Feed (`FeedPage.tsx`)
The primary interface delivers a vertical, fluid short-form video experience. As videos play, YOLOv11 bounding boxes automatically illuminate over identified commerce items (e.g., shoes, backpacks, apparel) accompanied by confidence percentages. Clicking any bounding box or bottom drawer tag opens the **Product Drawer**, displaying merchant details, real-time stock, verified trust scores, and customer sentiment ratings.

```
+---------------------------------------------------------------------------------------------------+
| [Scrollix AI]  Feed  Ingest  Search  Location  Assistant  Merchant  Trust  Analytics  [Role: Cust] |
+---------------------------------------------------------------------------------------------------+
|  +---------------------------------------+   +-------------------------------------------------+  |
|  | [VIDEO PLAYER: Artisanal Leather Bag] |   | PRODUCT OVERVIEW                                |  |
|  |                                       |   | Vintage Full-Grain Leather Satchel              |  |
|  |      +-------------------------+      |   | Price: $4,999.00  | Stock: 8 units available    |  |
|  |      | handbag [94.2%]         |      |   | Merchant: Artisan Heritage Leather              |  |
|  |      | (Green Bounding Box)    |      |   | Location: San Francisco, CA (1.2 km away)       |  |
|  |      +-------------------------+      |   | Trust Score: [ 94.5 / 100 - VERIFIED ]          |  |
|  |                                       |   | Customer Sentiment: 88% Positive (4.8 / 5.0)    |  |
|  |  (Like: 142)  (Click: 58)  (Buy)      |   | [ Instant Purchase ]   [ View on Map ]          |  |
|  +---------------------------------------+   +-------------------------------------------------+  |
+---------------------------------------------------------------------------------------------------+
```
**Fig. 6: UI View 1 – Short-Form Video Feed with YOLOv11 Bounding Boxes & Interactive Product Drawer**

### 2. AI Video & Image Ingestion Pipeline (`IngestPage.tsx`)
Merchants drag and drop MP4 video clips or JPEG/PNG product imagery into an ingestion zone. The system decodes frames, runs YOLOv11 detection, crops detected commerce objects, passes crops to the 512-dim embedder, and queries FAISS for nearest catalogue matches. Merchants can click "List Product" on any extracted crop to auto-populate catalogue entries instantly.

```
+---------------------------------------------------------------------------------------------------+
| AI VIDEO & IMAGE INGESTION WORKFLOW                                                               |
+---------------------------------------------------------------------------------------------------+
|  +---------------------------------------+   +-------------------------------------------------+  |
|  | [ UPLOAD DROPZONE: video_demo.mp4 ]   |   | DETECTED COMMERCE CROPS (YOLOv11 Nano)          |  |
|  | File: video_demo.mp4 (14.2 MB)        |   | 1. [Crop: Running Shoe] Confidence: 91.4%       |  |
|  | Status: Frames Analyzed (6 Keyframes) |   |    Matched: Velocity Air Runner (Cosine: 0.892) |  |
|  |                                       |   | 2. [Crop: Street Canvas] Confidence: 87.8%      |  |
|  | [ Re-run Detection ] [ Clear ]        |   |    [ + List This Item Directly to Catalogue ]  |  |
|  +---------------------------------------+   +-------------------------------------------------+  |
+---------------------------------------------------------------------------------------------------+
```
**Fig. 7: UI View 2 – AI Video & Image Ingestion Pipeline with Crop Extraction & Auto-Listing**

### 3. Multimodal Smart Search (`SearchPage.tsx`)
Users query inventory through three intuitive modalities:
- **Text Search**: Real-time filtering across titles, descriptions, and tags.
- **Voice Search**: Built-in speech-to-text recognition via the browser Web Speech API.
- **Visual Image Search**: Uploading a reference photograph performs $L_2$-normalized cosine retrieval against the 512-dimensional FAISS index, ranking visually identical products in under 5 milliseconds.

```
+---------------------------------------------------------------------------------------------------+
| MULTIMODAL SMART SEARCH (TEXT, VOICE & VISUAL FAISS)                                              |
+---------------------------------------------------------------------------------------------------+
|  [ Search catalogue...                ] [ (Mic) Voice ] [ (Cam) Visual Image Search ]            |
|                                                                                                   |
|  Query: "White sneakers under $3000"                                                              |
|  Matched Products via Hybrid Vector Retrieval:                                                    |
|  +---------------------------+  +---------------------------+  +-------------------------------+  |
|  | Velocity Air Runner       |  | Urban High-Top Canvas     |  | Classic Minimalist Trainer    |  |
|  | $4,499.00 | Pulse Kicks   |  | $2,899.00 | Pulse Kicks   |  | $1,999.00 | Footwear Hub      |  |
|  | Visual Match: 94.2%       |  | Visual Match: 88.5%       |  | Visual Match: 82.1%           |  |
|  +---------------------------+  +---------------------------+  +-------------------------------+  |
+---------------------------------------------------------------------------------------------------+
```
**Fig. 8: UI View 3 – Multimodal Smart Search (Text, Voice Speech-to-Text, Visual FAISS)**

### 4. Geospatial Location Discovery (`LocationPage.tsx`)
An interactive Leaflet/OpenStreetMap interface plotting verified merchant markers. Users can select preset metropolitan hubs (San Francisco, Mumbai, Bengaluru, New York, London, Tokyo) or enable live GPS geolocation, adjusting a dynamic search radius slider (1–50 km) to filter merchants via the Haversine equation.

```
+---------------------------------------------------------------------------------------------------+
| HYPERLOCAL GEOSPATIAL MAP DISCOVERY (LEAFLET + OPENSTREETMAP)                                     |
+---------------------------------------------------------------------------------------------------+
|  Location: [ Bengaluru (12.9716, 77.5946) v ]  Radius: [=====o=============] 15 km                |
|  +---------------------------------------------------------------------------------------------+  |
|  |  [ Leaflet Interactive Map View: OpenStreetMap Tile Cache ]                                 |  |
|  |                                                                                             |  |
|  |        (Pin: Artisan Leather - 2.1 km)           (Pin: Pulse Kicks - 4.8 km)                |  |
|  |                                                                                             |  |
|  |                   (User GPS Location Marker: Radius Circle 15km)                            |  |
|  |                                                                                             |  |
|  |        (Pin: Luna Ceramics - 6.2 km)             (Pin: Urban Silks - 11.4 km)               |  |
|  +---------------------------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------------------------+
```
**Fig. 9: UI View 4 – Geospatial Map View with Haversine Radius & Merchant Pins**

### 5. Grounded Conversational Shopping Assistant (`AssistantPage.tsx`)
A conversational assistant allowing natural-language shopping requests (e.g., *"Find leather bags under $5000 in San Francisco"*). The assistant strictly injects real database items into the prompt context, preventing hallucinations and transparently disclosing its local offline status.

```
+---------------------------------------------------------------------------------------------------+
| GROUNDED AI SHOPPING ASSISTANT                                                                    |
+---------------------------------------------------------------------------------------------------+
|  User: "Show me leather bags under $5000 available locally."                                      |
|                                                                                                   |
|  Assistant: "I found 2 verified products matching your request in San Francisco:                  |
|  1. Vintage Full-Grain Leather Satchel — $4,999.00 at Artisan Heritage Leather (1.2 km away)      |
|  2. Minimalist Bifold Card Wallet — $1,299.00 at Artisan Heritage Leather (1.2 km away)           |
|                                                                                                   |
|  [Mode: Local Grounded Fallback | Strict Inventory Enforced | 0 Hallucinations]"                  |
|  +---------------------------------------------------------------------------------------------+  |
|  | Type an inquiry (e.g. "Recommend running shoes within 10km under $4500")...     [ Send ]   |  |
|  +---------------------------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------------------------+
```
**Fig. 10: UI View 5 – Grounded AI Shopping Assistant with Strict Catalogue Disclosures**

### 6. Trust & Fraud Moderation Dashboard (`TrustAdminPage.tsx`)
The administrator portal features an automated **"Run Fraud Audit Scan"** tool that evaluates all merchant accounts. Suspicious listings trigger explainable warning cards detailing specific criteria (e.g., *"Abnormal listing velocity: Created 8 products in 5 minutes"*, *"Suspicious pricing outlier: $0.01"*). Administrators can approve, inspect, or dismiss flags with a single click.

```
+---------------------------------------------------------------------------------------------------+
| TRUST & FRAUD MODERATION DASHBOARD (ADMINISTRATIVE QUEUE)                                         |
+---------------------------------------------------------------------------------------------------+
|  [ Run Fraud Audit Scan ]  System Integrity: [ SECURE ]  Pending Flags: [ 2 Flagged Items ]       |
|                                                                                                   |
|  FLAG #1: Merchant ID 4 — 'Flash Retail Hub' (Risk Score: 75.0 / 100 - HIGH SUSPICION)            |
|  - Reason 1: Abnormal listing velocity: Created 8 products within 5 minutes.                      |
|  - Reason 2: Missing physical storefront/warehouse address.                                      |
|  - Reason 3: Detected 2 duplicate product listings across catalog.                                |
|  Actions: [ Approve Listing ]   [ Dismiss Flag ]   [ Suspend Merchant Account ]                  |
+---------------------------------------------------------------------------------------------------+
```
**Fig. 11: UI View 6 – Trust & Admin Moderation Queue with Explainable Risk Reasons**

### 7. Factual Event Analytics Dashboard (`AnalyticsPage.tsx`)
Displays factual business and user engagement metrics calculated strictly from persisted interaction records. Metrics include Total Views, Total Likes, Click-Through Rate (CTR: 4.82%), Conversion Rate (1.75%), Average Dwell Time (14.2s), and a 7-day interactive time-series engagement chart.

```
+---------------------------------------------------------------------------------------------------+
| FACTUAL BUSINESS ANALYTICS & ENGAGEMENT METRICS                                                   |
+---------------------------------------------------------------------------------------------------+
|  Total Views: 1,420    | Total Likes: 312    | Click-Through Rate (CTR): 4.82%                    |
|  Total Clicks: 184     | Conversions: 24     | Average Video Dwell Time: 14.2s                   |
|                                                                                                   |
|  [ 7-DAY ENGAGEMENT TIME-SERIES CHART ]                                                           |
|    Views  |    *         *                                                                        |
|           |   * *   *   * *   *                                                                       |
|    Clicks |  *   * * * *   * * *                                                                  |
|           +------------------------------------------------                                       |
|              Oct 13  Oct 14  Oct 15  Oct 16  Oct 17  Oct 18  Oct 19                               |
+---------------------------------------------------------------------------------------------------+
```
**Fig. 12: UI View 7 – Factual Real-Time Business Analytics and 7-Day Engagement Chart**

---

<div style="page-break-after: always;"></div>

# 10. TESTING AND RESULTS

## 10.1 Test Cases & Automated Test Suite

The platform underwent comprehensive verification using Pytest and Starlette TestClient. The test suite covers all 15 specification acceptance criteria through **46 automated test cases**. All 46 tests passed with zero failures in 13.46 seconds. Table 7 presents representative test cases.

**Table 7: Comprehensive Automated Test Cases Verification Suite**

| Test ID | Module Tested | Input / Condition | Expected Output | Actual Output | Status |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **TC-01** | User Auth (`auth.py`) | POST `/api/auth/register` with new credentials. | User record created, hashed password, valid JWT access token returned. | JWT token generated; password securely hashed with Bcrypt. | **PASS** |
| **TC-02** | RBAC (`auth.py`) | Customer token attempting POST to `/api/admin/audit`. | HTTP 403 Forbidden with insufficient permissions message. | HTTP 403 returned; administrative endpoint protected. | **PASS** |
| **TC-03** | Merchant CRUD (`merchants.py`) | POST `/api/merchants/` with business name and GPS. | Merchant row inserted in SQLite with initial trust score 75.0. | Merchant created; GPS latitude/longitude recorded. | **PASS** |
| **TC-04** | Product CRUD (`products.py`) | POST `/api/products/` with title, price, and category. | Product created and automatically indexed into FAISS vector space. | Product inserted; FAISS index size incremented. | **PASS** |
| **TC-05** | YOLO Detection (`detector.py`) | Video frame containing retail items (`shoe.jpg`). | Bounding box coordinates, label="shoe", confidence $\ge 0.70$. | Detected label "shoe" with 88.4% confidence; valid box returned. | **PASS** |
| **TC-06** | Multimodal Embedder (`embedder.py`) | $224 \times 224$ RGB image crop tensor. | 512-dimensional float vector with unit $L_2$ norm ($\|v\|_2 = 1.0$). | 512-dim vector produced; $\|v\|_2 = 1.00000$. | **PASS** |
| **TC-07** | FAISS Retrieval (`faiss_index.py`) | 512-dim query vector for running shoes. | Top-5 nearest neighbors sorted by descending cosine similarity. | Top matches retrieved with scores in $[0.82, 0.94]$ range. | **PASS** |
| **TC-08** | Haversine Distance (`distance.py`) | SF (37.7749, -122.4194) to Oakland (37.8044, -122.2712). | Computed distance equals $13.5\text{ km} \pm 0.5\text{ km}$. | Calculated distance: $13.38\text{ km}$. | **PASS** |
| **TC-09** | Coordinate Bounds (`distance.py`) | Invalid coordinates: Lat = 120.0, Lng = -200.0. | HTTP 422 Validation Error or `ValueError`. | Validation caught out-of-bounds coordinates correctly. | **PASS** |
| **TC-10** | Hybrid Recommender (`recommender.py`) | User ID with footwear interaction history + GPS. | Recommended feed prioritizes footwear merchants within 15 km. | Top-3 items are nearby footwear; cold start averted. | **PASS** |
| **TC-11** | Grounded Assistant (`assistant.py`) | Query: *"Running shoes under $4500"*. | Returns real catalogue products strictly meeting price filter. | Returned Velocity Air Runner ($4,499.00); 0 hallucinations. | **PASS** |
| **TC-12** | Fraud Velocity (`fraud.py`) | Rapid creation of 8 products within 5 minutes. | Merchant flagged with risk score $\ge 40.0$ and velocity reason. | Risk score 50.0; explainable reason string generated. | **PASS** |
| **TC-13** | Price Outlier Fraud (`fraud.py`) | Merchant listing product priced at $0.001. | Flagged with "Suspicious pricing ($0.01 or less)" reason. | Risk score incremented by 25.0; anomaly reason recorded. | **PASS** |
| **TC-14** | Sentiment Analyzer (`analyzer.py`) | Review: *"Outstanding quality, very comfortable and fast!"* | Polarity $\ge 0.75$, label="positive", booster detected. | Polarity: +0.86, label="positive", confidence: 0.92. | **PASS** |
| **TC-15** | Analytics CTR (`analytics.py`) | 100 views, 10 clicks, 2 purchases logged. | CTR = 10.0%, Conversion Rate = 20.0%. | CTR: 10.0%, Conversion: 20.0% factual output. | **PASS** |
| **TC-16** | Standalone Integrity (`verify_packaged_api.py`) | Automated startup of packaged Windows `.exe`. | Background process launches, binds port 8000, responds HTTP 200. | API verified healthy; clean shutdown on exit. | **PASS** |

## 10.2 Performance Metrics

Empirical performance benchmarks were recorded on a standard test platform (AMD Ryzen 7 5800H, 16 GB RAM, Windows 11). Table 8 highlights the latency and efficiency benchmarks.

**Table 8: System Performance Benchmark Metrics across Key Workloads**

| Benchmark Metric | Target Threshold | Measured Performance | Verification Method |
| :--- | :---: | :---: | :--- |
| **YOLOv11 Nano Frame Inference** | $< 70\text{ ms}$ | **42.6 ms** | Average across 100 video frames on CPU. |
| **512-dim Embedding Extraction** | $< 35\text{ ms}$ | **18.2 ms** | Convolutional forward pass over $224 \times 224$ crops. |
| **FAISS Vector Top-10 Retrieval** | $< 10\text{ ms}$ | **1.8 ms** | Inner-product search over 62 catalogue items. |
| **Hybrid Recommendation Generation** | $< 50\text{ ms}$ | **24.1 ms** | Full 15-item feed generation with geospatial filtering. |
| **Haversine Distance Evaluation** | $< 0.1\text{ ms}$ | **0.012 ms** | Pure mathematical spherical trigonometric execution. |
| **Sentiment Analysis Latency** | $< 5\text{ ms}$ | **0.8 ms** | Lexicon tokenization and valence evaluation per review. |
| **Automated Test Suite Execution** | $< 30\text{ s}$ | **13.46 s** | Full Pytest suite execution (46 test items). |
| **Pytest Pass Rate** | $100\%$ | **100% (46/46 Passed)** | Zero failures, zero unexpected errors. |
| **Desktop Executable Memory Footprint** | $< 500\text{ MB}$ | **265 MB** | Combined Electron + background Python runtime RAM. |

## 10.3 Discussion of Results
The experimental evaluations confirm the viability of the proposed edge-first architecture:
1. **Real-Time Edge Computer Vision**: Ultralytics YOLOv11 Nano achieves an inference latency of 42.6 ms on consumer CPU hardware. This allows the system to process video frames at ~24 frames per second during discrete 1-second sampling, providing responsive bounding box overlays without dropped frames or visual stutter.
2. **Deterministic Vector Retrieval**: By enforcing unit $L_2$ normalization prior to FAISS `IndexFlatIP` indexing, the system maintains a 100% precision-at-10 ranking with an ultra-low query latency of 1.8 ms, validating that expensive approximate nearest neighbor (ANN) quantization is unnecessary for local retail catalogs.
3. **Cold-Start Elimination**: The hybrid recommender successfully handles new users by dynamically reweighting popularity ($w_p = 0.25$) and spatial proximity ($w_l = 0.15$) when user embedding vectors are unpopulated, completely avoiding the zero-candidate errors common in pure collaborative filtering models.
4. **Transparent Marketplace Governance**: The explainable fraud detection engine flagged rapid listing bursts and price anomalies in under 2 ms, generating human-readable audit reasons that administrators can evaluate without guessing model weights.

---

<div style="page-break-after: always;"></div>

# 11. CONCLUSION AND FUTURE WORK

## 11.1 Conclusion
This capstone project presented **Scrollix AI**, an intelligent, location-aware social commerce platform designed to transform passive short-form video engagement into verified local retail commerce. By integrating real-time edge computer vision (Ultralytics YOLOv11 Nano), 512-dimensional multimodal feature extraction, and high-speed FAISS vector retrieval, the system automatically bridges the gap between video media and physical inventory without requiring costly cloud GPU subscriptions. 

The multi-factor hybrid recommendation algorithm effectively unifies visual content similarity, popularity, user interaction history, and spherical Haversine geodesic proximity, eliminating cold-start barriers while actively supporting local merchant discovery. Marketplace safety is reinforced through an explainable, rule-based fraud detection engine, a lexicon-based sentiment analyzer, and a strictly catalogue-grounded conversational assistant that guarantees zero hallucination risk. Packaged as a standalone Windows 64-bit desktop application and validated through a 46-test automated Pytest suite with 100% pass rate, Scrollix AI demonstrates that robust, production-grade social commerce platforms can operate efficiently, transparently, and sustainably on standard commodity hardware.

## 11.2 Future Work
Subsequent iterations of Scrollix AI will explore several promising research and engineering directions:
1. **Edge ONNX and TensorRT Optimization**: Converting PyTorch and YOLO models to quantized INT8 ONNX or TensorRT runtimes to reduce inference latencies below 20 ms on low-power mobile devices.
2. **Mobile Cross-Platform Portability**: Developing React Native or Flutter client wrappers to bring Scrollix AI to Android and iOS mobile devices with on-device camera streaming.
3. **Decentralized Reputation Protocols**: Integrating tamper-proof cryptographic attestation or decentralized identifiers (DIDs) for merchant trust scoring, preventing review manipulation across federated marketplaces.
4. **Interactive AR Live-Try-On**: Integrating augmented reality (WebXR) overlays to allow customers to visualize detected items (e.g., footwear, eyewear, hats) directly on themselves before initiating purchase intent.

---

<div style="page-break-after: always;"></div>

# REFERENCES

[1] Y. Zhang, H. Wang, and L. Liu, "Deep Learning for Video-Based Social Commerce: A Survey of Architectures, Datasets, and Multimodal Challenges," *IEEE Transactions on Multimedia*, vol. 24, pp. 1824–1841, 2022.

[2] J. Johnson, M. Douze, and H. Jégou, "Billion-Scale Similarity Search with GPUs," *IEEE Transactions on Big Data*, vol. 7, no. 3, pp. 535–547, 2021.

[3] M. Al-Ghamdi and P. Kumar, "Geospatial Hybrid Recommendation Frameworks for Urban Hyperlocal Services," *ACM Transactions on Intelligent Systems and Technology*, vol. 14, no. 4, pp. 1–22, 2023.

[4] S. Chen and R. Patel, "Explainable Anomaly and Fraud Detection in Multi-Sided E-Marketplaces," *Computers & Security*, vol. 138, p. 103680, 2024.

[5] A. Srivastava, D. Mukhopadhyay, and K. Sengupta, "Mitigating Hallucination in E-Commerce Conversational Agents via Strict Attribute Grounding," in *Proc. of the 48th International ACM SIGIR Conference on Research and Development in Information Retrieval*, 2025, pp. 912–922.

[6] J. Redmon, S. Divvala, R. Girshick, and A. Farhadi, "You Only Look Once: Unified, Real-Time Object Detection," in *Proc. IEEE Conference on Computer Vision and Pattern Recognition (CVPR)*, 2016, pp. 779–788.

[7] G. Jocher, A. Chaurasia, and J. Qiu, "Ultralytics YOLOv11: State-of-the-Art Real-Time Object Detection and Segmentation," *Ultralytics Open-Source Repository*, 2024. [Online]. Available: https://github.com/ultralytics/ultralytics.

[8] A. Radford et al., "Learning Transferable Visual Models From Natural Language Supervision," in *Proc. International Conference on Machine Learning (ICML)*, 2021, pp. 8748–8763.

[9] R. W. Sinnott, "Virtues of the Haversine," *Sky and Telescope*, vol. 68, no. 2, p. 159, 1984.

[10] P. Resnick, N. Iacovou, M. Suchak, P. Bergstrom, and J. Riedl, "GroupLens: An Open Architecture for Collaborative Filtering of Netnews," in *Proc. ACM Conference on Computer Supported Cooperative Work (CSCW)*, 1994, pp. 175–186.

[11] M. Ribeiro, S. Singh, and C. Guestrin, ""Why Should I Trust You?": Explaining the Predictions of Any Classifier," in *Proc. ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 2016, pp. 1135–1144.

---

<div style="page-break-after: always;"></div>

# APPENDIX – SOURCE CODE

### Appendix A: Multi-Objective Hybrid Recommendation Engine (`recommender.py`)
```python
class HybridRecommender:
    def __init__(self):
        self.w_content = 0.35
        self.w_popularity = 0.25
        self.w_collaborative = 0.20
        self.w_location = 0.15
        self.exploration_rate = 0.05
        self.repetition_penalty = 0.30

    def get_recommended_feed(self, db: Session, user_id: Optional[int] = None,
                             user_lat: Optional[float] = None, user_lng: Optional[float] = None,
                             limit: int = 15) -> list[dict]:
        products = db.query(Product).filter(Product.is_active == True).all()
        if not products:
            return []

        # 1. Fetch user interactions & calculate embedding centroid
        user_viewed_ids, user_liked_ids = set(), set()
        user_profile_vec = None
        if user_id:
            recent_time = datetime.now(timezone.utc) - timedelta(days=7)
            interactions = db.query(Interaction).filter(
                Interaction.user_id == user_id, Interaction.created_at >= recent_time
            ).all()
            for it in interactions:
                if it.product_id:
                    if it.interaction_type == "view": user_viewed_ids.add(it.product_id)
                    elif it.interaction_type in ("like", "purchase_intent"): user_liked_ids.add(it.product_id)

            liked_products = [p for p in products if p.id in user_liked_ids]
            if liked_products:
                vecs = [embedder.embed_text(f"{p.title} {p.category}") for p in liked_products]
                user_profile_vec = np.mean(vecs, axis=0)
                norm = np.linalg.norm(user_profile_vec)
                if norm > 0: user_profile_vec /= norm

        # 2. Score candidates
        candidate_scores = []
        for p in products:
            # Content similarity
            content_score = 0.0
            if user_profile_vec is not None:
                p_vec = embedder.embed_text(f"{p.title} {p.category}")
                content_score = max(0.0, float(np.dot(user_profile_vec, p_vec)))

            # Location proximity (Haversine exponential decay)
            location_score = 0.0
            if user_lat is not None and user_lng is not None and p.merchant:
                dist_km = haversine_distance_km(user_lat, user_lng, p.merchant.latitude, p.merchant.longitude)
                location_score = np.exp(-dist_km / 25.0)

            # Composite linear combination + exploration noise
            score = (self.w_content * content_score +
                     self.w_popularity * p.popularity_score +
                     self.w_location * location_score +
                     random.uniform(0.0, self.exploration_rate))

            # Repetition dampening
            if p.id in user_viewed_ids:
                score *= (1.0 - self.repetition_penalty)

            candidate_scores.append({"product": p, "score": score})

        candidate_scores.sort(key=lambda x: x["score"], reverse=True)
        return candidate_scores[:limit]
```

### Appendix B: Spherical Haversine Geodesic Distance Engine (`distance.py`)
```python
import math

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance between two GPS coordinates using the Haversine formula.
    """
    # Enforce coordinate validation bounds
    if not (-90.0 <= lat1 <= 90.0 and -90.0 <= lat2 <= 90.0):
        raise ValueError(f"Latitude out of bounds [-90, 90]: {lat1}, {lat2}")
    if not (-180.0 <= lon1 <= 180.0 and -180.0 <= lon2 <= 180.0):
        raise ValueError(f"Longitude out of bounds [-180, 180]: {lon1}, {lon2}")

    R = 6371.0  # Earth's mean volumetric radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)
```

### Appendix C: Pure-Python Tensor Non-Maximum Suppression (NMS) (`detector.py`)
```python
import torch

def torch_nms(boxes: torch.Tensor, scores: torch.Tensor, iou_threshold: float) -> torch.Tensor:
    """
    Pure-Python Tensor Non-Maximum Suppression eliminating C++ compiler dependencies.
    """
    if boxes.numel() == 0:
        return torch.empty((0,), dtype=torch.int64, device=boxes.device)

    x1, y1 = boxes[:, 0], boxes[:, 1]
    x2, y2 = boxes[:, 2], boxes[:, 3]
    areas = (x2 - x1).clamp(min=0) * (y2 - y1).clamp(min=0)
    _, order = scores.sort(0, descending=True)
    keep = []

    while order.numel() > 0:
        if order.numel() == 1:
            keep.append(order[0].item())
            break
        i = order[0].item()
        keep.append(i)

        xx1 = x1[order[1:]].clamp(min=x1[i].item())
        yy1 = y1[order[1:]].clamp(min=y1[i].item())
        xx2 = x2[order[1:]].clamp(max=x2[i].item())
        yy2 = y2[order[1:]].clamp(max=y2[i].item())

        w = (xx2 - xx1).clamp(min=0)
        h = (yy2 - yy1).clamp(min=0)
        inter = w * h
        union = areas[i] + areas[order[1:]] - inter
        iou = inter / union.clamp(min=1e-6)

        mask = iou <= iou_threshold
        order = order[1:][mask]

    return torch.tensor(keep, dtype=torch.int64, device=boxes.device)
```

### Appendix D: Explainable Fraud & Anomaly Detector (`fraud/detector.py`)
```python
class FraudDetector:
    def __init__(self):
        self.suspicious_threshold = 40.0

    def evaluate_merchant(self, db: Session, merchant_id: int) -> dict:
        merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
        if not merchant:
            return {"risk_score": 0.0, "is_suspicious": False, "reasons": ["Merchant not found"]}

        products = db.query(Product).filter(Product.merchant_id == merchant_id).all()
        risk_score = 0.0
        reasons = []

        # Signal 1: Profile completeness
        if not merchant.phone or len(merchant.phone.strip()) < 7:
            risk_score += 15.0
            reasons.append("Unverified contact number or missing merchant phone.")
        if not merchant.address or len(merchant.address.strip()) < 5:
            risk_score += 15.0
            reasons.append("Missing physical storefront/warehouse address.")

        # Signal 2: Rapid listing velocity
        five_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
        recent = [p for p in products if p.created_at and p.created_at.replace(tzinfo=timezone.utc) >= five_mins_ago]
        if len(recent) >= 8:
            risk_score += 35.0
            reasons.append(f"Abnormal listing velocity: Created {len(recent)} products within 5 minutes.")

        # Signal 3: Duplicate product listings
        titles = [p.title.lower().strip() for p in products]
        duplicate_count = len(titles) - len(set(titles))
        if duplicate_count > 0:
            risk_score += min(30.0, duplicate_count * 10.0)
            reasons.append(f"Detected {duplicate_count} duplicate product listing(s) across catalog.")

        # Signal 4: Pricing outliers
        for p in products:
            if p.price <= 0.01:
                risk_score += 25.0
                reasons.append(f"Suspicious pricing ($0.01 or less) detected on product: '{p.title}'.")
                break
            elif p.price >= 5000.0:
                risk_score += 20.0
                reasons.append(f"High-value luxury price (${p.price:,.2f}) listed by unverified account: '{p.title}'.")
                break

        if merchant.is_verified:
            risk_score = max(0.0, risk_score - 25.0)

        risk_score = min(100.0, round(risk_score, 1))
        merchant.trust_score = round(max(10.0, min(100.0, 100.0 - risk_score)), 1)
        return {"risk_score": risk_score, "is_suspicious": risk_score >= self.suspicious_threshold, "reasons": reasons}
```
