"""Parquet fixture 헬퍼.

실제 .parquet 파일은 저장소에 커밋하지 않는다.
pytest tmp_path 에 런타임 생성한다.

사용 예 (test 함수 내):
    from pathlib import Path
    from tests.fixtures.mock_local_parquet import write_mock_parquet

    def test_something(tmp_path: Path):
        parquet_path = write_mock_parquet(tmp_path)
        ...
"""

from __future__ import annotations

from pathlib import Path


def write_mock_parquet(
    tmp_path: Path,
    filename: str = "mock_data.parquet",
) -> Path:
    """26컬럼 mock row 5개를 tmp_path 에 parquet 로 저장하고 경로 반환.

    pyarrow / pandas 의존. 미설치 시 ImportError (uv add pyarrow pandas).
    실제 인물 또는 dataset row 사용 금지 — 합성 데이터만 사용.
    """
    try:
        import pandas as pd  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ImportError("pandas 미설치. uv add pandas 후 재실행.") from exc

    try:
        import pyarrow  # type: ignore[import-not-found]  # noqa: F401
    except ImportError as exc:
        raise ImportError("pyarrow 미설치. uv add pyarrow 후 재실행.") from exc

    rows = [
        {
            "uuid": "33333333-0001-4000-8000-000000000001",
            "professional_persona": "소프트웨어 회사에서 QA 엔지니어로 일해요.",
            "sports_persona": "매주 배드민턴 동호회에 참여해요.",
            "arts_persona": "재즈 음악과 재즈 카페를 좋아해요.",
            "travel_persona": "동남아 배낭여행을 즐겨요.",
            "culinary_persona": "태국 음식과 베트남 쌀국수를 즐겨요.",
            "family_persona": "자취 생활 3년차예요.",
            "persona": "서울 구로구에 사는 27세 QA 엔지니어예요.",
            "cultural_background": "IT 개발자 문화와 친숙해요.",
            "skills_and_expertise": "테스트 자동화, 품질 관리",
            "skills_and_expertise_list": "테스트 자동화|품질 관리",
            "hobbies_and_interests": "배드민턴, 재즈, 여행",
            "hobbies_and_interests_list": "배드민턴|재즈|여행",
            "career_goals_and_ambitions": "QA 리드 엔지니어로 성장하고 싶어요.",
            "sex": "M",
            "age": 27,
            "marital_status": "미혼",
            "military_status": "전역",
            "family_type": "1인 가구",
            "housing_type": "원룸",
            "education_level": "대학교 졸업",
            "bachelors_field": "전자공학",
            "occupation": "QA 엔지니어",
            "district": "구로구",
            "province": "서울특별시",
            "country": "Korea",
        },
        {
            "uuid": "33333333-0002-4000-8000-000000000002",
            "professional_persona": "부동산 중개사로 아파트 매매를 전문으로 해요.",
            "sports_persona": "주말 등산과 산악회 활동을 해요.",
            "arts_persona": "트로트 음악을 즐겨 듣고 노래방을 좋아해요.",
            "travel_persona": "국내 유명 산과 국립공원을 즐겨 가요.",
            "culinary_persona": "삼겹살과 막걸리를 즐겨요.",
            "family_persona": "배우자와 중학생 자녀 둘과 살아요.",
            "persona": "경기 의정부에 사는 46세 부동산 중개사예요.",
            "cultural_background": "부동산 시장과 지역 커뮤니티를 잘 알아요.",
            "skills_and_expertise": "부동산 중개, 시장 분석, 고객 상담",
            "skills_and_expertise_list": "부동산 중개|시장 분석|고객 상담",
            "hobbies_and_interests": "등산, 노래방, 낚시",
            "hobbies_and_interests_list": "등산|노래방|낚시",
            "career_goals_and_ambitions": "부동산 법인을 설립하고 싶어요.",
            "sex": "M",
            "age": 46,
            "marital_status": "기혼",
            "military_status": "전역",
            "family_type": "핵가족",
            "housing_type": "아파트",
            "education_level": "전문대 졸업",
            "bachelors_field": "부동산학",
            "occupation": "부동산 중개사",
            "district": "의정부시",
            "province": "경기도",
            "country": "Korea",
        },
        {
            "uuid": "33333333-0003-4000-8000-000000000003",
            "professional_persona": "유튜브 뷰티 크리에이터로 메이크업 콘텐츠를 제작해요.",
            "sports_persona": "필라테스와 헬스로 몸을 관리해요.",
            "arts_persona": "패션 잡지와 뷰티 트렌드 영상을 즐겨봐요.",
            "travel_persona": "해외 뷰티 박람회와 팝업 행사를 방문해요.",
            "culinary_persona": "촬영 전 피부를 위해 채식 위주로 먹어요.",
            "family_persona": "동생과 함께 살아요.",
            "persona": "서울 강남구에 사는 24세 뷰티 크리에이터예요.",
            "cultural_background": "SNS와 뷰티 인플루언서 문화에 깊이 몸담고 있어요.",
            "skills_and_expertise": "메이크업, 영상 편집, SNS 마케팅",
            "skills_and_expertise_list": "메이크업|영상 편집|SNS 마케팅",
            "hobbies_and_interests": "뷰티, 쇼핑, 여행",
            "hobbies_and_interests_list": "뷰티|쇼핑|여행",
            "career_goals_and_ambitions": (
                "구독자 100만 달성 후 자체 뷰티 브랜드를 론칭하고 싶어요."
            ),
            "sex": "F",
            "age": 24,
            "marital_status": "미혼",
            "military_status": "해당없음",
            "family_type": "기타",
            "housing_type": "오피스텔",
            "education_level": "대학교 재학",
            "bachelors_field": "미디어커뮤니케이션",
            "occupation": "유튜버",
            "district": "강남구",
            "province": "서울특별시",
            "country": "Korea",
        },
        {
            "uuid": "33333333-0004-4000-8000-000000000004",
            "professional_persona": "지방 중소기업에서 생산 관리 업무를 담당해요.",
            "sports_persona": "볼링 동호회 활동을 오래 해왔어요.",
            "arts_persona": "7080 가요와 국내 드라마를 즐겨요.",
            "travel_persona": "국내 온천 여행과 가족 패키지 여행을 선호해요.",
            "culinary_persona": "국밥과 순대국을 즐겨 먹어요.",
            "family_persona": "부모님과 미혼인 동생과 함께 살아요.",
            "persona": "전남 순천에 사는 39세 생산 관리자예요.",
            "cultural_background": "제조업 현장 문화와 지역 공동체를 중시해요.",
            "skills_and_expertise": "생산 관리, 품질 검사, 엑셀",
            "skills_and_expertise_list": "생산 관리|품질 검사|엑셀",
            "hobbies_and_interests": "볼링, 드라마, 낚시",
            "hobbies_and_interests_list": "볼링|드라마|낚시",
            "career_goals_and_ambitions": "생산 팀장으로 승진하고 싶어요.",
            "sex": "M",
            "age": 39,
            "marital_status": "미혼",
            "military_status": "전역",
            "family_type": "핵가족",
            "housing_type": "단독주택",
            "education_level": "전문대 졸업",
            "bachelors_field": "산업공학",
            "occupation": "생산 관리자",
            "district": "순천시",
            "province": "전라남도",
            "country": "Korea",
        },
        {
            "uuid": "33333333-0005-4000-8000-000000000005",
            "professional_persona": "NGO 사무국에서 환경 캠페인을 기획하고 운영해요.",
            "sports_persona": "자전거 출퇴근과 주말 등산을 즐겨요.",
            "arts_persona": "환경 관련 다큐멘터리와 독립 영화를 즐겨봐요.",
            "travel_persona": "생태 여행과 지속 가능한 여행을 추구해요.",
            "culinary_persona": "비건 식단을 유지하고 제로 웨이스트를 실천해요.",
            "family_persona": "파트너와 함께 살고 있어요.",
            "persona": "서울 마포구에 사는 30세 환경 활동가예요.",
            "cultural_background": "환경 운동과 사회 변화에 관심이 높아요.",
            "skills_and_expertise": "캠페인 기획, 환경 교육, 커뮤니티 조직",
            "skills_and_expertise_list": "캠페인 기획|환경 교육|커뮤니티 조직",
            "hobbies_and_interests": "자전거, 환경 운동, 텃밭",
            "hobbies_and_interests_list": "자전거|환경 운동|텃밭",
            "career_goals_and_ambitions": "환경 정책 전문가로 정부 기관에 기여하고 싶어요.",
            "sex": "F",
            "age": 30,
            "marital_status": "미혼",
            "military_status": "해당없음",
            "family_type": "기타",
            "housing_type": "빌라",
            "education_level": "대학교 졸업",
            "bachelors_field": "환경공학",
            "occupation": "NGO 활동가",
            "district": "마포구",
            "province": "서울특별시",
            "country": "Korea",
        },
    ]

    df = pd.DataFrame(rows)
    out_path = tmp_path / filename
    df.to_parquet(out_path, index=False)
    return out_path
