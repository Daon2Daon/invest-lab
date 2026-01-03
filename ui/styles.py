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

/* 사용자 정보 박스 */
.user-info-box {
    background: #F8FAFC;
    padding: 16px;
    border-radius: 10px;
    border: 1px solid #E2E8F0;
    margin-bottom: 20px;
}
.user-info-label {
    font-size: 12px;
    color: #64748B;
    margin-bottom: 4px;
}
.user-info-name {
    font-size: 16px;
    font-weight: 600;
    color: #0F172A;
}

/* 빈 포트폴리오 메시지 */
.empty-portfolio {
    background: #FFFFFF;
    border: 1px dashed #CBD5E1;
    border-radius: 12px;
    padding: 40px;
    text-align: center;
    color: #64748B;
}

/* 그룹 헤더 */
.group-header {
    font-weight: 600;
    font-size: 12px;
    color: #475569;
    margin-bottom: 2px;
}

/* 종목 정보 텍스트 */
.stock-name {
    color: #64748B;
    font-size: 13px;
}
.stock-currency {
    color: #94A3B8;
    font-size: 12px;
}

/* AI 분석 박스 */
.ai-analysis-box {
    margin-top: 15px;
    background: white;
    padding: 25px;
    border-radius: 10px;
    border: 1px solid #E2E8F0;
    line-height: 1.6;
    font-size: 15px;
}

