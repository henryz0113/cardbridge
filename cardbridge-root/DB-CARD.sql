-- Create and use the database
CREATE DATABASE IF NOT EXISTS cardbridge_db;
USE cardbridge_db;

-- 1. Merchants Table (20 Entries)
CREATE TABLE IF NOT EXISTS merchants (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    lat DECIMAL(9,6),
    lng DECIMAL(9,6)
);

INSERT INTO merchants (id, name, category, lat, lng) VALUES
('S1', '스타벅스 금호역점', 'Cafe', 37.548, 127.023),
('S2', '맥도날드 한남점', 'Food', 37.534, 127.009),
('S3', 'SK에너지 강남주유소', 'Gas', 37.525, 127.039),
('S4', '루이비통 메종 서울', 'Shopping', 37.525, 127.042),
('S5', 'GS25 카이스트점', 'CV', 37.592, 127.046),
('S6', '강남 세브란스 병원', 'Hospital', 37.492, 127.046),
('S7', '아웃백 스테이크하우스', 'Food', 37.517, 127.040),
('S8', '현대오일뱅크 신사', 'Gas', 37.521, 127.022),
('S9', '신세계백화점 본점', 'Shopping', 37.560, 126.981),
('S10', '남서울 CC', 'Golf', 37.378, 127.098),
('S11', '블루보틀 성수', 'Cafe', 37.543, 127.044),
('S12', '파이브가이즈 강남', 'Food', 37.502, 127.025),
('S13', 'S-OIL 망원점', 'Gas', 37.556, 126.901),
('S14', '무신사 스탠다드 홍대', 'Shopping', 37.555, 126.923),
('S15', 'CU 서울역점', 'CV', 37.555, 126.971),
('S16', '아산병원 송파', 'Hospital', 37.526, 127.108),
('S17', '잭니클라우스 GC', 'Golf', 37.382, 126.634),
('S18', '투썸플레이스 여의도', 'Cafe', 37.521, 126.924),
('S19', '신선설농탕 잠실', 'Food', 37.511, 127.103),
('S20', '갤러리아 명품관', 'Shopping', 37.528, 127.041);

-- 2. Cards Table (16 Entries)
CREATE TABLE IF NOT EXISTS cards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company VARCHAR(50),
    name VARCHAR(100),
    card_type VARCHAR(20),
    color VARCHAR(20),
    logo VARCHAR(50)
);

INSERT INTO cards (company, name, card_type, color, logo) VALUES
('Shinhan', 'Deep Dream', 'Credit', '#0046FF', 'fa-gem'),
('Shinhan', 'Hey Young', 'Debit', '#00C3FF', 'fa-rocket'),
('KB', 'FinTech Special', 'Credit', '#FFBC00', 'fa-bolt'),
('KB', 'Nori Debit', 'Debit', '#6D35B3', 'fa-star'),
('Woori', 'DA@카드의정석', 'Credit', '#003A78', 'fa-landmark'),
('Woori', '오하쳌', 'Debit', '#FF8E99', 'fa-heart'),
('Hana', 'Any PLUS', 'Credit', '#008485', 'fa-infinity'),
('Hana', '트래블로그', 'Debit', '#008485', 'fa-plane'),
('Samsung', 'iD PETROL', 'Credit', '#007AFF', 'fa-gas-pump'),
('Samsung', 'iD ON', 'Credit', '#2D3E50', 'fa-shopping-cart'),
('Hyundai', 'Zero Gold', 'Credit', '#1A1A1A', 'fa-crown'),
('Hyundai', 'M Boost', 'Credit', '#E60000', 'fa-m'),
('Kakao', 'Friends Debit', 'Debit', '#FEE500', 'fa-comment'),
('Toss', 'Wide Debit', 'Debit', '#0064FF', 'fa-wallet'),
('K-Bank', 'MY Debit', 'Debit', '#333333', 'fa-k'),
('Naver', 'Pay Debit', 'Debit', '#03C75A', 'fa-n');

-- 3. Card Benefits Table (Seeding representative data)
CREATE TABLE IF NOT EXISTS card_benefits (
    card_id INT,
    category VARCHAR(50),
    reward_rate DECIMAL(5,4),
    PRIMARY KEY (card_id, category),
    FOREIGN KEY (card_id) REFERENCES cards(id)
);

-- Example Reward: Shinhan Deep Dream (ID 1) gets 5% at Cafes
INSERT INTO card_benefits (card_id, category, reward_rate) VALUES (1, 'Cafe', 0.050), (1, 'Shopping', 0.012), (1, 'Food', 0.008);
-- Example Reward: Kakao Friends Debit (ID 13) gets 10% at CV
INSERT INTO card_benefits (card_id, category, reward_rate) VALUES (13, 'CV', 0.100), (13, 'Cafe', 0.020);