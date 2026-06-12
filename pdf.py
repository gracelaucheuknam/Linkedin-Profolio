from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import math

W, H = 1080, 1080  # square for LinkedIn carousel (points ≈ pixels at 1:1 here)
OUTPUT = "/mnt/user-data/outputs/data_story_slides.pdf"

# ── Palette ──────────────────────────────────────────────────────────────────
BG_DARK   = HexColor("#0f1117")
BG_CARD   = HexColor("#1a1d27")
BG_CARD2  = HexColor("#141720")
BLUE      = HexColor("#378ADD")
BLUE_DIM  = HexColor("#1a3a5c")
TEAL      = HexColor("#1D9E75")
TEAL_DIM  = HexColor("#0d3b2c")
AMBER     = HexColor("#EF9F27")
AMBER_DIM = HexColor("#3d2a09")
CORAL     = HexColor("#D85A30")
CORAL_DIM = HexColor("#3d1a0c")
PURPLE    = HexColor("#7F77DD")
PURPLE_DIM= HexColor("#252050")
WHITE     = HexColor("#f0efe9")
GRAY      = HexColor("#5f5e5a")
GRAY_LIGHT= HexColor("#b4b2a9")

def style(size, color=WHITE, bold=False, align=TA_LEFT, leading=None):
    return ParagraphStyle(
        's', fontName='Helvetica-Bold' if bold else 'Helvetica',
        fontSize=size, textColor=color,
        alignment=align, leading=leading or size*1.35,
        wordWrap='CJK'
    )

def draw_para(c, text, x, y, w, sty):
    p = Paragraph(text, sty)
    pw, ph = p.wrap(w, 2000)
    p.drawOn(c, x, y - ph)
    return ph

def rounded_rect(c, x, y, w, h, r, fill_color, stroke_color=None, stroke_width=0):
    c.saveState()
    if stroke_color:
        c.setStrokeColor(stroke_color)
        c.setLineWidth(stroke_width)
    else:
        c.setStrokeColor(fill_color)
    c.setFillColor(fill_color)
    c.roundRect(x, y, w, h, r, fill=1, stroke=1 if stroke_color else 0)
    c.restoreState()

def accent_line(c, x, y, length, color, width=3):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x, y, x+length, y)
    c.restoreState()

def chip(c, x, y, text, fg, bg, font_size=22, pad_x=24, pad_h=14):
    c.saveState()
    p = Paragraph(text, style(font_size, fg, bold=True, align=TA_CENTER))
    tw, th = p.wrap(400, 100)
    rw = tw + pad_x*2
    rh = th + pad_h*2
    rounded_rect(c, x, y, rw, rh, rh/2, bg)
    p.drawOn(c, x+pad_x, y+pad_h)
    c.restoreState()
    return rw

def bar_h(c, x, y, val, max_val, bar_w, bar_h_px, fill, bg=BG_CARD2, label=None, val_label=None, label_color=GRAY_LIGHT):
    rounded_rect(c, x, y, bar_w, bar_h_px, bar_h_px/2, bg)
    filled_w = (val/max_val) * bar_w
    if filled_w > bar_h_px:
        rounded_rect(c, x, y, filled_w, bar_h_px, bar_h_px/2, fill)
    if label:
        c.saveState()
        c.setFont('Helvetica', 26)
        c.setFillColor(label_color)
        c.drawString(x, y + bar_h_px + 14, label)
        c.restoreState()
    if val_label:
        c.saveState()
        c.setFont('Helvetica-Bold', 26)
        c.setFillColor(fill)
        c.drawRightString(x + bar_w, y + bar_h_px + 14, val_label)
        c.restoreState()

def dot(c, x, y, r, color):
    c.saveState()
    c.setFillColor(color)
    c.circle(x, y, r, fill=1, stroke=0)
    c.restoreState()

def sparkline(c, points, x0, y0, width, height, color, fill_color=None):
    if len(points) < 2: return
    mn, mx = min(points), max(points)
    rng = mx - mn or 1
    xs = [x0 + i/(len(points)-1)*width for i in range(len(points))]
    ys = [y0 + (p-mn)/rng*height for p in points]
    if fill_color:
        c.saveState()
        c.setFillColor(fill_color)
        path = c.beginPath()
        path.moveTo(xs[0], y0)
        for xi, yi in zip(xs, ys):
            path.lineTo(xi, yi)
        path.lineTo(xs[-1], y0)
        path.close()
        c.drawPath(path, fill=1, stroke=0)
        c.restoreState()
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(4)
    p = c.beginPath()
    p.moveTo(xs[0], ys[0])
    for xi, yi in zip(xs[1:], ys[1:]):
        p.lineTo(xi, yi)
    c.drawPath(p, fill=0, stroke=1)
    c.restoreState()

