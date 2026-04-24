import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime

# ═══════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════
st.set_page_config(
    page_title="Sleepsy · Финансовый калькулятор",
    layout="wide",
    page_icon="🌙"
)

# ═══════════════════════════════════════════════════
#  ГЛОБАЛЬНЫЕ СТИЛИ — тёмная ночная тема Sleepsy
# ═══════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&display=swap');

/* ── Базовые шрифты ─────────────────────────── */
html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', system-ui, sans-serif !important;
}

/* ── Метрические карточки ───────────────────── */
.sc {
    background: linear-gradient(145deg, rgba(30,27,75,0.9) 0%, rgba(49,46,129,0.7) 100%);
    border: 1px solid rgba(167,139,250,0.2);
    border-radius: 18px;
    padding: 1.2rem 1.4rem;
    color: #fff;
    margin-bottom: 0.5rem;
    transition: transform .25s ease, box-shadow .25s ease;
    backdrop-filter: blur(6px);
    position: relative;
    overflow: hidden;
}
.sc::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 0% 0%, rgba(167,139,250,0.12) 0%, transparent 60%);
    pointer-events: none;
}
.sc:hover { transform: translateY(-3px); box-shadow: 0 12px 30px rgba(99,60,220,0.25); }
.sc.good {
    background: linear-gradient(145deg, rgba(2,44,34,0.9), rgba(6,78,59,0.8));
    border-color: rgba(52,211,153,0.3);
}
.sc.good::before { background: radial-gradient(ellipse at 0% 0%, rgba(52,211,153,0.1) 0%, transparent 60%); }
.sc.bad {
    background: linear-gradient(145deg, rgba(69,10,10,0.9), rgba(127,29,29,0.8));
    border-color: rgba(252,165,165,0.3);
}
.sc.bad::before { background: radial-gradient(ellipse at 0% 0%, rgba(252,165,165,0.1) 0%, transparent 60%); }
.sc .lbl { font-size:.68rem; font-weight:600; letter-spacing:.1em; text-transform:uppercase; opacity:.65; margin-bottom:.25rem; }
.sc .val { font-family:'Syne',sans-serif; font-size:1.75rem; font-weight:700; line-height:1.15; }
.sc .dlt { font-size:.78rem; opacity:.75; margin-top:.2rem; }

/* ── Секционный заголовок ───────────────────── */
.s-sect {
    display: flex;
    align-items: center;
    gap: .5rem;
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #a78bfa;
    padding: .5rem 0;
    border-bottom: 1px solid rgba(167,139,250,.18);
    margin: 1.4rem 0 .9rem;
    letter-spacing: .02em;
}

/* ── Информационный баннер ──────────────────── */
.s-info {
    background: linear-gradient(135deg, rgba(79,70,229,0.14), rgba(96,165,250,0.10));
    border: 1px solid rgba(167,139,250,.35);
    border-radius: 12px;
    padding: .8rem 1.2rem;
    color: #c4b5fd;
    font-size: .92rem;
    margin: .8rem 0 1rem;
    line-height: 1.55;
}

/* ── Подсказка-бейдж ────────────────────────── */
.s-badge {
    display: inline-block;
    background: rgba(167,139,250,.15);
    border: 1px solid rgba(167,139,250,.3);
    border-radius: 8px;
    padding: .25rem .7rem;
    font-size: .78rem;
    color: #c4b5fd;
    font-weight: 500;
    margin-bottom: .5rem;
}

/* ── Табы ───────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(15,12,50,.7);
    border-radius: 14px;
    padding: 5px 6px;
    gap: 4px;
    border: 1px solid rgba(99,102,241,.2);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    font-weight: 500;
    color: #818cf8;
    font-size: .88rem;
    padding: .4rem 1.1rem;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4338ca, #6d28d9) !important;
    color: #fff !important;
    box-shadow: 0 4px 12px rgba(99,60,220,.35);
}

/* ── Экспандеры ─────────────────────────────── */
details[data-testid="stExpander"] > summary {
    color: #c4b5fd !important;
    font-weight: 600 !important;
    font-size: .95rem;
}
div[data-testid="stExpander"] {
    background: rgba(30,27,75,.4) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(167,139,250,.18) !important;
}

/* ── Делитель ───────────────────────────────── */
hr { border-color: rgba(167,139,250,.12) !important; margin: 1.2rem 0 !important; }

/* ── Алёрты ─────────────────────────────────── */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
#  УТИЛИТЫ
# ═══════════════════════════════════════════════════
def metric_card(label: str, value: str, delta: str = "", variant: str = "") -> str:
    delta_html = f'<div class="dlt">{delta}</div>' if delta else ""
    return (
        f'<div class="sc {variant}">'
        f'  <div class="lbl">{label}</div>'
        f'  <div class="val">{value}</div>'
        f'  {delta_html}'
        f'</div>'
    )

def section(icon: str, title: str):
    st.markdown(f'<div class="s-sect"><span>{icon}</span><span>{title}</span></div>',
                unsafe_allow_html=True)

def info_box(html: str):
    st.markdown(f'<div class="s-info">{html}</div>', unsafe_allow_html=True)

