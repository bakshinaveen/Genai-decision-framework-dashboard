"""
MBA Final Project — Phase 6: Decision Intelligence Dashboard
From Hype to Value: GenAI Investment Strategy for Indian Knowledge-Based SMEs
Naveen Bakshi — M24MSE003

Run:     python -m streamlit run MBA_Phase6_Dashboard.py
Requires: pip install streamlit plotly pandas
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GenAI Investment Decision Framework",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── AHP Global Weights from Phase 4 ──────────────────────────────────────────
WEIGHTS = {
    "Total TCO":           0.1692,
    "Budget Availability": 0.1692,
    "Expected ROI":        0.0846,
    "Tech Infrastructure": 0.0516,
    "AI Talent":           0.0961,
    "Data Readiness":      0.0516,
    "Leadership Literacy": 0.0278,
    "Competitive Diff.":   0.0364,
    "Productivity Gain":   0.0660,
    "Client/Market Demand":0.0201,
    "Regulatory Risk":     0.1224,
    "Vendor Lock-in":      0.0372,
    "Workforce Resistance":0.0675,
}

META = {
    "Total TCO":           "Cost & Financial",
    "Budget Availability": "Cost & Financial",
    "Expected ROI":        "Cost & Financial",
    "Tech Infrastructure": "Org Readiness",
    "AI Talent":           "Org Readiness",
    "Data Readiness":      "Org Readiness",
    "Leadership Literacy": "Org Readiness",
    "Competitive Diff.":   "Strategic Value",
    "Productivity Gain":   "Strategic Value",
    "Client/Market Demand":"Strategic Value",
    "Regulatory Risk":     "Impl. Risk",
    "Vendor Lock-in":      "Impl. Risk",
    "Workforce Resistance":"Impl. Risk",
}

RISK_VARS = {"Regulatory Risk", "Vendor Lock-in", "Workforce Resistance"}

# ── Colours — all in rgba() so Plotly accepts them ───────────────────────────
META_COLORS = {
    "Cost & Financial": "#E74C3C",
    "Org Readiness":    "#27AE60",
    "Strategic Value":  "#F39C12",
    "Impl. Risk":       "#2980B9",
}
META_RGBA_FILL = {
    "Cost & Financial": "rgba(231,76,60,0.15)",
    "Org Readiness":    "rgba(39,174,96,0.15)",
    "Strategic Value":  "rgba(243,156,18,0.15)",
    "Impl. Risk":       "rgba(41,128,185,0.15)",
}

STRATEGY_COLORS = {
    "BUILD":    "#27AE60",
    "BUY":      "#2980B9",
    "OUTSOURCE":"#F39C12",
    "DELAY":    "#E74C3C",
}
STRATEGY_RGBA_FILL = {
    "BUILD":    "rgba(39,174,96,0.18)",
    "BUY":      "rgba(41,128,185,0.18)",
    "OUTSOURCE":"rgba(243,156,18,0.18)",
    "DELAY":    "rgba(231,76,60,0.18)",
}
STRATEGY_ICONS = {
    "BUILD":    "🔨",
    "BUY":      "🛒",
    "OUTSOURCE":"🤝",
    "DELAY":    "⏳",
}

# ── Scoring anchors ───────────────────────────────────────────────────────────
ANCHORS = {
    "Total TCO":{"help":"Full 3-year cost of GenAI adoption relative to annual revenue",
        "labels":{1:"Build cost >30% revenue — unaffordable",2:"Build cost 20–30% — very high",
                  3:"Build cost 10–20% or Buy <Rs 10L/yr",4:"Build cost 5–10% or Buy <Rs 5L/yr",
                  5:"Build cost <5% revenue or Buy <Rs 2L/yr — very affordable"}},
    "Budget Availability":{"help":"Discretionary capital available for GenAI investment",
        "labels":{1:"No AI budget at all",2:"<Rs 5L available",3:"Rs 5L–25L",
                  4:"Rs 25L–1Cr",5:">Rs 1Cr committed to AI"}},
    "Expected ROI":{"help":"Projected productivity/revenue gain from GenAI vs investment cost",
        "labels":{1:"No visible productivity use case",2:"<10% productivity gain",
                  3:"10–20% gain expected",4:"20–40% gain expected",5:">40% gain or revenue growth"}},
    "Tech Infrastructure":{"help":"Cloud readiness, APIs, and workflow digitisation level",
        "labels":{1:"Paper-based, no cloud",2:"Basic cloud (email/storage only)",
                  3:"Cloud tools + some APIs",4:"Cloud-native + integration capability",
                  5:"Full cloud-native + data pipelines + APIs"}},
    "AI Talent":{"help":"In-house AI/ML skills. Score = 1 triggers DELAY gate.",
        "labels":{1:"Zero AI skills — no one can evaluate AI tools",
                  2:"1–2 staff with basic AI awareness",
                  3:"1+ staff with AI/ML hands-on exposure",
                  4:"Dedicated data analyst or ML engineer on team",
                  5:"In-house AI team or proven AI lead hired"}},
    "Data Readiness":{"help":"Quality and structure of proprietary data for AI use",
        "labels":{1:"Knowledge in people's heads, no digital records",
                  2:"Unstructured PDFs and emails only",
                  3:"Structured data in spreadsheets",
                  4:"Structured data in CRM/ERP systems",
                  5:"Clean tagged data with API access — GenAI-ready"}},
    "Leadership Literacy":{"help":"CEO understanding of GenAI. Score = 1 triggers DELAY.",
        "labels":{1:"CEO unaware of GenAI — forces DELAY gate",
                  2:"CEO aware but sceptical",
                  3:"CEO interested, no formal strategy",
                  4:"CEO has pilot mandate and budget approved",
                  5:"CEO-driven AI strategy with board commitment"}},
    "Competitive Diff.":{"help":"Degree to which GenAI creates sustainable competitive advantage",
        "labels":{1:"No differentiation in our market",2:"Minor marginal improvement",
                  3:"Some differentiation possible",4:"Clear competitive advantage",
                  5:"First-mover advantage — clients will pay premium"}},
    "Productivity Gain":{"help":"Estimated time saved per person per day from GenAI automation",
        "labels":{1:"Tasks not amenable to GenAI (<30 min/day)",
                  2:"30 min–1 hr/day saved per person",
                  3:"1–2 hours/day saved",4:"2–4 hours/day saved",
                  5:">4 hours/day saved — transformative"}},
    "Client/Market Demand":{"help":"Strength of external pressure from clients or competitors",
        "labels":{1:"No client or market pressure",2:"Occasional client enquiry",
                  3:"Some clients asking about AI usage",
                  4:"Clients expect AI-enabled deliverables",
                  5:"Clients requiring GenAI or will switch provider"}},
    "Regulatory Risk":{"help":"Regulatory liability and compliance exposure. HIGH score = HIGH risk.",
        "labels":{1:"No regulatory constraint (e.g. internal coding tools)",
                  2:"Minor data handling considerations",
                  3:"Moderate data privacy requirements (DPDP Act)",
                  4:"Significant compliance risk (financial advice, PII-heavy)",
                  5:"Extreme regulation + liability (legal submissions)"}},
    "Vendor Lock-in":{"help":"Risk of dependency on a specific GenAI vendor. HIGH score = HIGH risk.",
        "labels":{1:"Open standards, easy switching",2:"Some integration dependency",
                  3:"Moderate switching cost — 3–6 months migration",
                  4:"High switching cost, deep API integration",
                  5:"Extreme lock-in — proprietary data trapped"}},
    "Workforce Resistance":{"help":"Probability of employee resistance to GenAI. HIGH score = HIGH risk.",
        "labels":{1:"Team excited — actively requesting AI tools",
                  2:"Mild scepticism, easily managed",
                  3:"Mixed — some resistance from senior staff",
                  4:"Strong resistance from majority of senior staff",
                  5:"Active resistance — professional body concerns"}},
}

# ── Recommendation engine ─────────────────────────────────────────────────────
def get_recommendation(scores):
    if scores.get("Leadership Literacy", 3) <= 1:
        return "DELAY", "G2: Leadership Gate — CEO must sponsor adoption first", 0.0, True
    if scores.get("Budget Availability", 3) <= 1:
        return "DELAY", "G4: Budget Gate — no discretionary AI budget available", 0.0, True
    if scores.get("Regulatory Risk", 1) >= 5 and scores.get("AI Talent", 3) <= 2:
        return "OUTSOURCE", "G3: Regulatory+Talent Gate — specialist vendor with data indemnification required", 0.0, True
    if scores.get("AI Talent", 3) <= 1:
        return "DELAY", "G1: Talent Gate — no internal AI capability to implement any strategy", 0.0, True
    data_gate = scores.get("Data Readiness", 3) <= 1
    cs = 0.0
    for var, wt in WEIGHTS.items():
        s = scores.get(var, 3)
        if var in RISK_VARS:
            s = 6 - s
        cs += s * wt
    if cs >= 3.5 and not data_gate:
        return "BUILD", f"Composite Score = {cs:.3f} ≥ 3.50", cs, False
    elif cs >= 3.5 and data_gate:
        return "BUY", f"CS={cs:.3f} ≥ 3.50 but G5 Data Gate fires — BUILD downgraded to BUY", cs, True
    elif cs >= 2.75:
        return "BUY", f"Composite Score = {cs:.3f}  (range 2.75 – 3.49)", cs, False
    elif cs >= 2.0:
        return "OUTSOURCE", f"Composite Score = {cs:.3f}  (range 2.00 – 2.74)", cs, False
    else:
        return "DELAY", f"Composite Score = {cs:.3f}  — insufficient readiness", cs, False

def get_meta_scores(scores):
    meta = {"Cost & Financial":0.0,"Org Readiness":0.0,"Strategic Value":0.0,"Impl. Risk":0.0}
    for var, wt in WEIGHTS.items():
        s = scores.get(var, 3)
        if var in RISK_VARS:
            s = 6 - s
        meta[META[var]] += s * wt
    return meta

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🏢 Firm Profile")
firm_name    = st.sidebar.text_input("Firm name", value="My SME Firm")
sector       = st.sidebar.selectbox("Sector", ["IT Services","Management Consulting","Legal Services / LPO"])
firm_size    = st.sidebar.selectbox("Headcount", ["10–25 staff","26–50 staff","51–100 staff","101–250 staff"])
firm_revenue = st.sidebar.selectbox("Annual turnover", ["<Rs 10 Cr","Rs 10–50 Cr","Rs 50–100 Cr","Rs 100–250 Cr"])

st.sidebar.markdown("---")
st.sidebar.markdown("## 📊 Score Your Firm (1–5)")
st.sidebar.caption("1 = Very Low / Unfavourable → 5 = Very High / Favourable  \n"
                   "⚠️ Risk variables: higher score = higher risk")

scores = {}
current_meta = None
for var, wt in WEIGHTS.items():
    m = META[var]
    if m != current_meta:
        meta_wt = sum(WEIGHTS[v] for v in WEIGHTS if META[v] == m)
        st.sidebar.markdown(f"**{m}** *(AHP weight: {meta_wt:.1%})*")
        current_meta = m
    is_risk = var in RISK_VARS
    anchor  = ANCHORS[var]
    label   = f"{'⚠️ ' if is_risk else ''}{var} ({wt:.1%})"
    val     = st.sidebar.slider(label, 1, 5, 3, help=anchor["help"])
    st.sidebar.caption(f"*{anchor['labels'][val]}*")
    scores[var] = val

# ── Compute outputs ───────────────────────────────────────────────────────────
strategy, basis, cs, gate = get_recommendation(scores)
meta_scores  = get_meta_scores(scores)
col_color    = STRATEGY_COLORS[strategy]
col_fill     = STRATEGY_RGBA_FILL[strategy]
icon         = STRATEGY_ICONS[strategy]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.rec-box{padding:20px;border-radius:12px;text-align:center;margin-bottom:8px}
.gate-box{background:#FEF3CD;border-left:4px solid #F39C12;padding:8px 14px;
          border-radius:6px;margin:6px 0;font-size:13px}
.explain-box{background:#F0F4FA;border-radius:10px;padding:16px 20px;margin:8px 0;font-size:13px;line-height:1.6}
.explain-box h4{margin:0 0 6px 0;font-size:14px;font-weight:600}
</style>
""", unsafe_allow_html=True)

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("🤖 GenAI Investment Decision Framework")
st.caption("From Hype to Value — Indian Knowledge-Based SMEs  |  MBA Final Project — Naveen Bakshi M24MSE003")
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# ROW 1 — HEADLINE OUTPUT
# ══════════════════════════════════════════════════════════════════════════════
c1, c2, c3, c4 = st.columns([2.2, 0.9, 0.9, 0.9])

