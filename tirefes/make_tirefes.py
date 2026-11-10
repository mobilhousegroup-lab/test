from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, sys
F="/usr/share/fonts/opentype/noto/"
def f(w,s): return ImageFont.truetype(F+f"NotoSansCJK-{w}.ttc", s, index=0)
NAVY=(31,56,100); DEEP=(14,28,56); RED=(220,30,40); YEL=(255,204,0); WHITE=(255,255,255)

def tire(d, cx, cy, r, alpha_img):
    # outer tire
    g=ImageDraw.Draw(alpha_img)
    g.ellipse((cx-r,cy-r,cx+r,cy+r), fill=(25,25,30,255))
    # tread blocks
    for i in range(48):
        a=2*math.pi*i/48
        for k,(r1,r2) in enumerate([(r*0.86,r*0.99)]):
            w=0.045
            pts=[(cx+r1*math.cos(a-w),cy+r1*math.sin(a-w)),(cx+r2*math.cos(a-w+0.02),cy+r2*math.sin(a-w+0.02)),
                 (cx+r2*math.cos(a+w+0.02),cy+r2*math.sin(a+w+0.02)),(cx+r1*math.cos(a+w),cy+r1*math.sin(a+w))]
            g.polygon(pts, fill=(55,55,62,255))
    g.ellipse((cx-r*0.80,cy-r*0.80,cx+r*0.80,cy+r*0.80), fill=(40,40,46,255))
    g.ellipse((cx-r*0.62,cy-r*0.62,cx+r*0.62,cy+r*0.62), fill=(185,190,200,255))
    g.ellipse((cx-r*0.56,cy-r*0.56,cx+r*0.56,cy+r*0.56), fill=(120,126,138,255))
    for i in range(5):
        a=2*math.pi*i/5-math.pi/2
        g.line((cx,cy,cx+r*0.55*math.cos(a),cy+r*0.55*math.sin(a)), fill=(200,205,215,255), width=int(r*0.16))
    g.ellipse((cx-r*0.16,cy-r*0.16,cx+r*0.16,cy+r*0.16), fill=(210,214,222,255))
    g.ellipse((cx-r*0.07,cy-r*0.07,cx+r*0.07,cy+r*0.07), fill=(90,95,105,255))