def badge(text: str):
    st.markdown(f'<div class="s-badge">{text}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
#  ШАПКА
# ═══════════════════════════════════════════════════
h_col1, h_col2 = st.columns([5, 2])
with h_col1:
    st.markdown(
        '<p style="font-family:Syne,sans-serif;font-size:2rem;font-weight:800;'
        'background:linear-gradient(90deg,#a78bfa,#60a5fa);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        'margin:0;line-height:1.15">🌙 Sleepsy — Финансовый калькулятор</p>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p style="color:#818cf8;font-size:.95rem;margin:.3rem 0 0;opacity:.85">'
        'Юнит-экономика: реклама → квиз → разбор сна → подписка</p>',
        unsafe_allow_html=True
    )
with h_col2:
    st.markdown("")   # spacer

st.divider()

# ═══════════════════════════════════════════════════
#  ВКЛАДКИ
# ═══════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "🚀  Трафик",
    "🎯  Воронка квиза",
    "🔄  Подписки",
    "⚙️  Параметры"
])


# ──────────────────────────────────────────────────
# ТАБ 1 · ТРАФИК
# ──────────────────────────────────────────────────
with tab1:
    section("📡", "Рекламный трафик")

    calc_mode = st.radio(
        "Что рассчитывать автоматически?",
        ["Количество переходов", "Стоимость клика (CPC)", "Лимит бюджета"],
        horizontal=True,
        key="calc_mode",
        help=(
            "Выберите один параметр — он будет вычислен из двух остальных. "
            "Например, задайте CPC + бюджет → получите объём трафика."
        )
    )

    col_a, col_b, col_c = st.columns(3)
    default_cpc    = st.session_state.get("cpc_raw", 30.0)
    default_clicks = st.session_state.get("clicks_raw", 10_000)
    default_budget = st.session_state.get("budget_raw", 300_000.0)

    with col_a:
        if calc_mode == "Стоимость клика (CPC)":
            # Вычислим после чтения активных полей — временная заглушка
            cpc_raw = default_cpc
        else:
            cpc_raw = st.number_input(
                "💸 Стоимость клика, ₽ (CPC)",
                min_value=0.01,
                value=float(st.session_state.get("cpc_raw", 30.0)),
                step=0.5, key="cpc_raw",
                help="Средняя цена клика из Яндекс.Директ или другого источника. Включая НДС."
            )
    with col_b:
        if calc_mode == "Количество переходов":
            clicks_raw = default_clicks
        else:
            clicks_raw = st.number_input(
                "🖱️ Количество переходов",
                min_value=1,
                value=int(st.session_state.get("clicks_raw", 10_000)),
                step=500, key="clicks_raw",
                help="Плановое/фактическое число кликов по объявлениям Sleepsy за расчётный период."
            )
    with col_c:
        if calc_mode == "Лимит бюджета":
            budget_raw = default_budget
        else:
            budget_raw = st.number_input(
                "💰 Рекламный бюджет, ₽",
                min_value=0.0,
                value=float(st.session_state.get("budget_raw", 300_000.0)),
                step=5_000.0, key="budget_raw",
                help="Совокупный бюджет на рекламу (Директ, VK Ads, Telegram Ads и т.д.)."
            )

    # ── Взаимозависимый пересчёт ──────────────────
    # Порядок: сначала читаем активные поля, потом вычисляем заблокированное
    if calc_mode == "Количество переходов":
        actual_cpc    = cpc_raw
        actual_budget = budget_raw
        actual_clicks = int(actual_budget / actual_cpc) if actual_cpc > 0 else 0
        # Теперь рисуем задизейбленный инпут с вычисленным значением
        with col_b:
            st.number_input(
                "🖱️ Количество переходов",
                value=actual_clicks, min_value=0, step=500,
                disabled=True,
                key="_clicks_disp",
                help="Рассчитывается автоматически из бюджета и CPC."
            )
    elif calc_mode == "Стоимость клика (CPC)":
        actual_clicks = clicks_raw
        actual_budget = budget_raw
        actual_cpc    = (actual_budget / actual_clicks
                         if actual_clicks > 0 else 0.0)
        with col_a:
            st.number_input(
                "💸 Стоимость клика, ₽ (CPC)",
                value=round(actual_cpc, 2), min_value=0.0, step=0.5,
                disabled=True,
                key="_cpc_disp",
                help="Рассчитывается автоматически из бюджета и кликов."
            )
    else:   # Лимит бюджета
        actual_cpc    = cpc_raw
        actual_clicks = clicks_raw
        actual_budget = actual_cpc * actual_clicks
        with col_c:
            st.number_input(
                "💰 Рекламный бюджет, ₽",
                value=round(actual_budget, 2), min_value=0.0, step=5_000.0,
                disabled=True,
                key="_budget_disp",
                help="Рассчитывается автоматически из CPC и кликов."
            )

    info_box(
        f"📊 Итог: <strong>{actual_clicks:,} переходов</strong> "
        f"× <strong>{actual_cpc:.2f} ₽</strong> "
        f"= <strong>{actual_budget:,.0f} ₽</strong> рекламных расходов"
    )


