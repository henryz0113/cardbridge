import random
import json
import requests
import mysql.connector
from flask import Flask, render_template_string, jsonify, request

# ==============================================================================
# PROJECT     : CardBridge (AI Fintech - VVIP Social Matching Platform)
# FILE NAME   : full-ai-cardbrdige.py
# DESCRIPTION : Core logic for Recommendation & Matching Engines
#               FULL AI Version (Recommnedation & Matching Engines)
# 
# AUTHOR      : sudo-kill9er
# VERSION     : v3.1.6
# CREATED DATE: 2026-05-09
# LAST UPDATED: 2026-05-23
# ==============================================================================

app = Flask(__name__)

# --- [1. 데이터 설계: MySQL 연동 및 기존 로직 유지] ---

def get_db_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='Oframe06a!@',
            database='cardbridge_db'
        )
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        return None

def fetch_merchants_from_db():
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.connector.connect().cursor(dictionary=True) if conn is None else conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM merchants")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

# [수정 반영] 소비 패턴 유사도 매칭 및 2차(프로필), 3차(부동산/차량) 데이터 패키징 연동
def fetch_opponent_from_db(user_name):
    conn = get_db_connection()
    if not conn:
        return "익명의 자산가", {"Golf": "33.3%", "Shopping": "33.3%", "Food": "33.4%"}, {}, {}
    
    cursor = conn.cursor(dictionary=True)
    group_b_pool = [
        "청담동 벨루가", "한남동 아르망디", "트리마제 하이엔드", "시그니엘 펜트", 
        "성수동 갤러리아", "갤러리아 팰리스", "도곡동 타워팰리스", "평창동 저택포식자"
    ]
    
    try:
        cursor.execute("SELECT * FROM user_assets WHERE user_name = %s", (user_name,))
        user_info = cursor.fetchone()
        
        format_strings = ','.join(['%s'] * len(group_b_pool))
        cursor.execute(f"SELECT * FROM user_assets WHERE user_name IN ({format_strings})", tuple(group_b_pool))
        candidates = cursor.fetchall()
        
        if user_info and candidates:
            u_patterns = {user_info['cat1_name']: user_info['cat1_val'], 
                          user_info['cat2_name']: user_info['cat2_val'], 
                          user_info['cat3_name']: user_info['cat3_val']}
            
            best_opponent = None
            min_difference = float('inf')
            best_opp_patterns = {}
            opp_profile = {}
            opp_estate = {}
            
            for cand in candidates:
                c_patterns = {cand['cat1_name']: cand['cat1_val'], 
                              cand['cat2_name']: cand['cat2_val'], 
                              cand['cat3_name']: cand['cat3_val']}
                
                total_diff = 0
                all_cats = set(u_patterns.keys()).union(set(c_patterns.keys()))
                for cat in all_cats:
                    total_diff += abs(u_patterns.get(cat, 0) - c_patterns.get(cat, 0))
                
                if total_diff < min_difference:
                    min_difference = total_diff
                    best_opponent = cand['user_name']
                    best_opp_patterns = {
                        cand['cat1_name']: f"{cand['cat1_val']}.0%",
                        cand['cat2_name']: f"{cand['cat2_val']}.0%",
                        cand['cat3_name']: f"{cand['cat3_val']}.0%"
                    }
                    # 2차 공개용 프로필 바인딩
                    opp_profile = {
                        "blood": cand['blood_type'],
                        "height": f"{cand['height']}cm",
                        "job": cand['job']
                    }
                    # 3차 공개용 자산 원장 바인딩
                    opp_estate = {
                        "home_owner": cand['home_owner'],
                        "home_loc": cand['home_location'],
                        "car": cand['car_brand']
                    }
            
            return best_opponent, best_opp_patterns, opp_profile, opp_estate

        if candidates:
            lucky = random.choice(candidates)
            return lucky['user_name'], {lucky['cat1_name']: f"{lucky['cat1_val']}.0%"}, {"blood": "O", "height": "175cm", "job": "자산가"}, {"home_owner": "자가", "home_loc": "서울", "car": "외제차"}
            
    except mysql.connector.Error as err:
        print(f"Database Error in tech match: {err}")
    finally:
        cursor.close()
        conn.close()
        
    return "익명의 자산가", {"Shopping": "50.0%"}, {"blood": "O", "height": "175cm", "job": "자산가"}, {"home_owner": "자가", "home_loc": "서울", "car": "외제차"}

# 전역 변수 MERCHANTS를 DB 데이터로 초기화
MERCHANTS = fetch_merchants_from_db()

DOMESTIC_MCC_MAP = {
    "Cafe": {"mcc_code": "O001", "mcc_name": "커피전문점/베이커리"},
    "Food": {"mcc_code": "O002", "mcc_name": "일반한식/외식업종"},
    "Gas": {"mcc_code": "O003", "mcc_name": "국내주유소/충전소"},
    "Shopping": {"mcc_code": "O004", "mcc_name": "대형할인점/온라인쇼핑"},
    "CV": {"mcc_code": "O005", "mcc_name": "편의점/잡화"},
    "Hospital": {"mcc_code": "O006", "mcc_name": "의료기관/약국"},
    "Golf": {"mcc_code": "O007", "mcc_name": "골프장/레저스포츠"}
}

CATEGORIES = ["Cafe", "Food", "Gas", "Shopping", "CV", "Hospital", "Golf"]
API_KEY = "AIzaSyD1tnhxQKa4QWvNBmr_PeKQUGQ5KFk0vVs"
#MODEL_NAME = "gemini-2.5-flash-lite" 
MODEL_NAME = "gemini-2.5-flash" 

KOREAN_NAMES = ["김철수", "이영희", "박지민", "최유진", "정민호", "한소라", "강태윤", "윤서연"]

NAME_ENG_MAP = {
    "김철수": "CHULSOO KIM",
    "이영희": "YOUNGHEE LEE",
    "박지민": "JIMIN PARK",
    "최유진": "YUJIN CHOI",
    "정민호": "MINHO JUNG",
    "한소라": "SORA HAN",
    "강태윤": "TAEYUN KANG",
    "윤서연": "SEOVEON YOON"
}

AGE_STRATEGY_DATA = {
    "10": {"card": "Kakao Friends Debit", "color": "linear-gradient(135deg, #FFE500 0%, #F4C400 100%)", "logo": "fa-comment", "desc": "첫 금융 생활, 친근한 캐릭터와 편의점 혜택으로 시작하세요."},
    "20": {"card": "Toss Wide Debit", "color": "linear-gradient(135deg, #0064FF 0%, #0036B3 100%)", "logo": "fa-wallet", "desc": "대학생활/사회초년생을 위한 조건 없는 전 가맹점 적립."},
    "30": {"card": "Shinhan Deep Dream", "color": "linear-gradient(135deg, #0046FF 0%, #001A99 100%)", "logo": "fa-gem", "desc": "본격적인 소비 트렌드, 가장 많이 쓴 영역 자동 적립."},
    "40": {"card": "Hyundai Zero Gold", "color": "linear-gradient(135deg, #2C2C2E 0%, #111112 100%)", "logo": "fa-crown", "desc": "생활비 및 공과금 등 가족형 소비를 위한 강력한 할인."}
}

MARKET_CARDS = [
    {"id": "M1", "company": "롯데카드", "name": "LOCA LIKIT 1.2", "color": "linear-gradient(135deg, #ED1C24 0%, #990005 100%)", "logo": "fa-credit-card", "benefits": {"Cafe": 0.10, "Shopping": 0.05}, "url": "https://www.lottecard.co.kr/"},
    {"id": "M2", "company": "신한카드", "name": "Mr.Life", "color": "linear-gradient(135deg, #0046FF 0%, #001C66 100%)", "logo": "fa-house", "benefits": {"CV": 0.10, "Gas": 0.10}, "url": "https://www.shinhancard.com/"},
    {"id": "M3", "company": "KB국민카드", "name": "My WE:SH 카드", "color": "linear-gradient(135deg, #FFBC00 0%, #B38400 100%)", "logo": "fa-face-smile", "benefits": {"Cafe": 0.30, "CV": 0.10}, "url": "https://card.kbcard.com/"},
    {"id": "M4", "company": "현대카드", "name": "Hyundai Card M Boost", "color": "linear-gradient(135deg, #444444 0%, #111111 100%)", "logo": "fa-rocket", "benefits": {"Shopping": 0.05, "Cafe": 0.03}, "url": "https://www.hyundaicard.com/"}
]

