"""UI 스타일 정의 모듈"""

# CSS 스타일 상수
APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1E293B; }
.stApp { background-color: #F1F5F9; }

/* ------------------------------------------------------- */
/* [사이드바 스타일] */
/* ------------------------------------------------------- */
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

.sidebar-section-header {
    font-size: 11px;
    font-weight: 700;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 24px;
    margin-bottom: 8px;
}

/* Radio 메뉴 스타일 */
[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 8px !important;
    display: flex !important;
    flex-direction: column !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] > div {
    width: 100% !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label {
    width: 100% !important;
    min-width: 100% !important;
    max-width: 100% !important;
    background-color: #F8FAFC !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    box-sizing: border-box !important;
    display: block !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background-color: #F1F5F9 !important;
    border-color: #CBD5E1 !important;
}

[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
    background-color: #0F172A !important;
    border-color: #0F172A !important;
    color: white !important;
}

/* Radio 버튼 원형 아이콘 숨기기 */
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}

/* 라벨 내부 텍스트도 전체 너비 */
[data-testid="stSidebar"] div[role="radiogroup"] label > div {
    width: 100% !important;
}

/* ------------------------------------------------------- */
/* [메인 화면 - 카드 UI] */
/* ------------------------------------------------------- */
/* 컨테이너에 카드 스타일 적용 (border=True일 때) */
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] > div {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
    padding: 20px;
}

/* 섹션 제목 스타일 */
.section-label {
    font-size: 14px; font-weight: 600; color: #475569; margin-bottom: 6px; display: block;
}