def center(d, y, text, font, fill, W, stroke=0, sfill=None):
    b=d.textbbox((0,0),text,font=font,stroke_width=stroke)
    d.text(((W-(b[2]-b[0]))/2-b[0], y-b[1]), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    return y+(b[3]-b[1])

def build(W,H,out,tall):
    im=Image.new("RGB",(W,H),DEEP)
    d=ImageDraw.Draw(im)
    # radial-ish gradient
    for y in range(H):
        t=y/H; c=tuple(int(NAVY[i]*(1-t)+DEEP[i]*t) for i in range(3)); d.line((0,y,W,y),fill=c)
    # sunburst
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    cx,cy=W/2,(H*0.30 if tall else H*0.33)
    for i in range(24):
        if i%2: continue
        a1=2*math.pi*i/24; a2=2*math.pi*(i+1)/24; R=2000
        od.polygon([(cx,cy),(cx+R*math.cos(a1),cy+R*math.sin(a1)),(cx+R*math.cos(a2),cy+R*math.sin(a2))],fill=(255,255,255,14))
    im=Image.alpha_composite(im.convert("RGBA"),ov)
    # confetti
    import random; random.seed(3)
    cf=Image.new("RGBA",(W,H),(0,0,0,0)); cd=ImageDraw.Draw(cf)
    for _ in range(70):
        x=random.randint(0,W); y=random.randint(0,int(H*0.55)); s=random.randint(8,18)
        col=random.choice([RED,YEL,WHITE,(80,170,255)])+(200,)
        cd.rectangle((x,y,x+s,y+s*0.5),fill=col)
    cf=cf.rotate(8,resample=Image.BICUBIC)
    im=Image.alpha_composite(im,cf)
    # tire with shadow
    tr=int(W*0.26) if tall else int(W*0.19)
    tcy=540 if tall else 360
    sh=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(sh).ellipse((W/2-tr,tcy-tr+30,W/2+tr,tcy+tr+30),fill=(0,0,0,140))
    im=Image.alpha_composite(im,sh.filter(ImageFilter.GaussianBlur(25)))
    tl=Image.new("RGBA",(W,H),(0,0,0,0)); tire(None,W//2,tcy,tr,tl); im=Image.alpha_composite(im,tl)
    d=ImageDraw.Draw(im)
    # 開催中 badge (top)
    by=int(H*0.045) if tall else 50
    if tall: by=150  # TikTok top UI
    bf=f("Black",52); txt="ただいま開催中！"
    b=d.textbbox((0,0),txt,font=bf); bw=b[2]-b[0]+90; bh=b[3]-b[1]+40
    d.rounded_rectangle(((W-bw)/2,by,(W+bw)/2,by+bh),radius=bh//2,fill=RED)
    d.text(((W-(b[2]-b[0]))/2-b[0],by+20-b[1]),txt,font=bf,fill=WHITE)
    # title
    y=tcy+tr+(50 if tall else 30)
    y=center(d,y,"車検のコバック",f("Bold",54 if tall else 46),WHITE,W)+ (22 if tall else 16)
    y=center(d,y,"タイヤ祭",f("Black",210 if tall else 150),YEL,W,stroke=10,sfill=RED)+(40 if tall else 28)
    # subtitle band
    st="冬タイヤの準備はお早めに！"
    sf=f("Bold",58 if tall else 50); b=d.textbbox((0,0),st,font=sf); bh=b[3]-b[1]+44
    d.rectangle((0,y,W,y+bh),fill=WHITE)
    d.text(((W-(b[2]-b[0]))/2-b[0],y+22-b[1]),st,font=sf,fill=NAVY)
    y+=bh+(46 if tall else 32)
    # three points
    pts=["タイヤ販売","交換・組み替え","溝・ひび点検"]
    n=3; gap=24; pw=(W-2*60-gap*2)/3; ph=120 if tall else 104
    pf=f("Bold",36 if tall else 34)
    for i,p in enumerate(pts):
        x0=60+i*(pw+gap)
        d.rounded_rectangle((x0,y,x0+pw,y+ph),radius=20,fill=(10,20,45),outline=YEL,width=5)
        b=d.textbbox((0,0),p,font=pf)
        d.text((x0+(pw-(b[2]-b[0]))/2-b[0],y+(ph-(b[3]-b[1]))/2-b[1]),p,font=pf,fill=WHITE)
    y+=ph+(50 if tall else 34)
    y=center(d,y,"詳しくは店頭・お電話でお気軽に！",f("Medium",40 if tall else 34),WHITE,W)+(40 if tall else 26)
    if not tall: y=H-180
    # store footer
    fh=200 if tall else 180
    fy=y
    d.rectangle((0,fy,W,fy+fh),fill=WHITE)
    hf=f("Bold",36 if tall else 33); tf=f("Black",44 if tall else 40)
    for i,(n,tel) in enumerate([("富山掛尾店","076-423-2227"),("富山西店","076-466-2228")]):
        cx0=W/4+i*W/2
        for yy,(t,ft,c) in zip([fy+(40 if tall else 34),fy+(105 if tall else 95)],[(n,hf,NAVY),("TEL "+tel,tf,RED)]):
            b=d.textbbox((0,0),t,font=ft); d.text((cx0-(b[2]-b[0])/2-b[0],yy-b[1]),t,font=ft,fill=c)
    d.line((W/2,fy+30,W/2,fy+fh-30),fill=(200,200,200),width=3)
    im.convert("RGB").save(out,quality=95)
    print(out, "footer bottom", fy+fh, "H", H)

build(1080,1350,sys.argv[1]+"/kobac_tirefes_insta_feed.jpg",False)
build(1080,1920,sys.argv[1]+"/kobac_tirefes_tiktok_story.jpg",True)
