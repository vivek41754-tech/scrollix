import os
import time
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Ellipse, Rectangle

def create_staruml_usecase_diagram(output_paths):
    # Set up high-resolution canvas (300 DPI, publication quality)
    fig_w, fig_h = 25, 17.0
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    
    # Coordinate system: 0 to 100 on both axes
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Pure white canvas background (StarUML standard export)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    # Color Palette: Authentic StarUML Default Theme
    COLOR_BORDER = '#263238'       # Crisp dark charcoal
    COLOR_UC_FILL = '#FFFDE7'      # Soft warm cream / ivory (Signature StarUML use case color)
    COLOR_UC_SHADOW = '#E0E0E0'    # Clean subtle drop shadow
    COLOR_ACTOR = '#1A1A1A'        # Solid deep charcoal
    COLOR_LINE = '#37474F'         # Dark slate grey for actor associations
    COLOR_DEP = '#455A64'          # Slate grey for dependencies
    COLOR_TEXT = '#111111'         # Deep black for text
    COLOR_MUTED = '#455A64'        # Slate for stereotypes
    
    FONT_FAMILY = 'Segoe UI'       # Native Windows & StarUML font

    # =========================================================================
    # 1. SYSTEM BOUNDARY (Subject Frame - UML 2.5 / StarUML Style)
    # =========================================================================
    sys_x1, sys_y1 = 12.0, 3.5
    sys_w, sys_h = 76.0, 93.0
    
    # Main outer rectangle
    sys_rect = Rectangle(
        (sys_x1, sys_y1), sys_w, sys_h,
        facecolor='#FFFFFF', edgecolor=COLOR_BORDER,
        linewidth=1.8, zorder=1
    )
    ax.add_patch(sys_rect)

    # Full-width Top Subject Header Compartment (Clean StarUML Standard)
    hdr_h = 5.0
    hdr_y = sys_y1 + sys_h - hdr_h
    hdr_rect = Rectangle(
        (sys_x1, hdr_y), sys_w, hdr_h,
        facecolor='#ECEFF1', edgecolor=COLOR_BORDER,
        linewidth=1.6, zorder=2
    )
    ax.add_patch(hdr_rect)
    
    # Clean centered system title (No top-right clutter)
    ax.text(
        sys_x1 + sys_w / 2.0, hdr_y + hdr_h * 0.50,
        "«system»   Scrollix AI Core Platform",
        fontsize=19.0, fontweight='bold', fontfamily=FONT_FAMILY, color='#111111',
        ha='center', va='center', zorder=3
    )

    # =========================================================================
    # 2. ACTOR DRAWING FUNCTION (StarUML Stick Figure with Large Labels)
    # =========================================================================
    def draw_actor(x, y, name, subtitle=None):
        head_radius = 1.45
        head_cy = y + 3.1
        neck_y = head_cy - head_radius
        spine_len = 3.3
        crotch_y = neck_y - spine_len
        shoulder_y = neck_y - 1.0
        arm_half = 2.0
        leg_len = 3.5
        leg_half = 1.8
        foot_y = crotch_y - leg_len

        # Head (solid white fill, crisp dark outline)
        head = plt.Circle(
            (x, head_cy), head_radius,
            facecolor='#FFFFFF', edgecolor=COLOR_ACTOR,
            linewidth=2.3, zorder=5
        )
        ax.add_patch(head)
        
        # Spine
        ax.plot([x, x], [neck_y, crotch_y], color=COLOR_ACTOR, linewidth=2.3, solid_capstyle='round', zorder=5)
        # Arms
        ax.plot([x - arm_half, x + arm_half], [shoulder_y, shoulder_y], color=COLOR_ACTOR, linewidth=2.3, solid_capstyle='round', zorder=5)
        # Left Leg
        ax.plot([x, x - leg_half], [crotch_y, foot_y], color=COLOR_ACTOR, linewidth=2.3, solid_capstyle='round', zorder=5)
        # Right Leg
        ax.plot([x, x + leg_half], [crotch_y, foot_y], color=COLOR_ACTOR, linewidth=2.3, solid_capstyle='round', zorder=5)

        # Actor Labels (Large, Bold and Prominent)
        lbl_y = foot_y - 1.2
        ax.text(
            x, lbl_y, "«actor»",
            fontsize=13.0, fontfamily=FONT_FAMILY, color=COLOR_MUTED,
            ha='center', va='top', zorder=5
        )
        ax.text(
            x, lbl_y - 2.1, name,
            fontsize=18.5, fontweight='bold', fontfamily=FONT_FAMILY, color=COLOR_TEXT,
            ha='center', va='top', zorder=5
        )
        if subtitle:
            ax.text(
                x, lbl_y - 4.6, subtitle,
                fontsize=12.0, fontstyle='italic', fontfamily=FONT_FAMILY, color='#616161',
                ha='center', va='top', zorder=5
            )

        return (x, shoulder_y)

    # Actor coordinates (Customer left at Y=52, Merchant top-right at Y=67, Admin bottom-right at Y=20)
    actor_cust_pt  = draw_actor(5.8,  52.0, "Customer", "(Shopper / End User)")
    actor_merch_pt = draw_actor(94.2, 67.0, "Merchant", "(Store Owner)")
    actor_admin_pt = draw_actor(94.2, 20.0, "Administrator", "(System & Trust)")

    # =========================================================================
    # 3. USE CASES DEFINITION (Positions, Sizes, and Labels)
    # =========================================================================
    UC_W = 18.2
    UC_H = 6.0

    # Rows coordinated for optimal horizontal alignments
    # Row 1: Y = 86.5 (Customer Watch Video <--- YOLOv11 Detect) | (Merchant Register Store)
    # Row 2: Y = 72.5 (Customer Search <--- FAISS Vectors)       | (Merchant Manage Catalogue)
    # Row 3: Y = 58.5 (Customer Explore Map <--- Haversine)     | (Merchant Review Analytics)
    # Row 4: Y = 44.5 (Customer AI Assistant) | (Auto-Extract Embeddings <--- Merchant Upload Media)
    # Row 5: Y = 30.5 (Customer Log Interactions) | (Evaluate Risk Rules <--- Admin Trigger Fraud Scan)
    # Row 6: Y = 23.0 (Admin Review Flags)
    # Row 7: Y = 16.5 (Customer Review & Rating)
    # Row 8: Y = 15.5 (Admin Approve / Dismiss Flags)
    # Row 9: Y = 8.0  (Admin Monitor System Health)

    use_cases = {
        # --- LEFT COLUMN: Customer Direct Interactions (X = 24.5) ---
        'UC_C1': (24.5, 86.5, "Watch Video Feed &\nView Bounding Boxes", UC_W, UC_H),
        'UC_C2': (24.5, 72.5, "Search Products via\nText, Voice & Image", UC_W, UC_H),
        'UC_C3': (24.5, 58.5, "Explore Nearby Stores\non Interactive Map", UC_W, UC_H),
        'UC_C4': (24.5, 44.5, "Inquire with Grounded\nAI Shopping Assistant", UC_W, UC_H),
        'UC_C5': (24.5, 30.5, "Log Interactions\n(Views, Likes, Clicks)", UC_W, UC_H),
        'UC_C6': (24.5, 16.5, "Submit Product\nReview & Rating", UC_W, UC_H),

        # --- CENTER COLUMN: Subsystem & AI Compute Engines (X = 50.0) ---
        'UC_E1': (50.0, 86.5, "Detect Objects &\nApply NMS (YOLOv11)", UC_W, UC_H),
        'UC_E2': (50.0, 72.5, "Match 512-dim Vectors\nin FAISS (IndexFlatIP)", UC_W, UC_H),
        'UC_E3': (50.0, 58.5, "Compute Proximity\n(Haversine Spherical)", UC_W, UC_H),
        'UC_E4': (50.0, 44.5, "Auto-Extract 512-dim\nEmbeddings & Ingest", UC_W, UC_H),
        'UC_E5': (50.0, 30.5, "Evaluate Risk & Fraud\nAnomaly Rules (0–100)", UC_W, UC_H),

        # --- RIGHT COLUMN (TOP): Merchant Store Management (X = 75.5) ---
        'UC_M1': (75.5, 86.5, "Register & Update Store\nProfile with GPS", UC_W, UC_H),
        'UC_M2': (75.5, 72.5, "Manage Catalogue,\nPricing & Inventory", UC_W, UC_H),
        'UC_M3': (75.5, 58.5, "Review Store Analytics,\nCTR & Conversion", UC_W, UC_H),
        'UC_M4': (75.5, 44.5, "Upload Video Clip or\nProduct Photo Media", UC_W, UC_H),

        # --- RIGHT COLUMN (BOTTOM): Administrator Trust & Governance (X = 75.5) ---
        'UC_A1': (75.5, 30.5, "Trigger Automated\nFraud Audit Scan", UC_W, UC_H),
        'UC_A2': (75.5, 23.0, "Review Explainable\nSuspicion Flags", UC_W, UC_H),
        'UC_A3': (75.5, 15.5, "Approve or Dismiss\nFlagged Listings", UC_W, UC_H),
        'UC_A4': (75.5, 8.0,   "Monitor System Health,\nDatabase & FAISS Index", UC_W, UC_H)
    }

    # Render Use Cases
    uc_patches = {}
    for uc_id, (ux, uy, utext, uw, uh) in use_cases.items():
        # Drop shadow
        shadow = Ellipse(
            (ux + 0.35, uy - 0.35), uw, uh,
            facecolor=COLOR_UC_SHADOW, edgecolor='none', zorder=2
        )
        ax.add_patch(shadow)

        # Main Use Case Ellipse
        el = Ellipse(
            (ux, uy), uw, uh,
            facecolor=COLOR_UC_FILL,
            edgecolor=COLOR_BORDER,
            linewidth=1.6,
            zorder=3
        )
        ax.add_patch(el)
        uc_patches[uc_id] = (ux, uy, uw, uh)
        
        # Centered Text: 14.8 pt bold
        ax.text(
            ux, uy, utext,
            fontsize=14.8, fontweight='bold', fontfamily=FONT_FAMILY, color=COLOR_TEXT,
            ha='center', va='center', linespacing=1.20, zorder=4
        )

    # =========================================================================
    # 4. ACTOR ASSOCIATIONS (Solid Lines)
    # =========================================================================
    def draw_assoc(actor_pt, uc_id, side='left'):
        ux, uy, uw, uh = uc_patches[uc_id]
        if side == 'left':
            tx = ux - (uw / 2.0)
            ty = uy
            ax.plot([actor_pt[0] + 1.8, tx], [actor_pt[1], ty],
                    color=COLOR_LINE, linewidth=1.6, linestyle='-', zorder=2)
        else:
            tx = ux + (uw / 2.0)
            ty = uy
            ax.plot([actor_pt[0] - 1.8, tx], [actor_pt[1], ty],
                    color=COLOR_LINE, linewidth=1.6, linestyle='-', zorder=2)

    # Customer Associations (Clean fan from Y=52 to 86.5, 72.5, 58.5, 44.5, 30.5, 16.5)
    for ucid in ['UC_C1', 'UC_C2', 'UC_C3', 'UC_C4', 'UC_C5', 'UC_C6']:
        draw_assoc(actor_cust_pt, ucid, side='left')

    # Merchant Associations (Clean fan from Y=67 to 86.5, 72.5, 58.5, 44.5)
    for ucid in ['UC_M1', 'UC_M2', 'UC_M3', 'UC_M4']:
        draw_assoc(actor_merch_pt, ucid, side='right')

    # Administrator Associations (Clean fan from Y=20 to 30.5, 23.0, 15.5, 8.0)
    for ucid in ['UC_A1', 'UC_A2', 'UC_A3', 'UC_A4']:
        draw_assoc(actor_admin_pt, ucid, side='right')

    # =========================================================================
    # 5. DEPENDENCY RELATIONSHIPS («include» and «extend»)
    # =========================================================================
    def draw_dep(src_id, tgt_id, stereotype='«include»', src_side='right', tgt_side='left', bend=0.0):
        sx, sy, sw, sh = uc_patches[src_id]
        tx, ty, tw, th = uc_patches[tgt_id]
        
        x1 = sx + (sw / 2.0) if src_side == 'right' else sx - (sw / 2.0)
        y1 = sy
        x2 = tx - (tw / 2.0) if tgt_side == 'left' else tx + (tw / 2.0)
        y2 = ty
        
        if bend == 0.0:
            ax.annotate(
                '', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle="->,head_length=0.85,head_width=0.60",
                    color=COLOR_DEP,
                    linewidth=1.7,
                    linestyle=(0, (4, 3))
                ),
                zorder=2
            )
            mid_x = (x1 + x2) / 2.0
            mid_y = (y1 + y2) / 2.0
        else:
            rad = bend
            ax.annotate(
                '', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(
                    arrowstyle="->,head_length=0.85,head_width=0.60",
                    color=COLOR_DEP,
                    linewidth=1.7,
                    linestyle=(0, (4, 3)),
                    connectionstyle=f"arc3,rad={rad}"
                ),
                zorder=2
            )
            mid_x = (x1 + x2) / 2.0
            mid_y = (y1 + y2) / 2.0 + bend * 2.5

        # Stereotype Label (13.0 pt bold italic, crisp white background cutout)
        ax.text(
            mid_x, mid_y, stereotype,
            fontsize=13.0, fontweight='bold', fontstyle='italic', fontfamily=FONT_FAMILY, color=COLOR_MUTED,
            ha='center', va='center',
            bbox=dict(boxstyle='square,pad=0.25', facecolor='#FFFFFF', edgecolor='none'),
            zorder=4
        )

    # 1. Customer Subsystem Inclusions (All 3 perfectly horizontal!)
    draw_dep('UC_C1', 'UC_E1', '«include»', src_side='right', tgt_side='left')
    draw_dep('UC_C2', 'UC_E2', '«include»', src_side='right', tgt_side='left')
    draw_dep('UC_C3', 'UC_E3', '«include»', src_side='right', tgt_side='left')

    # 2. Merchant Media Ingestion Inclusion (Horizontally aligned at Y = 44.5!)
    draw_dep('UC_M4', 'UC_E4', '«include»', src_side='left', tgt_side='right')

    # 3. Admin Fraud Scan Inclusion (Horizontally aligned at Y = 30.5!)
    draw_dep('UC_A1', 'UC_E5', '«include»', src_side='left', tgt_side='right')

    # 4. Admin Extension: Approving/Dismissing extends Reviewing Flags
    draw_dep('UC_A3', 'UC_A2', '«extend»', src_side='left', tgt_side='left', bend=-0.32)

    plt.tight_layout()

    # Save to a temporary master file first, then safely copy to targets
    temp_master = r"c:\Users\SCROLL\temp_master_usecase.png"
    fig.savefig(temp_master, format='png', dpi=300, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close(fig)

    for p in output_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        for attempt in range(5):
            try:
                shutil.copyfile(temp_master, p)
                print(f"Exported clean diagram: {p}")
                break
            except Exception as e:
                time.sleep(0.5)
        else:
            print(f"Warning: Could not copy to {p} due to file lock: {e}")

    if os.path.exists(temp_master):
        os.remove(temp_master)

if __name__ == '__main__':
    targets = [
        r"C:\Users\vivek\Downloads\Scrollix_AI_UseCase_Diagram.png",
        r"c:\Users\SCROLL\Scrollix_AI_UseCase_Diagram.png"
    ]
    create_staruml_usecase_diagram(targets)