def funnel_bar(c, x, y, w, h_bar, color, label, num, pct, dim_color):
    rounded_rect(c, x + (W - 80 - x - w)//2 + x, y, w, h_bar, 6, color)
    c.saveState()
    c.setFont('Helvetica-Bold', 28)
    c.setFillColor(WHITE)
    c.drawCentredString(x + (W - 80 - x - w)//2 + x + w/2, y + h_bar/2 - 10, num)
    c.setFont('Helvetica', 22)
    c.setFillColor(GRAY_LIGHT)
    c.drawString(60, y + h_bar/2 - 10, label)
    c.setFillColor(dim_color)
    c.drawRightString(W-60, y + h_bar/2 - 10, pct)
    c.restoreState()

# ── PAGE HELPERS ─────────────────────────────────────────────────────────────
def new_page(c):
    c.setFillColor(BG_DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)

def slide_number(c, n, total=7):
    c.saveState()
    c.setFont('Helvetica', 20)
    c.setFillColor(GRAY)
    c.drawRightString(W-50, 44, f"{n} / {total}")
    c.restoreState()

def bottom_bar(c, text="E-Commerce Analytics · FY 2024"):
    c.saveState()
    c.setFillColor(HexColor("#0a0c12"))
    c.rect(0, 0, W, 56, fill=1, stroke=0)
    c.setFont('Helvetica', 20)
    c.setFillColor(GRAY)
    c.drawString(60, 18, text)
    c.restoreState()

# ═════════════════════════════════════════════════════════════════════════════
#  SLIDES
# ═════════════════════════════════════════════════════════════════════════════
c = canvas.Canvas(OUTPUT, pagesize=(W, H))
c.setTitle("E-Commerce Data Story · FY 2024")

# ── SLIDE 1 · COVER ───────────────────────────────────────────────────────────
new_page(c)

# Background grid lines
c.saveState()
c.setStrokeColor(HexColor("#1e2130"))
c.setLineWidth(1)
for i in range(0, W, 90):
    c.line(i, 0, i, H)
for j in range(0, H, 90):
    c.line(0, j, W, j)
c.restoreState()

# Big accent circle
c.saveState()
c.setFillColor(HexColor("#0d1f35"))
c.circle(W*0.72, H*0.52, 320, fill=1, stroke=0)
c.setFillColor(BLUE_DIM)
c.circle(W*0.72, H*0.52, 220, fill=1, stroke=0)
c.setFillColor(BLUE)
c.setStrokeColor(BLUE)
c.setLineWidth(3)
c.circle(W*0.72, H*0.52, 145, fill=0, stroke=1)
c.restoreState()

# Central metric inside circle
c.saveState()
c.setFont('Helvetica-Bold', 88)
c.setFillColor(WHITE)
c.drawCentredString(W*0.72, H*0.52 - 24, "$4.2M")
c.setFont('Helvetica', 28)
c.setFillColor(BLUE)
c.drawCentredString(W*0.72, H*0.52 - 68, "FY 2024 Revenue")
c.restoreState()

# Left content
accent_line(c, 60, H-140, 80, BLUE, 4)
draw_para(c, "From Raw Data<br/>to Revenue Story", 60, H-165, 520,
          style(72, WHITE, bold=True, leading=84))
draw_para(c, "A data analyst's interactive portfolio —<br/>forecasting, SQL, and actionable insights.", 60, H-390, 480,
          style(28, GRAY_LIGHT, leading=40))

# Stat chips row
cx = 60
for txt, col in [("↑ 18.3% YoY", TEAL), ("38,490 Orders", BLUE), ("MAPE 4.2%", PURPLE)]:
    w = chip(c, cx, H-510, txt, col, HexColor("#0a0c12"), font_size=22, pad_x=20, pad_h=10)
    cx += w + 16

bottom_bar(c)
slide_number(c, 1)
c.showPage()

# ── SLIDE 2 · KPI OVERVIEW ────────────────────────────────────────────────────
new_page(c)
accent_line(c, 60, H-80, 60, BLUE, 3)
draw_para(c, "The numbers at a glance", 60, H-100, W-120,
          style(52, WHITE, bold=True))
draw_para(c, "FY 2024 · All regions combined", 60, H-180, 500,
          style(26, GRAY_LIGHT))

# 4 KPI cards 2×2
kpis = [
    ("$4.2M", "Total Revenue", "↑ 18.3% YoY", BLUE, BLUE_DIM),
    ("38,490", "Orders", "↑ 11.6% YoY", TEAL, TEAL_DIM),
    ("$109", "Avg Order Value", "↑ 6.0% YoY", PURPLE, PURPLE_DIM),
    ("12.4%", "Churn Rate", "↑ 1.1pp — watch this", CORAL, CORAL_DIM),
]
cw, ch = 460, 230
margin = 50
for i, (val, label, delta, col, dim) in enumerate(kpis):
    col_i = i % 2
    row_i = i // 2
    cx2 = 60 + col_i*(cw + margin)
    cy2 = H - 260 - row_i*(ch + margin) - ch
    rounded_rect(c, cx2, cy2, cw, ch, 16, BG_CARD, col, 1.5)
    # coloured left accent strip
    rounded_rect(c, cx2, cy2, 8, ch, 4, col)
    c.saveState()
    c.setFont('Helvetica-Bold', 62)
    c.setFillColor(col)
    c.drawString(cx2+28, cy2+ch-88, val)
    c.setFont('Helvetica', 26)
    c.setFillColor(GRAY_LIGHT)
    c.drawString(cx2+28, cy2+ch-124, label)
    c.setFont('Helvetica', 22)
    c.setFillColor(col if 'YoY' in delta else CORAL)
    c.drawString(cx2+28, cy2+22, delta)
    c.restoreState()

# small sparkline background in cards
monthly = [280,305,320,290,350,410,445,470,430,490,520,480]
for i, (_, _, _, col, _) in enumerate(kpis):
    col_i = i % 2; row_i = i // 2
    cx2 = 60 + col_i*(cw+margin)
    cy2 = H - 260 - row_i*(ch+margin) - ch
    sparkline(c, monthly, cx2+cw-180, cy2+20, 160, 60,
              HexColor(f"#{col.hexval()[2:]}").clone() if hasattr(col,'clone') else col,
              fill_color=HexColor("#00000000"))

bottom_bar(c)
slide_number(c, 2)
c.showPage()

# ── SLIDE 3 · REGIONAL GROWTH ─────────────────────────────────────────────────
new_page(c)
accent_line(c, 60, H-80, 60, TEAL, 3)
draw_para(c, "APAC is pulling ahead", 60, H-100, W-120,
          style(58, WHITE, bold=True))
draw_para(c, "YoY revenue growth by region — and why it matters", 60, H-185, W-120,
          style(27, GRAY_LIGHT))

regions = [
    ("APAC",     1600, 24.1, BLUE),
    ("EMEA",     1400, 15.0, TEAL),
    ("Americas", 1200, 12.0, PURPLE),
]
bar_start_y = H - 280
bw = W - 200
bh_px = 80
gap = 50
for region, val, yoy, col in regions:
    bar_h(c, 100, bar_start_y, val, 1800, bw, bh_px, col, BG_CARD2,
          label=region, val_label=f"${val/1000:.1f}M  ↑{yoy}%",
          label_color=GRAY_LIGHT)
    bar_start_y -= (bh_px + gap + 30)

# insight box
iy = bar_start_y - 60
rounded_rect(c, 60, iy, W-120, 150, 12, HexColor("#0d1f35"), BLUE, 1)
c.saveState()
c.setFont('Helvetica-Bold', 24)
c.setFillColor(BLUE)
c.drawString(84, iy+100, "KEY INSIGHT")
c.setFont('Helvetica', 24)
c.setFillColor(WHITE)
c.drawString(84, iy+64, "APAC's AOV ($113) beats global average ($109) — growth is quality-driven,")
c.drawString(84, iy+34, "not just volume. Expand premium SKUs in APAC to compound this advantage.")
c.restoreState()

bottom_bar(c)
slide_number(c, 3)
c.showPage()

# ── SLIDE 4 · CONVERSION FUNNEL ───────────────────────────────────────────────
new_page(c)
accent_line(c, 60, H-80, 60, AMBER, 3)
draw_para(c, "$380K sitting in<br/>the checkout gap", 60, H-100, W-120,
          style(58, WHITE, bold=True, leading=70))
draw_para(c, "Conversion funnel · 520K sessions → 38K purchases", 60, H-230, W-120,
          style(26, GRAY_LIGHT))

funnel_data = [
    ("Sessions",     "520,000", "100%",   W-120, BLUE),
    ("Product view", "210,000",  "40%",   (W-120)*0.78, HexColor("#1a6aad")),
    ("Add to cart",  " 96,000",  "18%",   (W-120)*0.56, TEAL),
    ("Checkout",     " 63,000",  "12%",   (W-120)*0.38, AMBER),
    ("Purchase",     " 38,490",   "7.4%", (W-120)*0.22, CORAL),
]
fy = H - 290
fh = 72
fgap = 16
for label, num, pct, fw, col in funnel_data:
    fx = 60 + (W-120-fw)//2
    rounded_rect(c, fx, fy, fw, fh, 8, col)
    c.saveState()
    c.setFont('Helvetica-Bold', 28)
    c.setFillColor(WHITE)
    c.drawCentredString(fx + fw/2, fy + fh/2 - 10, num)
    c.setFont('Helvetica', 22)
    c.setFillColor(GRAY_LIGHT)
    c.drawString(60, fy + fh/2 - 8, label)
    c.setFont('Helvetica-Bold', 24)
    c.setFillColor(col)
    c.drawRightString(W-60, fy + fh/2 - 8, pct)
    c.restoreState()
    fy -= (fh + fgap)

# big callout
iy = fy - 30
rounded_rect(c, 60, iy, W-120, 120, 12, AMBER_DIM, AMBER, 1.5)
c.saveState()
c.setFont('Helvetica-Bold', 56)
c.setFillColor(AMBER)
c.drawString(84, iy+50, "34% drop at checkout  →  biggest lever to pull")
c.setFont('Helvetica', 24)
c.setFillColor(GRAY_LIGHT)
c.drawString(84, iy+18, "A/B test on checkout UX already recovered 8pp in Q4. Scale it.")
c.restoreState()

bottom_bar(c)
slide_number(c, 4)
c.showPage()

# ── SLIDE 5 · COHORT RETENTION ────────────────────────────────────────────────
new_page(c)
accent_line(c, 60, H-80, 60, PURPLE, 3)
draw_para(c, "Retention is improving —<br/>and we know why", 60, H-100, W-120,
          style(56, WHITE, bold=True, leading=68))
draw_para(c, "Cohort M1 retention by signup month", 60, H-218, W-120,
          style(26, GRAY_LIGHT))

cohorts = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
ret = [
    [100, 68, 54, 48, 42, 38],
    [100, 71, 57, 50, 44],
    [100, 69, 55, 49],
    [100, 72, 58],
    [100, 74],
    [100],
]

def ret_color(v):
    if v == 100: return BLUE
    if v >= 70:  return TEAL
    if v >= 55:  return HexColor("#3aad82")
    if v >= 45:  return AMBER
    if v >= 35:  return CORAL
    return HexColor("#a32d2d")

cell_w, cell_h = 130, 60
start_x = 160
start_y = H - 280
headers = ["M0","M1","M2","M3","M4","M5"]

# header row
c.saveState()
c.setFont('Helvetica-Bold', 22)
c.setFillColor(GRAY)
for j, h in enumerate(headers):
    c.drawCentredString(start_x + j*cell_w + cell_w/2, start_y + cell_h + 14, h)
c.restoreState()

for i, (coh, row) in enumerate(zip(cohorts, ret)):
    cy3 = start_y - i*(cell_h+8)
    c.saveState()
    c.setFont('Helvetica', 24)
    c.setFillColor(GRAY_LIGHT)
    c.drawRightString(start_x - 16, cy3 + cell_h/2 - 8, coh)
    c.restoreState()
    for j in range(6):
        cx3 = start_x + j*cell_w
        if j < len(row):
            v = row[j]
            col = ret_color(v)
            rounded_rect(c, cx3+3, cy3+3, cell_w-6, cell_h-6, 8, col)
            c.saveState()
            c.setFont('Helvetica-Bold', 26)
            c.setFillColor(WHITE)
            c.drawCentredString(cx3+cell_w/2, cy3+cell_h/2-9, f"{v}%")
            c.restoreState()
        else:
            rounded_rect(c, cx3+3, cy3+3, cell_w-6, cell_h-6, 8, BG_CARD2)
            c.saveState()
            c.setFont('Helvetica', 22)
            c.setFillColor(GRAY)
            c.drawCentredString(cx3+cell_w/2, cy3+cell_h/2-8, "—")
            c.restoreState()

# Arrow annotation
ay = start_y - 1*(cell_h+8)
c.saveState()
c.setStrokeColor(PURPLE)
c.setLineWidth(2)
c.setDash([6,4])
c.line(start_x + 1*cell_w + cell_w/2, start_y+4,
       start_x + 1*cell_w + cell_w/2, ay + cell_h + 4)
c.restoreState()
c.saveState()
c.setFont('Helvetica-Bold', 22)
c.setFillColor(PURPLE)
c.drawString(start_x + 1*cell_w + cell_w + 8, start_y - 22, "68% → 74%")
c.setFont('Helvetica', 20)
c.setFillColor(GRAY_LIGHT)
c.drawString(start_x + 1*cell_w + cell_w + 8, start_y - 48, "after onboarding redesign")
c.restoreState()

# insight
iy2 = start_y - 6*(cell_h+8) - 36
rounded_rect(c, 60, iy2, W-120, 110, 12, PURPLE_DIM, PURPLE, 1)
c.saveState()
c.setFont('Helvetica-Bold', 24)
c.setFillColor(PURPLE)
c.drawString(84, iy2+72, "Every 1pp gain in M1 retention = compounding revenue across 12 purchase cycles.")
c.setFont('Helvetica', 23)
c.setFillColor(GRAY_LIGHT)
c.drawString(84, iy2+36, "Target: 75% by Q1 2025.  Current trajectory is on track.")
c.restoreState()

bottom_bar(c)
slide_number(c, 5)
c.showPage()

# ── SLIDE 6 · FORECAST ────────────────────────────────────────────────────────
new_page(c)
accent_line(c, 60, H-80, 60, CORAL, 3)
draw_para(c, "Where are we headed?", 60, H-100, W-120,
          style(58, WHITE, bold=True))
draw_para(c, "FY 2025 revenue forecast · Seasonal decomposition model", 60, H-185, W-120,
          style(26, GRAY_LIGHT))

# Chart area
chart_x, chart_y = 60, 140
chart_w, chart_h = W-120, 500

rounded_rect(c, chart_x, chart_y, chart_w, chart_h, 12, BG_CARD)

# Grid lines
c.saveState()
c.setStrokeColor(HexColor("#1e2130"))
c.setLineWidth(1)
for i in range(5):
    gy = chart_y + i*(chart_h//5) + chart_h//10
    c.line(chart_x+60, gy, chart_x+chart_w-20, gy)
c.restoreState()

# Actual 12 months
actual = [280,305,320,290,350,410,445,470,430,490,520,480]
# Forecast 12 months (seasonal)
forecast_base = 480
seasonal_f = [0.93,0.96,0.98,0.95,1.02,1.08,1.12,1.15,1.08,1.14,1.18,1.12]
forecast = [round(forecast_base*(1+0.02*i)*seasonal_f[i%12]) for i in range(1,13)]
upper = [v+v*0.07 for v in forecast]
lower = [v-v*0.07 for v in forecast]

all_vals = actual + upper
mn_v, mx_v = 200, 700

def to_y(v):
    return chart_y + 30 + (v - mn_v)/(mx_v - mn_v)*(chart_h - 60)

def to_x(i, total=24):
    return chart_x + 60 + i/(total-1)*(chart_w-80)

# Confidence band
c.saveState()
c.setFillColor(HexColor("#2a1f5c"))
path = c.beginPath()
path.moveTo(to_x(12), to_y(upper[0]))
for i,v in enumerate(upper):
    path.lineTo(to_x(12+i), to_y(v))
for i,v in enumerate(reversed(lower)):
    path.lineTo(to_x(12+len(lower)-1-i), to_y(v))
path.close()
c.drawPath(path, fill=1, stroke=0)
c.restoreState()

# Actual line
c.saveState()
c.setStrokeColor(BLUE)
c.setLineWidth(4)
path = c.beginPath()
path.moveTo(to_x(0), to_y(actual[0]))
for i,v in enumerate(actual):
    path.lineTo(to_x(i), to_y(v))
c.drawPath(path, fill=0, stroke=1)
c.restoreState()

# Forecast line (dashed purple)
c.saveState()
c.setStrokeColor(PURPLE)
c.setLineWidth(3)
c.setDash([8,5])
path = c.beginPath()
path.moveTo(to_x(11), to_y(actual[-1]))
for i,v in enumerate(forecast):
    path.lineTo(to_x(12+i), to_y(v))
c.drawPath(path, fill=0, stroke=1)
c.restoreState()

# Month labels
months_all = ["J","F","M","A","M","J","J","A","S","O","N","D",
              "J","F","M","A","M","J","J","A","S","O","N","D"]
c.saveState()
c.setFont('Helvetica', 18)
c.setFillColor(GRAY)
for i, lbl in enumerate(months_all):
    c.drawCentredString(to_x(i), chart_y+12, lbl)
c.restoreState()

# Year labels
c.saveState()
c.setFont('Helvetica-Bold', 22)
c.setFillColor(BLUE)
c.drawCentredString(to_x(6), chart_y + chart_h - 24, "2024  (actual)")
c.setFillColor(PURPLE)
c.drawCentredString(to_x(18), chart_y + chart_h - 24, "2025  (forecast)")
c.restoreState()

# Vertical divider
c.saveState()
c.setStrokeColor(GRAY)
c.setLineWidth(1.5)
c.setDash([4,3])
c.line(to_x(11.5), chart_y+40, to_x(11.5), chart_y+chart_h-40)
c.restoreState()

# 3 scenario chips
scenarios = [("Bear  –1%/mo  →  $4.6M", CORAL), ("Base  +2%/mo  →  $5.1M", BLUE), ("Bull  +5%/mo  →  $5.9M", TEAL)]
sx = 60
for txt, col in scenarios:
    sw = chip(c, sx, chart_y - 58, txt, col, BG_CARD2, font_size=21, pad_x=18, pad_h=9)
    sx += sw + 12

bottom_bar(c, "Seasonal decomp · MAPE 4.2% · 95% CI shown")
slide_number(c, 6)
c.showPage()

# ── SLIDE 7 · RFM + CALL TO ACTION ───────────────────────────────────────────
new_page(c)
accent_line(c, 60, H-80, 60, AMBER, 3)
draw_para(c, "Know your customers.<br/>Act on the segments.", 60, H-100, W-120,
          style(56, WHITE, bold=True, leading=68))
draw_para(c, "RFM segmentation · 38,490 customers ranked by Recency · Frequency · Monetary value", 60, H-225,
          W-120, style(23, GRAY_LIGHT))

segments = [
    ("Champions",       6928,  "$458", 12,  BLUE,   "52% of revenue"),
    ("Loyal",           11540, "$234", 28,  TEAL,   "High frequency"),
    ("New customers",   8260,  "$112", 8,   PURPLE, "Recently acquired"),
    ("At risk",         2412,  "$318", 94,  CORAL,  "↑ Priority win-back"),
]
sw2 = (W - 120 - 30) // 2
sh = 200
for i, (name, cust, ltv, days, col, note) in enumerate(segments):
    ci = i % 2; ri = i // 2
    sx2 = 60 + ci*(sw2+30)
    sy2 = H - 290 - ri*(sh+20)
    rounded_rect(c, sx2, sy2, sw2, sh, 14, BG_CARD, col, 1.5)
    rounded_rect(c, sx2, sy2+sh-8, sw2, 8, 8, col)
    c.saveState()
    c.setFont('Helvetica-Bold', 30)
    c.setFillColor(WHITE)
    c.drawString(sx2+20, sy2+sh-58, name)
    c.setFont('Helvetica', 22)
    c.setFillColor(GRAY_LIGHT)
    c.drawString(sx2+20, sy2+sh-90, f"{cust:,} customers · Avg LTV {ltv}")
    c.setFont('Helvetica', 20)
    c.setFillColor(GRAY)
    c.drawString(sx2+20, sy2+sh-118, f"Avg {days} days since last order")
    c.setFont('Helvetica-Bold', 22)
    c.setFillColor(col)
    c.drawString(sx2+20, sy2+22, note)
    c.restoreState()

# Final CTA
cta_y = H - 290 - 2*(sh+20) - 50
rounded_rect(c, 60, cta_y, W-120, 140, 14, HexColor("#0a0c12"), BLUE, 1)

c.saveState()
c.setFont('Helvetica-Bold', 32)
c.setFillColor(WHITE)
c.drawCentredString(W/2, cta_y+90, "Like this kind of analysis?")
c.setFont('Helvetica', 26)
c.setFillColor(BLUE)
c.drawCentredString(W/2, cta_y+52, "View the full interactive dashboard  →  github.com/your-username/ecommerce-analytics")
c.setFont('Helvetica', 22)
c.setFillColor(GRAY_LIGHT)
c.drawCentredString(W/2, cta_y+22, "SQL · Forecasting · Cohort Analysis · RFM · A/B Testing")
c.restoreState()

bottom_bar(c)
slide_number(c, 7)
c.showPage()

c.save()
print("PDF saved to", OUTPUT)
