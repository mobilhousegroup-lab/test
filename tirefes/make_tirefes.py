"""車検のコバック「冬のタイヤ交換祭」SNS画像生成
出典: https://www.mobilhouse.co.jp/news/20260915-1173/
使い方: python3 make_tirefes.py <出力ディレクトリ>
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random, sys, os

F = "/usr/share/fonts/opentype/noto/"
def font(w, s): return ImageFont.truetype(F + f"NotoSansCJK-{w}.ttc", s, index=0)

NAVY = (31, 56, 100); DEEP = (10, 22, 48); RED = (215, 25, 35); YEL = (255, 204, 0)
WHITE = (255, 255, 255); ICE = (170, 215, 255); DARK = (8, 16, 36)

def tsize(d, t, f, sw=0):
    b = d.textbbox((0, 0), t, font=f, stroke_width=sw); return b, b[2] - b[0], b[3] - b[1]

def text_c(d, cx, y, t, f, fill, sw=0, sf=None):
    """cxを中心、yを文字の上端としてテキストを置く"""
    b, w, h = tsize(d, t, f, sw)
    d.text((cx - w / 2 - b[0], y - b[1]), t, font=f, fill=fill, stroke_width=sw, stroke_fill=sf)
    return h

# ---------- 背景 ----------
def snowflake(g, x, y, r, col, w):
    for i in range(6):
        a = math.pi / 3 * i
        ex, ey = x + r * math.cos(a), y + r * math.sin(a)
        g.line((x, y, ex, ey), fill=col, width=w)
        for k in (0.55,):
            mx, my = x + r * k * math.cos(a), y + r * k * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.pi / 4
                g.line((mx, my, mx + r * 0.3 * math.cos(b), my + r * 0.3 * math.sin(b)), fill=col, width=w)

def tire(g, cx, cy, r):
    g.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(25, 25, 30, 255))
    for i in range(56):
        a = 2 * math.pi * i / 56; w = 0.04
        r1, r2 = r * 0.86, r * 0.99
        g.polygon([(cx + r1 * math.cos(a - w), cy + r1 * math.sin(a - w)), (cx + r2 * math.cos(a - w + .02), cy + r2 * math.sin(a - w + .02)),
                   (cx + r2 * math.cos(a + w + .02), cy + r2 * math.sin(a + w + .02)), (cx + r1 * math.cos(a + w), cy + r1 * math.sin(a + w))], fill=(58, 58, 66, 255))
    for rr, c in ((0.80, (40, 40, 46)), (0.62, (185, 190, 200)), (0.56, (120, 126, 138))):
        g.ellipse((cx - r * rr, cy - r * rr, cx + r * rr, cy + r * rr), fill=c + (255,))
    for i in range(5):
        a = 2 * math.pi * i / 5 - math.pi / 2
        g.line((cx, cy, cx + r * .55 * math.cos(a), cy + r * .55 * math.sin(a)), fill=(200, 205, 215, 255), width=int(r * .16))
    g.ellipse((cx - r * .16, cy - r * .16, cx + r * .16, cy + r * .16), fill=(210, 214, 222, 255))
    g.ellipse((cx - r * .07, cy - r * .07, cx + r * .07, cy + r * .07), fill=(90, 95, 105, 255))

def background(W, H, seed=1, with_tire=True):
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line((0, y, W, y), fill=tuple(int(NAVY[i] * (1 - t) + DEEP[i] * t) for i in range(3)))
    im = im.convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    cx, cy = W / 2, H * 0.22
    for i in range(0, 28, 2):
        a1, a2 = 2 * math.pi * i / 28, 2 * math.pi * (i + 1) / 28
        od.polygon([(cx, cy), (cx + 3000 * math.cos(a1), cy + 3000 * math.sin(a1)), (cx + 3000 * math.cos(a2), cy + 3000 * math.sin(a2))], fill=(255, 255, 255, 12))
    random.seed(seed)
    for _ in range(26):
        x, y = random.randint(0, W), random.randint(0, H); r = random.randint(10, 34)
        snowflake(od, x, y, r, ICE + (random.randint(60, 140),), max(2, r // 9))
    im = Image.alpha_composite(im, ov)
    if with_tire:
        tl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); tire(ImageDraw.Draw(tl), int(W * 0.93), int(H * 0.06), int(W * 0.24))
        tl.putalpha(tl.getchannel("A").point(lambda a: int(a * 0.55)))
        im = Image.alpha_composite(im, tl)
        tl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); tire(ImageDraw.Draw(tl), int(W * 0.04), int(H * 0.50), int(W * 0.17))
        tl.putalpha(tl.getchannel("A").point(lambda a: int(a * 0.35)))
        im = Image.alpha_composite(im, tl)
    return im

# ---------- ブロック(高さを先に計算→余白を均等配分) ----------
class Block:
    def __init__(self, h, fn): self.h, self.fn = h, fn

def B_pill(d, W, t, f, bg, fg, padx=50, pady=18):
    b, w, h = tsize(d, t, f)
    def draw(d, y):
        d.rounded_rectangle(((W - w) / 2 - padx, y, (W + w) / 2 + padx, y + h + pady * 2), radius=(h + pady * 2) // 2, fill=bg)
        text_c(d, W / 2, y + pady, t, f, fg)
    return Block(h + pady * 2, draw)

def B_text(d, W, t, f, fill, sw=0, sf=None):
    b, w, h = tsize(d, t, f, sw)
    return Block(h, lambda d, y: text_c(d, W / 2, y, t, f, fill, sw, sf))

def B_band(d, W, t, f, bg, fg, pady=22):
    b, w, h = tsize(d, t, f)
    def draw(d, y):
        d.rectangle((0, y, W, y + h + pady * 2), fill=bg); text_c(d, W / 2, y + pady, t, f, fg)
    return Block(h + pady * 2, draw)

def B_price(d, W, big):
    """「作業工賃 1台」+ 500円(税込) ワンコイン"""
    lf = font("Bold", 50 if big else 44)
    nf = font("Black", 300 if big else 250); yf = font("Black", 120 if big else 100); tf = font("Black", 40 if big else 36)
    _, lw, lh = tsize(d, "タイヤ交換 作業工賃 1台", lf)
    nb, nw, nh = tsize(d, "500", nf, 12); yb, yw, yh = tsize(d, "円", yf, 8)
    tb, tw, th = tsize(d, "税込", tf)
    gap = 26
    cw = th + 40  # 税込バッジの直径
    total = cw + 18 + nw + 10 + yw
    H = lh + gap + nh
    def draw(d, y):
        text_c(d, W / 2, y, "タイヤ交換 作業工賃 1台", lf, WHITE)
        ny = y + lh + gap
        x = (W - total) / 2
        # 税込バッジ(丸)
        by = ny + nh - cw - 10
        d.ellipse((x, by, x + cw, by + cw), fill=RED, outline=WHITE, width=4)
        text_c(d, x + cw / 2, by + (cw - th) / 2, "税込", tf, WHITE)
        x += cw + 18
        d.text((x - nb[0], ny - nb[1]), "500", font=nf, fill=YEL, stroke_width=12, stroke_fill=RED)
        x += nw + 10
        # 「円」は数字のベースラインに揃える
        d.text((x - yb[0], ny + nh - yh - yb[1]), "円", font=yf, fill=YEL, stroke_width=8, stroke_fill=RED)
    return Block(H, draw)

def B_chips(d, W, items, f, h=96, mx=60, gap=22, fill=DARK, outline=YEL, fg=WHITE):
    n = len(items); w = (W - 2 * mx - gap * (n - 1)) / n
    def draw(d, y):
        for i, t in enumerate(items):
            x0 = mx + i * (w + gap)
            d.rounded_rectangle((x0, y, x0 + w, y + h), radius=18, fill=fill, outline=outline, width=5)
            b, tw, th = tsize(d, t, f)
            d.text((x0 + (w - tw) / 2 - b[0], y + (h - th) / 2 - b[1]), t, font=f, fill=fg)
    return Block(h, draw)

def B_table(d, W, rows, kf, vf, mx=60, rowh=96, kw=250):
    def draw(d, y):
        for i, (k, v) in enumerate(rows):
            y0 = y + i * (rowh + 12)
            d.rounded_rectangle((mx, y0, W - mx, y0 + rowh), radius=16, fill=WHITE)
            d.rounded_rectangle((mx, y0, mx + kw, y0 + rowh), radius=16, fill=NAVY)
            d.rectangle((mx + kw - 16, y0, mx + kw, y0 + rowh), fill=NAVY)
            b, tw, th = tsize(d, k, kf); d.text((mx + (kw - tw) / 2 - b[0], y0 + (rowh - th) / 2 - b[1]), k, font=kf, fill=WHITE)
            b, tw, th = tsize(d, v, vf); d.text((mx + kw + 30 - b[0], y0 + (rowh - th) / 2 - b[1]), v, font=vf, fill=NAVY)
    return Block(len(rows) * (rowh + 12) - 12, draw)

def B_card(d, W, title, lines, tf, lf, mx=60, pad=34, lgap=18, title_bg=RED):
    _, _, th = tsize(d, title, tf)
    hs = [tsize(d, l, lf)[2] for l in lines]
    H = th + pad * 2 + pad + sum(hs) + lgap * (len(lines) - 1) + pad
    def draw(d, y):
        d.rounded_rectangle((mx, y, W - mx, y + H), radius=22, fill=WHITE)
        d.rounded_rectangle((mx, y, W - mx, y + th + pad * 2), radius=22, fill=title_bg)
        d.rectangle((mx, y + th + pad, W - mx, y + th + pad * 2), fill=title_bg)
        text_c(d, W / 2, y + pad, title, tf, WHITE)
        yy = y + th + pad * 3
        for l, h in zip(lines, hs):
            b = d.textbbox((0, 0), l, font=lf); d.text((mx + 40 - b[0], yy - b[1]), l, font=lf, fill=NAVY); yy += h + lgap
    return Block(H, draw)

def B_footer(d, W, big):
    hf = font("Bold", 34 if big else 31); tf = font("Black", 42 if big else 38); sf = font("Medium", 26 if big else 24)
    stores = [("車検のコバック 富山掛尾店", "076-423-2227", "定休日：水曜日"),
              ("車検のコバック 富山西店", "0120-589-418", "定休日：日曜日・祝日")]
    H = 200 if big else 182
    def draw(d, y):
        d.rectangle((0, y, W, y + H), fill=WHITE)
        for i, (n, tel, off) in enumerate(stores):
            cx = W / 4 + i * W / 2
            text_c(d, cx, y + 30, n, hf, NAVY)
            text_c(d, cx, y + (88 if big else 80), "TEL " + tel, tf, RED)
            text_c(d, cx, y + (152 if big else 138), off, sf, (90, 90, 90))
        d.line((W / 2, y + 26, W / 2, y + H - 26), fill=(200, 200, 200), width=3)
    return Block(H, draw)

def layout(im, blocks, top, bottom, footer=None, max_gap=70):
    """blocksをtop〜bottomの範囲に均等配置。footerは最下部に固定"""
    d = ImageDraw.Draw(im)
    if footer:
        footer.fn(d, bottom - footer.h); bottom -= footer.h
    total = sum(b.h for b in blocks)
    gap = (bottom - top - total) / (len(blocks) + 1)
    assert gap > 8, f"内容がはみ出しています gap={gap:.0f}"
    gap = min(gap, max_gap)
    y = top + (bottom - top - total - gap * (len(blocks) - 1)) / 2
    for b in blocks:
        b.fn(d, y); y += b.h + gap
    return im

# ---------- スライド ----------
def slide_main(W, H, tall):
    im = background(W, H, 1); d = ImageDraw.Draw(im); big = tall
    blocks = [
        B_pill(d, W, "11/1(日)〜12/15(火) 開催中！", font("Black", 50 if big else 44), RED, WHITE),
        B_text(d, W, "車検のコバック", font("Bold", 52 if big else 44), WHITE),
        B_text(d, W, "冬のタイヤ交換祭", font("Black", 120 if big else 112), WHITE, 8, NAVY),
        B_price(d, W, big),
        B_band(d, W, "衝撃のワンコイン！", font("Black", 64 if big else 54), YEL, RED, pady=18),
        B_chips(d, W, ["1日5台限定", "完全予約制"], font("Black", 48 if big else 42), h=110 if big else 96, mx=100, gap=40),
        B_text(d, W, "※当店を初めてご利用のお車限定。その他条件あり", font("Medium", 32 if big else 28), ICE),
    ]
    top, bottom = (150, 1720) if tall else (40, H)
    return layout(im, blocks, top, bottom, B_footer(d, W, big), max_gap=60)

def slide_detail(W, H, tall):
    im = background(W, H, 2, with_tire=False); d = ImageDraw.Draw(im); big = tall
    kf = font("Bold", 38 if big else 34); vf = font("Bold", 40 if big else 36)
    blocks = [
        B_text(d, W, "冬のタイヤ交換祭", font("Black", 96 if big else 84), YEL, 6, RED),
        B_text(d, W, "ご予約前にご確認ください", font("Bold", 44 if big else 38), WHITE),
        B_table(d, W, [("開催期間", "11/1(日)〜12/15(火)"), ("作業工賃", "1台 税込500円"),
                       ("受付時間", "10:00〜12:00／13:00〜16:00"), ("限定台数", "1日5台限定（完全予約制）")],
                kf, vf, rowh=100 if big else 88, kw=230),
        B_card(d, W, "ご利用条件", [
            "✓ 当店を初めてご利用いただくお車限定",
            "✓ 完全予約制（予約なしは受付できません）",
            "✓ ホイール付きスタッドレスをお持ち込み",
            "× 輸入車・18インチ以上・同業他社様・",
            "　 他社リース契約車両は対象外",
        ], font("Black", 42 if big else 38), font("Bold", 34 if big else 31), pad=26 if big else 22, lgap=20 if big else 14),
    ]
    top, bottom = (150, 1720) if tall else (40, H)
    return layout(im, blocks, top, bottom, B_footer(d, W, big), max_gap=56)

def slide_check(W, H, tall):
    im = background(W, H, 3); d = ImageDraw.Draw(im); big = tall
    blocks = [
        B_text(d, W, "そのスタッドレス", font("Black", 92 if big else 80), WHITE, 6, NAVY),
        B_text(d, W, "今年も使えますか？", font("Black", 92 if big else 80), YEL, 6, RED),
        B_band(d, W, "交換予約日の前に【無料】でチェック！", font("Black", 50 if big else 44), WHITE, RED, pady=20),
        B_chips(d, W, ["残り溝を測定", "ゴムの硬さを確認"], font("Black", 44 if big else 40), h=110 if big else 96, mx=70, gap=30),
        B_card(d, W, "タイヤだけ店頭へお持ち込みOK", [
            "プロの整備士が専用ゲージで残り溝を測り、",
            "ゴムの硬度もチェック。「今年も安心して",
            "走れる状態か」をアドバイスします。",
        ], font("Black", 42 if big else 38), font("Bold", 34 if big else 31), title_bg=NAVY, pad=26 if big else 22),
        B_text(d, W, "当日になって使えないと分かると大変です💦", font("Bold", 36 if big else 32), ICE) if False else
        B_text(d, W, "当日「使えない…」とならないように、お早めに！", font("Bold", 36 if big else 31), ICE),
    ]
    top, bottom = (150, 1720) if tall else (40, H)
    return layout(im, blocks, top, bottom, B_footer(d, W, big), max_gap=60)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    for name, fn in (("1_main", slide_main), ("2_detail", slide_detail), ("3_check", slide_check)):
        fn(1080, 1350, False).convert("RGB").save(f"{out}/insta_{name}.jpg", quality=95)
        fn(1080, 1920, True).convert("RGB").save(f"{out}/tiktok_{name}.jpg", quality=95)
        print("ok", name)