ROULETTE_ROOMS = {}

def generate_complex_benefits():
    benefits = {}
    selected_cats = random.sample(CATEGORIES, random.randint(3, 5))
    REALISTIC_RATES = [0.012, 0.03, 0.05, 0.10, 0.30, 0.50]
    for cat in selected_cats:
        benefits[cat] = random.choice(REALISTIC_RATES)
    return benefits

def get_cards_by_age(age):
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, company, name, card_type as type, color, logo, performance_limit, total_limit, annual_fee FROM cards")
    card_pool = cursor.fetchall()

    color_map = {
        "#FEE500": "linear-gradient(135deg, rgba(255, 236, 64, 0.8) 0%, rgba(212, 175, 55, 0.4) 100%)",
        "#0064FF": "linear-gradient(135deg, rgba(58, 135, 255, 0.8) 0%, rgba(0, 68, 179, 0.4) 100%)",
        "#0046FF": "linear-gradient(135deg, rgba(26, 102, 255, 0.8) 0%, rgba(0, 34, 128, 0.4) 100%)",
        "#1A1A1A": "linear-gradient(135deg, rgba(68, 68, 70, 0.8) 0%, rgba(28, 28, 30, 0.4) 100%)"
    }

    selected_pool = []
    if age == "10": 
        available = [c for c in card_pool if c["type"] == "Debit"]
        selected_pool = random.sample(available, 1) if available else []
    elif age == "20": 
        selected_pool = random.sample(card_pool, min(len(card_pool), 2))
    elif age == "30": 
        selected_pool = random.sample(card_pool, min(len(card_pool), 4))
    elif age == "40": 
        selected_pool = random.sample(card_pool, min(len(card_pool), 3))
    
    selected = []
    for i, card in enumerate(selected_pool):
        c = card.copy()
        raw_color = c.get("color", "#1A1A1A")
        c["color"] = color_map.get(raw_color, f"linear-gradient(135deg, {raw_color} 0%, #111 100%)")
        
        rand_last_digits = str(random.randint(1000, 9999))
        rand_brand = "VISA" if random.random() > 0.5 else "MASTER"
        
        real_benefits = {}
        cursor.execute("SELECT category, reward_rate FROM card_benefits WHERE card_id = %s", (c["id"],))
        benefit_rows = cursor.fetchall()
        for b_row in benefit_rows:
            real_benefits[b_row["category"]] = float(b_row["reward_rate"])
        
        for cat in CATEGORIES:
            if cat not in real_benefits:
                real_benefits[cat] = 0.0

        c.update({
            "id": f"C{age}_{i}", 
            "benefits": real_benefits,
            "last_digits": rand_last_digits,
            "brand": rand_brand,
            "performance_limit": c.get("performance_limit", 300000),
            "total_limit": c.get("total_limit", 10000),
            "annual_fee": c.get("annual_fee", 0),
            "current_performance": random.randint(150000, 600000) 
        })
        selected.append(c)
        
    cursor.close()
    conn.close()
    return selected