# ──────────────────────────────────────────────────
# ТАБ 2 · ВОРОНКА КВИЗА
# ──────────────────────────────────────────────────
with tab2:
    section("🧠", "Квиз-воронка Sleepsy")
    badge("Путь: клик → квиз без регистрации → оплата разбора")

    st.markdown(
        '<p style="color:#818cf8;font-size:.88rem;margin:0 0 .8rem">'
        'Пользователь вводит сон, проходит вовлекающие шаги (commitment escalation), '
        'затем оплачивает полный разбор. Регистрация — опционально.</p>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    with col1:
        conv_quiz = st.slider(
            "📋 Доля завершивших квиз (лиды), %",
            0.0, 100.0,
            float(st.session_state.get("conv_quiz_pct", 35.0)),
            0.5, key="conv_quiz_pct",
            help=(
                "% посетителей, которые прошли квиз до конца и оставили контакт/инвестировали время. "
                "Benchmark квиз-воронок: 25–45%. Для Яндекс.Директ ожидайте 20–35%."
            )
        ) / 100.0
    with col2:
        conv_purchase = st.slider(
            "🌙 Конверсия в покупку разбора, %",
            0.0, 100.0,
            float(st.session_state.get("conv_purchase_pct", 18.0)),
            0.5, key="conv_purchase_pct",
            help=(
                "% прошедших квиз, совершивших покупку полного анализа сна. "
                "При цене 149 ₽ и высокой вовлечённости benchmark: 12–25%."
            )
        ) / 100.0

    st.divider()
    section("💜", "Цена и себестоимость разбора сна")

    col3, col4 = st.columns(2)
    with col3:
        price_one_time = st.number_input(
            "💜 Цена полного разбора сна, ₽",
            min_value=0.0,
            value=float(st.session_state.get("price_one_time", 149.0)),
            step=10.0, key="price_one_time",
            help="Публичная цена одного AI-анализа. По умолчанию 149 ₽ — стандарт Sleepsy."
        )
    with col4:
        cogs_one_time = st.number_input(
            "🤖 Себестоимость разбора (AI-токены + инфра), ₽",
            min_value=0.0,
            value=float(st.session_state.get("cogs_one_time", 12.0)),
            step=1.0, key="cogs_one_time",
            help=(
                "Прямые затраты на один разбор: токены LLM (Claude/GPT), "
                "хостинг, поддержка, налоги. Ориентир: 8–20 ₽."
            )
        )

    st.divider()
    section("📧", "Монетизация лидов без покупки")

    email_monet = st.number_input(
        "📨 Доход с лида без покупки, ₽",
        min_value=0.0,
        value=float(st.session_state.get("email_monet", 5.0)),
        step=0.5, key="email_monet",
        help=(
            "Средний доход с пользователя, прошедшего квиз, но НЕ купившего разбор. "
            "Включает: email-последовательности с повторными офферами, PDF-бонус, "
            "партнёрские ссылки, ретаргетинг-аудитории."
        )
    )


# ──────────────────────────────────────────────────
# ТАБ 3 · ПОДПИСКИ
# ──────────────────────────────────────────────────
with tab3:
    section("🔄", "Подписочные тарифы Sleepsy")

    info_box(
        "💡 Конверсия в подписку считается <strong>от числа разовых покупателей</strong>. "
        "Пользователь выбирает <em>один</em> тариф — убедитесь, что суммарная конверсия ≤ 100%. "
        "LTV нетто учитывает ожидаемый срок жизни подписки."
    )

    # Тарифы с названиями в стиле Sleepsy
    TARIFF_META = [
        {
            "name": "🌙 Базовый",
            "desc": "Ограниченные разборы в месяц, базовая аналитика",
            "conv": 15.0, "price": 299.0, "renew": 80.0, "dur": 5.0, "cogs": 20.0
        },
        {
            "name": "⭐ Стандарт",
            "desc": "Неограниченные разборы, 6 методологий психоанализа",
            "conv": 7.0, "price": 599.0, "renew": 87.0, "dur": 7.7, "cogs": 40.0
        },
        {
            "name": "🔮 Премиум",
            "desc": "Полный доступ: психо + эзотерический трек + PDF-бонусы",
            "conv": 3.0, "price": 999.0, "renew": 93.0, "dur": 14.3, "cogs": 70.0
        }
    ]

    tariffs = []
    for idx, meta in enumerate(TARIFF_META):
        with st.expander(f"{meta['name']} — {meta['desc']}", expanded=(idx == 0)):
            col_t1, col_t2, col_t3 = st.columns(3)
            with col_t1:
                conv = st.number_input(
                    "Конверсия в тариф, %", key=f"conv_{idx}",
                    value=float(st.session_state.get(f"conv_{idx}", meta["conv"])),
                    min_value=0.0, max_value=100.0, step=0.5,
                    help="% разовых покупателей, оформивших именно этот тариф."
                ) / 100.0
            with col_t2:
                price = st.number_input(
                    "Цена в месяц, ₽", key=f"price_{idx}",
                    value=float(st.session_state.get(f"price_{idx}", meta["price"])),
                    min_value=0.0, step=10.0,
                    help="Ежемесячный платёж за подписку."
                )
            with col_t3:
                renew = st.number_input(
                    "Ретеншн (продление), %", key=f"renew_{idx}",
                    value=float(st.session_state.get(f"renew_{idx}", meta["renew"])),
                    min_value=0.0, max_value=99.9, step=1.0,
                    help="Вероятность продления подписки на следующий месяц."
                ) / 100.0

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                theory_life = round(1 / (1 - renew), 1) if renew < 1 else 999.0
                duration = st.number_input(
                    "Ожидаемый срок подписки, мес", key=f"dur_{idx}",
                    value=float(st.session_state.get(f"dur_{idx}", meta["dur"])),
                    min_value=0.1, step=0.1,
                    help=(
                        f"Средний срок жизни подписки. "
                        f"При ретеншне {renew*100:.0f}% теоретический LT = 1/(1−r) = {theory_life} мес. "
                        f"Задайте реалистичный срок с учётом контракта и платформы."
                    )
                )
            with col_d2:
                cogs = st.number_input(
                    "Себестоимость в месяц, ₽", key=f"cogs_{idx}",
                    value=float(st.session_state.get(f"cogs_{idx}", meta["cogs"])),
                    min_value=0.0, step=5.0,
                    help="Затраты на обслуживание одного подписчика в месяц: AI-токены, хостинг, поддержка."
                )

            tariffs.append({
                "name": meta["name"],
                "conv": conv, "price": price, "renew": renew,
                "dur": duration, "cogs": cogs
            })


# ──────────────────────────────────────────────────
# ТАБ 4 · ПАРАМЕТРЫ
# ──────────────────────────────────────────────────
with tab4:
    section("⚙️", "Финансовые параметры")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        payment_fee = st.slider(
            "💳 Комиссия платёжной системы, %",
            0.0, 10.0,
            float(st.session_state.get("payment_fee_pct", 3.5)),
            0.1, key="payment_fee_pct",
            help=(
                "Комиссия YooMoney/Lava — основных платёжных систем Sleepsy. "
                "YooMoney: ~3.5%, Lava: ~3.0%. "
                "Считается от каждого успешного платежа."
            )
        ) / 100.0
    with col_s2:
        refund_rate = st.slider(
            "↩️ Возвраты и чарджбэки, %",
            0.0, 20.0,
            float(st.session_state.get("refund_rate_pct", 1.0)),
            0.1, key="refund_rate_pct",
            help=(
                "% платежей с возвратом или оспариванием. "
                "Для цифровых продуктов до 149 ₽ ожидайте 0.5–1.5%."
            )
        ) / 100.0

    st.divider()
    section("📐", "Справка: ключевые формулы")

    info_box(
        "<strong>ROI</strong> = Валовая прибыль / Рекламный бюджет × 100% "
        "&nbsp;|&nbsp; "
        "<strong>LTV</strong> = (Цена − Себест.) × Срок × (1 − Комиссия − Возвраты) "
        "&nbsp;|&nbsp; "
        "<strong>CAC</strong> = Бюджет / Разовых покупателей "
        "&nbsp;|&nbsp; "
        "<strong>Окупаемость CAC</strong> = CAC / Месячная маржа подписки"
    )

    st.divider()
    section("💾", "Профили настроек")

    PROFILES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sleepsy_profiles.json")

    def load_profiles() -> dict:
        if os.path.exists(PROFILES_FILE):
            try:
                with open(PROFILES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f).get("profiles", {})
            except Exception:
                return {}
        return {}

    def save_profiles(profiles: dict):
        with open(PROFILES_FILE, "w", encoding="utf-8") as f:
            json.dump({"profiles": profiles}, f, ensure_ascii=False, indent=2)

    profiles = load_profiles()

    # ── Сохранение ────────────────────────────────
    pf_col1, pf_col2 = st.columns([3, 1])
    with pf_col1:
        profile_name = st.text_input(
            "Имя профиля", value="Базовый сценарий",
            placeholder="Например: Агрессивный рост", key="_pf_name"
        )
    with pf_col2:
        st.markdown("<div style='margin-top:1.8rem'></div>", unsafe_allow_html=True)
        if st.button("💾 Сохранить", use_container_width=True):
            if profile_name.strip():
                tariff_data = []
                for idx in range(3):
                    tariff_data.append({
                        "conv":  st.session_state.get(f"conv_{idx}", [15.0, 7.0, 3.0][idx]),
                        "price": st.session_state.get(f"price_{idx}", [299.0, 599.0, 999.0][idx]),
                        "renew": st.session_state.get(f"renew_{idx}", [80.0, 87.0, 93.0][idx]),
                        "dur":   st.session_state.get(f"dur_{idx}", [5.0, 7.7, 14.3][idx]),
                        "cogs":  st.session_state.get(f"cogs_{idx}", [20.0, 40.0, 70.0][idx]),
                    })
                profiles[profile_name.strip()] = {
                    "saved_at": datetime.now().isoformat(timespec="seconds"),
                    "traffic": {
                        "cpc":       st.session_state.get("cpc_raw", 30.0),
                        "clicks":    st.session_state.get("clicks_raw", 10000),
                        "budget":    st.session_state.get("budget_raw", 300000.0),
                        "calc_mode": st.session_state.get("calc_mode", "Количество переходов"),
                    },
                    "quiz": {
                        "conv_quiz":      st.session_state.get("conv_quiz_pct", 35.0),
                        "conv_purchase":  st.session_state.get("conv_purchase_pct", 18.0),
                        "price_one_time": st.session_state.get("price_one_time", 149.0),
                        "cogs_one_time":  st.session_state.get("cogs_one_time", 12.0),
                        "email_monet":    st.session_state.get("email_monet", 5.0),
                    },
                    "params": {
                        "payment_fee": st.session_state.get("payment_fee_pct", 3.5),
                        "refund_rate": st.session_state.get("refund_rate_pct", 1.0),
                    },
                    "tariffs": tariff_data,
                }
                save_profiles(profiles)
                st.success(f"✅ Профиль «{profile_name.strip()}» сохранён!")

    # ── Загрузка / удаление ───────────────────────
    if profiles:
        st.markdown("<div style='margin-top:.5rem'></div>", unsafe_allow_html=True)
        ld_col1, ld_col2, ld_col3 = st.columns([3, 1, 1])
        with ld_col1:
            selected_profile = st.selectbox(
                "Загрузить профиль", options=list(profiles.keys()), key="_pf_select"
            )
        with ld_col2:
            st.markdown("<div style='margin-top:1.8rem'></div>", unsafe_allow_html=True)
            if st.button("📂 Загрузить", use_container_width=True):
                pdata = profiles[selected_profile]
                # Трафик
                t = pdata.get("traffic", {})
                st.session_state["calc_mode"]  = t.get("calc_mode", "Количество переходов")
                st.session_state["cpc_raw"]    = float(t.get("cpc", 30.0))
                st.session_state["clicks_raw"] = int(t.get("clicks", 10000))
                st.session_state["budget_raw"] = float(t.get("budget", 300000.0))
                # Квиз
                q = pdata.get("quiz", {})
                st.session_state["conv_quiz_pct"]     = float(q.get("conv_quiz", 35.0))
                st.session_state["conv_purchase_pct"] = float(q.get("conv_purchase", 18.0))
                st.session_state["price_one_time"]    = float(q.get("price_one_time", 149.0))
                st.session_state["cogs_one_time"]     = float(q.get("cogs_one_time", 12.0))
                st.session_state["email_monet"]       = float(q.get("email_monet", 5.0))
                # Параметры
                p = pdata.get("params", {})
                st.session_state["payment_fee_pct"] = float(p.get("payment_fee", 3.5))
                st.session_state["refund_rate_pct"] = float(p.get("refund_rate", 1.0))
                # Тарифы
                for idx, td in enumerate(pdata.get("tariffs", [])):
                    st.session_state[f"conv_{idx}"]  = float(td.get("conv", [15.0, 7.0, 3.0][idx]))
                    st.session_state[f"price_{idx}"] = float(td.get("price", [299.0, 599.0, 999.0][idx]))
                    st.session_state[f"renew_{idx}"] = float(td.get("renew", [80.0, 87.0, 93.0][idx]))
                    st.session_state[f"dur_{idx}"]   = float(td.get("dur", [5.0, 7.7, 14.3][idx]))
                    st.session_state[f"cogs_{idx}"]  = float(td.get("cogs", [20.0, 40.0, 70.0][idx]))
                st.success(f"✅ Загружен профиль «{selected_profile}»")
                st.rerun()
        with ld_col3:
            st.markdown("<div style='margin-top:1.8rem'></div>", unsafe_allow_html=True)
            if st.button("🗑️ Удалить", use_container_width=True):
                del profiles[selected_profile]
                save_profiles(profiles)
                st.success(f"Профиль «{selected_profile}» удалён")
                st.rerun()

        # Дата сохранения
        saved_at = profiles.get(selected_profile, {}).get("saved_at", "")
        if saved_at:
            st.caption(f"🕐 Сохранён: {saved_at}")
    else:
        st.info("Нет сохранённых профилей. Введите имя выше и нажмите «Сохранить».")


# ═══════════════════════════════════════════════════
#  РАСЧЁТНАЯ ЛОГИКА
#  ── Исправлены баги оригинала:
#     1. ROI: убрана ошибочная −1 (прибыль уже нетто)
#     2. exp_months: используем dur напрямую (не геом. ряд)
#     3. payback: cac_per / monthly_margin (не cac*conv)
# ═══════════════════════════════════════════════════
def calculate_metrics():
    ad_spend = actual_clicks * actual_cpc

    # ── Воронка ───────────────────────────────────
    leads             = int(actual_clicks * conv_quiz)
    one_time_buys     = int(leads * conv_purchase)

    # ── Разовые разборы ───────────────────────────
    gross_ot    = one_time_buys * price_one_time
    cogs_ot     = one_time_buys * cogs_one_time
    fees_ot     = gross_ot * payment_fee
    refunds_ot  = gross_ot * refund_rate
    net_ot      = gross_ot - cogs_ot - fees_ot - refunds_ot

    # ── Подписки ──────────────────────────────────
    subs_rows = []
    total_sub_rev = total_sub_cogs = total_sub_fees = total_sub_refunds = 0

    cac_per_purchase = ad_spend / one_time_buys if one_time_buys > 0 else 0

    for i, t in enumerate(tariffs):
        count    = int(one_time_buys * t["conv"])
        # FIX: используем заданный срок напрямую,
        #      а не обрезанный геометрический ряд
        exp_m    = t["dur"]

        rev_per     = t["price"] * exp_m
        cogs_per    = t["cogs"]  * exp_m
        fees_per    = rev_per * payment_fee
        refunds_per = rev_per * refund_rate
        net_per     = rev_per - cogs_per - fees_per - refunds_per

        total_sub_rev     += count * rev_per
        total_sub_cogs    += count * cogs_per
        total_sub_fees    += count * fees_per
        total_sub_refunds += count * refunds_per

        monthly_margin = (t["price"] - t["cogs"]) * (1 - payment_fee - refund_rate)
        # FIX: срок окупаемости CAC через маржу от подписки
        payback = (cac_per_purchase / monthly_margin
                   if monthly_margin > 0 and cac_per_purchase > 0 else float("inf"))

        subs_rows.append({
            "Тариф":           t["name"],
            "Подписчиков":     count,
            "LTV нетто, ₽":    f"{net_per:,.0f}",
            "Окупаемость CAC": f"{payback:.1f} мес." if payback != float("inf") else "∞"
        })

    # ── Email-монетизация лидов без покупки ───────
    non_buyers = leads - one_time_buys
    email_rev  = non_buyers * email_monet

    # ── Сводные финансы ───────────────────────────
    total_revenue = gross_ot + total_sub_rev + email_rev
    total_costs   = cogs_ot + total_sub_cogs + ad_spend
    all_fees      = total_sub_fees + total_sub_refunds + fees_ot + refunds_ot
    gross_profit  = total_revenue - total_costs - all_fees

    # ── Взвешенный LTV на одного покупателя ───────
    # = чистая прибыль с разбора + вероятностные LTV подписок
    ltv_one_time = (price_one_time - cogs_one_time) * (1 - payment_fee - refund_rate)
    weighted_ltv = ltv_one_time if one_time_buys > 0 else 0
    for t in tariffs:
        exp_m   = t["dur"]   # FIX: напрямую, не геом. ряд
        net_sub = (t["price"] - t["cogs"]) * exp_m * (1 - payment_fee - refund_rate)
        weighted_ltv += net_sub * t["conv"]

    ltv_cac = weighted_ltv / cac_per_purchase if cac_per_purchase > 0 else 0

    # FIX ROI: прибыль уже включает вычет ad_spend,
    #          поэтому ROI = прибыль / затраты × 100
    #          (убрана ошибочная «−1», которая давала ROMI-100%)
    roi    = (gross_profit / ad_spend * 100) if ad_spend > 0 else 0
    margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
    cpl    = ad_spend / leads if leads > 0 else 0

    # ── Помесячная выручка (12 мес.) ─────────────
    # Месяц 1: разборы + email + первые платежи подписок
    # Месяц 2–12: только продления (с учётом ретеншна)
    N_MONTHS = 12
    monthly_breakdown = []
    for m in range(1, N_MONTHS + 1):
        if m == 1:
            rev_ot_m    = gross_ot
            rev_email_m = email_rev
            rev_subs_m  = sum(
                int(one_time_buys * t["conv"]) * t["price"]
                for t in tariffs
            )
        else:
            rev_ot_m    = 0.0
            rev_email_m = 0.0
            rev_subs_m  = sum(
                int(one_time_buys * t["conv"]) * t["price"] * (t["renew"] ** (m - 1))
                for t in tariffs
            )
        monthly_breakdown.append({
            "Месяц": m,
            "Разборы": rev_ot_m,
            "Подписки": rev_subs_m,
            "Email": rev_email_m,
            "Итого": rev_ot_m + rev_subs_m + rev_email_m,
        })
    monthly_df = pd.DataFrame(monthly_breakdown)

    # ── Данные для графиков ───────────────────────
    pnl_df = pd.DataFrame({
        "Статья": [
            "Разборы снов", "Подписки", "Email-монет.",
            "Реклама", "Себестоимость", "Комиссии и возвраты"
        ],
        "Сумма": [
            gross_ot, total_sub_rev, email_rev,
            -ad_spend, -(cogs_ot + total_sub_cogs), -all_fees
        ],
        "Тип": ["доход", "доход", "доход", "расход", "расход", "расход"]
    })

    funnel_df = pd.DataFrame({
        "Этап": [
            "🖱️ Клики по рекламе",
            "📋 Прошли квиз",
            "💜 Купили разбор",
            "🔄 Оформили подписку"
        ],
        "Пользователей": [
            actual_clicks,
            leads,
            one_time_buys,
            sum(int(one_time_buys * t["conv"]) for t in tariffs)
        ]
    })

    return {
        "traffic":   {"clicks": actual_clicks, "leads": leads, "cpl": cpl},
        "one_time":  one_time_buys,
        "summary": {
            "total_revenue": total_revenue,
            "gross_profit":  gross_profit,
            "roi":           roi,
            "margin":        margin,
            "ltv_cac":       ltv_cac,
            "cac":           cac_per_purchase,
            "ltv":           weighted_ltv
        },
        "subs":    pd.DataFrame(subs_rows),
        "monthly": monthly_df,
        "charts":  {"pnl": pnl_df, "funnel": funnel_df}
    }


res = calculate_metrics()
s   = res["summary"]
one_time_buys_calc = res["one_time"]


# ═══════════════════════════════════════════════════
#  ДАШБОРД — KPI-карточки
# ═══════════════════════════════════════════════════
st.divider()
st.markdown(
    '<p style="font-family:Syne,sans-serif;font-size:1.3rem;font-weight:700;'
    'color:#a78bfa;margin-bottom:.8rem">📊 Результаты модели</p>',
    unsafe_allow_html=True
)

row1 = st.columns(4)
row2 = st.columns(3)

profit_ok = s["gross_profit"] > 0
ltv_ok    = s["ltv_cac"] >= 3

with row1[0]:
    st.markdown(metric_card(
        "Общая выручка",
        f"{s['total_revenue']:,.0f} ₽",
        f"Маржа: {s['margin']:.1f}%"
    ), unsafe_allow_html=True)

with row1[1]:
    st.markdown(metric_card(
        "Валовая прибыль",
        f"{s['gross_profit']:,.0f} ₽",
        f"ROI: {s['roi']:+.1f}%",
        "good" if profit_ok else "bad"
    ), unsafe_allow_html=True)

with row1[2]:
    st.markdown(metric_card(
        "LTV : CAC",
        f"{s['ltv_cac']:.2f}×",
        "✅ Здоровый" if ltv_ok else ("⚠️ Допустимый" if s["ltv_cac"] >= 2 else "🔴 Критичный"),
        "good" if ltv_ok else ("" if s["ltv_cac"] >= 2 else "bad")
    ), unsafe_allow_html=True)

with row1[3]:
    st.markdown(metric_card(
        "CAC (стоимость покупателя)",
        f"{s['cac']:,.0f} ₽",
        "Бюджет / Разовых покупателей"
    ), unsafe_allow_html=True)

with row2[0]:
    st.markdown(metric_card(
        "Лидов из квиза",
        f"{res['traffic']['leads']:,}",
        f"CPL: {res['traffic']['cpl']:.0f} ₽"
    ), unsafe_allow_html=True)

with row2[1]:
    st.markdown(metric_card(
        "Разовых покупателей",
        f"{one_time_buys_calc:,}",
        f"Конверс. из лида: {res['traffic']['leads'] and one_time_buys_calc / res['traffic']['leads'] * 100:.1f}%"
        if res["traffic"]["leads"] > 0 else "—"
    ), unsafe_allow_html=True)

with row2[2]:
    st.markdown(metric_card(
        "LTV на покупателя (нетто)",
        f"{s['ltv']:,.0f} ₽",
        "Разбор + вероятностные подписки"
    ), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
#  АНАЛИТИКА — вложенные вкладки
# ═══════════════════════════════════════════════════
st.divider()
tab_c1, tab_c2, tab_c3, tab_c4 = st.tabs(
    ["📊  P&L структура", "🔽  Воронка", "📅  Помесячно", "🔬  Сценарии"]
)

# ── P&L ───────────────────────────────────────────
with tab_c1:
    pnl_df = res["charts"]["pnl"]
    COLOR_MAP = {
        "доход":  "#818cf8",
        "расход": "#f472b6"
    }
    fig_pnl = px.bar(
        pnl_df, x="Статья", y="Сумма", color="Тип",
        color_discrete_map=COLOR_MAP,
        text_auto=".0f", height=340,
        title="Структура доходов и расходов, ₽"
    )
    fig_pnl.update_layout(
        showlegend=True,
        legend_title_text="",
        plot_bgcolor  ="rgba(0,0,0,0)",
        paper_bgcolor ="rgba(0,0,0,0)",
        font_color    ="#c4b5fd",
        title_font    =dict(size=14, family="DM Sans"),
        margin        =dict(t=40, b=20, l=10, r=10),
        bargap        =0.25,
    )
    fig_pnl.update_traces(marker_line_width=0, textfont_color="#fff")
    st.plotly_chart(fig_pnl, use_container_width=True)

    st.markdown(
        '<p style="font-family:Syne,sans-serif;font-size:.95rem;font-weight:700;'
        'color:#a78bfa;margin:.6rem 0 .4rem">Детализация по подписочным тарифам</p>',
        unsafe_allow_html=True
    )
    st.dataframe(res["subs"], use_container_width=True, hide_index=True)


# ── Воронка ───────────────────────────────────────

with tab_c2:
    funnel_df = res["charts"]["funnel"]
    fig_fun = go.Figure(go.Funnel(
        y=funnel_df["Этап"],
        x=funnel_df["Пользователей"],
        textposition="inside",
        textinfo="value+percent initial",
        marker=dict(
            color=["#6366f1", "#7c3aed", "#a78bfa", "#c4b5fd"],
            line=dict(color="rgba(0,0,0,0)", width=0)
        ),
        connector=dict(line=dict(color="rgba(167,139,250,0.25)", width=2))
    ))
    fig_fun.update_layout(
        height=350,
        plot_bgcolor ="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color   ="#c4b5fd",
        font_family  ="DM Sans",
        margin       =dict(t=20, b=20, l=10, r=10)
    )
    st.plotly_chart(fig_fun, use_container_width=True)


# ── Помесячная динамика ────────────────────────────
with tab_c3:
    monthly_df = res["monthly"]
    fig_month = go.Figure()
    fig_month.add_trace(go.Bar(
        x=monthly_df["Месяц"], y=monthly_df["Подписки"],
        name="Подписки", marker_color="#818cf8"
    ))
    fig_month.add_trace(go.Bar(
        x=monthly_df["Месяц"], y=monthly_df["Разборы"],
        name="Разборы", marker_color="#a78bfa"
    ))
    fig_month.add_trace(go.Bar(
        x=monthly_df["Месяц"], y=monthly_df["Email"],
        name="Email-монет.", marker_color="#f472b6"
    ))
    fig_month.update_layout(
        barmode="stack", height=360,
        title="📅 Динамика выручки по месяцам, ₽",
        title_font=dict(size=14, family="DM Sans"),
        xaxis=dict(title="Месяц", tickmode="linear", tick0=1, dtick=1, color="#c4b5fd"),
        yaxis=dict(title="Выручка, ₽", color="#c4b5fd"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#c4b5fd", font_family="DM Sans",
        legend=dict(orientation="h", y=1.12, x=0),
        margin=dict(t=55, b=20, l=10, r=10),
    )
    fig_month.update_traces(marker_line_width=0)
    st.plotly_chart(fig_month, use_container_width=True)

    disp_df = monthly_df.copy()
    for col in ["Разборы", "Подписки", "Email", "Итого"]:
        disp_df[col] = disp_df[col].map(lambda x: f"{x:,.0f} ₽")
    st.dataframe(disp_df, use_container_width=True, hide_index=True)


# ── Сценарии ──────────────────────────────────────
with tab_c4:
    st.markdown(
        '<p style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;'
        'color:#a78bfa;margin-bottom:.5rem">🔬 Анализ чувствительности</p>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p style="color:#818cf8;font-size:.86rem;margin-bottom:1rem">'
        'Как изменение конверсий в квизе и покупке влияет на ключевые метрики?</p>',
        unsafe_allow_html=True
    )

    sc1, sc2 = st.columns(2)
    with sc1:
        ce_t = st.slider(
            "Тест. доля завершивших квиз, %",
            5.0, 70.0, conv_quiz * 100, 1.0
        ) / 100.0
    with sc2:
        cp_t = st.slider(
            "Тест. конверсия в покупку, %",
            2.0, 50.0, conv_purchase * 100, 1.0
        ) / 100.0

    test_leads = int(actual_clicks * ce_t)
    test_purch = int(test_leads * cp_t)
    test_cac   = actual_budget / test_purch if test_purch > 0 else 1e9

    # LTV остаётся той же (конверсии в подписку не меняем в сценарии)
    test_ltv = (price_one_time - cogs_one_time) * (1 - refund_rate - payment_fee)
    for t in tariffs:
        exp_m    = t["dur"]   # FIX
        net_sub  = (t["price"] - t["cogs"]) * exp_m * (1 - payment_fee - refund_rate)
        test_ltv += net_sub * t["conv"]

    test_email_rev = (test_leads - test_purch) * email_monet
    # FIX ROI: прибыль = LTV × покупателей + email_rev − бюджет
    test_profit = test_purch * test_ltv + test_email_rev - actual_budget
    test_roi    = (test_profit / actual_budget * 100) if actual_budget > 0 else 0
    test_ltv_cac = test_ltv / test_cac if test_cac < 1e8 else 0

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(
            "Покупателей разборов",
            f"{test_purch:,}",
            delta=f"{test_purch - one_time_buys_calc:+,}"
        )
    with m2:
        st.metric(
            "ROI сценария",
            f"{test_roi:+.1f}%",
            delta=f"{test_roi - s['roi']:+.1f} п.п."
        )
    with m3:
        st.metric(
            "LTV:CAC сценария",
            f"{test_ltv_cac:.2f}×",
            delta=f"{test_ltv_cac - s['ltv_cac']:+.2f}×"
        )


# ═══════════════════════════════════════════════════
#  ИТОГОВЫЙ ДИАГНОСТИЧЕСКИЙ СИГНАЛ
# ═══════════════════════════════════════════════════
st.divider()
ltv_ratio = s["ltv_cac"]
if ltv_ratio < 1:
    st.error(
        "🔴 **LTV:CAC < 1×** — реклама не окупается. "
        "Бизнес убыточен на каждом привлечённом пользователе. "
        "Пересмотрите цену разбора, конверсию воронки или снизьте CPC."
    )
elif ltv_ratio < 2:
    st.error(
        "🔴 **LTV:CAC < 2×** — экономика отрицательная. "
        "Рост ретеншна подписок или конверсии в покупку приоритетны."
    )
elif ltv_ratio < 3:
    st.warning(
        "🟡 **LTV:CAC 2–3×** — юнит-экономика работает, но с низким запасом. "
        "Оптимизируйте ретеншн подписок или снизьте CAC для масштабирования."
    )
else:
    st.success(
        "🟢 **LTV:CAC ≥ 3×** — здоровая юнит-экономика Sleepsy. "
        "Можно уверенно масштабировать рекламный бюджет."
    )

st.caption(
    "💡 Расчёты носят оценочный характер и предназначены для стратегического планирования. "
    "Данные по умолчанию ориентированы на продукт Sleepsy: AI-анализ снов, "
    "цена разбора 149 ₽, YooMoney/Lava, квиз-воронка без регистрации."
)
