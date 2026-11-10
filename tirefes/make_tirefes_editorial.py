"""冬のタイヤ交換祭 エディトリアル版バナー（ミニマル・モダン）
使い方: python3 make_tirefes_editorial.py <出力ディレクトリ>
2倍サイズで描画して縮小し、細い線をなめらかにしている。
"""
from PIL import Image, ImageDraw, ImageFont
import math, sys, os

S = 2  # supersampling
NF = "/usr/share/fonts/opentype/noto/"; IF = "/usr/share/fonts/opentype/inter/"
def sans(w, s): return ImageFont.truetype(NF + f"NotoSansCJK-{w}.ttc", s * S, index=0)
def serif(w, s): return ImageFont.truetype(NF + f"NotoSerifCJK-{w}.ttc", s * S, index=0)
def inter(w, s): return ImageFont.truetype(IF + f"Inter-{w}.otf", s * S)

BG = (244, 243, 240)      # ウォームライトグレー
NAVY = (28, 42, 58)       # 深いネイビー
GREY = (112, 118, 126)    # 補足テキスト
LINE = (205, 205, 200)    # 罫線
GOLD = (176, 141, 87)     # 落ち着いたゴールド（アクセント1色のみ）

def T(d, x, y, t, f, fill, track=0, anchor="l"):
    """x,yはベース座標。trackは字間(px)。anchor l/r"""
    x, y = x * S, y * S
    if track == 0:
        b = d.textbbox((0, 0), t, font=f); w = b[2] - b[0]
        if anchor == "r": x -= w
        d.text((x - b[0], y - b[1]), t, font=f, fill=fill); return w / S
    ws = [d.textlength(c, font=f) for c in t]; w = sum(ws) + track * S * (len(t) - 1)
    if anchor == "r": x -= w
    top = d.textbbox((0, 0), t, font=f)[1]
    for c, cw in zip(t, ws):
        d.text((x, y - top), c, font=f, fill=fill); x += cw + track * S
    return w / S

def tire_lineart(d, cx, cy, r, col):
    cx, cy, r = cx * S, cy * S, r * S; w = 2 * S
    def circ(rr, width=w, c=col): d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=c, width=width)
    circ(r); circ(r * 0.80); circ(r * 0.60); circ(r * 0.56); circ(r * 0.13); circ(r * 0.06)
    # トレッド（外周の細い溝）
    for i in range(96):
        a = 2 * math.pi * i / 96
        r1, r2 = r * (0.86 if i % 2 else 0.90), r * 0.97
        d.line((cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + r2 * math.cos(a + 0.02), cy + r2 * math.sin(a + 0.02)), fill=col, width=w)
    # スポーク（細い2本線×5）
    for i in range(5):
        a = 2 * math.pi * i / 5 - math.pi / 2
        for s in (-1, 1):
            o = 0.075 * s
            d.line((cx + r * 0.15 * math.cos(a + o * 2.2), cy + r * 0.15 * math.sin(a + o * 2.2),
                    cx + r * 0.55 * math.cos(a + o * 0.55), cy + r * 0.55 * math.sin(a + o * 0.55)), fill=col, width=w)
    # ボルト穴
    for i in range(5):
        a = 2 * math.pi * i / 5 - math.pi / 2 + math.pi / 5
        bx, by, br = cx + r * 0.095 * math.cos(a), cy + r * 0.095 * math.sin(a), r * 0.013
        d.ellipse((bx - br, by - br, bx + br, by + br), outline=col, width=w)

