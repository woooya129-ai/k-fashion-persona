# Image Concept Assist Design

Status: v0.8.0 candidate, not implemented in v0.7.0.

## Product Boundary

`이미지 기반 컨셉 설명 보조` is an optional input helper. It is not an image evaluation feature.

Default state: OFF.

## Flow

```text
Toggle OFF
-> continue with text input only

Toggle ON
-> upload image
-> call image analysis API once
-> generate concept-description draft
-> user edits and confirms the draft
-> confirmed text only goes into persona evaluation
```

## Rules

- Do not send the image to every persona evaluation call.
- Do not run persona evaluation from unconfirmed image-analysis output.
- Do not store uploaded images by default.
- Show a warning before any external image API call.
- Block wording that implies real image validation, product authentication, sales prediction, or market proof.

## Warning Copy

```text
이미지는 외부 AI API로 전송되어 컨셉 설명 초안을 만드는 데 사용됩니다.
이미지는 페르소나 평가에 반복 사용되지 않습니다.
생성된 설명은 실행 전 직접 수정·확정해야 합니다.
출시 전 민감한 디자인이나 비공개 샘플은 업로드하지 마세요.
```
