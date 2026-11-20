"""2027 新春初売DM（A4縦・両面）ラフ
使い方: python3 make_dm_rough.py <出力ディレクトリ>
ロゴ・車両写真は未入手のため灰色の仮枠で表示。150dpi相当（1240x1754）。
"""
from PIL import Image, ImageDraw, ImageFont
import sys, os

F = "/usr/share/fonts/opentype/noto/"
def font(w, s): return ImageFont.truetype(F + f"NotoSansCJK-{w}.ttc", s, index=0)

W, H = 1240, 1754
RED = (206, 22, 32); DRED = (140, 10, 18); GOLD = (232, 180, 40); YEL = (255, 222, 0)
WHITE = (255, 255, 255); INK = (30, 30, 30); GREEN = (0, 140, 70); GREY = (205, 205, 205)
DGREY = (120, 120, 120); CREAM = (255, 248, 230)

def tb(d, t, f, sw=0):
    b = d.textbbox((0, 0), t, font=f, stroke_width=sw); return b, b[2] - b[0], b[3] - b[1]

def text(d, x, y, t, f, fill, sw=0, sf=None, anchor="l"):
    """(x,y)=左上(anchor l) / 上中央(c) / 右上(r)"""
    b, w, h = tb(d, t, f, sw)
    if anchor == "c": x -= w / 2
    elif anchor == "r": x -= w
    d.text((x - b[0], y - b[1]), t, font=f, fill=fill, stroke_width=sw, stroke_fill=sf)
    return w, h

def rich(d, cx, base, segs, size, w_max=None, align="c"):
    """複数の色・太さを1行に並べる。segs=[(文字, {fill, weight, mul, bg, sw, sf})]。baseはベースラインのy"""
    def build(sz):
        out = []
        for t, o in segs:
            f = font(o.get("weight", "Black"), int(sz * o.get("mul", 1)))
            out.append((t, o, f, d.textlength(t, font=f) + 2 * o.get("sw", 0) + (16 if o.get("bg") else 0)))
        return out
    while True:
        parts = build(size); tw = sum(p[3] for p in parts)
        if not w_max or tw <= w_max or size <= 10: break
        size -= 1
    x = cx - tw / 2 if align == "c" else cx
    for t, o, f, w in parts:
        if o.get("bg"):
            asc = f.size * 0.92
            d.rectangle((x, base - asc, x + w, base + f.size * 0.18), fill=o["bg"])
            x += 8
        d.text((x + o.get("sw", 0), base), t, font=f, fill=o.get("fill", WHITE), anchor="ls",
               stroke_width=o.get("sw", 0), stroke_fill=o.get("sf"))
        x += w - (8 if o.get("bg") else 0)
    return tw

def fit(d, t, w_max, weight, size, sw=0):
    while size > 8 and tb(d, t, font(weight, size), sw)[1] > w_max: size -= 1
    return font(weight, size)

def placeholder(d, box, label):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(232, 232, 232), outline=DGREY, width=2)
    d.line((x0, y0, x1, y1), fill=GREY, width=2); d.line((x0, y1, x1, y0), fill=GREY, width=2)
    f = fit(d, label, x1 - x0 - 12, "Bold", 22)
    _, w, h = tb(d, label, f)
    d.rectangle(((x0 + x1 - w) / 2 - 6, (y0 + y1 - h) / 2 - 6, (x0 + x1 + w) / 2 + 6, (y0 + y1 + h) / 2 + 6), fill=(232, 232, 232))
    text(d, (x0 + x1) / 2, (y0 + y1 - h) / 2, label, f, DGREY, anchor="c")

def dashed_rect(d, box, col, w=4, dash=18, gap=10):
    x0, y0, x1, y1 = box
    for x in range(int(x0), int(x1), dash + gap):
        d.line((x, y0, min(x + dash, x1), y0), fill=col, width=w); d.line((x, y1, min(x + dash, x1), y1), fill=col, width=w)
    for y in range(int(y0), int(y1), dash + gap):
        d.line((x0, y, x0, min(y + dash, y1)), fill=col, width=w); d.line((x1, y, x1, min(y + dash, y1)), fill=col, width=w)

def red_bg(d, y0, y1):
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        d.line((0, y, W, y), fill=tuple(int(RED[i] * (1 - t) + DRED[i] * t) for i in range(3)))