# --- [2. UI/Template 및 프론트엔드 제어 스크립트] ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>CardBridge Pro v17 | Team 4 Premium</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root { 
            --ios-blue: #0a84ff; 
            --ios-red: #ff453a; 
            --ios-green: #32d74b; 
            --gold: #ffd700; 
            --roulette-black: #0c0c0e; 
            --liquid-bg: rgba(255, 255, 255, 0.06);
            --liquid-border: rgba(255, 255, 255, 0.12);
            --liquid-glow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        body { 
            background: linear-gradient(135deg, #070708 0%, #141419 100%); 
            color: #fff; 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, sans-serif; 
            margin: 0; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 100vh; 
            overflow: hidden; 
        }
        .iphone { 
            width: 375px; 
            height: 812px; 
            background: #000; 
            border-radius: 50px; 
            border: 12px solid #2c2c2e; 
            position: relative; 
            overflow: hidden; 
            display: flex; 
            flex-direction: column; 
            box-shadow: 0 25px 60px -10px rgba(0,0,0,0.8), inset 0 0 2px 2px rgba(255,255,255,0.1);
        }
        
        #welcome-screen {
            position: absolute; inset: 0; background: radial-gradient(circle at center, #18181f 0%, #050507 100%);
            z-index: 9999; display: flex; flex-direction: column; align-items: center; justify-content: center;
            text-align: center; cursor: pointer; transition: 1s cubic-bezier(0.1, 1, 0.1, 1);
        }
        .crystal-logo {
            width: 85px; height: 85px; 
            background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.02) 100%);
            border: 1px solid var(--liquid-border); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            border-radius: 24px; margin-bottom: 24px; box-shadow: var(--liquid-glow), 0 0 30px rgba(10,132,255,0.2);
            display: flex; align-items: center; justify-content: center; font-size: 38px; color: #fff;
        }
        .welcome-text { font-size: 32px; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 8px; opacity: 0; transform: translateY(20px); animation: fadeInUp 0.8s forwards 0.3s; }
        .welcome-sub { color: #8e8e93; font-size: 16px; opacity: 0; animation: fadeInUp 0.8s forwards 0.6s; }
        .tap-hint { position: absolute; bottom: 60px; color: #555; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; animation: pulse 2s infinite; }
        @keyframes fadeInUp { to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }

        .tab-content { display: none; height: 100%; padding: 0 20px 100px; box-sizing: border-box; overflow-y: auto; }
        .tab-content.active { display: block; }
        
        .map-section { 
            background: #121216; border-radius: 24px; margin-bottom: 15px; border: 1px solid var(--liquid-border); 
            height: 180px; position: relative; overflow: hidden; background-size: cover; background-position: center; 
            display: flex; justify-content: center; align-items: center; margin-top: 10px;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.6);
        }
        .map-pin { position: absolute; z-index: 2; color: var(--ios-red); font-size: 24px; filter: drop-shadow(0 2px 8px rgba(255,69,58,0.4)); }
        #displayLoc { position: absolute; bottom: 15px; background: rgba(18,18,24,0.75); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); border: 1px solid var(--liquid-border); padding: 6px 16px; border-radius: 20px; font-size: 13px; z-index: 3; }
        
        .card-stack-container { position: relative; margin-top: 10px; }
        .section-header { color: #8e8e93; font-size: 12px; font-weight: 600; margin: 24px 0 12px 5px; text-transform: uppercase; letter-spacing: 0.5px; }
        .card-stack { position: relative; transition: height 0.5s; margin-bottom: 20px; }
        
        .card { 
            width: 100%; 
            height: 210px; 
            border-radius: 24px; 
            padding: 24px; 
            box-sizing: border-box; 
            position: absolute; 
            transition: transform 0.5s cubic-bezier(0.1, 1, 0.1, 1), opacity 0.5s, top 0.5s; 
            backdrop-filter: blur(30px); -webkit-backdrop-filter: blur(30px);
            border: 1px solid rgba(255,255,255,0.18); 
            cursor: pointer; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.3);
            overflow: hidden;
        }
        .card::before {
            content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0) 70%);
            transform: rotate(30deg); pointer-events: none;
        }
        .card:hover { transform: translateY(-30px) scale(1.03) rotate(-1deg); z-index: 100 !important; }
        
        .card-brand-area { position: absolute; bottom: 24px; right: 24px; display: flex; align-items: center; }
        .brand-master-circles { display: flex; align-items: center; }
        .brand-circle { width: 26px; height: 26px; border-radius: 50%; opacity: 0.9; filter: blur(0.3px); }
        .circle-red { background: #FF5F00; margin-right: -10px; }
        .circle-yellow { background: #F79E1B; }
        .brand-visa-text { font-size: 19px; font-weight: 900; font-style: italic; color: #fff; letter-spacing: -0.5px; text-shadow: 0 1px 2px rgba(0,0,0,0.3); }
        .brand-visa-text span { color: #F79E1B; }

        .card-type-badge { position: absolute; top: 24px; right: 24px; font-size: 10px; background: rgba(255,255,255,0.12); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 10px; letter-spacing: 0.5px; font-weight: 600; text-transform: uppercase; }
        
        .stat-card { 
            background: var(--liquid-bg); border-radius: 24px; padding: 22px; margin-bottom: 15px; 
            border: 1px solid var(--liquid-border); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            cursor: pointer; transition: 0.3s; box-shadow: var(--liquid-glow);
        }
        .stat-card:hover { transform: scale(1.02); background: rgba(255,255,255,0.09); border-color: rgba(255,255,255,0.2); }
        
        .overlay { 
            position: absolute; bottom: -100%; left: 0; width: 100%; height: 58%; 
            background: rgba(24, 24, 30, 0.85); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px);
            border-radius: 36px 36px 0 0; transition: 0.5s cubic-bezier(0.1, 1, 0.1, 1); padding: 32px; 
            box-sizing: border-box; z-index: 9000; border-top: 1px solid rgba(255,255,255,0.15); 
            box-shadow: 0 -15px 40px rgba(0,0,0,0.6); display: flex; flex-direction: column; 
        }
        .overlay.active { bottom: 85px; pointer-events: auto; }
        
        .nav { 
            position: absolute; bottom: 0; width: 100%; height: 85px; 
            background: rgba(14, 14, 18, 0.6); backdrop-filter: blur(30px); -webkit-backdrop-filter: blur(30px);
            display: flex; justify-content: space-around; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.07); z-index: 8500; 
        }
        .nav-item { text-align: center; color: #77777e; font-size: 10px; cursor: pointer; width: 25%; transition: 0.2s; }
        .nav-item i { font-size: 20px; margin-bottom: 4px; transition: 0.2s; }
        .nav-item.active { color: var(--ios-blue); }
        .nav-item.active i { transform: translateY(-2px); }
        
        #chatMessages, #rouletteMessages { height: 420px; overflow-y: auto; padding: 10px; display: flex; flex-direction: column; gap: 14px; }
        .msg { padding: 12px 18px; border-radius: 20px; max-width: 82%; font-size: 14px; line-height: 1.45; word-break: break-word; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .msg.user { background: linear-gradient(135deg, #0a84ff 0%, #0055ff 100%); align-self: flex-end; border-bottom-right-radius: 4px; }
        .msg.ai { background: rgba(255,255,255,0.07); border: 1px solid var(--liquid-border); align-self: flex-start; border-bottom-left-radius: 4px; }
        .msg.dealer { background: linear-gradient(135deg, #2b0005 0%, #150002 100%); color: #fff; align-self: center; text-align: center; border: 1px solid rgba(255,69,58,0.3); border-radius: 18px; font-weight: 600; width: 92%; font-size: 13px; padding: 14px; box-shadow: 0 0 20px rgba(255,69,58,0.1); }
        .msg table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 12px; background: rgba(0,0,0,0.2); border-radius: 8px; overflow: hidden; }
        .msg th, .msg td { padding: 8px 10px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .msg th { background: rgba(255,255,255,0.1); font-weight: 600; }

        .premium-tab-btn { color: var(--gold) !important; font-weight: bold; display: none; }
        .roulette-panel { background: linear-gradient(135deg, #121216 0%, #08080a 100%); border: 1px solid rgba(255,215,0,0.25); border-radius: 24px; padding: 18px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; box-shadow: var(--liquid-glow); }
        .action-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 5px 0; }
        
        .btn-game { border: none; padding: 16px; border-radius: 16px; font-weight: 700; font-size: 15px; cursor: pointer; color: #fff; transition: 0.2s cubic-bezier(0.1, 1, 0.1, 1); }
        .btn-game:active { transform: scale(0.96); }
        .btn-trust { background: linear-gradient(135deg, #32d74b 0%, #1e9a30 100%); box-shadow: 0 8px 20px rgba(50,215,75,0.25); }
        .btn-betray { background: linear-gradient(135deg, #ff453a 0%, #c61a11 100%); box-shadow: 0 8px 20px rgba(255,69,58,0.25); }
        
        select, input[type="text"] {
            background: rgba(255,255,255,0.06); border: 1px solid var(--liquid-border); 
            padding: 16px; border-radius: 16px; color: #fff; font-size: 15px; outline: none;
            backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); transition: 0.3s;
        }
        select:focus, input[type="text"]:focus { border-color: var(--ios-blue); background: rgba(255,255,255,0.1); }
        
        button.optimize-btn {
            background: #fff; color: #000; border: none; width: 100%; padding: 18px; 
            border-radius: 18px; font-weight: 700; font-size: 16px; margin-top: 15px; 
            cursor: pointer; transition: 0.3s cubic-bezier(0.1, 1, 0.1, 1); box-shadow: 0 10px 25px rgba(255,255,255,0.15);
        }
        button.optimize-btn:active { transform: scale(0.97); opacity: 0.9; }

        .cylinder-spin { font-size: 22px; color: var(--gold); animation: spin 0.6s linear infinite; display: inline-block; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="iphone">
        <div id="welcome-screen" onclick="startOnboarding()">
            <div class="crystal-logo"><i class="fas fa-bridge"></i></div>
            <div class="welcome-text">안녕하세요</div>
            <div class="welcome-sub">Welcome to CardBridge</div>
            <div class="tap-hint">Tap to Continue</div>
        </div>

        <div id="onboarding" style="position:absolute; inset:0; background: #09090b; z-index:9500; padding:60px 30px; display:flex; flex-direction:column; transition:0.6s cubic-bezier(0.1, 1, 0.1, 1); transform: translateY(100%);">
            <h2 style="font-size:34px; letter-spacing: -1px; margin-bottom: 30px;">CardBridge<br><span style="color:var(--ios-blue)">Wallet 설정</span></h2>
            <div style="margin:25px 0; display:flex; flex-direction:column; gap:24px;">
                <div>
                    <label style="color:#8e8e93; font-size:13px; font-weight:600; text-transform:uppercase; margin-left:4px;">연령대 선택</label>
                    <select id="userAge" style="width:100%; margin-top:8px;">
                        <option value="10">10대</option><option value="20">20대</option><option value="30" selected>30대</option><option value="40">40대</option>
                    </select>
                </div>
                
                <div style="background:rgba(255,255,255,0.03); border:1px solid var(--liquid-border); padding:16px; border-radius:20px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="max-width: 80%;">
                        <span style="font-size:14px; font-weight:600; color:#fff;">스페셜 AI 에이전트 구독</span>
                        <div style="font-size:11px; color:#8e8e93; margin-top:4px; line-height:1.3;">소비 분석 및 맞춤형 금융 챗봇 상담 활성화</div>
                    </div>
                    <input type="checkbox" id="premiumToggle" checked style="width:22px; height:22px; accent-color: var(--ios-blue);">
                </div>

                <div style="background:rgba(255,255,255,0.03); border:1px solid var(--liquid-border); padding:16px; border-radius:20px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="max-width: 80%;">
                        <span style="font-size:14px; font-weight:600; color:var(--gold);"><i class="fas fa-crown"></i> 블랙 룰렛 매칭 옵션</span>
                        <div style="font-size:11px; color:#8e8e93; margin-top:4px; line-height:1.3;">상위 0.1% 자산 계층 전용 1:1 심리전 매칭 서비스</div>
                    </div>
                    <input type="checkbox" id="rouletteToggle" checked style="width:22px; height:22px; accent-color: var(--gold);">
                </div>
            </div>
            <button onclick="finishOnboarding()" style="background:var(--ios-blue); color:white; border:none; padding:18px; border-radius:18px; font-weight:700; font-size:16px; cursor:pointer; margin-top:auto; box-shadow: 0 8px 25px rgba(10,132,255,0.3);">Wallet 시작하기</button>
        </div>

        <div id="wallet" class="tab-content active">
            <div style="padding:40px 15px 10px;"><h1 style="font-size:34px; font-weight:700; letter-spacing:-1px; margin:0;">지갑</h1></div>
            <div class="map-section" id="mapView">
                <i class="fas fa-location-dot map-pin"></i>
                <div id="displayLoc">위치를 선택하세요</div>
            </div>
            <select id="mSelect" onchange="updateLoc()" style="width:100%;">
                {% for m in merchants %}<option value="{{ m.id }}">{{ m.name }} ({{ m.category }})</option>{% endfor %}
            </select>
            
            <button onclick="recommend()" class="optimize-btn">최적의 해택 카드 찾기</button>
            
            <div id="cardContainer" class="card-stack-container"></div>
        </div>

        <div id="report" class="tab-content">
            <div style="padding:40px 15px 10px;"><h1 style="font-size:34px; font-weight:700; letter-spacing:-1px; margin:0;">Insights</h1></div>
            <div class="stat-card" onclick="triggerLimitPopup()"><div style="font-size:12px; color:#8e8e93; font-weight:600; text-transform:uppercase; margin-bottom:8px;">실시간 실적 충족 알림</div><div id="limitText" style="font-size:24px; font-weight:700; color:var(--ios-red);">로딩중...</div></div>
            <div class="stat-card" onclick="triggerPruningPopup()"><div style="font-size:12px; color:#8e8e93; font-weight:600; text-transform:uppercase; margin-bottom:8px;">카드 자산 최적화</div><div id="pruningText" style="font-size:24px; font-weight:700; color:var(--ios-green);">분석 중...</div></div>
            <div class="stat-card" onclick="triggerStatsPopup()"><div style="font-size:12px; color:#8e8e93; font-weight:600; text-transform:uppercase; margin-bottom:8px;">2026년 누적 혜택 가치</div><div id="totalBenefitText" style="font-size:24px; font-weight:700; color:var(--ios-blue);">₩0</div></div>
            <div class="stat-card" id="ageStrategyCard" style="border: 1px solid rgba(10,132,255,0.25); background: rgba(10,132,255,0.03);" onclick="triggerAgeBridgePopup()"><div id="ageStrategyTitle" style="font-size:18px; font-weight:700; color:#fff;"></div><p style="font-size:12px; color:#8e8e93; margin-top:8px; margin-bottom:0;">생애주기 맞춤 AI 추천</p></div>
        </div>

        <div id="ai-tab" class="tab-content">
            <div style="padding:40px 15px 10px;"><h1 style="font-size:34px; font-weight:700; letter-spacing:-1px; margin:0;">AI Agent</h1></div>
            <div style="background:var(--liquid-bg); border-radius:24px; flex:1; display:flex; flex-direction:column; border:1px solid var(--liquid-border); margin-bottom:10px; box-shadow: var(--liquid-glow);">
                <div id="chatMessages"><div class="msg ai">무엇을 도와드릴까요? 카드 데이터 기반으로 맞춤 상담을 시작합니다!</div></div>
                <div style="padding:12px; border-top:1px solid var(--liquid-border); display:flex; gap:10px; background: rgba(0,0,0,0.2);">
                    <input type="text" id="aiInput" placeholder="질문하기..." style="flex:1; border-radius:24px; padding:12px 18px;">
                    <button onclick="sendAiMsg()" style="background:var(--ios-blue); border:none; color:#fff; width:44px; height:44px; border-radius:50%; display:flex; align-items:center; justify-content:center; cursor:pointer; box-shadow: 0 4px 12px rgba(10,132,255,0.3);"><i class="fas fa-arrow-up" style="font-size:16px;"></i></button>
                </div>
            </div>
        </div>

        <div id="roulette-tab" class="tab-content">
            <div style="padding:40px 15px 5px; display:flex; justify-content:space-between; align-items:center;">
                <h1 style="color:var(--gold); font-size:30px; font-weight:700; letter-spacing:-1px; margin:0;"><i class="fas fa-crosshairs"></i> Black</h1>
                <span id="gameRoundBadge" style="background:var(--ios-red); padding:4px 10px; border-radius:12px; font-size:11px; font-weight:700; letter-spacing:0.3px;">대기방</span>
            </div>
            
            <div class="roulette-panel" style="margin-top:10px;">
                <div>
                    <div style="font-size:11px; color:#8e8e93; font-weight:600;">매칭 보증금 (Buy-in)</div>
                    <div style="font-size:17px; font-weight:bold; color:#fff; margin-top:2px;">₩100,000</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:11px; color:#8e8e93; font-weight:600;">현재 라운드 판돈</div>
                    <div id="roomPrizeText" style="font-size:17px; font-weight:bold; color:var(--gold); margin-top:2px;">₩0</div>
                </div>
            </div>

            <div style="background:rgba(0,0,0,0.4); border:1px solid var(--liquid-border); border-radius:24px; flex:1; display:flex; flex-direction:column; height:360px; margin-bottom:12px; box-shadow: inset 0 0 20px rgba(0,0,0,0.8);">
                <div id="rouletteMessages">
                    <div class="msg dealer">🎰 VVIP 블랙 룰렛 라운지에 오신 것을 환영합니다. 아래 버튼을 누르면 자산 인증을 완료한 동일 등급(월 소비 5,000만 원 상당)의 익명 사용자 정보가 연결됩니다.</div>
                </div>
            </div>

            <div id="rouletteControls">
                <button onclick="startRouletteMatch()" style="background:linear-gradient(135deg, #ffd700 0%, #b8860b 100%); color:#000; border:none; width:100%; padding:18px; border-radius:18px; font-weight:700; font-size:16px; cursor:pointer; box-shadow: 0 8px 25px rgba(255,215,0,0.2);">VVIP 서바이벌 매칭 시작</button>
            </div>
        </div>

        <div class="overlay" id="ovl">
            <div style="width:36px; height:5px; background:rgba(255,255,255,0.2); border-radius:5px; margin:0 auto 20px;"></div>
            <h2 id="ovlHeader" style="margin-top:0; font-size:22px; font-weight:700; letter-spacing:-0.5px;">Result</h2>
            <div id="ovlVisual" style="padding:24px; border-radius:20px; color:#fff; box-shadow: inset 0 1px 1px rgba(255,255,255,0.2), 0 10px 30px rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.1);">
                <div id="ovlName" style="font-size:18px; font-weight:800; letter-spacing:-0.3px;"></div>
                <div id="ovlRate" style="font-size:26px; margin-top:12px; font-weight:800; color:var(--gold);"></div>
                <div id="nextBestArea" style="margin-top:18px; padding-top:18px; border-top:1px solid rgba(255,255,255,0.15); display:none;">
                    <div style="font-size:11px; opacity:0.5; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Next Best Choice</div>
                    <div id="nextBestName" style="display:flex; justify-content:space-between; margin-top:6px; font-size:14px; font-weight:600;"></div>
                </div>
            </div>
            
            <div id="ovlButtonContainer" style="margin-top:auto;">
                <button onclick="closeOvl()" style="background:rgba(255,255,255,0.08); border:1px solid var(--liquid-border); color:white; border:none; width:100%; padding:18px; border-radius:16px; font-weight:700; margin-top:20px; cursor:pointer; backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px);">확인</button>
            </div>
        </div>

        <div class="nav">
            <div class="nav-item active" onclick="switchTab('wallet', this)"><i class="fas fa-wallet"></i><br>지갑</div>
            <div class="nav-item" onclick="switchTab('report', this)"><i class="fas fa-chart-bar"></i><br>인사이트</div>
            <div class="nav-item" id="navAi" onclick="switchTab('ai-tab', this)" style="display:none;"><i class="fas fa-robot"></i><br>AI</div>
            <div class="nav-item premium-tab-btn" id="navRoulette" onclick="switchTab('roulette-tab', this)"><i class="fas fa-crosshairs"></i><br>룰렛 매칭</div>
        </div>
    </div>

    <script>
        let MY_CARDS_DATA = []; let STATS_DATA = {}; const MERCHANTS = {{ merchants | tojson }};
        let SESSION_USER_NAME = null; let CURRENT_AGE = "30";
        let CURRENT_ROOM_ID = null;

        const NAME_MAP_JS = {{ NAME_ENG_MAP | tojson }};

        function startOnboarding() {
            document.getElementById('welcome-screen').style.opacity = '0';
            setTimeout(() => {
                document.getElementById('welcome-screen').style.display = 'none';
                document.getElementById('onboarding').style.transform = 'translateY(0)';
            }, 500);
        }

        async function finishOnboarding() {
            CURRENT_AGE = document.getElementById('userAge').value;
            const res = await fetch(`/api/cards?age=${CURRENT_AGE}`);
            const data = await res.json();
            MY_CARDS_DATA = data.cards; STATS_DATA = data.stats; SESSION_USER_NAME = data.session_name;
            renderCards(); updateDash();
            
            const isAiChecked = document.getElementById('premiumToggle').checked;
            const isRouletteChecked = document.getElementById('rouletteToggle').checked;

            if(isAiChecked) {
                document.getElementById('navAi').style.display = 'block';
            } else {
                document.getElementById('navAi').style.display = 'none';
            }
            
            if(isRouletteChecked) {
                document.getElementById('navRoulette').style.display = 'block';
            } else {
                document.getElementById('navRoulette').style.display = 'none';
            }
            
            document.getElementById('onboarding').style.transform = 'translateY(-100%)'; 
            updateLoc();

            if (!isAiChecked && !isRouletteChecked) {
                triggerRandomAdPopup();
            }
        }

        async function triggerRandomAdPopup() {
            const res = await fetch('/get-random-ad');
            const adCard = await res.json();
            
            const ovl = document.getElementById('ovl');
            document.getElementById('ovlHeader').innerText = "💡 맞춤형 추천 마켓 상품";
            document.getElementById('ovlVisual').style.background = adCard.color;
            
            document.getElementById('ovlName').innerHTML = `
                <div style="font-size: 13px; opacity: 0.7; margin-bottom:4px; font-weight:600;">${adCard.company}</div>
                <div style="font-size: 22px; font-weight: 800; line-height: 1.2; letter-spacing:-0.5px;">${adCard.name}</div>
            `;
            
            let benefitHtml = '<div style="display:grid; gap:8px; margin-top:16px;">';
            for(let [cat, rate] of Object.entries(adCard.benefits)) {
                benefitHtml += `
                    <div style="display:flex; justify-content:space-between; background:rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.05); padding:10px 14px; border-radius:12px; font-size:13px;">
                        <span>${cat} 영역</span>
                        <span style="font-weight:700; color:var(--gold);">${(rate*100).toFixed(0)}% 청구할인</span>
                    </div>`;
            }
            benefitHtml += '</div>';
            
            document.getElementById('ovlRate').innerHTML = benefitHtml;
            document.getElementById('nextBestArea').style.display = 'none';
            
            document.getElementById('ovlButtonContainer').innerHTML = `
                <button onclick="window.open('${adCard.url}', '_blank')" style="background:var(--gold); color:#000; border:none; width:100%; padding:18px; border-radius:16px; font-weight:800; font-size:15px; margin-top:15px; cursor:pointer; box-shadow:0 8px 20px rgba(255,215,0,0.25);"><i class="fas fa-external-link-alt"></i> 카드사 상세 혜택 알아보기</button>
                <button onclick="closeOvl()" style="background:rgba(255,255,255,0.06); border:1px solid var(--liquid-border); color:white; border:none; width:100%; padding:14px; border-radius:16px; font-weight:700; margin-top:10px; cursor:pointer;">닫기</button>
            `;
            
            ovl.classList.add('active');
        }

        function renderCards() {
            const container = document.getElementById('cardContainer'); 
            container.innerHTML = "";
            
            const credits = MY_CARDS_DATA.filter(c => c.type === 'Credit');
            const debits = MY_CARDS_DATA.filter(c => c.type === 'Debit');

            if (credits.length > 0) {
                const header = document.createElement('div');
                header.className = 'section-header'; header.innerText = 'Credit Cards';
                container.appendChild(header);

                const stack = document.createElement('div');
                stack.className = 'card-stack';
                stack.style.height = (210 + (credits.length - 1) * 35) + 'px';
                credits.forEach((card, i) => stack.appendChild(createCardUI(card, i)));
                container.appendChild(stack);
            }

            if (debits.length > 0) {
                const header = document.createElement('div');
                header.className = 'section-header'; header.innerText = 'Debit Cards';
                container.appendChild(header);

                const stack = document.createElement('div');
                stack.className = 'card-stack';
                stack.style.height = (210 + (debits.length - 1) * 35) + 'px';
                debits.forEach((card, i) => stack.appendChild(createCardUI(card, i)));
                container.appendChild(stack);
            }
        }

        function createCardUI(card, i) {
            const div = document.createElement('div'); 
            div.className = 'card'; div.style.background = card.color;
            div.style.top = `${i*35}px`; div.style.zIndex = i+1; 
            div.onclick = (e) => { e.stopPropagation(); showCardDetail(card.id); };
            
            const engName = NAME_MAP_JS[SESSION_USER_NAME] || "CARD HOLDER";
            
            let brandHtml = "";
            if (card.brand === "VISA") {
                brandHtml = `<div class="brand-visa-text">VISA<span>.</span></div>`;
            } else {
                brandHtml = `
                    <div class="brand-master-circles">
                        <div class="brand-circle circle-red"></div>
                        <div class="brand-circle circle-yellow"></div>
                    </div>
                `;
            }
            
            div.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; font-size:15px; letter-spacing:-0.3px; text-shadow: 0 1px 2px rgba(0,0,0,0.5);">${card.company}</span>
                </div>
                <div style="font-size:22px; font-weight:800; margin-top:24px; letter-spacing:-0.8px; text-shadow: 0 2px 5px rgba(0,0,0,0.4);">${card.name}</div>
                <div class="card-type-badge">${card.type}</div>
                <div style="position:absolute; bottom:54px; left:24px; font-family: monospace; font-size:14px; letter-spacing:1.5px; opacity:0.85; text-shadow: 0 1px 2px rgba(0,0,0,0.6);">•••• •••• •••• ${card.last_digits}</div>
                <div style="position:absolute; bottom:22px; left:24px; font-size:11px; font-weight:600; letter-spacing:0.5px; opacity:0.9; text-transform:uppercase;">${engName}</div>
                <div class="card-brand-area">
                    ${brandHtml}
                </div>
            `;
            return div;
        }

        function updateDash() {
            document.getElementById('totalBenefitText').innerText = `₩${STATS_DATA.total_benefit.toLocaleString()}`;
            document.getElementById('ageStrategyTitle').innerText = CURRENT_AGE + "대 생애주기 전략";
            const credits = MY_CARDS_DATA.filter(c => c.type === 'Credit');
            document.getElementById('limitText').innerText = credits.length ? `${credits[0].company} 실적 충족 ${STATS_DATA.limit_percent}%` : "신용카드 없음";
            document.getElementById('pruningText').innerText = credits.length > 1 ? "미사용 카드 정리 제안" : "최적의 구성";
        }
        function updateLoc() {
            const m = MERCHANTS.find(m => m.id == document.getElementById('mSelect').value);
            if(!m) return;
            document.getElementById('displayLoc').innerText = m.name;
            const mapUrl = `https://static-maps.yandex.ru/1.x/?lang=en_US&ll=${m.lng},${m.lat}&z=16&l=map&size=450,200`;
            document.getElementById('mapView').style.backgroundImage = `linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url('${mapUrl}')`;
        }
        function showCardDetail(id) {
            const card = MY_CARDS_DATA.find(c => c.id === id); const ovl = document.getElementById('ovl');
            document.getElementById('ovlHeader').innerText = card.name + " 혜택";
            let list = '<div style="display:grid; gap:8px;">';
            for(let [cat, rate] of Object.entries(card.benefits)) {
                if(rate > 0) {
                    list += `<div style="display:flex; justify-content:space-between; background:rgba(0,0,0,0.2); border:1px solid rgba(255,255,255,0.05); padding:10px 14px; border-radius:12px; font-size:13px;"><span>${cat}</span><span style="font-weight:700; color:var(--ios-blue);">${(rate*100).toFixed(1)}%</span></div>`;
                }
            }
            document.getElementById('ovlName').innerHTML = list + '</div>';
            document.getElementById('ovlRate').innerText = ""; document.getElementById('nextBestArea').style.display = 'none';
            document.getElementById('ovlVisual').style.background = card.color;
            
            document.getElementById('ovlButtonContainer').innerHTML = `
                <button onclick="closeOvl()" style="background:rgba(255,255,255,0.1); border:1px solid var(--liquid-border); color:white; border:none; width:100%; padding:18px; border-radius:16px; font-weight:700; margin-top:20px; cursor:pointer; backdrop-filter:blur(10px);">확인</button>
            `;
            ovl.classList.add('active');
        }
        function recommend() {
            const m = MERCHANTS.find(m => m.id == document.getElementById('mSelect').value);
            
            const sorted = [...MY_CARDS_DATA].sort((a,b) => {
                let a_rate = a.benefits[m.category] || 0;
                let b_rate = b.benefits[m.category] || 0;
                return b_rate - a_rate;
            });
            
            const best = sorted[0]; const next = sorted[1];
            document.getElementById('ovlHeader').innerText = "Optimize Strategy";
            document.getElementById('ovlVisual').style.background = best.color;
            document.getElementById('ovlName').innerText = best.name;
            
            if (best.current_performance < best.performance_limit) {
                document.getElementById('ovlRate').innerText = ((best.benefits[m.category]||0)*100).toFixed(1) + "% Reward (전월 실적 미달로 현재 사용 불가)";
            } else {
                document.getElementById('ovlRate').innerText = ((best.benefits[m.category]||0)*100).toFixed(1) + "% Reward";
            }
            
            if(next && next.benefits[m.category]) {
                document.getElementById('nextBestArea').style.display = 'block';
                let next_rate = next.current_performance >= next.performance_limit ? ((next.benefits[m.category]*100).toFixed(1) + "%") : "실적 미달";
                document.getElementById('nextBestName').innerHTML = `<span>${next.name}</span><span style="color:var(--gold);">${next_rate}</span>`;
            } else { document.getElementById('nextBestArea').style.display = 'none'; }
            
            document.getElementById('ovlButtonContainer').innerHTML = `
                <button onclick="closeOvl()" style="background:rgba(255,255,255,0.1); border:1px solid var(--liquid-border); color:white; border:none; width:100%; padding:18px; border-radius:16px; font-weight:700; margin-top:20px; cursor:pointer; backdrop-filter:blur(10px);">확인</button>
            `;
            document.getElementById('ovl').classList.add('active');
        }
        function triggerStatsPopup() {
            const ovl = document.getElementById('ovl'); document.getElementById('ovlHeader').innerText = "Benefit Analysis";
            document.getElementById('ovlVisual').style.background = "linear-gradient(135deg, #1f1f2e 0%, #111116 100%)";
            document.getElementById('ovlName').innerHTML = `<span style="color:var(--ios-red); font-size:20px; font-weight:700;">손실 방어: ₩${Math.floor(STATS_DATA.total_benefit*0.82).toLocaleString()}</span>`;
            document.getElementById('ovlRate').innerText = "+12.4% 개선됨";
            document.getElementById('nextBestArea').style.display = 'none'; 
            document.getElementById('ovlButtonContainer').innerHTML = `
                <button onclick="closeOvl()" style="background:rgba(255,255,255,0.1); border:1px solid var(--liquid-border); color:white; border:none; width:100%; padding:18px; border-radius:16px; font-weight:700; margin-top:20px; cursor:pointer; backdrop-filter:blur(10px);">확인</button>
            `;
            ovl.classList.add('active');
        }
        function triggerLimitPopup() {
            const ovl = document.getElementById('ovl'); const credits = MY_CARDS_DATA.filter(c => c.type === 'Credit');
            if(!credits.length) return; document.getElementById('ovlHeader').innerText = "실적 충족 현황";
            document.getElementById('ovlVisual').style.background = credits[0].color;
            document.getElementById('ovlName').innerText = credits[0].name;
            document.getElementById('ovlRate').innerText = STATS_DATA.limit_percent + "% 달성";
            document.getElementById('nextBestArea').style.display = 'none'; 
            document.getElementById('ovlButtonContainer').innerHTML = `
                <button onclick="closeOvl()" style="background:rgba(255,255,255,0.1); border:1px solid var(--liquid-border); color:white; border:none; width:100%; padding:18px; border-radius:16px; font-weight:700; margin-top:20px; cursor:pointer; backdrop-filter:blur(10px);">확인</button>
            `;
            ovl.classList.add('active');
        }
        function triggerPruningPopup() {
            const ovl = document.getElementById('ovl'); document.getElementById('ovlHeader').innerText = "카드 최적화";
            document.getElementById('ovlVisual').style.background = "linear-gradient(135deg, #14351f 0%, #081a10 100%)";
            document.getElementById('ovlName').innerText = MY_CARDS_DATA.length > 2 ? MY_CARDS_DATA[MY_CARDS_DATA.length-1].name : "추가 정리 대상 없음";
            document.getElementById('ovlRate').innerText = MY_CARDS_DATA.length > 2 ? "사용 빈도 낮음 (정리 권장)" : "최적 유지 중";
            document.getElementById('nextBestArea').style.display = 'none'; 
            document.getElementById('ovlButtonContainer').innerHTML = `
                <button onclick="closeOvl()" style="background:rgba(255,255,255,0.1); border:1px solid var(--liquid-border); color:white; border:none; width:100%; padding:18px; border-radius:16px; font-weight:700; margin-top:20px; cursor:pointer; backdrop-filter:blur(10px);">확인</button>
            `;
            ovl.classList.add('active');
        }
        async function triggerAgeBridgePopup() {
            const res = await fetch(`/api/age-strategy?age=${CURRENT_AGE}`); const strat = await res.json();
            const ovl = document.getElementById('ovl'); document.getElementById('ovlHeader').innerText = `${CURRENT_AGE}대 라이프스타일 추천`;
            document.getElementById('ovlVisual').style.background = strat.color;
            document.getElementById('ovlName').innerHTML = `<i class="fas ${strat.logo}" style="margin-right:10px;"></i>${strat.card}`;
            document.getElementById('ovlRate').innerText = "AI 전략 카드";
            document.getElementById('nextBestArea').style.display = 'none'; 
            document.getElementById('ovlButtonContainer').innerHTML = `
                <button onclick="closeOvl()" style="background:rgba(255,255,255,0.1); border:1px solid var(--liquid-border); color:white; border:none; width:100%; padding:18px; border-radius:16px; font-weight:700; margin-top:20px; cursor:pointer; backdrop-filter:blur(10px);">확인</button>
            `;
            ovl.classList.add('active');
        }
        async function sendAiMsg() {
            const input = document.getElementById('aiInput'); const text = input.value; if(!text) return;
            const msgBox = document.getElementById('chatMessages');
            msgBox.innerHTML += `<div class="msg user">${text}</div>`; input.value = "";
            try {
                const res = await fetch('/api/ai-ask', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ query: text, data: {cards: MY_CARDS_DATA, stats: STATS_DATA}, session_name: SESSION_USER_NAME })
                });
                const data = await res.json(); msgBox.innerHTML += `<div class="msg ai">${marked.parse(data.answer)}</div>`;
            } catch (e) { msgBox.innerHTML += `<div class="msg ai">서버 응답 오류가 발생했습니다.</div>`; }
            msgBox.scrollTop = msgBox.scrollHeight;
        }
        function switchTab(id, el) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById(id).classList.add('active'); el.classList.add('active');
        }
        function closeOvl() { document.getElementById('ovl').classList.remove('active'); }

        async function startRouletteMatch() {
            const msgBox = document.getElementById('rouletteMessages');
            msgBox.innerHTML += `<div class="msg dealer"><i class="fas fa-circle-notch cylinder-spin"></i> 계정 원장 심사 완료. 동등한 카드 스케일의 익명 유저 검색 중...</div>`;
            
            const res = await fetch('/api/roulette/match', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_name: SESSION_USER_NAME, user_cards: MY_CARDS_DATA })
            });
            const data = await res.json();
            CURRENT_ROOM_ID = data.room_id;
            
            setTimeout(() => {
                msgBox.innerHTML = "";
                document.getElementById('gameRoundBadge').innerText = "1 ROUND";
                document.getElementById('roomPrizeText').innerText = `₩${data.prize.toLocaleString()}`;
                msgBox.innerHTML += `<div class="msg dealer">🔺 통신 연결 성공. 비밀 서바이벌 룸에 익명의 자산가 [${data.opponent_hidden_name}] 님이 입장했습니다.</div>`;
                msgBox.innerHTML += `<div class="msg ai">${marked.parse(data.dealer_comment)}</div>`;
                
                document.getElementById('rouletteControls').innerHTML = `
                    <div class="action-grid">
                        <button onclick="submitGameChoice('TRUST')" class="btn-game btn-trust"><i class="fas fa-heart"></i> 신뢰 (Trust)</button>
                        <button onclick="submitGameChoice('BETRAY')" class="btn-game btn-betray"><i class="fas fa-skull"></i> 배신 (Betray)</button>
                    </div>
                `;
            }, 1200);
        }

        async function submitGameChoice(choice) {
            const msgBox = document.getElementById('rouletteMessages');
            msgBox.innerHTML += `<div class="msg user">${choice === 'TRUST' ? '상대를 믿고 생존(Trust)을 선택했습니다.' : '독식을 목적으로 배신(Betray)을 당겼습니다.'}</div>`;
            
            const res = await fetch('/api/roulette/choice', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ room_id: CURRENT_ROOM_ID, choice: choice, user_name: SESSION_USER_NAME })
            });
            const data = await res.json();
            
            msgBox.innerHTML += `<div class="msg dealer">철컥... 실린더 계산 완료. 룰렛 정산 결과 발표합니다.</div>`;
            msgBox.innerHTML += `<div class="msg ai">${marked.parse(data.result_text)}</div>`;
            
            if (data.status === 'CONTINUE') {
                document.getElementById('gameRoundBadge').innerText = data.next_round + " ROUND";
                document.getElementById('roomPrizeText').innerText = `₩${data.prize.toLocaleString()}`;
            } else {
                document.getElementById('gameRoundBadge').innerText = "종료";
                document.getElementById('rouletteControls').innerHTML = `
                    <button onclick="startRouletteMatch()" style="background:linear-gradient(135deg, #ffd700 0%, #b8860b 100%); color:#000; border:none; width:100%; padding:18px; border-radius:18px; font-weight:700; font-size:16px; cursor:pointer;">새로운 서바이벌 매칭 시작</button>
                `;
            }
            msgBox.scrollTop = msgBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): 
    current_merchants = fetch_merchants_from_db()
    return render_template_string(HTML_TEMPLATE, merchants=current_merchants, NAME_ENG_MAP=NAME_ENG_MAP)

@app.route('/get-random-ad')
def get_random_ad():
    return jsonify(random.choice(MARKET_CARDS))

@app.route('/api/cards')
def api_cards():
    age = request.args.get('age', '30')
    cards = get_cards_by_age(age)
    
    total_benefit = 0
    for card in cards:
        if card["current_performance"] >= card["performance_limit"]:
            total_benefit += min(random.randint(15000, 45000), card["total_limit"] * 2) - int(card["annual_fee"] / 12)
    if total_benefit <= 0:
        total_benefit = (int(age) * 14000) + random.randint(2000, 20000)
        
    session_name = random.choice(KOREAN_NAMES)
    return jsonify({"cards": cards, "stats": {"total_benefit": int(total_benefit), "limit_percent": random.randint(86, 99)}, "session_name": session_name})

@app.route('/api/age-strategy')
def api_age_strategy():
    age = request.args.get('age', '30')
    strat = AGE_STRATEGY_DATA.get(age, AGE_STRATEGY_DATA["30"])
    return jsonify(strat)

@app.route('/api/ai-ask', methods=['POST'])
def api_ai_ask():
    req = request.json
    current_user_name = req.get('session_name', random.choice(KOREAN_NAMES))
    
    exclusion_clause = ""
    if "공과금" in req['query'] or "상품권" in req['query'] or "세금" in req['query']:
        exclusion_clause = "주의: 해당 요청은 국내 카드 혜택 제외 가맹점 대상(상품권/공과금 등)이므로 예상 혜택율은 0%로 고정 계산되어야 합니다."

    prompt = {
        "contents": [{"parts": [{"text": f"""
            역할: 금융 전문가 'CardBridge AI' / 대상: {current_user_name}님
            현재 보유 카드: {json.dumps(req['data']['cards'])}
            현재 실적 상태: {json.dumps(req['data']['stats'])}
            사용자 질문: "{req['query']}"
            제외대상 필터링 정보: {exclusion_clause}
            
            [수행 지침 - 상황별 맞춤 응답]
            1. [특정 장소/활동에 대한 카드 추천 요청 시]: 보유 카드 내에서만 추천.
            2. [실적/데이터 분석 및 최적화 요청 시]: 보유 카드(X)와 시장 카드(Y) 비교 진단.

            [출력 양식 - 마크다운 표 엄수]
            ---
            ### 🏆 {current_user_name}님을 위한 [맞춤 추천 / 진단 결과]
            **전략: [카드사 명] [카드 이름]**
            
            | 비교/분석 항목 | 내용 |
            | :--- | :--- |
            | 선택된 분야 | [분야] |
            | 예상 혜택율 | **[00.0]%** |
            
            [실적 분석 요청인 경우에만 아래 표 추가]
            | 구분 | 보유 카드 (X) | 추천 카드 (Y) |
            | :--- | :--- | :--- |
            | 혜택 차이 | [기존]% | **[신규]%** |
            ---
            - 추천 이유: {current_user_name}님의 데이터를 근거로 위트 있게 설명.
        """}]}]
    }
    try:
        URL = "https://generativelanguage.googleapis.com/v1beta/models/" + MODEL_NAME + ":generateContent?key=" + API_KEY
        response = requests.post(URL, json=prompt, timeout=12)
        res_json = response.json()
        if 'candidates' in res_json:
            return jsonify({"answer": res_json['candidates'][0]['content']['parts'][0]['text']})
        return jsonify({"answer": f"죄송합니다 {current_user_name}님, 다시 시도해주세요."})
    except Exception as e: return jsonify({"answer": "시스템 오류입니다."})

@app.route('/api/roulette/match', methods=['POST'])
def roulette_match():
    req = request.json
    user_name = req.get('user_name', '참가자')
    room_id = f"ROOM_{random.randint(1000, 9999)}"
    
    # DB에서 1차(소비패턴), 2차(프로필), 3차(부동산 및 자산) 묶음을 원스톱으로 서칭
    opponent, opp_cats, opp_profile, opp_estate = fetch_opponent_from_db(user_name)
    
    ROULETTE_ROOMS[room_id] = {
        "user_name": user_name,
        "opponent": opponent,
        "round": 1,
        "prize": 100000,  
        "opp_cats": opp_cats,
        "opp_profile": opp_profile,
        "opp_estate": opp_estate
    }
    
    prompt_text = f"""
    역할: 데스매치 서바이벌의 냉혹한 'AI 악마 딜러'
    상황: 1라운드 매칭 개시
    플레이어: {user_name} (본인) VS {opponent} (상대방)
    상대방의 1차 정보(소비): {json.dumps(opp_cats)}
    
    [출력 규칙 - 텍스트는 최소화하고 아이콘/대시보드 형태로 구성]
    1. 쓸데없는 미사여구와 줄글 설명을 전부 제거하고 콤팩트하게 구성하라.
    2. 아래 마크다운 템플릿의 형태를 반드시 엄수하여 출력하라. 카테고리 종류에 걸맞은 적절한 아이콘 이모지(⛳, 🛍️, 🍔, ☕, 🚗, 🏪, 🏥)를 활용하라.

    [고정 출력 포맷]
    ---
    ### ⚔️ ROUND 1 매칭 완료
    **{user_name}** (YOU)  vs  **{opponent}** (OPPONENT)
    
    | 📊 상대방 VVIP 소비 분석 레이더 | 비중 |
    | :--- | :--- |
    | [적절한 이모지] [가장 높은 카테고리명] | **[해당비중]** (최대 소비) |
    | [적절한 이모지] [두번째 카테고리명] | [해당비중] |
    | [적절한 이모지] [세번째 카테고리명] | [해당비중] |
    
    🚨 **딜러의 경고**: 상대는 당신의 보증금을 사냥하기 위해 움직이기 시작했습니다. 맹목적인 '신뢰'인가, 생존을 위한 '배신'인가. 선택하십시오.
    ---
    """
    
    dealer_comment = "룰렛 하우스 통신망 장애... 하지만 생존 권총 장전은 완료되었습니다."
    try:
        URL = "https://generativelanguage.googleapis.com/v1beta/models/" + MODEL_NAME + ":generateContent?key=" + API_KEY
        res = requests.post(URL, json={"contents": [{"parts": [{"text": prompt_text}]}]}, timeout=10)
        res_json = res.json()
        if 'candidates' in res_json:
            dealer_comment = res_json['candidates'][0]['content']['parts'][0]['text']
    except: pass

    return jsonify({
        "room_id": room_id,
        "opponent_hidden_name": opponent,
        "prize": 100000,
        "dealer_comment": dealer_comment
    })

@app.route('/api/roulette/choice', methods=['POST'])
def roulette_choice():
    req = request.json
    room_id = req.get('room_id')
    user_choice = req.get('choice')
    
    if room_id not in ROULETTE_ROOMS:
        return jsonify({"status": "ERROR", "result_text": "만료되거나 존재하지 않는 매칭방입니다."})
        
    room = ROULETTE_ROOMS[room_id]
    opp_choice = "TRUST" if random.random() > (0.25 * room["round"]) else "BETRAY"
    
    status = "CONTINUE"
    result_title = ""
    
    if user_choice == "TRUST" and opp_choice == "TRUST":
        room["round"] += 1
        room["prize"] += 50000  
        result_title = "MUTUAL_TRUST"
    elif user_choice == "TRUST" and opp_choice == "BETRAY":
        status = "GAME_OVER"
        result_title = "USER_BETRAYED"
    elif user_choice == "BETRAY" and opp_choice == "TRUST":
        status = "USER_WIN_EAT"
        result_title = "USER_MUG_TAE"
    else:
        status = "DOUBLE_KILL"
        result_title = "BOTH_BETRAY"

    # [수정 반영] 라운드 수에 따라 2차 정보(2라운드) 및 3차 정보(3라운드) 대시보드가 오픈되도록 마크다운 설계
    next_info_block = ""
    if status == "CONTINUE" and room["round"] == 2:
        next_info_block = f"""
        \n### 🔓 2대 영역 해금: 상대방 신상 프로필 명세서
        | 프로필 항목 | 데이터 정보 |
        | :--- | :--- |
        | 🩸 혈액형 | {room['opp_profile']['blood']}형 |
        | 📏 신장 (키) | {room['opp_profile']['height']} |
        | 💼 현직 업종 | **{room['opp_profile']['job']}** |
        """
    elif status == "CONTINUE" and room["round"] == 3:
        next_info_block = f"""
        \n### 👑 3대 영역 해금: 상대방 하이엔드 자산 원장
        | 자산 검증 항목 | 데이터 정보 |
        | :--- | :--- |
        | 🏠 자가 소유 여부 | {room['opp_estate']['home_owner']} |
        | 📍 부동산 실위치 | {room['opp_estate']['home_loc']} |
        | 🏎️ 보유 차량 브랜드 | **{room['opp_estate']['car']}** |
        """

    prompt_text = f"""
    역할: 데스매치 게임 중계 AI 진행자
    결과 상태 코드: {result_title}
    참가자 명: {room['user_name']} ({user_choice} 선택)
    상대방 명: {room['opponent']} ({opp_choice} 선택)
    현재 총 예치 판돈: ₩{room['prize']}
    
    [출력 가이드]
    1. 긴 줄글 해설을 완전히 배제하고, 라운드 스코어 보드처럼 간결하게 표시하라.
    2. 상황에 맞는 직관적인 대형 결과 이모지(✅, ❌, 👑, 💀)를 배치하라.
    3. 하단에 주어지는 다음 라운드 데이터 블록을 누락 없이 본문에 붙여서 출력하라.
    
    [고정 출력 포맷]
    ---
    ### 🛎️ 정산 결과: [{result_title} 상황에 맞는 한글 요약문구]
    
    | 플레이어 | 선택 | 결과 |
    | :--- | :--- | :--- |
    | 👤 {room['user_name']} (YOU) | {user_choice} | [성공/사망/독식 등] |
    | 👥 {room['opponent']} | {opp_choice} | [성공/사망/독식 등] |
    
    💰 **누적 판돈 원장**: **₩{room['prize']:,}**
    {next_info_block}
    
    [결과별 핵심 코멘트 (1줄 고정)]
    - MUTUAL_TRUST인 경우: "공동 생존 성공. 판돈이 증액되어 다음 라운드로 연장됩니다."
    - USER_BETRAYED인 경우: "완벽히 이용당했습니다. 보증금이 전액 강탈되었습니다."
    - USER_MUG_TAE인 경우: "포식 성공. 적의 예치금을 전액 강탈하여 처단했습니다."
    - BOTH_BETRAY인 경우: "동시 배신. 공멸하여 모든 보증금은 하우스로 귀속 몰수됩니다."
    ---
    """
    
    result_text = "총기 해체 연산 에러..."
    try:
        URL = "https://generativelanguage.googleapis.com/v1beta/models/" + MODEL_NAME + ":generateContent?key=" + API_KEY
        res = requests.post(URL, json={"contents": [{"parts": [{"text": prompt_text}]}]}, timeout=10)
        res_json = res.json()
        if 'candidates' in res_json:
            result_text = res_json['candidates'][0]['content']['parts'][0]['text']
    except: pass

    return jsonify({
        "status": status,
        "next_round": room["round"],
        "prize": room["prize"],
        "result_text": result_text
    })

if __name__ == '__main__':
#    app.run(debug=True, port=5003)
     app.run(debug=True, host='0.0.0.0', port=5003)
