"""Mock persona raw rows — 26개 컬럼 전부 채움.

실제 데이터셋 행 사용 금지 (저작권 + security policy).
컬럼명 기준: lock-in v1.2 §1.1 / PM v3 Section 7.2.
"""

MOCK_PERSONA_1: dict = {
    "uuid": "mock-001-seoulgi-f25",
    "age": 25,
    "sex": "F",
    "province": "서울특별시",
    "district": "강남구",
    "occupation": "마케터",
    "marital_status": "미혼",
    "military_status": "해당없음",
    "family_type": "1인 가구",
    "housing_type": "오피스텔",
    "education_level": "대학교 졸업",
    "bachelors_field": "경영학",
    "country": "Korea",
    "persona": (
        "저는 서울 강남에 사는 25세 마케터예요. "
        "트렌드에 민감하고 새로운 브랜드를 발굴하는 것을 즐깁니다."
    ),
    "professional_persona": (
        "디지털 마케팅 에이전시에서 SNS 콘텐츠 기획과 퍼포먼스 마케팅을 담당하고 있어요. "
        "데이터 기반으로 캠페인 성과를 분석하는 일에 보람을 느낍니다."
    ),
    "cultural_background": (
        "서울 토박이로 다양한 문화 행사와 팝업 스토어를 즐겨 방문해요. "
        "K-패션과 글로벌 트렌드를 함께 소화하는 편입니다."
    ),
    "family_persona": (
        "부모님과 별거하며 독립 생활 중이에요. 주말마다 가족과 브런치를 먹으며 교류합니다."
    ),
    "sports_persona": ("요가를 꾸준히 하고 있고, 봄가을에는 한강에서 러닝도 즐겨요."),
    "arts_persona": ("현대미술 전시회를 좋아하고, 온라인 드로잉 클래스를 수강 중입니다."),
    "travel_persona": (
        "매년 해외여행을 계획하며, 최근에는 도쿄와 방콕을 다녀왔어요. "
        "현지 패션 거리 탐방이 여행의 큰 목적 중 하나예요."
    ),
    "culinary_persona": (
        "새로 오픈한 레스토랑을 탐방하는 것을 즐기며, 비건 메뉴에도 관심이 높아요."
    ),
    "skills_and_expertise": "디지털 마케팅, 데이터 분석, SNS 콘텐츠 기획",
    "skills_and_expertise_list": "디지털 마케팅|데이터 분석|SNS 콘텐츠 기획",
    "hobbies_and_interests": "패션 쇼핑, 카페 투어, 영화 감상",
    "hobbies_and_interests_list": "패션 쇼핑|카페 투어|영화 감상",
    "career_goals_and_ambitions": "5년 내에 마케팅 디렉터로 성장하고 싶어요.",
}

MOCK_PERSONA_2: dict = {
    "uuid": "mock-002-busannam-m42",
    "age": 42,
    "sex": "M",
    "province": "부산광역시",
    "district": "해운대구",
    "occupation": "건축가",
    "marital_status": "기혼",
    "military_status": "전역",
    "family_type": "핵가족",
    "housing_type": "아파트",
    "education_level": "대학원 졸업",
    "bachelors_field": "건축학",
    "country": "Korea",
    "persona": (
        "부산 해운대에 사는 42세 건축가입니다. "
        "실용적이고 클래식한 스타일을 선호하며 품질을 중요하게 여깁니다."
    ),
    "professional_persona": (
        "중형 건축 설계 사무소에서 프로젝트 리드를 맡고 있습니다. "
        "주거용 건축물 설계를 주로 하며, 심미성과 기능성을 동시에 추구합니다."
    ),
    "cultural_background": (
        "부산 출신으로 바다와 도시 문화를 함께 즐기며 자랐습니다. "
        "서울과 부산의 감성 차이를 잘 이해하는 편이에요."
    ),
    "family_persona": (
        "배우자와 초등학생 자녀 두 명과 함께 살고 있어요. "
        "주말에는 가족과 함께 야외 활동을 즐깁니다."
    ),
    "sports_persona": ("등산을 좋아하고, 가끔 자전거를 타며 해안도로를 달립니다."),
    "arts_persona": ("건축 사진 촬영을 취미로 하며, 공간 디자인 전시를 자주 방문합니다."),
    "travel_persona": (
        "가족 여행은 주로 국내로 다니며, 건축물이 유명한 도시를 즐겨 찾습니다. "
        "유럽 건축 투어가 버킷리스트입니다."
    ),
    "culinary_persona": ("해산물 요리를 즐기고, 집에서 바베큐를 자주 합니다."),
    "skills_and_expertise": "건축 설계, CAD/BIM, 프로젝트 관리",
    "skills_and_expertise_list": "건축 설계|CAD/BIM|프로젝트 관리",
    "hobbies_and_interests": "등산, 건축 사진, 독서",
    "hobbies_and_interests_list": "등산|건축 사진|독서",
    "career_goals_and_ambitions": "자신의 이름을 건 건축 사무소를 열고 싶습니다.",
}

MOCK_PERSONA_3: dict = {
    "uuid": "mock-003-daeguji-f33",
    "age": 33,
    "sex": "F",
    "province": "대구광역시",
    "district": "중구",
    "occupation": "중학교 교사",
    "marital_status": "기혼",
    "military_status": "해당없음",
    "family_type": "핵가족",
    "housing_type": "아파트",
    "education_level": "대학교 졸업",
    "bachelors_field": "교육학",
    "country": "Korea",
    "persona": (
        "대구에 사는 33세 중학교 교사예요. 단정하고 실용적인 옷차림을 좋아하며 가성비를 중시합니다."
    ),
    "professional_persona": (
        "중학교에서 국어를 가르치고 있어요. "
        "학생들과 소통하는 것을 좋아하며 방과후 독서 클럽도 운영합니다."
    ),
    "cultural_background": (
        "대구에서 나고 자라 지역 문화에 애착이 강해요. 지역 축제와 골목 상권을 자주 이용합니다."
    ),
    "family_persona": (
        "남편과 두 살배기 아이와 함께 살고 있어요. "
        "육아와 직장을 병행하며 효율적인 생활을 추구합니다."
    ),
    "sports_persona": ("아이와 함께 공원 산책을 즐기며, 홈트레이닝으로 체력을 관리합니다."),
    "arts_persona": ("뜨개질과 핸드메이드 소품 만들기를 취미로 하고 있어요."),
    "travel_persona": ("국내 가족 여행을 선호하며, 제주도와 경주를 즐겨 찾아요."),
    "culinary_persona": ("집밥을 선호하며, 주말에는 직접 요리해 가족과 함께 식사합니다."),
    "skills_and_expertise": "교육 설계, 독서 지도, 학급 운영",
    "skills_and_expertise_list": "교육 설계|독서 지도|학급 운영",
    "hobbies_and_interests": "독서, 뜨개질, 가족 산책",
    "hobbies_and_interests_list": "독서|뜨개질|가족 산책",
    "career_goals_and_ambitions": "학생들의 문해력 향상을 위한 교육 프로그램을 개발하고 싶어요.",
}

ALL_MOCK_PERSONAS: list[dict] = [MOCK_PERSONA_1, MOCK_PERSONA_2, MOCK_PERSONA_3]