def price_man(d, x, y, num, size, fill=YEL, sf=DRED):
    """「月々 1.1万円〜」をベースライン揃えで描く。戻り値は全体幅"""
    f1 = font("Black", int(size * 0.42)); f2 = font("Black", size); f3 = font("Black", int(size * 0.5))
    _, w1, h1 = tb(d, "月々", f1, 4); _, w2, h2 = tb(d, num, f2, 8); _, w3, h3 = tb(d, "万円〜", f3, 6)
    base = y + h2
    text(d, x, base - h1, "月々", f1, WHITE, 4, sf)
    text(d, x + w1 + 8, y, num, f2, fill, 8, sf)
    text(d, x + w1 + w2 + 16, base - h3, "万円〜", f3, fill, 6, sf)
    return w1 + w2 + w3 + 24

STORES = [
    ("車検のコバック 富山掛尾店", "0120-589-417", "AM8:30〜PM6:30", "富山市掛尾栄町5番地2", "定休日：水曜"),
    ("車検のコバック 富山西店", "0120-589-418", "AM8:30〜PM6:30", "富山市婦中町広田5250", "定休日：日曜・祝日"),
    ("コバックカーズ 富山掛尾店", "0120-554-514", "AM9:30〜PM6:30", "富山市掛尾町629", "定休日：水曜"),
]

CARS = [  # (メーカー 車種, 月額) ※ジョイカル特選車チラシ画像から読み取り。正式価格表で要確認
    ("ダイハツ ミライース L", "11,000"), ("ダイハツ ムーヴ L", "13,200"), ("ダイハツ タント L", "15,400"), ("スズキ スペーシア HYBRID G", "15,400"),
    ("ダイハツ タフト X", "15,400"), ("スズキ ハスラー HYBRID G", "15,400"), ("ダイハツ ムーヴキャンバス", "16,500"), ("ホンダ N-BOX", "17,600"),
    ("スズキ スペーシアカスタム", "17,600"), ("スズキ スペーシアギア", "18,700"), ("ダイハツ タントカスタム X", "18,700"), ("ダイハツ タントファンクロス", "18,700"),
    ("ホンダ N-BOXカスタム", "19,800"), ("スズキ ジムニー XG ※", "19,800"), ("ホンダ N-BOX JOY", "20,900"), ("三菱 デリカミニ G", "20,900"),
]