with c1:
    st.markdown(f"""
    <div class="rec-box" style="background:{col_fill};border:2px solid {col_color}">
      <div style="font-size:11px;font-weight:700;text-transform:uppercase;
                  letter-spacing:1px;color:#555;margin-bottom:4px">
        Primary Recommendation for {firm_name}
      </div>
      <div style="font-size:44px">{icon}</div>
      <div style="font-size:34px;font-weight:900;color:{col_color};margin:4px 0">{strategy}</div>
      <div style="font-size:12px;color:#444;margin-top:6px">{basis}</div>
    </div>
    """, unsafe_allow_html=True)
    if gate:
        st.markdown(f'<div class="gate-box">⚡ <strong>Gating rule triggered</strong> — '
                    f'this override takes precedence over the composite score</div>',
                    unsafe_allow_html=True)

with c2:
    st.metric("Composite Score", f"{cs:.3f}" if cs > 0 else "GATED",
              help="Range 0–5. BUILD ≥ 3.50 | BUY ≥ 2.75 | OUTSOURCE ≥ 2.00 | DELAY < 2.00")
with c3:
    st.metric("Sector", sector)
with c4:
    max_r = sum(WEIGHTS[v] for v in WEIGHTS if META[v]=="Org Readiness") * 5
    r_pct = (meta_scores["Org Readiness"] / max_r) * 100
    st.metric("Readiness", f"{r_pct:.0f}%",
              help="Organisational readiness score as % of maximum possible")

