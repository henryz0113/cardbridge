-- 1. 자산, 소비 패턴, 프로필, 부동산/차량 자산 통합 테이블 생성
DROP TABLE IF EXISTS user_assets;
CREATE TABLE user_assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(50) NOT NULL UNIQUE,
    monthly_consumption VARCHAR(50) NOT NULL, -- 기준 소비 규모
    -- [1차 섹터] 소비 패턴 데이터
    cat1_name VARCHAR(20) NOT NULL, cat1_val INT NOT NULL,                     
    cat2_name VARCHAR(20) NOT NULL, cat2_val INT NOT NULL,                     
    cat3_name VARCHAR(20) NOT NULL, cat3_val INT NOT NULL,
    -- [2차 섹터] 신상 프로필 데이터 (혈액형, 키, 직업)
    blood_type VARCHAR(10) NOT NULL,
    height INT NOT NULL,
    job VARCHAR(50) NOT NULL,
    -- [3차 섹터] 하이엔드 자산 데이터 (자가여부 및 위치, 차종 브랜드)
    home_owner VARCHAR(10) NOT NULL,        -- '자가' 또는 '없음'
    home_location VARCHAR(50) NOT NULL,     -- '강남구 삼성동', '없음' 등
    car_brand VARCHAR(50) NOT NULL          -- '포르쉐', '페라리', '없음' 등
);

-- 2. 그룹 A(한국 이름 8명) 및 그룹 B(별명 8명) 8대8 대칭 데이터 삽입
INSERT INTO user_assets VALUES
-- [그룹 A : 일반 회원 풀 (사용자)]
(1, '김철수', '500만원', 'CV', 50, 'Food', 35, 'Cafe', 15, 'A', 176, 'IT 대기업 개발자', '없음', '없음', '현대 아반떼'),
(2, '이영희', '1000만원', 'Shopping', 45, 'Food', 40, 'Cafe', 15, 'B', 162, '필라테스 스튜디오 원장', '자가', '성동구 금호동', 'MINI 쿠퍼'),
(3, '박지민', '3000만원', 'Shopping', 55, 'Food', 25, 'Gas', 20, 'AB', 181, '스타트업 CBO', '자가', '송파구 잠실동', 'BMW 5시리즈'),
(4, '최유진', '5000만원', 'Golf', 40, 'Shopping', 35, 'Food', 25, 'O', 168, '패션 브랜드 디렉터', '자가', '용산구 한남동', '포르쉐 마칸'),
(5, '정민호', '1억원', 'Gas', 45, 'Shopping', 35, 'Food', 20, 'B', 178, '성형외과 전문의', '자가', '강남구 압구정동', '벤츠 G바겐'),
(6, '한소라', '1억원 이상', 'Golf', 55, 'Shopping', 30, 'Hospital', 15, 'O', 170, '벤처캐피탈 파트너', '자가', '강남구 청담동', '벤틀리 컨티넨탈'),
(7, '강태윤', '5000만원', 'Food', 45, 'Gas', 35, 'Shopping', 20, 'A', 185, '건축설계사무소 소장', '자가', '서초구 반포동', '포르쉐 타이칸'),
(8, '윤서연', '3000만원', 'Food', 45, 'Shopping', 35, 'Cafe', 20, 'O', 165, '로펌 변호사', '자가', '마포구 상암동', '아우디 Q7'),

-- [그룹 B : VVIP 매칭 대상 풀 (별명)]
(9, '청담동 벨루가', '1억원 이상', 'Shopping', 50, 'Golf', 35, 'Food', 15, 'O', 173, '글로벌 커머스 대표', '자가', '강남구 청담동', '페라리 로마'),
(10, '한남동 아르망디', '1억원', 'Food', 45, 'Shopping', 35, 'Golf', 20, 'B', 180, '프라이빗 자산운용가', '자가', '용산구 한남동', '람보르기니 우루스'),
(11, '트리마제 하이엔드', '1억원 이상', 'Shopping', 60, 'Food', 25, 'Cafe', 15, 'A', 167, '갤러리 디렉터', '자가', '성동구 성수동', '애스턴마틴'),
(12, '시그니엘 펜트', '5000만원', 'Gas', 45, 'Shopping', 35, 'Food', 20, 'AB', 183, 'F&B 프랜차이즈 의장', '자가', '송파구 신천동', '포르쉐 911'),
(13, '성수동 갤러리아', '3000만원', 'Shopping', 50, 'Food', 30, 'Cafe', 20, 'A', 164, '파인아티스트', '자가', '성동구 성수동', '포르쉐 카이엔'),
(14, '갤러리아 팰리스', '3000만원', 'Food', 50, 'Shopping', 30, 'Gas', 20, 'O', 177, '회계법인 파트너', '자가', '송파구 잠실동', '벤츠 CLS'),
(15, '도곡동 타워팰리스', '1000만원', 'Shopping', 50, 'Food', 35, 'Cafe', 15, 'B', 175, '공인회계사', '자가', '강남구 도곡동', 'BMW X6'),
(16, '평창동 저택포식자', '500만원', 'CV', 45, 'Food', 40, 'Cafe', 15, 'A', 179, '웹툰 작가', '자가', '종로구 평창동', '지프 랭글러')
ON DUPLICATE KEY UPDATE monthly_consumption = VALUES(monthly_consumption);