# ---------------- 表面（宛名面） ----------------
def front():
    im = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(im)
    # 郵便表示
    d.ellipse((60, 50, 240, 230), outline=INK, width=3); d.line((68, 110, 232, 110), fill=INK, width=2)
    text(d, 150, 125, "料金後納", font("Medium", 30), INK, anchor="c"); text(d, 150, 168, "郵便", font("Medium", 30), INK, anchor="c")
    d.rounded_rectangle((60, 250, 240, 300), radius=12, outline=INK, width=3)
    text(d, 150, 260, "ゆうメール", font("Medium", 26), INK, anchor="c")
    d.rectangle((50, 316, 300, 418), fill=RED); d.rectangle((60, 324, 290, 410), fill=GOLD)
    for i, t in enumerate(("コバック", "ご利用のお客様", "限定案内状")):
        text(d, 175, 332 + i * 26, t, font("Black", 22), DRED, anchor="c")
    # 宛名位置
    dashed_rect(d, (420, 40, 1180, 400), GREY, w=3)
    text(d, 800, 200, "宛名ラベル貼付位置", font("Medium", 30), GREY, anchor="c")

    # メイン帯
    top, bot = 430, 1505
    red_bg(d, top, bot)
    text(d, 50, top + 18, "2027", font("Black", 46), GOLD)
    text(d, 650, top + 10, "新春初売!!", font("Black", 150), YEL, 10, DRED, anchor="c")
    # サブコピー（2行）
    Y = {"fill": YEL}; Wt = {"fill": WHITE}
    rich(d, 620, top + 206, [("定額リースも、低金利ローンも、現金も！", Wt)], 36, W - 100)
    rich(d, 620, top + 254, [("あなたに一番お得な買い方が見つかる", Wt),
                             ("27日間", {"fill": RED, "bg": YEL, "mul": 1.25}), ("！", Wt)], 36, W - 100)
    pill = "1/5(火)〜1/31(日)　3店舗同時開催"
    pf = font("Black", 38); _, pw, ph = tb(d, pill, pf)
    d.rounded_rectangle((620 - pw / 2 - 36, top + 276, 620 + pw / 2 + 36, top + 276 + ph + 24), radius=36, fill=WHITE)
    text(d, 620, top + 288, pill, pf, RED, anchor="c")

    # 月々1.1万円（左）＋車両写真（右）
    y = top + 360
    rich(d, 620, y + 34, [("スマホ代感覚", {"fill": RED, "bg": YEL}), ("で新車に乗れる！", Wt),
                          ("ジョイカルのコミコミ定額プラン", {"fill": WHITE, "weight": "Bold", "mul": 0.85})], 38, W - 90)
    placeholder(d, (60, y + 60, 290, y + 106), "7MAXロゴ")
    text(d, 310, y + 58, "新車が", font("Black", 46), WHITE, 4, DRED)
    pw2 = price_man(d, 60, y + 128, "1.1", 160)
    text(d, 60 + pw2, y + 116, "税込", font("Black", 26), WHITE, anchor="r")
    text(d, 60, y + 276, "3年でも 5年でも 7年でも 月々同額!", font("Black", 38), YEL, 4, DRED)
    placeholder(d, (800, y + 62, 1180, y + 272), "車両写真（ハスラー等）")
    d.rounded_rectangle((800, y + 280, 1180, y + 322), radius=10, fill=WHITE)
    t = "車検・税金・自賠責・オイル交換もコミコミ"
    text(d, 990, y + 289, t, fit(d, t, 360, "Bold", 23), RED, anchor="c")

    # 比較の帯（2行）
    by = y + 336
    d.rectangle((0, by, W, by + 104), fill=WHITE)
    rich(d, 620, by + 48, [("「リースとローン、どっちが得？」も", {"fill": INK}),
                           ("全部比較できます！", {"fill": RED, "mul": 1.15})], 38, W - 80)
    rich(d, 620, by + 92, [("現金・ローン・7MAX ", {"fill": INK, "weight": "Bold"}), ("すべて対応！", {"fill": RED})], 30, W - 80)
    text(d, 620, by + 116, "さらに 新車ご購入で 車検7年分 差し上げます!!", font("Black", 42), WHITE, 5, DRED, anchor="c")
    text(d, 620, by + 170, "※車検基本料2回分・12ヶ月定期点検4回分・エンジンオイル交換13回分（条件は裏面）", font("Medium", 19), CREAM, anchor="c")

    # 持参クーポン
    cy0, cy1 = by + 200, bot - 12
    d.rectangle((40, cy0, W - 40, cy1), fill=CREAM); dashed_rect(d, (40, cy0, W - 40, cy1), DRED, w=4)
    d.rectangle((56, cy0 + 14, 380, cy1 - 14), fill=RED)
    text(d, 218, cy0 + 22, "このDMご持参で", font("Black", 26), WHITE, anchor="c")
    text(d, 218, cy0 + 58, "先着50名様", font("Black", 44), YEL, anchor="c")
    text(d, 218, cy0 + 114, "ご成約で", font("Black", 24), WHITE, anchor="c")
    text(d, 800, cy0 + 16, "選べる特大プレゼント!", font("Black", 50), RED, anchor="c")
    for i in range(5):
        x = 410 + i * 154
        placeholder(d, (x, cy0 + 80, x + 142, cy1 - 14), "景品" if i < 4 else "ほか多数")

    # 店舗
    sy = bot + 10
    text(d, 40, sy, "（株）モービルハウスグループ", font("Bold", 20), INK)
    for i, (n, tel, hr, ad, off) in enumerate(STORES):
        yy = sy + 32 + i * 70
        d.line((40, yy - 6, 770, yy - 6), fill=GREY, width=2)
        text(d, 40, yy + 2, n, font("Black", 27), RED)
        text(d, 770, yy, "☎ " + tel, font("Black", 30), INK, anchor="r")
        if "西店" in n: off += "（1/11・1/31休業）"
        text(d, 40, yy + 40, f"●営業 {hr}　●{ad}　●{off}", fit(d, f"●営業 {hr}　●{ad}　●{off}", 730, "Medium", 19), INK)
    placeholder(d, (795, sy, 1200, H - 20), "地図（前回DMデータ）")
    return im

# ---------------- 裏面 ----------------
FEATURED = [  # (区分, 車種, 7MAX月額, ローン月額) ※コンパクト・ミニバンの車種と価格、ローン月額は未定
    ("軽自動車", "スズキ ハスラー HYBRID G", "15,400", "○,○○○"),
    ("軽自動車", "ホンダ N-BOX", "17,600", "○,○○○"),
    ("コンパクト", "車種未定（例：ヤリス・ノート等）", "○○,○○○", "○,○○○"),
    ("ミニバン", "車種未定（例：シエンタ・フリード等）", "○○,○○○", "○,○○○"),
]
TAG = {"軽自動車": (230, 120, 0), "コンパクト": (0, 90, 170), "ミニバン": (120, 60, 160)}