# ── Visual explanation ① ──────────────────────────────────────────────────────
st.markdown("""
<div class="explain-box">
<h4>📌 How to read this output</h4>
The coloured box above is your <strong>primary recommendation</strong> — the GenAI investment strategy
the framework calculates as optimal for your firm's current profile.
The <strong>Composite Score</strong> (0–5) summarises all 13 AHP-weighted variable scores into one number.
If a <strong>gating rule</strong> fired (shown in orange), it overrides the composite score because
a critical condition — no budget, no talent, extreme regulation, or absent leadership — makes other
strategies unviable regardless of the overall score.
<em>Action: scroll down to see which variables are driving the recommendation and what to do next.</em>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# ROW 2 — CHARTS
# ══════════════════════════════════════════════════════════════════════════════
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Weighted Variable Contributions")

    chart_data = []
    for var in WEIGHTS:
        s   = scores[var]
        eff = (6 - s) if var in RISK_VARS else s
        chart_data.append({
            "Variable": var,
            "Effective Score": eff,
            "Weighted Contribution": round(eff * WEIGHTS[var], 4),
            "Meta": META[var],
        })
    df = pd.DataFrame(chart_data)

    fig_bar = go.Figure()
    for meta_name, color in META_COLORS.items():
        sub = df[df["Meta"] == meta_name]
        fig_bar.add_trace(go.Bar(
            x=sub["Variable"],
            y=sub["Weighted Contribution"],
            name=meta_name,
            marker_color=color,
            hovertemplate="<b>%{x}</b><br>Contribution: %{y:.4f}<extra></extra>",
        ))
    fig_bar.update_layout(
        barmode="group", height=340,
        xaxis_tickangle=-38,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=40, b=80, l=0, r=0),
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis_title="Weighted score contribution",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("""
    <div class="explain-box">
    <h4>📊 What this chart shows</h4>
    Each bar is one of your 13 decision variables, coloured by its meta-criterion category.
    Taller bars = stronger positive contribution to the composite score.
    <strong>Risk variables</strong> (Regulatory Risk, Vendor Lock-in, Workforce Resistance)
    are automatically inverted — a high risk score appears as a <em>short</em> bar,
    correctly pulling your composite score down.
    <br><br>
    <strong>What to look for:</strong> Your shortest bars identify the variables most limiting
    your composite score — these are your priority improvement areas before revisiting strategy.
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.subheader("🕸️ Strategy Radar — Meta-Criterion Scores")

    meta_keys   = list(meta_scores.keys())
    # Normalise to 0–5 scale for radar
    meta_vals   = [round(meta_scores[k], 3) for k in meta_keys]
    # Close the polygon
    theta       = meta_keys + [meta_keys[0]]
    r_firm      = meta_vals + [meta_vals[0]]

    fig_radar = go.Figure()

    # Firm polygon — use rgba() strings, NOT hex+alpha
    fig_radar.add_trace(go.Scatterpolar(
        r=r_firm,
        theta=theta,
        fill="toself",
        name=firm_name,
        line=dict(color=col_color, width=2),
        fillcolor=col_fill,          # ← rgba() string, fixes the error
        hovertemplate="%{theta}: %{r:.3f}<extra></extra>",
    ))

    # Threshold rings — scaled per meta-criterion axis
    meta_max = {mk: sum(WEIGHTS[v] for v in WEIGHTS if META[v]==mk)*5 for mk in meta_keys}
    for cs_threshold, t_label, t_color in [
        (3.5, "BUILD ≥ 3.50", "#27AE60"),
        (2.75,"BUY ≥ 2.75",   "#2980B9"),
        (2.0, "OUTSOURCE ≥ 2.00","#F39C12"),
    ]:
        # Scale each axis by proportion: threshold/5 * meta_max gives per-dimension target
        r_ring = [round(cs_threshold/5 * meta_max[mk], 3) for mk in meta_keys]
        r_ring += [r_ring[0]]
        fig_radar.add_trace(go.Scatterpolar(
            r=r_ring,
            theta=theta,
            mode="lines",
            name=t_label,
            line=dict(color=t_color, dash="dash", width=1),
            hoverinfo="skip",
        ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(meta_max.values())])),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, font=dict(size=11)),
        height=340,
        margin=dict(t=40, b=80, l=50, r=50),
        paper_bgcolor="white",
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("""
    <div class="explain-box">
    <h4>🕸️ What this chart shows</h4>
    The radar shows your firm's score on each of the <strong>4 meta-criteria</strong>
    (Cost, Readiness, Strategic Value, Risk) as a shaded polygon.
    The three dashed rings mark the score thresholds for each strategy:
    <strong style="color:#27AE60">green = BUILD</strong>,
    <strong style="color:#2980B9">blue = BUY</strong>,
    <strong style="color:#F39C12">amber = OUTSOURCE</strong>.
    Anything inside the amber ring falls in the DELAY zone.
    <br><br>
    <strong>What to look for:</strong> Which axis is pulling your polygon inward the most?
    That meta-criterion is your biggest constraint — improving scores on those variables
    will shift your recommendation to the next strategy tier.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# ROW 3 — STRATEGY MAP
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🗺️ Where Your Firm Sits on the Strategy Map")

strategies_info = {
    "BUILD":    {"range":"CS ≥ 3.50","desc":"Build in-house GenAI capability",
                 "when":"High readiness + budget + strategic value. No talent or data gate.",
                 "examples":"Custom LLM fine-tuning · proprietary AI product · internal AI team"},
    "BUY":      {"range":"2.75 ≤ CS < 3.50","desc":"Purchase third-party GenAI tools",
                 "when":"Good budget + clear use case. Talent gap limits build capability.",
                 "examples":"Microsoft Copilot · GitHub Copilot · Google Gemini Workspace"},
    "OUTSOURCE":{"range":"2.00 ≤ CS < 2.75","desc":"Engage an AI implementation vendor",
                 "when":"Limited readiness. Regulatory risk or talent gap blocks build/buy.",
                 "examples":"Specialist legal AI · AI consulting firm · managed AI service"},
    "DELAY":    {"range":"CS < 2.00","desc":"Postpone — build digital foundations first",
                 "when":"Insufficient budget, talent, or leadership. Gates triggered.",
                 "examples":"CRM setup · cloud migration · data structuring · AI literacy"},
}
cols = st.columns(4)
for i, (strat, info) in enumerate(strategies_info.items()):
    with cols[i]:
        is_active = strat == strategy
        border    = f"3px solid {STRATEGY_COLORS[strat]}" if is_active else "1px solid #ddd"
        bg        = STRATEGY_RGBA_FILL[strat] if is_active else "#fafafa"
        label     = "  ← YOUR FIRM" if is_active else ""
        st.markdown(f"""
        <div style="border:{border};background:{bg};border-radius:10px;
                    padding:14px;min-height:210px">
          <div style="font-size:26px">{STRATEGY_ICONS[strat]}</div>
          <div style="font-weight:800;font-size:15px;color:{STRATEGY_COLORS[strat]}">
            {strat}{label}
          </div>
          <div style="font-size:11px;color:#666;margin:3px 0">{info['range']}</div>
          <div style="font-size:12px;margin-top:6px;font-weight:600">{info['desc']}</div>
          <div style="font-size:11px;color:#555;margin-top:5px"><em>{info['when']}</em></div>
          <div style="font-size:10px;color:#888;margin-top:5px">{info['examples']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div class="explain-box" style="margin-top:14px">
<h4>🗺️ What this section shows</h4>
The four cards show all possible strategy outcomes.
Your firm's card is highlighted with a coloured border and labelled "← YOUR FIRM".
The score range under each strategy name is the composite score band that routes a firm there.
The description, trigger condition, and tool examples help you understand <em>why</em>
this strategy was recommended and <em>what it looks like in practice</em> for Indian knowledge-based SMEs.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# ROW 4 — COMPOSITE SCORE GAUGE
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🎯 Composite Score Breakdown")
c_gauge, c_breakdown = st.columns([1, 2])

with c_gauge:
    if cs > 0:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(cs, 3),
            title={"text": "Composite Score", "font": {"size": 14}},
            number={"font": {"size": 28, "color": col_color}},
            gauge={
                "axis": {"range": [0, 5], "tickwidth": 1},
                "bar":  {"color": col_color, "thickness": 0.3},
                "steps": [
                    {"range": [0,   2.0],  "color": "rgba(231,76,60,0.15)"},
                    {"range": [2.0, 2.75], "color": "rgba(243,156,18,0.15)"},
                    {"range": [2.75,3.5],  "color": "rgba(41,128,185,0.15)"},
                    {"range": [3.5, 5.0],  "color": "rgba(39,174,96,0.15)"},
                ],
                "threshold": {
                    "line":  {"color": col_color, "width": 3},
                    "thickness": 0.75,
                    "value": cs,
                },
            },
        ))
        fig_gauge.update_layout(
            height=260, margin=dict(t=40, b=10, l=20, r=20),
            paper_bgcolor="white",
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
    else:
        st.markdown(f"""
        <div style="background:{col_fill};border:2px solid {col_color};
                    border-radius:10px;padding:30px;text-align:center">
          <div style="font-size:32px">{icon}</div>
          <div style="font-size:20px;font-weight:800;color:{col_color}">GATED</div>
          <div style="font-size:12px;color:#555;margin-top:8px">{basis}</div>
        </div>
        """, unsafe_allow_html=True)

with c_breakdown:
    st.markdown("**Score by meta-criterion**")
    for meta_name, val in meta_scores.items():
        meta_wt  = sum(WEIGHTS[v] for v in WEIGHTS if META[v] == meta_name)
        meta_max_val = meta_wt * 5
        pct      = int((val / meta_max_val) * 100) if meta_max_val > 0 else 0
        color    = META_COLORS[meta_name]
        st.markdown(f"""
        <div style="margin-bottom:10px">
          <div style="display:flex;justify-content:space-between;
                      font-size:12px;margin-bottom:3px">
            <span style="font-weight:600">{meta_name}</span>
            <span style="color:{color};font-weight:700">{val:.3f} / {meta_max_val:.3f}
              &nbsp;({pct}%)</span>
          </div>
          <div style="background:#eee;border-radius:4px;height:10px">
            <div style="background:{color};width:{pct}%;height:10px;
                        border-radius:4px;transition:width 0.3s"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="explain-box" style="margin-top:10px">
    <h4>🎯 What this section shows</h4>
    The <strong>gauge</strong> plots your composite score on the 0–5 scale.
    The coloured zones show where each strategy begins and ends.
    The <strong>progress bars</strong> show how much of the maximum possible score
    your firm achieves within each meta-criterion.
    A bar below 50% in any dimension signals a weak area worth addressing
    before moving to the next strategy tier.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# ROW 5 — ACTION PRIORITIES
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🎯 Your Top 3 Action Priorities")

action_map = {
    "BUILD":[
        ("1. Hire or appoint an AI Lead",
         "Designate an internal GenAI champion with technical credibility. "
         "Give them a defined mandate, 90-day pilot scope, and dedicated budget. "
         "This person owns the roadmap from Build to production."),
        ("2. Identify 2–3 proprietary use cases",
         "Find tasks unique to your firm's data and domain where customised GenAI "
         "outperforms off-the-shelf tools — e.g. custom code review rules, "
         "firm-specific document templates, or proprietary knowledge bases. "
         "These are your Build targets."),
        ("3. Start with an open-source LLM foundation",
         "Use Llama or Mistral as the base model and fine-tune on your own data. "
         "This avoids vendor lock-in, keeps data in your jurisdiction, and builds "
         "internal capability that grows with the firm."),
    ],
    "BUY":[
        ("1. Run a 30-day pilot on one tool",
         "Pick the highest-ROI use case (coding assistance, proposal generation, "
         "or research synthesis) and pilot one commercial tool. "
         "Measure before-and-after: hours saved per deliverable. "
         "Microsoft Copilot, GitHub Copilot, and Google Gemini Workspace "
         "are the tools with the strongest Indian SME evidence base."),
        ("2. Evaluate data privacy terms before deploying",
         "Verify: does client data leave Indian jurisdiction? "
         "Is it used to train the vendor's model? What audit rights do you retain? "
         "For consulting and legal sectors, keep all client data offline — "
         "use GenAI only on internal, non-confidential content first."),
        ("3. Standardise on one tool for 6–12 months",
         "Resist the temptation to subscribe to multiple tools simultaneously. "
         "Tool fragmentation destroys productivity gains through context-switching "
         "and duplicated training effort. One tool, one use case, one measurable outcome first."),
    ],
    "OUTSOURCE":[
        ("1. Issue a focused RFP to specialist AI vendors",
         "Specify exactly: your primary use case, data sovereignty requirements, "
         "required indemnification clause (vendor accepts liability for AI errors "
         "in client-facing outputs), accuracy SLA, and data residency. "
         "For legal sector firms: Luminance, Kira Systems, and Thomson Reuters CoCounsel "
         "are documented as appropriate platforms with legal-specific provisions."),
        ("2. Negotiate data protection terms explicitly",
         "The vendor must accept contractual liability for AI-generated errors. "
         "Ensure all client data remains in Indian jurisdiction or the jurisdiction "
         "specified in your client's NDA. "
         "This is the most critical clause for legal and consulting SMEs."),
        ("3. Build an exit ramp into the contract",
         "Structure the vendor relationship as a knowledge-transfer engagement, "
         "not a perpetual outsourcing dependency. Include milestones for building "
         "internal capability over 12–18 months so you can transition "
         "to a BUY or BUILD strategy as your readiness improves."),
    ],
    "DELAY":[
        ("1. Launch a 6-month digital readiness programme",
         "Before GenAI: implement a CRM system, migrate to cloud storage, "
         "and begin structuring institutional knowledge into searchable digital formats. "
         "GenAI needs a digital foundation — firms that skip this step "
         "consistently fail to extract value from adoption."),
        ("2. Build leadership AI literacy now",
         "CEO and at least one senior manager should complete an AI-for-business "
         "leaders programme (ISB, IIM Executive Education, or Coursera). "
         "This unblocks the Leadership Gate — the hardest gate to override "
         "and the one that blocks all other strategies."),
        ("3. Define your use cases and shortlist vendors",
         "Even while delaying, document the 2–3 highest-ROI GenAI use cases "
         "specific to your firm's workflow. Research and shortlist vendors now. "
         "When your readiness criteria are met, you should be able to "
         "execute a pilot within 30 days — not start the evaluation from scratch."),
    ],
}

for title, detail in action_map.get(strategy, []):
    with st.expander(f"**{title}**", expanded=True):
        st.write(detail)

st.markdown("""
<div class="explain-box">
<h4>🎯 How to use these action priorities</h4>
These three actions are the highest-leverage next steps for your specific recommended strategy,
drawn from NASSCOM (2024), McKinsey (2024), PwC (2024), and Thomson Reuters (2024) best practices
for Indian SMEs.
Complete them in order — each one builds the foundation for the next.
After completing all three, re-score your firm in this dashboard:
your composite score should increase and you may qualify for the next strategy tier.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# ROW 6 — GATING RULES STATUS
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("🔐 Gating Rules Status")

gate_checks = [
    ("G1 — Talent Gate",
     scores["AI Talent"] <= 1,
     f"AI Talent = {scores['AI Talent']}",
     "Score = 1 forces DELAY. No internal AI capability means no strategy is implementable.",
     "Hire an AI lead or upskill one existing staff member to unblock."),
    ("G2 — Leadership Gate",
     scores["Leadership Literacy"] <= 1,
     f"Leadership = {scores['Leadership Literacy']}",
     "Score = 1 forces DELAY. Without CEO sponsorship, no budget or mandate exists.",
     "CEO must complete AI literacy programme and issue a formal pilot mandate."),
    ("G3 — Regulatory+Talent Gate",
     scores["Regulatory Risk"] >= 5 and scores["AI Talent"] <= 2,
     f"Reg Risk = {scores['Regulatory Risk']}, Talent = {scores['AI Talent']}",
     "Both triggered: extreme regulatory risk + low talent forces OUTSOURCE to specialist vendor.",
     "Engage a specialist legal AI vendor with data indemnification SLA."),
    ("G4 — Budget Gate",
     scores["Budget Availability"] <= 1,
     f"Budget = {scores['Budget Availability']}",
     "Score = 1 forces DELAY. No discretionary AI budget makes even Buy unsustainable.",
     "Apply for MSME Innovation Scheme grant or allocate budget in next planning cycle."),
    ("G5 — Data Gate",
     scores["Data Readiness"] <= 1,
     f"Data = {scores['Data Readiness']}",
     "Score = 1 downgrades BUILD → BUY. Build requires clean structured data for fine-tuning.",
     "Migrate to CRM/ERP and structure institutional knowledge before attempting Build."),
]

gcols = st.columns(5)
for i, (gname, triggered, score_txt, explanation, fix) in enumerate(gate_checks):
    with gcols[i]:
        bg    = "#FEEFEF" if triggered else "#E8F5EF"
        ic    = "⚡" if triggered else "✅"
        color = "#E74C3C" if triggered else "#27AE60"
        label = "TRIGGERED" if triggered else "CLEAR"
        st.markdown(f"""
        <div style="background:{bg};border-radius:8px;padding:10px;
                    text-align:center;min-height:120px">
          <div style="font-size:20px">{ic}</div>
          <div style="font-weight:700;font-size:11px;color:{color};margin:4px 0">{gname}</div>
          <div style="font-size:10px;color:#555">{score_txt}</div>
          <div style="font-size:10px;font-weight:700;color:{color};margin-top:4px">{label}</div>
        </div>
        """, unsafe_allow_html=True)
        if triggered:
            with st.expander("Why?", expanded=False):
                st.caption(explanation)
                st.caption(f"**Fix:** {fix}")

st.markdown("""
<div class="explain-box" style="margin-top:14px">
<h4>🔐 What the gating rules mean</h4>
Gating rules are absolute barriers — they override the composite score when a critical variable
makes a strategy impossible regardless of other scores.
<strong>Green = clear</strong> (no barrier), <strong>red = triggered</strong> (barrier active).
If any gate is triggered, expand it to see exactly why and what action unblocks it.
Fixing a gate is almost always more impactful than improving marginal variables —
a firm that unblocks its Talent Gate (G1) by hiring one AI-capable person
may jump from DELAY to BUY overnight.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# ROW 7 — "WHAT WOULD IT TAKE?" SENSITIVITY
# ══════════════════════════════════════════════════════════════════════════════
st.subheader("💡 What Would It Take to Move Up One Strategy Tier?")

next_strategy = {"DELAY":"OUTSOURCE","OUTSOURCE":"BUY","BUY":"BUILD","BUILD":"Already at the highest tier"}
next_s = next_strategy.get(strategy, "")
threshold_map = {"OUTSOURCE":2.0,"BUY":2.75,"BUILD":3.5}

if strategy != "BUILD" and cs > 0:
    target_cs  = threshold_map.get(next_s, 0)
    gap        = max(0, target_cs - cs)
    st.markdown(f"""
    <div style="background:#F0F4FA;border-radius:10px;padding:16px 20px;font-size:13px">
      <strong>Current strategy:</strong> {strategy} (CS = {cs:.3f}) &nbsp;→&nbsp;
      <strong>Next tier:</strong> {next_s} (requires CS ≥ {target_cs:.2f})
      &nbsp;|&nbsp; <strong>Gap to close:</strong> {gap:.3f} composite score points
      <br><br>
      The fastest way to close this gap is to improve the variables with the
      <strong>highest AHP weights</strong> that currently score below 4.
      Look at Budget Availability ({scores['Budget Availability']}/5, weight 16.9%)
      and AI Talent ({scores['AI Talent']}/5, weight 9.6%) first —
      a +1 improvement on either of these variables adds approximately
      {0.1692:.3f} or {0.0961:.3f} to your composite score respectively.
    </div>
    """, unsafe_allow_html=True)
elif strategy == "BUILD":
    st.success("✅ Your firm is already at the highest strategy tier (BUILD). "
               "Focus on execution quality and transition from Buy tools to proprietary capability.")
else:
    st.info("Composite score is gated — fix the triggered gate(s) above first "
            "before optimising the composite score.")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="font-size:11px;color:#888;line-height:1.6">
<strong>Framework basis:</strong>
AHP weights derived from McKinsey (2023/24), NASSCOM (2024), Deloitte India (2024),
PwC (2024), Thomson Reuters (2024/25). All Consistency Ratios &lt; 0.01 (Saaty, 1980 threshold = 0.10).
TOE Framework: Tornatzky &amp; Fleischer (1990). Real Options: Trigeorgis (1996).
Validated against 4 Indian SME case studies — 100% match rate.
<br>
<strong>MBA Final Project</strong> — Naveen Bakshi M24MSE003 | June 2026
</div>
""", unsafe_allow_html=True)
