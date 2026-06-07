USE cardbridge_db;

-- =========================================================================
-- 1. 기존 테이블 구조 보완 (문법 에러 방지용 표준 방식으로 변경)
-- =========================================================================

-- cards 테이블에 컬럼 추가 (이미 존재하면 에러를 무시하고 진행하도록 분리)
-- 만약 이미 수동으로 넣으셨다면 에러가 나도 무시하고 다음 줄로 넘어갑니다.
ALTER TABLE cards ADD COLUMN performance_limit INT DEFAULT 300000;
ALTER TABLE cards ADD COLUMN total_limit INT DEFAULT 10000;
ALTER TABLE cards ADD COLUMN annual_fee INT DEFAULT 0;

-- merchants 테이블에 국내 표준 가맹점 업종 코드(MCC) 컬럼 추가
ALTER TABLE merchants ADD COLUMN mcc_code VARCHAR(10) DEFAULT 'O000';


-- =========================================================================
-- 2. 신규 추가 컬럼 데이터 업데이트 (현실 스펙 반영)
-- =========================================================================

-- [cards] 신용카드(Credit)와 체크카드(Debit)의 현실적인 실적/한도/연회비 밸런싱
UPDATE cards SET performance_limit = 300000, total_limit = 15000, annual_fee = 15000 WHERE card_type = 'Credit';
UPDATE cards SET performance_limit = 500000, total_limit = 30000, annual_fee = 30000 WHERE name IN ('Zero Gold', 'M Boost');

-- 체크카드 스펙 업데이트
UPDATE cards SET performance_limit = 200000, total_limit = 5000, annual_fee = 0 WHERE card_type = 'Debit';


-- [merchants] 국내 표준 가맹점 업종 코드(MCC) 매핑 현황 반영
UPDATE merchants SET mcc_code = 'O001' WHERE category = 'Cafe';
UPDATE merchants SET mcc_code = 'O002' WHERE category = 'Food';
UPDATE merchants SET mcc_code = 'O003' WHERE category = 'Gas';
UPDATE merchants SET mcc_code = 'O004' WHERE category = 'Shopping';
UPDATE merchants SET mcc_code = 'O005' WHERE category = 'CV';
UPDATE merchants SET mcc_code = 'O006' WHERE category = 'Hospital';
UPDATE merchants SET mcc_code = 'O007' WHERE category = 'Golf';


-- =========================================================================
-- 3. card_benefits 테이블 데이터 촘촘하게 추가 (Seed 데이터 보강)
-- =========================================================================
-- 중복 키 에러를 방지하기 위해 INSERT IGNORE 또는 ON DUPLICATE KEY UPDATE를 적용했습니다.

INSERT INTO card_benefits (card_id, category, reward_rate) VALUES
(1, 'Gas', 0.015), (1, 'CV', 0.012),
(2, 'Cafe', 0.200), (2, 'Food', 0.050), (2, 'CV', 0.050),
(3, 'Shopping', 0.070), (3, 'Cafe', 0.100), (3, 'CV', 0.050),
(4, 'Cafe', 0.200), (4, 'Food', 0.050), (4, 'Hospital', 0.050),
(5, 'Cafe', 0.013), (5, 'Food', 0.013), (5, 'Shopping', 0.013), (5, 'Gas', 0.013), (5, 'CV', 0.013), (5, 'Hospital', 0.013), (5, 'Golf', 0.013),
(6, 'Shopping', 0.050), (6, 'Cafe', 0.050), (6, 'Food', 0.030),
(7, 'Shopping', 0.017), (7, 'Cafe', 0.007), (7, 'Food', 0.007),
(8, 'Shopping', 0.003), (8, 'Cafe', 0.003), (8, 'CV', 0.003),
(9, 'Gas', 0.100), (9, 'CV', 0.050), (9, 'Food', 0.010),
(10, 'Shopping', 0.100), (10, 'Cafe', 0.300), (10, 'CV', 0.050),
(11, 'Hospital', 0.015), (11, 'Food', 0.015), (11, 'Cafe', 0.015), (11, 'Shopping', 0.015),
(12, 'Cafe', 0.050), (12, 'Shopping', 0.030), (12, 'Food', 0.020), (12, 'Gas', 0.020),
(13, 'Shopping', 0.020), (13, 'Food', 0.010),
(14, 'Cafe', 0.002), (14, 'Food', 0.002), (14, 'Shopping', 0.002), (14, 'Gas', 0.002), (14, 'CV', 0.002),
(15, 'Food', 0.015), (15, 'Cafe', 0.015), (15, 'CV', 0.015),
(16, 'Shopping', 0.022), (16, 'Cafe', 0.010), (16, 'Food', 0.010)
ON DUPLICATE KEY UPDATE reward_rate = VALUES(reward_rate);