def back():
    im = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(im)
    red_bg(d, 0, 286)
    placeholder(d, (40, 24, 220, 80), "JOYCALロゴ")
    placeholder(d, (40, 90, 220, 140), "7MAXロゴ")
    placeholder(d, (1100, 20, 1210, 170), "キャラ")
    rich(d, 660, 78, [("憧れの新車、", {"fill": WHITE, "sw": 4, "sf": DRED, "mul": 0.8}),
                      ("月々いくらで乗れる？", {"fill": YEL, "sw": 5, "sf": DRED})], 62, 840)
    rich(d, 660, 134, [("人気の", {"fill": WHITE}), ("軽からミニバンまで", {"fill": YEL}), ("全車種勢揃い！", {"fill": WHITE})], 38, 840)
    rich(d, 660, 182, [("7MAXなら ", {"fill": WHITE, "weight": "Bold"}), ("3年でも5年でも7年でも 月々同額!", {"fill": WHITE})], 30, 840)
    inc = ["車検費用", "自動車税", "自賠責", "オイル交換", "諸費用", "マット・バイザー"]
    text(d, 40, 222, "コミコミ!", font("Black", 30), YEL)
    bw = (W - 200 - 5 * 8) / 6
    for i, t in enumerate(inc):
        x = 190 + i * (bw + 8)
        d.rounded_rectangle((x, 216, x + bw, 264), radius=8, fill=WHITE)
        text(d, x + bw / 2, 227, t, fit(d, t, bw - 10, "Black", 22), GREEN, anchor="c")

    # 目玉4台（2x2）
    gx, gy, gap = 40, 302, 14; cw = (W - 2 * gx - gap) / 2; ch = 345
    for i, (cat, name, lease, loan) in enumerate(FEATURED):
        r, c = divmod(i, 2); x = gx + c * (cw + gap); y = gy + r * (ch + gap)
        d.rounded_rectangle((x, y, x + cw, y + ch), radius=14, fill=WHITE, outline=RED, width=4)
        tf = font("Black", 24); _, tw, th = tb(d, cat, tf)
        d.rounded_rectangle((x + 14, y + 14, x + 34 + tw, y + 22 + th + 10), radius=8, fill=TAG[cat])
        text(d, x + 24, y + 20, cat, tf, WHITE)
        text(d, x + 50 + tw, y + 18, name, fit(d, name, cw - tw - 80, "Black", 28), INK)
        placeholder(d, (x + 14, y + 64, x + cw * 0.46, y + ch - 14), "車両写真")
        px = x + cw * 0.46 + 14; pw = x + cw - 14 - px
        # 7MAX
        d.rounded_rectangle((px, y + 64, px + pw, y + 204), radius=10, fill=(232, 246, 236))
        text(d, px + 12, y + 72, "7MAX（リース）", font("Black", 22), GREEN)
        text(d, px + pw - 12, y + 76, "コミコミ", font("Bold", 18), GREEN, anchor="r")
        text(d, px + 12, y + 140, "月々", font("Black", 24), INK)
        text(d, px + pw - 12, y + 112, lease + "円", fit(d, lease + "円", pw - 80, "Black", 54), RED, anchor="r")
        # ローン
        d.rounded_rectangle((px, y + 218, px + pw, y + ch - 14), radius=10, fill=(232, 240, 250))
        text(d, px + 12, y + 228, "ローン（金利3.9%）", font("Black", 22), (0, 90, 170))
        text(d, px + 12, y + 290, "月々", font("Black", 24), INK)
        text(d, px + pw - 12, y + 264, loan + "円", fit(d, loan + "円", pw - 80, "Black", 50), (0, 90, 170), anchor="r")
    y0 = gy + 2 * (ch + gap)
    n = "※7MAX月額は税込・ボーナス加算33,000円(税込)×年2回の場合。ローン月額は頭金・ボーナス・回数の条件を確定後に記載。"
    text(d, 40, y0 - 6, n, fit(d, n, W - 80, "Medium", 18), INK)

    # ローン目玉
    y1 = y0 + 24
    d.rounded_rectangle((40, y1, W - 40, y1 + 150), radius=16, fill=(0, 90, 170))
    text(d, 70, y1 + 18, "ローンでもこの安さ!", font("Black", 34), YEL)
    text(d, 70, y1 + 66, "車種未定（目玉車）", font("Black", 30), WHITE)
    text(d, 70, y1 + 108, "新車金利3.9%・頭金／ボーナス／回数は確定後記載", font("Medium", 20), WHITE)
    f1 = font("Black", 40); f2 = font("Black", 110)
    _, w2, h2 = tb(d, "7,500", f2)
    text(d, W - 140, y1 + 18, "7,500", f2, YEL, 6, (0, 50, 110), anchor="r")
    text(d, W - 60, y1 + 70, "円〜", f1, YEL, anchor="r")
    text(d, W - 150 - w2, y1 + 70, "月々", f1, WHITE, anchor="r")

    # その他の特選車（文字のみ）
    y2 = y1 + 170
    d.rectangle((40, y2, W - 40, y2 + 40), fill=CREAM)
    text(d, 620, y2 + 6, "ほかにも ジョイカル特選車 全16車種 月々1.1万円〜（税込）  国産全メーカー全車種から選べます", fit(d, "ほかにも ジョイカル特選車 全16車種 月々1.1万円〜（税込）  国産全メーカー全車種から選べます", W - 100, "Black", 24), RED, anchor="c")
    others = [c for c in CARS if not any(k in c[0] for k in ("ハスラー", "ホンダ N-BOX"))][:12]
    cw2 = (W - 80) / 4
    for i, (nm, pr) in enumerate(others):
        r, c = divmod(i, 4); x = 40 + c * cw2; y = y2 + 52 + r * 34
        t = f"{nm.split(' ', 1)[1].replace(' ※', '')}  月々{pr}円"
        text(d, x + 6, y, t, fit(d, t, cw2 - 14, "Bold", 20), INK)

    # 特典＆たすカッター
    y3 = y2 + 168
    tw3 = (W - 80 - 2 * 14) / 3; th = 150
    boxes = [("車検7年分プレゼント", ["新車ご購入で", "車検2回・点検4回・オイル13回"], RED),
             ("卒業祝金 3万円", ["今春ご卒業の方", "新車リースご成約で"], RED),
             ("ジョイカルたすカッター", ["バンパーのキズ・ヘコミも補償", "7MAXに付いて安心!"], GREEN)]
    for i, (t, lines, col) in enumerate(boxes):
        x = 40 + i * (tw3 + 14)
        d.rounded_rectangle((x, y3, x + tw3, y3 + th), radius=14, fill=CREAM, outline=col, width=4)
        text(d, x + tw3 / 2, y3 + 16, t, fit(d, t, tw3 - 24, "Black", 34), col, anchor="c")
        for k, l in enumerate(lines):
            text(d, x + tw3 / 2, y3 + 70 + k * 34, l, fit(d, l, tw3 - 24, "Bold", 24), INK, anchor="c")
    y4 = y3 + th + 14
    pts = ["クレジットカード払いOK", "満了後に選べる4つの選択肢", "1年1万km走行OK", "国産全メーカー全車種OK"]
    pw4 = (W - 80 - 3 * 12) / 4
    for i, t in enumerate(pts):
        x = 40 + i * (pw4 + 12)
        d.rounded_rectangle((x, y4, x + pw4, y4 + 56), radius=10, fill=WHITE, outline=GREEN, width=3)
        text(d, x + pw4 / 2, y4 + 14, t, fit(d, t, pw4 - 16, "Black", 24), GREEN, anchor="c")
    y5 = y4 + 70
    notes = ["※成約プレゼントは本DMご持参・期間中ご成約の先着50名様。なくなり次第終了。商品は変更になる場合がございます。",
             "※価格・条件は2027年1月時点のものです。詳しくは店頭スタッフまでお尋ねください。"]
    for k, n in enumerate(notes):
        text(d, 40, y5 + k * 26, n, fit(d, n, W - 80, "Medium", 18), DGREY)
    d.rectangle((0, H - 56, W, H), fill=RED)
    rich(d, 620, H - 17, [("先着50名様の選べる特大プレゼントは", {"fill": WHITE}), ("早い者勝ち！", {"fill": YEL, "mul": 1.2}),
                          ("このDMを持って店舗へ急げ！", {"fill": WHITE})], 30, W - 50)
    return im

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    front().save(f"{out}/dm_front_rough.jpg", quality=92, dpi=(150, 150))
    back().save(f"{out}/dm_back_rough.jpg", quality=92, dpi=(150, 150))
    print("ok")
