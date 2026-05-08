# k-fashion-persona

![AI 디지털 패션 패널 개요](docs/assets/k-fashion-persona-images.jpeg)

## K-fashion 컨셉을 AI 페르소나로 먼저 점검

[![HF Dataset](https://img.shields.io/badge/HF-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea)
[![GitHub](https://img.shields.io/badge/GitHub-k--fashion--persona-181717?logo=github&logoColor=white)](https://github.com/woooya129-ai/k-fashion-persona)
[![Docs](https://img.shields.io/badge/Docs-INSTALL-2563EB?logo=readthedocs&logoColor=white)](INSTALL.md)
[![License: AGPL-3.0-only](https://img.shields.io/badge/license-AGPL--3.0--only-0F766E.svg)](LICENSE)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Woody%20Kim-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/woody-kim-ab2741403/)

K-Fashion Persona Screener는 패션 제품 컨셉을 실제 출시하거나 본조사를 하기 전에 AI 합성 페르소나 관점으로 빠르게 점검하는 local-first 도구입니다.

제품 카드에 카테고리, 가격, 핏, 소재, 컬러, 시즌, 착용 상황, 스타일 톤, 브랜드 메시지, 타깃 가설을 입력하면 여러 합성 페르소나가 해당 컨셉을 어떻게 받아들일 수 있는지 확인할 수 있습니다.

이 도구는 실제 소비자 반응, 구매율, 매출, 시장 점유율을 예측하는 서비스가 아닙니다. 본조사 전에 어떤 부분에서 관심이 생기고, 어떤 부분에서 망설임이 생길 수 있는지 초기 신호를 확인하는 보조 도구입니다.

```mermaid
flowchart LR
  A["Synthetic personas"] --> C["Persona panel"]
  B["Product card"] --> C
  C --> D["Taste check"]
  D --> E["Early signals"]
  E --> F["Next step"]
```

NVIDIA Nemotron-Personas-Korea는 한국 맥락을 반영한 합성 페르소나 데이터셋입니다. 이 도구는 제품 카드를 여러 합성 페르소나에게 보여주는 방식으로, 본 설문조사 전에 취향 적합성, 관심 이유, 망설임, 리스크 신호를 빠르게 훑어봅니다.

이 방식이 가능한 이유는 실제 구매를 예측하려는 것이 아니라, 제품 설명을 봤을 때 어떤 지점에서 관심이 생기고 어떤 지점에서 막히는지 early signal을 보는 용도이기 때문입니다. 최종 판단은 실제 설문, 판매 데이터, 전문가 검토와 함께 해야 합니다.

![K-Fashion Persona Screener main screen](docs/assets/kfashionpersona-screenshot-01.webp)

![K-Fashion Persona Screener result screen](docs/assets/kfashionpersona-screenshot-02.webp)

## 무엇을 확인할 수 있나요?

- 제품 카테고리, 가격대, 핏과 실루엣, 소재, 컬러
- 시즌, 착용 상황, 스타일 톤
- 브랜드 메시지와 제품 설명
- 타깃 고객 가설과 브랜드 가설
- 페르소나별 관심 이유와 망설임 이유
- 가격 부담, 핏 리스크, 소재와 관리 부담
- 코디 난이도, 착용 상황 불일치, 스타일 부담
- Markdown 또는 CSV 결과 리포트 다운로드

## 작동 방식

1. 사용자가 패션 제품 컨셉을 입력합니다.
2. 한국 맥락의 합성 페르소나 데이터를 불러옵니다.
3. 연령, 성별, 지역, 직업 조건으로 페르소나를 필터링할 수 있습니다.
4. seed 기반 샘플링으로 평가할 페르소나 패널을 구성합니다.
5. 각 페르소나 관점에서 LLM이 제품 컨셉을 평가합니다.
6. 결과는 정해진 JSON 스키마로 검증됩니다.
7. 결과를 집계해 Markdown 또는 CSV 리포트로 확인할 수 있습니다.

## 사용하는 데이터

기본 데이터셋은 [NVIDIA Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea)입니다.

이 데이터셋은 한국 맥락을 반영한 합성 페르소나 데이터셋입니다. 실제 인물 데이터가 아니며, 실제 소비자의 구매 행동을 직접 나타내지 않습니다.

로컬 CSV 또는 Parquet 파일을 사용할 경우 `data/` 하위에 두어야 합니다. 권장 위치는 `data/raw/`입니다.

## 실행 방식

이 앱은 hosted 서비스가 아니라 local-first 방식으로 실행됩니다. 사용자는 자신의 컴퓨터에서 앱을 실행하고, 자신이 보유한 LLM provider API key를 입력해 사용합니다.

기본 실행 방식은 Streamlit 앱입니다.

필요 조건:

- Python 3.11 이상
- uv
- Streamlit
- 사용할 LLM provider의 API key
- 필요 시 Hugging Face 접근 권한

실행 예시:

```bash
git clone https://github.com/woooya129-ai/k-fashion-persona.git
cd k-fashion-persona
uv sync --all-extras --dev
uv run streamlit run src/app.py
```

브라우저에서 `http://localhost:8501`을 엽니다.

자세한 설치와 실행 방법은 [INSTALL.md](INSTALL.md)를 참고하세요.

## API key와 데이터 보관

API key는 저장소에 넣지 않는 것이 원칙입니다. 기본 방식은 Streamlit 화면의 password 입력칸에 API key를 직접 입력하는 것입니다.

API key, Hugging Face token, cache, outputs, raw data는 공개 저장소에 포함하지 않습니다.

실행 메타데이터는 로컬 SQLite DB에 저장됩니다.

기본 위치:

```text
cache/screener.db
```

저장되는 정보의 예:

- dataset source
- dataset split
- dataset revision
- 후보 페르소나 수
- 최종 샘플 수
- sampling seed
- sampling strategy
- filter summary
- provider
- model
- prompt version
- schema version
- concept hash
- price context hash

별도 컬럼으로 저장하지 않는 정보:

- raw API key
- Hugging Face token
- raw provider response
- raw concept text

## 결과 해석 방법

결과는 합성 페르소나 기반 가설입니다.

적절한 활용:

- 본조사 전에 설문 문항을 정리할 때
- 제품 설명에서 막히는 부분을 찾을 때
- 가격, 소재, 핏, 착용 상황 관련 리스크를 빠르게 훑을 때
- 브랜드 메시지가 특정 생활자 맥락에서 어떻게 읽힐지 점검할 때
- 여러 컨셉 후보를 비교하기 전 초기 필터링을 할 때

부적절한 활용:

- 실제 구매율 예측
- 실제 매출 예측
- 시장 점유율 예측
- 실제 소비자 조사의 대체
- 최종 출시 여부의 단독 판단
- 발주량 또는 생산량 결정의 단독 근거

## 장점

- 한국 맥락의 합성 페르소나를 활용합니다.
- 패션 제품 카드 형식으로 입력할 수 있습니다.
- 로컬에서 실행할 수 있습니다.
- API key와 원본 데이터를 공개 저장소에 넣지 않는 구조입니다.
- seed 기반 샘플링으로 실행 재현성을 높입니다.
- LLM 결과를 정해진 스키마로 검증합니다.
- 가격, 핏, 소재, 코디, 착용 상황, 스타일 부담 같은 패션 리스크를 정리합니다.
- Markdown과 CSV 리포트를 생성할 수 있습니다.

## 한계

- 실제 소비자 데이터 기반 예측 모델이 아닙니다.
- 합성 페르소나 반응은 실제 구매 행동과 다를 수 있습니다.
- 데이터셋은 패션 구매 전용 데이터가 아닙니다.
- 이미지, 룩북, 착용 사진, 체형 정보는 기본 평가에 포함되지 않습니다.
- 브랜드 충성도, 구매 이력, 반품 이력, 사이즈 선호 같은 실제 커머스 데이터는 포함되지 않습니다.
- LLM 응답은 그럴듯할 수 있지만, 실제 시장 검증을 대체하지 않습니다.
- 최종 판단은 실제 설문, 판매 데이터, 전문가 검토와 함께 해야 합니다.

## 추천 사용 시나리오

적합한 사용자:

- 패션 브랜드 상품기획자
- MD
- 마케터
- UX 리서처
- D2C 브랜드 운영자
- 패션 AI 서비스 기획자
- 패션 컨셉 테스트를 빠르게 하고 싶은 개발팀

적합한 상황:

- 출시 전 제품 컨셉을 빠르게 점검하고 싶을 때
- 여러 타깃 가설을 비교하고 싶을 때
- 제품 설명 문구의 약점을 찾고 싶을 때
- 가격 부담 또는 소재/핏 관련 리스크를 미리 보고 싶을 때
- 본조사 전에 질문 방향을 정리하고 싶을 때

## 라이선스와 출처

코드 라이선스:

- GNU AGPL-3.0-only

기본 데이터셋:

- NVIDIA Nemotron-Personas-Korea

데이터셋 라이선스:

- CC BY 4.0 attribution 대상

상업적 서비스나 폐쇄형 제품에 도입하려면 AGPL-3.0-only 라이선스 조건을 반드시 검토해야 합니다.

## 한 문장 요약

K-Fashion Persona Screener는 한국 패션 제품 컨셉을 실제 조사 전에 합성 페르소나 패널로 빠르게 점검해 관심 이유, 망설임, 패션 리스크 신호를 정리해 주는 local-first 사전 분석 도구입니다.