def build(W, H, tall, out):
    im = Image.new("RGB", (W * S, H * S), BG); d = ImageDraw.Draw(im)
    M = 84
    top = 170 if tall else 80   # TikTok上部UIを避ける
    # レイアウト（下から確定させて重なりを防ぐ）
    if tall:
        L = dict(cx=820, cy=600, r=420, label=1050, hs=80, price_top=1390, foot=1690)
    else:
        L = dict(cx=860, cy=350, r=320, label=720, hs=64, price_top=975, foot=1286)
    # タイヤ線画（右上、画面外にはみ出させる）
    cx, cy, r = L["cx"], L["cy"], L["r"]
    tire_lineart(d, cx, cy, r, NAVY)
    # ゴールドの細い円弧（唯一のアクセント）
    rr = (r + 26) * S
    d.arc((cx * S - rr, cy * S - rr, cx * S + rr, cy * S + rr), 150, 205, fill=GOLD, width=2 * S)

    # ヘッダー
    T(d, M, top, "KOBAC", inter("SemiBold", 22), NAVY, track=6)
    T(d, M + 120, top, "WINTER TIRE SERVICE", inter("Regular", 22), GREY, track=4)
    T(d, M, top + 40, "2026", inter("Light", 18), GREY, track=4)

    # 見出し
    y = L["label"]; hs = L["hs"]
    d.line((M * S, (y + 11) * S, (M + 44) * S, (y + 11) * S), fill=GOLD, width=2 * S)
    T(d, M + 64, y, "冬のタイヤ交換祭", sans("Regular", 24), NAVY, track=6)
    T(d, M - 4, y + 60, "冬の足元を、", serif("Light", hs), NAVY, track=4)
    T(d, M - 4, y + 60 + int(hs * 1.45), "丁寧に整える。", serif("Light", hs), NAVY, track=4)

    # 価格行（罫線で挟む）
    py = L["price_top"]; ph = 160 if tall else 150
    d.line((M * S, py * S, (W - M) * S, py * S), fill=LINE, width=S)
    d.line((M * S, (py + ph) * S, (W - M) * S, (py + ph) * S), fill=LINE, width=S)
    T(d, M, py + 38, "タイヤ交換", sans("Light", 22), GREY, track=2)
    T(d, M, py + 74, "作業工賃 1台", sans("Light", 22), GREY, track=2)
    nf = inter("ExtraLight", 128 if tall else 112)
    nb = d.textbbox((0, 0), "500", font=nf); nh = (nb[3] - nb[1]) / S
    ny = py + (ph - nh) / 2
    nx = M + 240
    nw = T(d, nx, ny, "500", nf, NAVY, track=2)
    yf = sans("Light", 34); yb = d.textbbox((0, 0), "円", font=yf); yh = (yb[3] - yb[1]) / S
    T(d, nx + nw + 16, ny + nh - yh, "円", yf, NAVY)
    T(d, nx + nw + 16, ny + nh - yh - 34, "税込", sans("Light", 17), GREY, track=2)
    T(d, W - M, py + 38, "1日5台限定", sans("Regular", 22), NAVY, track=2, anchor="r")
    T(d, W - M, py + 74, "完全予約制", sans("Regular", 22), NAVY, track=2, anchor="r")

    # 開催期間・注記
    iy = py + ph + 34
    T(d, M, iy, "11.1 SUN — 12.15 TUE", inter("Regular", 22), NAVY, track=3)
    T(d, M, iy + 42, "※ 当店を初めてご利用のお車限定。その他条件はキャプションをご覧ください。", sans("Light", 16), GREY, track=1)

    # フッター
    fy = L["foot"]
    d.line((M * S, (fy - 26) * S, (W - M) * S, (fy - 26) * S), fill=LINE, width=S)
    T(d, M, fy, "車検のコバック", sans("Regular", 19), NAVY, track=2)
    T(d, W - M, fy, "富山掛尾店  076-423-2227　　富山西店  0120-589-418", sans("Light", 19), NAVY, track=1, anchor="r")

    im.resize((W, H), Image.LANCZOS).save(out, quality=95)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    build(1080, 1350, False, f"{out}/editorial_insta.jpg")
    build(1080, 1920, True, f"{out}/editorial_tiktok.jpg")
    print("ok")
