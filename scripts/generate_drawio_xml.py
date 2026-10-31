import os
import xml.etree.ElementTree as ET

def build_simplified_drawio_xml():
    xml_content = '''<mxfile host="app.diagrams.net" modified="2026-10-20T00:00:00.000Z" agent="Mozilla/5.0" version="24.0.0">
  <diagram id="scrollix-ai-architecture" name="Scrollix AI Architecture">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1200" pageHeight="780" background="#FFFFFF">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- ==================== TIER 1: CLIENT PRESENTATION TIER ==================== -->
        <mxCell id="tier1" value="1. CLIENT PRESENTATION TIER (Desktop Application)" style="swimlane;html=1;startSize=28;horizontal=1;fillColor=#F8FAFC;strokeColor=#475569;strokeWidth=1.5;rounded=1;arcSize=6;fontStyle=1;fontSize=12;fontFamily=Helvetica;fontColor=#0F172A;align=left;spacingLeft=15;" vertex="1" parent="1">
          <mxGeometry x="40" y="30" width="1120" height="135" as="geometry" />
        </mxCell>

        <mxCell id="client_shell" value="&lt;b&gt;Electron Desktop Shell&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;React 18 • TypeScript • Vite&lt;br&gt;Native Windows Interface&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#3B82F6;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#1E3A8A;" vertex="1" parent="tier1">
          <mxGeometry x="25" y="40" width="165" height="75" as="geometry" />
        </mxCell>

        <mxCell id="client_feed" value="&lt;b&gt;Video Feed&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;• Video Stream Player&lt;br&gt;• Live YOLO Boxes&lt;br&gt;• Product Drawer&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#3B82F6;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#1E3A8A;" vertex="1" parent="tier1">
          <mxGeometry x="205" y="40" width="165" height="75" as="geometry" />
        </mxCell>

        <mxCell id="client_ingest" value="&lt;b&gt;AI Video Ingest&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;• Drag &amp; Drop Upload&lt;br&gt;• Frame Extraction&lt;br&gt;• 1-Click Auto-Listing&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#3B82F6;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#1E3A8A;" vertex="1" parent="tier1">
          <mxGeometry x="385" y="40" width="165" height="75" as="geometry" />
        </mxCell>

        <mxCell id="client_search" value="&lt;b&gt;Smart Search&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;• Text Keyword Search&lt;br&gt;• Voice Input (Mic)&lt;br&gt;• Visual Image Search&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#3B82F6;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#1E3A8A;" vertex="1" parent="tier1">
          <mxGeometry x="565" y="40" width="165" height="75" as="geometry" />
        </mxCell>

        <mxCell id="client_map" value="&lt;b&gt;Nearby Store Map&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;• Leaflet + OpenStreetMap&lt;br&gt;• GPS &amp; City Selection&lt;br&gt;• 1–50 km Radius Slider&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#3B82F6;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#1E3A8A;" vertex="1" parent="tier1">
          <mxGeometry x="745" y="40" width="165" height="75" as="geometry" />
        </mxCell>

        <mxCell id="client_admin" value="&lt;b&gt;Admin &amp; Assistant&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;• Grounded Shopping Chat&lt;br&gt;• Merchant Inventory CRUD&lt;br&gt;• Fraud Scan &amp; Analytics&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EFF6FF;strokeColor=#3B82F6;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#1E3A8A;" vertex="1" parent="tier1">
          <mxGeometry x="925" y="40" width="170" height="75" as="geometry" />
        </mxCell>

        <!-- ==================== TIER 2: API GATEWAY & ORCHESTRATION ==================== -->
        <mxCell id="tier2" value="2. API GATEWAY &amp; REST ORCHESTRATION LAYER (FastAPI)" style="swimlane;html=1;startSize=28;horizontal=1;fillColor=#F8FAFC;strokeColor=#475569;strokeWidth=1.5;rounded=1;arcSize=6;fontStyle=1;fontSize=12;fontFamily=Helvetica;fontColor=#0F172A;align=left;spacingLeft=15;" vertex="1" parent="1">
          <mxGeometry x="40" y="205" width="1120" height="105" as="geometry" />
        </mxCell>

        <mxCell id="gw_auth" value="&lt;b&gt;Authentication &amp; Security&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;JWT Bearer Tokens • Bcrypt Hashing&lt;br&gt;Customer, Merchant &amp; Admin Roles&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ECFDF5;strokeColor=#10B981;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#065F46;" vertex="1" parent="tier2">
          <mxGeometry x="30" y="40" width="310" height="50" as="geometry" />
        </mxCell>

        <mxCell id="gw_routers" value="&lt;b&gt;REST API Endpoints&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;/videos • /products • /merchants • /search • /location • /admin&lt;br&gt;Pydantic Request Validation &amp; Error Handling&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ECFDF5;strokeColor=#10B981;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#065F46;" vertex="1" parent="tier2">
          <mxGeometry x="370" y="40" width="380" height="50" as="geometry" />
        </mxCell>

        <mxCell id="gw_dispatch" value="&lt;b&gt;Service Dispatcher&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;Coordinates Local AI &amp; Business Engines&lt;br&gt;100% Offline (Zero Cloud Dependency)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ECFDF5;strokeColor=#10B981;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#065F46;" vertex="1" parent="tier2">
          <mxGeometry x="780" y="40" width="310" height="50" as="geometry" />
        </mxCell>

        <!-- ==================== TIER 3: CORE AI & ALGORITHMIC ENGINES ==================== -->
        <mxCell id="tier3" value="3. CORE AI &amp; COMPUTATIONAL SERVICES LAYER (Local Inference)" style="swimlane;html=1;startSize=28;horizontal=1;fillColor=#F8FAFC;strokeColor=#475569;strokeWidth=1.5;rounded=1;arcSize=6;fontStyle=1;fontSize=12;fontFamily=Helvetica;fontColor=#0F172A;align=left;spacingLeft=15;" vertex="1" parent="1">
          <mxGeometry x="40" y="350" width="1120" height="150" as="geometry" />
        </mxCell>

        <mxCell id="ai_yolo" value="&lt;b&gt;Computer Vision&lt;/b&gt;&lt;br&gt;&lt;b&gt;YOLOv11 Nano&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;• Real-time Object Detection&lt;br&gt;• Retail/Commerce Classes&lt;br&gt;• Pure-Python Tensor NMS&lt;br&gt;• Keyframe Crop Extraction&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F3FF;strokeColor=#8B5CF6;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#5B21B6;" vertex="1" parent="tier3">
          <mxGeometry x="25" y="40" width="195" height="95" as="geometry" />
        </mxCell>

        <mxCell id="ai_embed" value="&lt;b&gt;Multimodal Embedder&lt;/b&gt;&lt;br&gt;&lt;b&gt;PyTorch CNN&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;• 512-dim Dense Vectors&lt;br&gt;• Unit L2 Normalization&lt;br&gt;• Image Crop Projections&lt;br&gt;• Text Feature Generation&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F3FF;strokeColor=#8B5CF6;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#5B21B6;" vertex="1" parent="tier3">
          <mxGeometry x="245" y="40" width="195" height="95" as="geometry" />
        </mxCell>

        <mxCell id="ai_faiss" value="&lt;b&gt;Vector Search&lt;/b&gt;&lt;br&gt;&lt;b&gt;FAISS IndexFlatIP&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;• Exact Cosine Similarity&lt;br&gt;• Nearest Neighbor Top-K&lt;br&gt;• Color Histogram Re-ranking&lt;br&gt;• Fast Catalog Matching&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F3FF;strokeColor=#8B5CF6;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#5B21B6;" vertex="1" parent="tier3">
          <mxGeometry x="465" y="40" width="195" height="95" as="geometry" />
        </mxCell>

        <mxCell id="ai_recom" value="&lt;b&gt;Hybrid Recommender&lt;/b&gt;&lt;br&gt;&lt;b&gt;Multi-Factor Ranking&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;• Content Similarity (0.35)&lt;br&gt;• Store Popularity (0.25)&lt;br&gt;• User History (0.20)&lt;br&gt;• Haversine Distance (0.15)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F3FF;strokeColor=#8B5CF6;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#5B21B6;" vertex="1" parent="tier3">
          <mxGeometry x="685" y="40" width="200" height="95" as="geometry" />
        </mxCell>

        <mxCell id="ai_geo_trust" value="&lt;b&gt;Geospatial &amp; Trust&lt;/b&gt;&lt;br&gt;&lt;b&gt;LBS, Fraud &amp; Sentiment&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;• Spherical Haversine Math&lt;br&gt;• Store Radius Boundary&lt;br&gt;• Explainable Fraud Rules&lt;br&gt;• Review Sentiment Polarity&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F3FF;strokeColor=#8B5CF6;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#5B21B6;" vertex="1" parent="tier3">
          <mxGeometry x="910" y="40" width="185" height="95" as="geometry" />
        </mxCell>

        <!-- ==================== TIER 4: PERSISTENT STORAGE TIER ==================== -->
        <mxCell id="tier4" value="4. DATA PERSISTENCE TIER (Local Storage)" style="swimlane;html=1;startSize=28;horizontal=1;fillColor=#F8FAFC;strokeColor=#475569;strokeWidth=1.5;rounded=1;arcSize=6;fontStyle=1;fontSize=12;fontFamily=Helvetica;fontColor=#0F172A;align=left;spacingLeft=15;" vertex="1" parent="1">
          <mxGeometry x="40" y="540" width="1120" height="135" as="geometry" />
        </mxCell>

        <mxCell id="db_sqlite" value="&lt;b&gt;Relational DB (SQLite: scrollix.db)&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;• Users, Merchants &amp; Store GPS&lt;br&gt;• Products, Categories &amp; Inventory&lt;br&gt;• Video Records &amp; Frame Detections&lt;br&gt;• User Interaction Events &amp; Reviews&lt;/font&gt;" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=8;fillColor=#FEF3C7;strokeColor=#F59E0B;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#92400E;align=left;spacingLeft=15;" vertex="1" parent="tier4">
          <mxGeometry x="30" y="40" width="360" height="80" as="geometry" />
        </mxCell>

        <mxCell id="db_faiss" value="&lt;b&gt;Vector Index Files&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;• products.index (512-dim Dense Matrix)&lt;br&gt;• products_meta.json (Product Mapping)&lt;br&gt;• Embedded In-Memory Lookup&lt;/font&gt;" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=8;fillColor=#FEF3C7;strokeColor=#F59E0B;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#92400E;align=left;spacingLeft=15;" vertex="1" parent="tier4">
          <mxGeometry x="420" y="40" width="320" height="80" as="geometry" />
        </mxCell>

        <mxCell id="db_media" value="&lt;b&gt;Local Media Directory&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#475569&quot;&gt;• data/uploads (Raw Videos &amp; Photos)&lt;br&gt;• data/catalogue_images (Catalog Items)&lt;br&gt;• Cropped Object Detections&lt;/font&gt;" style="shape=folder;whiteSpace=wrap;html=1;tabWidth=90;tabHeight=20;tabPosition=left;fillColor=#FEF3C7;strokeColor=#F59E0B;strokeWidth=1.5;fontSize=11;fontFamily=Helvetica;fontColor=#92400E;align=left;spacingLeft=15;" vertex="1" parent="tier4">
          <mxGeometry x="770" y="40" width="320" height="80" as="geometry" />
        </mxCell>

        <!-- ==================== CONNECTORS / DATA FLOW EDGES ==================== -->
        <mxCell id="edge_t1_t2" value="REST API / JSON Requests" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#2563EB;strokeWidth=2;fontSize=11;fontFamily=Helvetica;fontColor=#1E40AF;endArrow=classic;startArrow=classic;" edge="1" parent="1" source="tier1" target="tier2">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="600" y="180" />
              <mxPoint x="600" y="195" />
            </Array>
          </mxGeometry>
        </mxCell>

        <mxCell id="edge_t2_t3" value="Internal Service Calls" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#059669;strokeWidth=2;fontSize=11;fontFamily=Helvetica;fontColor=#065F46;endArrow=classic;startArrow=classic;" edge="1" parent="1" source="tier2" target="tier3">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="600" y="325" />
              <mxPoint x="600" y="340" />
            </Array>
          </mxGeometry>
        </mxCell>

        <mxCell id="edge_t3_t4" value="ORM Queries &amp; Vector / File I/O" style="edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#7C3AED;strokeWidth=2;fontSize=11;fontFamily=Helvetica;fontColor=#5B21B6;endArrow=classic;startArrow=classic;" edge="1" parent="1" source="tier3" target="tier4">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="600" y="515" />
              <mxPoint x="600" y="530" />
            </Array>
          </mxGeometry>
        </mxCell>

      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
    return xml_content

def save_and_verify():
    xml_data = build_simplified_drawio_xml()
    ET.fromstring(xml_data)
    print("Simplified XML successfully validated via ElementTree parser!")

    workspace_path = r"c:\Users\SCROLL\Scrollix_AI_Architecture.drawio"
    downloads_path = r"C:\Users\vivek\Downloads\Scrollix_AI_Architecture.drawio"

    with open(workspace_path, "w", encoding="utf-8") as f:
        f.write(xml_data)
    print(f"Saved drawio file to workspace: {workspace_path}")

    with open(downloads_path, "w", encoding="utf-8") as f:
        f.write(xml_data)
    print(f"Saved drawio file to Downloads: {downloads_path}")

if __name__ == "__main__":
    save_and_verify()