/* 로그인 페이지 */
.login-title {
    font-size: 32px;
    font-weight: 700;
    color: #1E293B;
}
.login-subtitle {
    color: #64748B;
    font-size: 14px;
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

/* ------------------------------------------------------- */
/* [다크 모드 지원] */
/* ------------------------------------------------------- */
@media (prefers-color-scheme: dark) {
    html, body, [class*="css"] {
        color: #F1F5F9 !important;
    }
    .stApp {
        background-color: #0F172A !important;
    }

    /* h1 태그 (메인 타이틀) 다크 모드 */
    h1 {
        color: #FFFFFF !important;
    }
    h2 {
        color: #F1F5F9 !important;
    }
    h3 {
        color: #F1F5F9 !important;
    }

    /* 일반 텍스트 다크 모드 */
    p {
        color: #E2E8F0 !important;
    }

    /* 사이드바 다크 모드 */
    [data-testid="stSidebar"] {
        background-color: #1E293B !important;
        border-right: 1px solid #334155 !important;
    }

    /* 사이드바 라디오 버튼 다크 모드 */
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background-color: #0F172A !important;
        border: 1px solid #475569 !important;
        color: #F1F5F9 !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: #1E293B !important;
        border-color: #64748B !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
        background-color: #3B82F6 !important;
        border-color: #3B82F6 !important;
        color: #FFFFFF !important;
    }

    /* 카드 배경 다크 모드 */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
    }

    /* 섹션 라벨 다크 모드 */
    .section-label {
        color: #FFFFFF !important;
    }

    /* 입력 필드 다크 모드 */
    div[data-baseweb="input"] {
        border-color: #475569 !important;
        background: #1E293B !important;
        color: #F1F5F9 !important;
    }
    div[data-baseweb="input"] input {
        color: #F1F5F9 !important;
        background: #1E293B !important;
    }
    div[data-baseweb="select"] > div {
        border-color: #475569 !important;
        background: #1E293B !important;
        color: #F1F5F9 !important;
    }
    div[data-baseweb="select"] input {
        color: #F1F5F9 !important;
    }

    /* Number input 다크 모드 (비중 입력) */
    [data-testid="stNumberInput"] div[data-baseweb="input"] {
        background: #1E293B !important;
        border-color: #475569 !important;
    }
    [data-testid="stNumberInput"] input {
        color: #F1F5F9 !important;
        background: #1E293B !important;
    }
    /* Number input 버튼 */
    [data-testid="stNumberInput"] button {
        color: #CBD5E1 !important;
        background: #334155 !important;
    }
    [data-testid="stNumberInput"] button:hover {
        background: #475569 !important;
        color: #E2E8F0 !important;
    }

    /* 구분선 다크 모드 */
    hr {
        border-color: #334155 !important;
    }

    /* 버튼 다크 모드 */
    button[kind="secondary"] {
        background: #1E293B !important;
        color: #60A5FA !important;
        border: 1px solid #3B82F6 !important;
    }
    button[kind="secondary"]:hover {
        background: #334155 !important;
        border-color: #60A5FA !important;
        color: #93C5FD !important;
    }

    /* 태그 다크 모드 */
    .tag-type {
        background: #1E3A8A !important;
        color: #93C5FD !important;
    }
    .tag-curr {
        background: #334155 !important;
        color: #CBD5E1 !important;
        border: 1px solid #475569 !important;
    }

    /* 자산 목록 행 다크 모드 */
    .asset-ticker {
        color: #F1F5F9 !important;
    }
    .asset-name {
        color: #94A3B8 !important;
    }

    /* Weight % 기호 다크 모드 */
    [data-testid="stHorizontalBlock"]:has(.asset-row) [data-testid="stNumberInput"]::after {
        color: #CBD5E1 !important;
    }

    /* 메트릭 카드 다크 모드 */
    [data-testid="stMetric"] {
        background: #0F172A !important;
    }
    [data-testid="stMetricLabel"] {
        color: #E2E8F0 !important;
    }
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }
    [data-testid="stMetricDelta"] {
        color: #E2E8F0 !important;
    }

    /* 사용자 정보 박스 다크 모드 */
    .sidebar-section-header {
        color: #FFFFFF !important;
    }

    .user-info-box {
        background: #0F172A !important;
        border: 1px solid #334155 !important;
    }
    .user-info-label {
        color: #E2E8F0 !important;
    }
    .user-info-name {
        color: #FFFFFF !important;
    }

    /* 빈 포트폴리오 다크 모드 */
    .empty-portfolio {
        background: #1E293B !important;
        border: 1px dashed #475569 !important;
        color: #E2E8F0 !important;
    }

    /* 그룹 헤더 다크 모드 */
    .group-header {
        color: #FFFFFF !important;
    }

    /* 종목 정보 텍스트 다크 모드 */
    .stock-name {
        color: #E2E8F0 !important;
    }
    .stock-currency {
        color: #CBD5E1 !important;
    }

    /* AI 분석 박스 다크 모드 */
    .ai-analysis-box {
        background: #1E293B !important;
        border: 1px solid #334155 !important;
        color: #E2E8F0 !important;
    }

    /* 차트 배경 다크 모드 */
    [data-testid="stPlotlyChart"] {
        background-color: #1E293B !important;
    }

    /* Plotly 차트 내부 요소 다크 모드 */
    [data-testid="stPlotlyChart"] .plotly .bg {
        fill: #1E293B !important;
    }
    [data-testid="stPlotlyChart"] text {
        fill: #E2E8F0 !important;
    }
    [data-testid="stPlotlyChart"] .gridlayer line {
        stroke: #334155 !important;
    }
    [data-testid="stPlotlyChart"] .zerolinelayer line {
        stroke: #475569 !important;
    }

    /* 히트맵 차트 텍스트 외곽선 (다크 모드) */
    [data-testid="stPlotlyChart"] .heatmaplayer text {
        fill: #FFFFFF !important;
        paint-order: stroke fill;
        stroke: #000000;
        stroke-width: 2.5px;
        stroke-linejoin: round;
    }

    /* 텍스트 입력 다크 모드 */
    [data-baseweb="textarea"] {
        background: #0F172A !important;
        border-color: #475569 !important;
        color: #E2E8F0 !important;
    }
    [data-baseweb="textarea"] textarea {
        color: #E2E8F0 !important;
    }

    /* 날짜 선택 다크 모드 */
    [data-testid="stDateInput"] input {
        background: #0F172A !important;
        border-color: #475569 !important;
        color: #E2E8F0 !important;
    }

    /* 로그인 페이지 다크 모드 */
    .login-title {
        color: #FFFFFF !important;
    }
    .login-subtitle {
        color: #E2E8F0 !important;
    }

    /* 텍스트 입력 레이블 다크 모드 */
    label[data-testid="stWidgetLabel"] {
        color: #F1F5F9 !important;
    }

    /* 텍스트 입력 placeholder 다크 모드 */
    input::placeholder {
        color: #64748B !important;
    }
    textarea::placeholder {
        color: #64748B !important;
    }

    /* 탭 다크 모드 */
    [data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 1px solid #334155 !important;
    }
    [data-baseweb="tab"] {
        color: #CBD5E1 !important;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom-color: #EF4444 !important;
    }
    [data-baseweb="tab"]:hover {
        color: #E2E8F0 !important;
    }

    /* Submit 버튼 다크 모드 */
    [type="submit"] {
        background: #F1F5F9 !important;
        color: #0F172A !important;
        border: 1px solid #475569 !important;
    }
    [type="submit"]:hover {
        background: #E2E8F0 !important;
    }

    /* 에러/성공 메시지 다크 모드 */
    .stAlert {
        background-color: rgba(30, 41, 59, 0.8) !important;
        border-color: #475569 !important;
    }
    [data-testid="stNotification"] {
        background-color: #1E293B !important;
        border-color: #475569 !important;
    }
    [data-testid="stNotification"] [data-testid="stMarkdownContainer"] {
        color: #F1F5F9 !important;
    }

    /* Markdown 컨테이너 다크 모드 */
    [data-testid="stMarkdownContainer"] {
        color: #F1F5F9 !important;
    }
    [data-testid="stMarkdownContainer"] p {
        color: #E2E8F0 !important;
    }
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4 {
        color: #FFFFFF !important;
    }

    /* Caption 다크 모드 */
    .stCaption {
        color: #E2E8F0 !important;
    }

    /* Small 텍스트 */
    small {
        color: #CBD5E1 !important;
    }

    /* Info/Warning/Success 박스 다크 모드 */
    [data-testid="stInfo"] {
        background-color: rgba(59, 130, 246, 0.1) !important;
        color: #93C5FD !important;
    }
    [data-testid="stWarning"] {
        background-color: rgba(251, 191, 36, 0.1) !important;
        color: #FCD34D !important;
    }
    [data-testid="stSuccess"] {
        background-color: rgba(34, 197, 94, 0.1) !important;
        color: #86EFAC !important;
    }
    [data-testid="stError"] {
        background-color: rgba(239, 68, 68, 0.1) !important;
        color: #FCA5A5 !important;
    }

    /* 라디오 버튼 텍스트 다크 모드 */
    [role="radiogroup"] label p {
        color: #F1F5F9 !important;
    }

    /* 체크박스 텍스트 다크 모드 */
    [data-testid="stCheckbox"] label p {
        color: #E2E8F0 !important;
    }

    /* 모든 span 태그 */
    span {
        color: inherit !important;
    }

    /* 리스트 아이템 */
    li {
        color: #E2E8F0 !important;
    }

    /* 코드 블록 */
    code {
        color: #F1F5F9 !important;
        background-color: #1E293B !important;
    }

    /* div 텍스트 */
    div {
        color: inherit !important;
    }

    /* strong, b 태그 */
    strong, b {
        color: #FFFFFF !important;
    }

    /* 테이블 */
    table {
        color: #E2E8F0 !important;
    }
    th {
        color: #F1F5F9 !important;
        background-color: #1E293B !important;
    }
    td {
        color: #E2E8F0 !important;
    }
}
</style>
"""


def apply_styles(st):
    """스타일 CSS를 Streamlit 앱에 적용"""
    st.markdown(APP_CSS, unsafe_allow_html=True)
