"""AI 분석 모듈"""

import logging
from google import genai
from google.genai import types

from config import GEMINI_MODEL

logger = logging.getLogger(__name__)


def generate_ai_analysis(portfolio, total_return, cagr, mdd, sharpe, api_key):
    """
    AI를 통한 포트폴리오 분석 보고서 생성

    Args:
        portfolio: 포트폴리오 리스트
        total_return: 총 수익률
        cagr: 연환산 수익률
        mdd: 최대 낙폭
        sharpe: 샤프 비율
        api_key: Gemini API 키

    Returns:
        str: AI 분석 결과
    """
    port_str = ", ".join([f"{p['ticker']}({p['weight']}%)" for p in portfolio])

    prompt = f"""당신은 전문 투자 자문가입니다. 다음 포트폴리오 백테스트 결과를 분석하고 한국어로 답변해주세요.

## 포트폴리오 구성
{port_str}

## 성과 지표
- 총 수익률: {total_return:.2f}%
- 연환산 수익률(CAGR): {cagr:.2f}%
- 최대 낙폭(MDD): {mdd:.2f}%
- 샤프 비율: {sharpe:.2f}

## 분석 요청사항
다음 형식으로 분석 보고서를 작성해주세요. 이모지는 사용하지 마세요.

### 1. 포트폴리오 총평
백테스트 결과를 종합적으로 평가하세요. (3-4문장)

### 2. 주요 장점
이 포트폴리오의 강점을 2-3가지 설명하세요.
- 장점 1:
- 장점 2:

### 3. 주요 리스크
이 포트폴리오의 위험 요소를 2-3가지 설명하세요.
- 리스크 1:
- 리스크 2:

### 4. 자산 배분 평가
각 자산의 역할과 비중의 적절성을 평가하세요.

### 5. 시장 상황별 예상 성과
- 상승장:
- 하락장:
- 횡보장:

### 6. 개선 제안
포트폴리오 개선을 위한 구체적인 제안을 1-2가지 제시하세요.
"""

    try:
        client = genai.Client(api_key=api_key)

        # Gemini 3 Flash 설정
        # thinking_level: minimal(거의 사고 안함), medium(균형), high(깊은 추론)
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="medium")
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=config
        )
        return response.text
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        return f"Error: {str(e)}"
