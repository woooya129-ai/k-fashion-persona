---
title: K-Fashion Persona
emoji: 🧥
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: agpl-3.0
short_description: AI persona screening for Korean fashion concepts.
datasets:
  - nvidia/Nemotron-Personas-Korea
tags:
  - streamlit
  - fashion
  - personas
  - market-research
---

<table align="right">
  <tr>
    <td align="left" valign="middle" width="256" height="256">
      <img src="docs/assets/k-fashion-persona-icon.svg" alt="k-fashion-persona icon" width="256" height="256" />
    </td>
    <td align="left" valign="middle" height="256">
      <h1>
        <strong><b>k</b></strong><br />
        <strong><b>fashion</b></strong><br />
        <strong><b>persona</b></strong>
      </h1>
    </td>
  </tr>
</table>

# K-fashion 컨셉을 AI 페르소나로 먼저 점검

[![Version](https://img.shields.io/badge/version-0.6.2-0F766E)](pyproject.toml)
[![HF Dataset](https://img.shields.io/badge/HF-Dataset-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea)
[![GitHub](https://img.shields.io/badge/GitHub-k--fashion--persona-181717?logo=github&logoColor=white)](https://github.com/woooya129-ai/k-fashion-persona)
[![HF Space](https://img.shields.io/badge/HF%20Space-k--fashion--persona-FFD21E?logo=huggingface&logoColor=black)](https://huggingface.co/spaces/w00ya/k-fashion-persona)
[![Live App](https://img.shields.io/badge/Live%20App-hf.space-0F766E)](https://w00ya-k-fashion-persona.hf.space)
[![Docs](https://img.shields.io/badge/Docs-INSTALL-2563EB?logo=readthedocs&logoColor=white)](docs/INSTALL.md)
[![English README](https://img.shields.io/badge/README-English-2563EB)](docs/README-ENG.md)
[![License: AGPL-3.0-only](https://img.shields.io/badge/license-AGPL--3.0--only-0F766E.svg)](LICENSE)

![k-fashion-persona overview](docs/assets/k-fashion-persona-images.jpeg)

`k-fashion-persona`는 한국 패션 제품 컨셉을 출시 전 단계에서 점검하는 local-first Streamlit 도구입니다. 제품 카드와 필터를 넣으면 합성 페르소나 패널이 관심 이유, 망설임, 가격 부담, 패션 리스크를 Markdown/CSV 리포트로 정리합니다.

실제 구매율, 매출, 시장점유율을 예측하는 서비스가 아닙니다. 설문, 인터뷰, 판매 데이터 분석 전에 가설을 좁히는 보조 도구입니다.

## Nemotron-Personas-Korea 소개

![Nemotron-Personas-Korea 생성 구조](docs/assets/nemotron-personas-korea.png)

Nemotron-Personas-Korea는 NVIDIA가 2026년 4월 공개한 CC BY 4.0 한국어 합성 페르소나 데이터셋입니다. KOSIS, 대법원, 국민건강보험공단, 한국농촌경제연구원, NAVER Cloud 통계 분포를 바탕으로 이름, 나이, 직업, 지역, 교육 수준 등을 합성해 한국 사회의 다양한 맥락을 반영합니다.

기존 영어 중심 데이터셋에서 과소 표현되던 고령층, 농촌 지역, 저학력 직군의 공백을 줄이고 한국어 AI의 편향 완화와 응답 다양성 향상을 돕습니다.

## 빠른 이해

| 구분 | 내용 |
|:---|:---|
| 입력 | 카테고리, 가격, 핏, 소재, 컬러, 시즌, 착용 상황, 스타일 톤, 타깃 가설, 제품 설명 |
| 패널 | NVIDIA Nemotron-Personas-Korea 기반 합성 페르소나 |
| 필터 | 연령, 성별, 지역, 직업, seed, 샘플 수 |
| 출력 | 반응 분포, 관심도, 주요 이유, 주요 우려, 가격 부담, 대표 카드, Markdown/CSV |
| 기본 프리셋 | FAST 50명, BALANCE 100명, HIGH 300명, MAX 1000명 |
| Advanced | 샘플 수 직접 입력 가능 |

![main screen](docs/assets/kfashionpersona-screenshot-01.webp)

![result screen](docs/assets/kfashionpersona-screenshot-02.webp)

## 실행 구조

- 앱 UI, 데이터셋 필터링, 샘플링, 프롬프트 생성, SQLite 캐시, Markdown/CSV 리포트 생성은 사용자 PC에서 로컬로 실행됩니다.
- Streamlit API 모드는 사용자가 선택한 provider API 서버로 프롬프트를 전송합니다.
- Agent Pack 모드는 프롬프트 파일을 내보내고, 사용자의 Codex 또는 Claude Code CLI가 평가합니다.
- API key는 앱이 저장하지 않습니다. 화면 입력값은 현재 Streamlit 세션에서만 사용합니다.
- LLM API endpoint는 `config/pricing_config.yaml`의 `api_base_url` host만 허용합니다. 설정을 바꾸면 허용 host set도 바뀌므로 공유 배포에서는 코드 리뷰 대상으로 봐야 합니다.
- 공개 HF Space는 `KFPS_REQUIRE_USER_PROVIDER_KEY=1`로 배포됩니다. 운영자 공용 LLM provider API key를 사용하지 않으며, 사용자가 본인 key를 입력해야 실행됩니다.

## 설치 방법

필요 조건:

- Git
- Python 3.11 이상
- `uv`
- 사용할 LLM provider API key 또는 로그인된 Codex/Claude Code CLI
- 필요 시 Hugging Face token

설치:

```bash
git clone https://github.com/woooya129-ai/k-fashion-persona.git
cd k-fashion-persona
uv sync --all-extras --dev
```

자세한 설치는 [docs/INSTALL.md](docs/INSTALL.md)를 참고하세요.

## 빠른 실행

```bash
uv run streamlit run src/app.py
```

브라우저에서 엽니다.

```text
http://localhost:8501
```

## 일반 사용

1. Streamlit 앱을 실행합니다.
2. provider와 model을 고릅니다.
3. provider API key를 입력합니다.
4. 제품 카드를 입력합니다.
5. 샘플 수, seed, 페르소나 필터를 조정합니다.
6. 예상 비용과 시간을 확인합니다.
7. `ENTER`로 실행하고 Markdown 또는 CSV 리포트를 내려받습니다.

반복 실행용 key는 저장소 밖 환경 파일이나 OS 환경변수에 둡니다. 저장소 root에 실제 `.env` 파일을 두거나 commit하지 마세요.

```env
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
GROQ_API_KEY=
DEEPSEEK_API_KEY=
QWEN_API_KEY=
HF_TOKEN=
KOSIS_API_KEY=
KOSIS_STATISTICS_DATA_URL=
```

## 구독형 Codex / Claude Code

구독형 Codex 또는 Claude Code 사용자는 `Agent Pack` 방식으로 API key 없이도 평가 흐름을 쓸 수 있습니다. 앱이 Codex/Claude를 provider처럼 자동 호출하는 구조가 아니라, `export -> CLI 실행 -> import` 순서의 오프라인 브릿지입니다.

Codex CLI:

```powershell
npm install -g @openai/codex
codex
```

Claude Code:

```powershell
irm https://claude.ai/install.ps1 | iex
claude
```

Agent Pack 생성:

```powershell
uv run python -m src.agent_bridge export --concept examples/agent_bridge_concept.example.json --out outputs/agent-pack-demo --sample-size 50 --audience unisex
```

Codex 실행 후 import:

```powershell
powershell -ExecutionPolicy Bypass -File outputs\agent-pack-demo\commands\run-codex.ps1
uv run python -m src.agent_bridge import --pack outputs\agent-pack-demo --results outputs\agent-pack-demo\results\codex --out outputs\agent-report-codex
```

Claude Code 실행 후 import:

```powershell
powershell -ExecutionPolicy Bypass -File outputs\agent-pack-demo\commands\run-claude.ps1
uv run python -m src.agent_bridge import --pack outputs\agent-pack-demo --results outputs\agent-pack-demo\results\claude --out outputs\agent-report-claude
```

메모:

- 50명 평가는 CLI 호출 50번입니다. 처음에는 `--sample-size 5` 또는 `--sample-size 10`으로 확인하세요.
- Claude 구독 계정은 기본 `run-claude.ps1`을 그대로 쓰면 됩니다. `KFPS_CLAUDE_BARE=1`은 API key 또는 별도 auth helper 자동화용입니다.
- 결과물은 `agent-report.md`, `agent-report.csv`, `normalized-results.jsonl`입니다.
- Codex 문서: [OpenAI Codex CLI](https://developers.openai.com/codex/cli)
- Claude 문서: [Claude Code setup](https://code.claude.com/docs/en/setup)

## 데이터와 통계

- 기본 데이터셋: [NVIDIA Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea)
- 데이터 성격: 실제 인물 데이터가 아닌 한국 맥락 합성 페르소나
- 라이선스: CC BY 4.0 attribution
- 크기: Hugging Face 공식 기준 100만 레코드, 700만 페르소나 설명, 26개 필드, 약 1.98GB Parquet
- 기본 로딩: Hugging Face `datasets` streaming
- 기본 scan: 실행마다 최대 3000행까지 순차 scan해서 조건에 맞는 패널을 채움

소득, 자산, 의류·신발 지출은 개별 페르소나에서 추정하지 않습니다. 리포트의 가격 부담 참고값은 KOSTAT/KOSIS 공개 통계 스냅샷 `data/public/kosis_household_context.csv`를 사용합니다. KOSIS API key와 `statisticsData` URL을 입력하면 실행 시 해당 응답을 먼저 참고하고, 실패하면 스냅샷으로 fallback합니다.

## 권장 사양

| 구분 | 최소 | 권장 |
|---|---:|---:|
| CPU | 2코어 이상 | 4코어 이상 |
| RAM | 8GB | 16GB 이상 |
| 저장공간 | 5GB 이상 여유 | 10-20GB 이상 여유 |
| GPU | 필요 없음 | 필요 없음 |
| 네트워크 | HF 데이터셋 로딩과 LLM API 호출에 필요 | 안정적인 broadband 권장 |

큰 샘플은 RAM보다 LLM API 비용과 실행 시간이 먼저 증가합니다.

## 결과 해석

적절한 사용:

- 정식 조사 전 설문 문항 정리
- 제품 설명의 약점 찾기
- 가격, 소재, 핏, 코디 리스크 점검
- 여러 컨셉 후보의 초기 비교

부적절한 사용:

- 실제 구매율 예측
- 실제 매출 예측
- 시장점유율 예측
- 실제 소비자 조사의 대체
- 출시, 생산, 발주 의사결정의 단독 근거

## 한계

- 합성 페르소나 반응은 실제 소비자 행동과 다를 수 있습니다.
- 데이터셋은 패션 구매 전용 데이터가 아닙니다.
- 이미지, 룩북, 착용 사진, 체형 정보는 기본 평가에 포함되지 않습니다.
- KOSIS/KOSTAT 값은 가구 단위 집계 통계이며, 개별 페르소나의 실제 경제 상태가 아닙니다.
- 최종 판단은 실제 조사, 판매 데이터, 전문가 검토와 함께 해야 합니다.

## 라이선스와 출처

- 코드 라이선스: GNU AGPL-3.0-only
- 기본 페르소나 데이터셋: NVIDIA Nemotron-Personas-Korea
- 데이터셋 라이선스: CC BY 4.0 attribution
- 통계 컨텍스트: KOSTAT / KOSIS 공개 통계
- 전체 고지: [LICENSE](LICENSE), [NOTICE](docs/legal/NOTICE.md), [THIRD_PARTY_NOTICES](docs/legal/THIRD_PARTY_NOTICES.md)
- 인용 형식: [CITATION.cff](CITATION.cff)
- 방법론: [docs/legal/METHODOLOGY_AND_RIGHTS.md](docs/legal/METHODOLOGY_AND_RIGHTS.md)

상업적 폐쇄 도입, 사내 SaaS, 재배포 제품, AGPL 조건 적용이 어려운 사용은 별도 상용 라이선스 또는 듀얼 라이선스 협의 대상입니다.

문의: woooya129 [at] gmail [dot] com

미국 패션 컨셉용 twin project: [us-fashion-persona](https://github.com/woooya129-ai/us-fashion-persona)