/* ------------------------------------------------------- */
/* [입력 필드 및 폼 요소] */
/* ------------------------------------------------------- */
div[data-baseweb="input"] { border-radius: 8px; border-color: #CBD5E1; background: #FFFFFF; }
div[data-baseweb="select"] > div { border-radius: 8px; border-color: #CBD5E1; background: #FFFFFF; }
div[data-testid="stNumberInput"] div[data-baseweb="input"] { height: 32px; min-height: 32px; font-size: 13px; }
hr { margin-top: 1.0rem; margin-bottom: 1.0rem; border-color: #E2E8F0; }

/* ------------------------------------------------------- */
/* [버튼 스타일] */
/* ------------------------------------------------------- */
button[kind="secondary"] {
    background: white; color: #2563EB; border: 1px solid #BFDBFE;
    height: 38px; border-radius: 6px; font-weight: 600;
    transition: all 0.2s; font-size: 13px;
}
button[kind="secondary"]:hover {
    background: #EFF6FF; border-color: #3B82F6; color: #1D4ED8;
    box-shadow: 0 2px 5px rgba(37, 99, 235, 0.1);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    border: none; box-shadow: 0 4px 6px rgba(15, 23, 42, 0.2);
    transition: transform 0.1s; color: white; border-radius: 8px;
    font-weight: 600; height: 44px;
}
.stButton > button[kind="primary"]:active { transform: scale(0.98); }
.stButton > button[kind="primary"]:hover { opacity: 0.9; }

/* ------------------------------------------------------- */
/* [태그 스타일] */
/* ------------------------------------------------------- */
.tag-type { background:#EFF6FF; color:#2563EB; padding:3px 8px; border-radius:6px; font-size:11px; font-weight:600; margin-right:4px; }
.tag-curr { background:#F1F5F9; color:#64748B; padding:3px 8px; border-radius:6px; font-size:11px; font-weight:600; border: 1px solid #E2E8F0; }

/* ------------------------------------------------------- */
/* [자산 목록 행 스타일] */
/* ------------------------------------------------------- */
.asset-row {
    display: flex;
    align-items: center;
    height: 32px;
    gap: 4px;
}
.asset-ticker {
    font-weight: 700;
    font-size: 14px;
    color: #0F172A;
}
.asset-name {
    font-size: 12px;
    color: #94A3B8;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* 자산 목록 행 간격 축소 */
[data-testid="stHorizontalBlock"]:has(.asset-row) {
    margin-bottom: -12px !important;
}

/* Weight 입력 필드에 % 표시 */
[data-testid="stHorizontalBlock"]:has(.asset-row) [data-testid="stNumberInput"] {
    position: relative;
}
[data-testid="stHorizontalBlock"]:has(.asset-row) [data-testid="stNumberInput"] input {
    padding-right: 24px !important;
}
[data-testid="stHorizontalBlock"]:has(.asset-row) [data-testid="stNumberInput"]::after {
    content: "%";
    position: absolute;
    left: 70px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 13px;
    color: #64748B;
    pointer-events: none;
    z-index: 1;
}


/* ------------------------------------------------------- */
/* [모바일 반응형 - 768px 이하] */
/* ------------------------------------------------------- */
@media (max-width: 768px) {
    /* 메인 컨텐츠 패딩 조정 */
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1rem !important;
    }

    /* 설정 영역 컬럼만 수직 스택 (자산 목록 제외) */
    .main > div > div > div > [data-testid="stVerticalBlockBorderWrapper"]:not(:has(.asset-row)) + [data-testid="stHorizontalBlock"],
    [data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]),
    [data-testid="stHorizontalBlock"]:has([data-testid="stCheckbox"]) {
        flex-wrap: wrap !important;
    }

    .main > div > div > div > [data-testid="stVerticalBlockBorderWrapper"]:not(:has(.asset-row)) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
    [data-testid="stHorizontalBlock"]:has([data-testid="stDateInput"]) > [data-testid="stColumn"],
    [data-testid="stHorizontalBlock"]:has([data-testid="stCheckbox"]) > [data-testid="stColumn"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }

    /* 자산 목록 행은 수평 유지 */
    [data-testid="stHorizontalBlock"]:has(.asset-row) {
        flex-wrap: nowrap !important;
        gap: 2px !important;
        margin-bottom: -14px !important;
    }
    [data-testid="stHorizontalBlock"]:has(.asset-row) > [data-testid="stColumn"] {
        min-width: 0 !important;
    }

    /* 모바일 자산 행 스타일 */
    .asset-row {
        height: 28px !important;
        gap: 2px !important;
    }
    .asset-ticker {
        font-size: 11px !important;
    }
    .asset-name {
        display: none !important;
    }
    .tag-type, .tag-curr {
        font-size: 9px !important;
        padding: 2px 4px !important;
    }

    /* 모바일에서 % 위치 조정 */
    [data-testid="stHorizontalBlock"]:has(.asset-row) [data-testid="stNumberInput"] input {
        padding-right: 22px !important;
    }
    [data-testid="stHorizontalBlock"]:has(.asset-row) [data-testid="stNumberInput"]::after {
        left: 70px !important;
        font-size: 11px !important;
    }

    /* 체크박스 컬럼 수평 유지 */
    [data-testid="stHorizontalBlock"]:has([data-testid="stCheckbox"]) {
        flex-wrap: nowrap !important;
        gap: 4px !important;
    }
    [data-testid="stHorizontalBlock"]:has([data-testid="stCheckbox"]) > [data-testid="stColumn"] {
        min-width: 0 !important;
        width: auto !important;
        flex: 1 !important;
    }
    /* 체크박스 라벨 축소 */
    [data-testid="stCheckbox"] label p {
        font-size: 12px !important;
    }

    /* 섹션 라벨 모바일 최적화 */
    .section-label {
        font-size: 13px;
        margin-bottom: 8px;
    }

    /* 메트릭 카드 모바일 최적화 - 2열 그리드 */
    [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) {
        display: grid !important;
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 8px !important;
    }
    [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) > [data-testid="stColumn"] {
        width: auto !important;
        flex: none !important;
        min-width: auto !important;
    }
    [data-testid="stMetric"] {
        padding: 10px !important;
        background: #F8FAFC;
        border-radius: 8px;
    }
    [data-testid="stMetricValue"] {
        font-size: 16px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 10px !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 9px !important;
    }

    /* 사이드바 기본 숨김 */
    [data-testid="stSidebar"] {
        min-width: 0px !important;
    }
    [data-testid="stSidebar"][aria-expanded="false"] {
        min-width: 0px !important;
        margin-left: -100% !important;
    }

    /* 차트 높이 조정 */
    [data-testid="stPlotlyChart"] {
        min-height: 250px !important;
    }

    /* 버튼 높이 조정 */
    .stButton > button {
        min-height: 44px !important;
    }

    /* 날짜 입력 모바일 최적화 */
    [data-testid="stDateInput"] input {
        font-size: 14px !important;
        padding: 8px !important;
    }

    /* 셀렉트박스 모바일 최적화 */
    [data-baseweb="select"] {
        min-height: 44px !important;
    }

    /* 실행 버튼 컨테이너 전체 너비 */
    [data-testid="stHorizontalBlock"]:has(button[kind="primary"]) > [data-testid="stColumn"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }

    /* 차트 컨테이너 패딩 줄이기 */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 12px !important;
    }

    /* 타이틀 폰트 크기 조정 */
    h1 {
        font-size: 22px !important;
    }

    /* 구분선 마진 조정 */
    hr {
        margin-top: 0.8rem !important;
        margin-bottom: 0.8rem !important;
    }
}
</style>
"""


def apply_styles(st):
    """스타일 CSS를 Streamlit 앱에 적용"""
    st.markdown(APP_CSS, unsafe_allow_html=True)
