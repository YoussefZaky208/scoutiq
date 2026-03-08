
import streamlit as st
import pandas as pd
import extra_streamlit_components as stx
import numpy as np
import joblib
import sqlite3
import hashlib
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="ScoutVision", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600;700&display=swap');
:root{color-scheme:dark only!important;}
html,body,[class*="css"],[data-testid="stAppViewContainer"],[data-testid="stApp"],.main,.stApp,
[data-testid="stHeader"],section[data-testid="stSidebar"]{background-color:#080c08!important;color:#e2efe2!important;font-family:'DM Sans',sans-serif!important;}
@media(prefers-color-scheme:light){html,body,[class*="css"]{background-color:#080c08!important;color:#e2efe2!important;}}
@media(prefers-color-scheme:dark){html,body,[class*="css"]{background-color:#080c08!important;color:#e2efe2!important;}}
#MainMenu,footer{visibility:hidden;} header{visibility:visible!important;}
.block-container{padding:2rem 2.5rem!important;max-width:1400px!important;}
[data-testid="stSidebar"]{background:#050905!important;border-right:1px solid #1a2e1a!important;} [data-testid="collapsedControl"]{display:block!important;visibility:visible!important;color:#00ff87!important;}
[data-testid="stSidebar"] *{color:#e2efe2!important;}
.stButton>button{background:linear-gradient(135deg,#00ff87,#00c853)!important;color:#040804!important;border:none!important;border-radius:10px!important;font-family:"DM Sans",sans-serif!important;font-weight:700!important;font-size:14px!important;padding:0.55rem 2rem!important;letter-spacing:1px!important;}
.stButton>button:hover{opacity:0.85!important;}
.stTextInput>div>div>input,.stNumberInput>div>div>input{background:#0a120a!important;border:1px solid #1f3a1f!important;border-radius:10px!important;color:#e2efe2!important;font-size:14px!important;}
.stTextInput>div>div>input:focus,.stNumberInput>div>div>input:focus{border-color:#00ff87!important;box-shadow:0 0 0 2px rgba(0,255,135,0.15)!important;}
.stSelectbox>div>div{background:#0a120a!important;border:1px solid #1f3a1f!important;border-radius:10px!important;color:#e2efe2!important;}
.card{background:#0d160d;border:1px solid #1a2e1a;border-radius:18px;padding:28px;margin-bottom:18px;position:relative;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.5);}
.card::before{content:"";position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#00ff87,transparent);}
.stat-card{background:#0d160d;border:1px solid #1a2e1a;border-radius:16px;padding:22px 16px;text-align:center;transition:border-color 0.2s;}
.stat-card:hover{border-color:#00ff87!important;}
.stat-num{font-family:"Bebas Neue",sans-serif;font-size:2.8rem;color:#00ff87;letter-spacing:2px;line-height:1;}
.stat-lbl{color:#4d7a4d;font-size:10px;text-transform:uppercase;letter-spacing:2px;margin-top:6px;}
.rng{background:#0a120a;border:1px solid #1a2e1a;border-radius:6px;padding:5px 10px;font-size:11px;color:#4d7a4d;margin-bottom:3px;display:block;}
.p90-badge{display:inline-block;background:rgba(0,212,255,0.15);color:#00d4ff;font-size:9px;font-weight:700;padding:1px 7px;border-radius:20px;letter-spacing:1px;margin-left:6px;vertical-align:middle;}
.stTabs [data-baseweb="tab-list"]{background:#050905!important;border-bottom:1px solid #1a2e1a!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:#4d7a4d!important;padding:0.6rem 1.4rem!important;border-radius:8px 8px 0 0!important;}
.stTabs [aria-selected="true"]{background:rgba(0,255,135,0.08)!important;color:#00ff87!important;border-bottom:2px solid #00ff87!important;}
div[data-testid="stDataFrame"]{background:#080c08!important;border-radius:12px!important;overflow:hidden!important;}
div[data-testid="stDataFrame"] *{color:#c8d8c8!important;background:#080c08!important;}
div[data-testid="stDataFrame"] table{color:#c8d8c8!important;background:#080c08!important;}
div[data-testid="stDataFrame"] thead tr th{background:#0d160d!important;color:#4d7a4d!important;font-size:11px!important;text-transform:uppercase!important;letter-spacing:1px!important;border-bottom:1px solid #1a2e1a!important;}
div[data-testid="stDataFrame"] tbody tr td{background:#080c08!important;color:#c8d8c8!important;border-bottom:1px solid #0f1f0f!important;font-size:13px!important;}
div[data-testid="stDataFrame"] tbody tr:hover td{background:#0d160d!important;color:#00ff87!important;}
div[data-testid="stDataFrame"] [data-testid="glideDataEditor"]{background:#080c08!important;}
div[data-testid="stDataFrame"] canvas{filter:invert(0)!important;}
.dvn-scroller{background:#080c08!important;}
::-webkit-scrollbar{width:6px;height:6px;}
::-webkit-scrollbar-track{background:#080c08;}
::-webkit-scrollbar-thumb{background:#1a2e1a;border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:#00ff87;}
div[data-testid="stRadio"] p{color:#ffffff!important;font-size:15px!important;}
div[data-testid="stRadio"] label p{color:#ffffff!important;}
div[data-testid="stRadio"] span{color:#ffffff!important;}
.stTextInput label p{color:#ffffff!important;}
.stTextInput>label{color:#ffffff!important;}

</style>
""", unsafe_allow_html=True)

PROJECT_PATH = "./"
DB_PATH = "./users.db"
TOP6 = ["Manchester City","Liverpool","Chelsea","Arsenal","Manchester Utd","Tottenham"]
SEASONS = ["All","2019-20","2020-21","2021-22","2022-23","2023-24"]
PL = dict(plot_bgcolor="#0d160d",paper_bgcolor="#080c08",font_color="#e2efe2",
          font_family="DM Sans",margin=dict(t=50,b=30,l=30,r=30))
META = {
    "Attackers":  {"r2":0.7981,"rmse":9.823, "mae":6.912,"seed":42,"gap":0.17,"n":297,"color":"#00ff87","icon":"⚽"},
    "Midfielders":{"r2":0.6708,"rmse":13.295,"mae":9.530,"seed":32,"gap":0.17,"n":400,"color":"#00d4ff","icon":"🎯"},
    "Defenders":  {"r2":0.7058,"rmse":9.595, "mae":6.643,"seed":40,"gap":0.10,"n":483,"color":"#ff6b35","icon":"🛡️"},
    "Goalkeepers":{"r2":0.7504,"rmse":7.684, "mae":5.590,"seed":29,"gap":0.10,"n":95, "color":"#c87dff","icon":"🧤"},
}
POS_COLORS = {k:v["color"] for k,v in META.items()}

def fmt(v): return f"€{v:.1f}M"

# ── AUTH ───────────────────────────────────────────────────────
def init_db():
    conn=sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL)""")
    conn.commit(); conn.close()

def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()

def register_user(u,e,p):
    try:
        conn=sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO users(username,email,password_hash)VALUES(?,?,?)",
                     (u.strip(),e.strip().lower(),hash_pw(p)))
        conn.commit(); conn.close(); return True,"Account created!"
    except sqlite3.IntegrityError: return False,"Username or email already exists."
    finally:
        try: conn.close()
        except: pass

def login_user(u,p):
    conn=sqlite3.connect(DB_PATH)
    row=conn.execute("SELECT username FROM users WHERE(username=? OR email=?)AND password_hash=?",
                     (u.strip(),u.strip().lower(),hash_pw(p))).fetchone()
    conn.close(); return row[0] if row else None

init_db()
for k,v in [("logged_in",False),("username",""),("auth_mode","login")]:
    if k not in st.session_state: st.session_state[k]=v

# Restore login from cookie
try:
    cookie_manager = stx.CookieManager()
    cookie_user = cookie_manager.get("scoutvision_user")
    if cookie_user and not st.session_state.logged_in:
        st.session_state.logged_in = True
        st.session_state.username = cookie_user
except: pass

def auth_page():
    _,col,_=st.columns([1,1.2,1])
    with col:
        st.markdown("<br><br>",unsafe_allow_html=True)
        st.markdown("""<div class="card" style="text-align:center;padding:44px 36px;color:#ffffff!important;">
          <div style="font-family:'Bebas Neue',sans-serif;font-size:54px;color:#00ff87;letter-spacing:6px;line-height:1;margin-bottom:10px;">ScoutVision</div>
          <div style="color:#4d7a4d;font-size:10px;text-transform:uppercase;letter-spacing:2.5px;margin-bottom:32px;">Turning performance data into transfer market intelligence</div>
        """,unsafe_allow_html=True)
        st.markdown("<style>div[data-testid='stRadio'] label{color:#ffffff!important;font-size:15px!important;}</style>",unsafe_allow_html=True)
        mode=st.radio("",["Sign In","Create Account"],horizontal=True,
                      index=0 if st.session_state.auth_mode=="login" else 1,
                      label_visibility="collapsed")
        if mode=="Sign In":
            st.session_state.auth_mode="login"
            st.markdown("<p style='color:#ffffff;font-size:14px;margin-bottom:4px;'>Username or Email</p>",unsafe_allow_html=True)
            u=st.text_input("",key="li_u",placeholder="Enter username or email",label_visibility="collapsed")
            st.markdown("<p style='color:#ffffff;font-size:14px;margin-bottom:4px;'>Password</p>",unsafe_allow_html=True)
            p=st.text_input("",type="password",key="li_p",placeholder="Enter password",label_visibility="collapsed")
            st.markdown("<br>",unsafe_allow_html=True)
            if st.button("SIGN IN →",use_container_width=True):
                r=login_user(u,p)
                if r:
                    st.session_state.logged_in=True
                    st.session_state.username=r
                    try: cookie_manager.set("scoutvision_user", r, max_age=86400)
                    except: pass
                    st.rerun()
                else: st.error("Invalid credentials.")
        else:
            st.session_state.auth_mode="register"
            st.markdown("<p style='color:#ffffff;font-size:14px;margin-bottom:4px;'>Username</p>",unsafe_allow_html=True)
            u=st.text_input("",key="rg_u",label_visibility="collapsed")
            st.markdown("<p style='color:#ffffff;font-size:14px;margin-bottom:4px;'>Email</p>",unsafe_allow_html=True)
            e=st.text_input("",key="rg_e",label_visibility="collapsed")
            st.markdown("<p style='color:#ffffff;font-size:14px;margin-bottom:4px;'>Password</p>",unsafe_allow_html=True)
            p=st.text_input("",type="password",key="rg_p",label_visibility="collapsed")
            st.markdown("<p style='color:#ffffff;font-size:14px;margin-bottom:4px;'>Confirm Password</p>",unsafe_allow_html=True)
            c=st.text_input("",type="password",key="rg_c",label_visibility="collapsed")
            st.markdown("<br>",unsafe_allow_html=True)
            if st.button("CREATE ACCOUNT →",use_container_width=True):
                if not u or not e or not p: st.error("All fields required.")
                elif len(p)<6: st.error("Password must be 6+ characters.")
                elif p!=c: st.error("Passwords do not match.")
                else:
                    ok,msg=register_user(u,e,p)
                    if ok: st.success(msg+" Please sign in."); st.session_state.auth_mode="login"; st.rerun()
                    else: st.error(msg)
        st.markdown("</div>",unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────
@st.cache_data
def load_all_data():
    preds,full={},{}
    for pos in ["attackers","midfielders","defenders","goalkeepers"]:
        df=pd.read_csv(PROJECT_PATH+f"{pos}_predictions.csv")
        df["position"]=pos.capitalize()
        # Add season_label if missing
        if "season_label" not in df.columns:
            try:
                pt=pd.read_csv(PROJECT_PATH+f"{pos.upper()}_PRETRAIN.csv")
                sl_map=pt.groupby("player")["season_label"].last().to_dict()
                df["season_label"]=df["player"].map(sl_map).fillna("")
            except: df["season_label"]=""
        preds[pos]=df
    for pos in ["attackers","midfielders","defenders","goalkeepers"]:
        df=pd.read_csv(PROJECT_PATH+f"{pos.upper()}_PRETRAIN.csv")
        df["position"]=pos.capitalize()
        if "market_value_in_eur" not in df.columns: df["market_value_in_eur"]=0
        if "predicted_value" not in df.columns: df["predicted_value"]=0
        full[pos]=df
    return preds,full

@st.cache_resource
def load_models():
    out={}
    for pos in ["attackers","midfielders","defenders","goalkeepers"]:
        out[pos]={
            "model":    joblib.load(PROJECT_PATH+f"{pos}_model.pkl"),
            "imputer":  joblib.load(PROJECT_PATH+f"{pos}_imputer.pkl"),
            "selector": joblib.load(PROJECT_PATH+f"{pos}_selector.pkl"),
            "features": joblib.load(PROJECT_PATH+f"{pos}_features.pkl"),
            "squad_map":joblib.load(PROJECT_PATH+f"{pos}_squad_map.pkl"),
            "nation_map":joblib.load(PROJECT_PATH+f"{pos}_nation_map.pkl"),
        }
    return out

def n(df,col,default=0):
    if col in df.columns:
        return pd.to_numeric(df[col].astype(str).str.replace("%","",regex=False),errors="coerce").fillna(default)
    return pd.Series(default,index=df.index,dtype=float)

def fe(df,pos,squad_map,nation_map):
    d=df.copy()
    meta={"player","squad","nation","season","season_label","pos","pos_primary","position"}
    for c in d.columns:
        if c not in meta:
            d[c]=pd.to_numeric(d[c].astype(str).str.replace("%","",regex=False),errors="coerce")
    age=n(d,"age",25); mins=n(d,"Minutes_total",0)
    mp=n(d,"Matches Played",1).replace(0,1); m90=mins/90+1e-5
    d["age_squared"]=age**2; d["min_per_match"]=mins/mp
    d["total_minutes"]=mins; d["age_x_minutes"]=age*mins
    d["top6_flag"]=d["squad"].isin(TOP6).astype(float)
    gm=np.mean(list(squad_map.values()))
    d["squad_target_enc"]=d["squad"].map(squad_map).fillna(gm)
    d["nation_encoded"]=d["nation"].map(nation_map).fillna(-1) if "nation" in d.columns else -1.0
    if "season" in d.columns:
        d["season_start_year"]=d["season"].astype(str).str[:4].apply(lambda x:float(x) if x.isdigit() else 2022.0)
    else:
        d["season_start_year"]=2022.0

    if pos=="attackers":
        peak=26; d["age_from_peak"]=(age-peak).abs(); d["prime_age"]=((age>=23)&(age<=28)).astype(float); afp=d["age_from_peak"]
        goals=n(d,"Goals"); assts=n(d,"Assists"); xg=n(d,"Expected Goals"); npg=n(d,"Non Penalty Goals")
        shots=n(d,"Total Shots"); pp=n(d,"Progressive Passes"); pc=n(d,"Progressive Carries")
        kp=n(d,"Key passes"); pia=n(d,"Passes into penalty area"); pl=n(d,"Possessions lost")
        err=n(d,"Errors made"); sca=n(d,"Shot creating actions p 90"); gca=n(d,"Goal creating actions p 90")
        sot=n(d,"% Shots on target"); pks=n(d,"Penalty Kicks Made"); expnpg=n(d,"Exp NPG")
        third=n(d,"1/3"); gps=n(d,"Goals per shot"); gpst=n(d,"Goals per shot on target")
        sp90=n(d,"Shots p 90"); gp90=n(d,"Goals p 90"); ap90=n(d,"Assists p 90")
        gc=goals+assts; gcp=gc/m90
        d["Penalty Kicks Made"]=pks; d["Exp NPG"]=expnpg; d["1/3"]=third
        d["Goals per shot"]=gps; d["Goals per shot on target"]=gpst
        d["Shots p 90"]=sp90; d["Goals p 90"]=gp90; d["Assists p 90"]=ap90
        d["Shot creating actions p 90"]=sca; d["Goal creating actions p 90"]=gca
        d["% Shots on target"]=sot; d["Goals & Assists"]=gc
        d["goals_per90"]=goals/m90; d["assists_per90"]=assts/m90; d["shots_per90"]=shots/m90
        d["xg_per90"]=xg/m90; d["npg_per90"]=npg/m90; d["sca_per90"]=sca/m90; d["gca_per90"]=gca/m90
        d["prog_carries_per90"]=pc/m90; d["prog_passes_per90"]=pp/m90; d["key_passes_per90"]=kp/m90
        d["pen_area_per90"]=pia/m90; d["conversion_rate"]=goals/(shots+1e-5)
        d["shot_on_tgt_rate"]=sot/100; d["xg_diff"]=goals-xg; d["npxg_diff"]=npg-expnpg
        d["goal_contributions"]=gc; d["gc_per90"]=gcp; d["prog_actions"]=pp+pc
        d["prog_actions_per90"]=(pp+pc)/m90; d["age_x_gc_per90"]=age*gcp
        d["age_x_xg_per90"]=age*(xg/m90); d["age_x_prog_per90"]=age*(d["prog_actions"]/m90)
        d["goals_x_sca"]=(goals/m90)*sca; d["gc_x_prog"]=gcp*(d["prog_actions"]/m90)
        d["xg_x_conversion"]=(xg/m90)*d["conversion_rate"]; d["season_x_gc"]=d["season_start_year"]*gcp
        d["prime_x_gc"]=d["prime_age"]*gcp; d["xg_x_prog"]=(xg/m90)*(d["prog_actions"]/m90)
        d["squad_x_age"]=d["squad_target_enc"]*age; d["gc_x_season"]=gcp*d["season_start_year"]
        d["xg_x_age_peak"]=(xg/m90)*(1/(afp+1)); d["gc_x_age_peak"]=gcp*(1/(afp+1))
        d["goals_x_age_peak"]=(goals/m90)*(1/(afp+1)); d["sca_x_age_peak"]=sca*(1/(afp+1))
        d["top6_x_age_peak"]=d["top6_flag"]*(1/(afp+1)); d["top6_x_gc"]=d["top6_flag"]*gcp

    elif pos=="midfielders":
        peak=26; d["age_from_peak"]=(age-peak).abs(); d["prime_age"]=((age>=23)&(age<=28)).astype(float); afp=d["age_from_peak"]
        goals=n(d,"Goals"); assts=n(d,"Assists"); xg=n(d,"Expected Goals"); npg=n(d,"Non Penalty Goals")
        expnpg=n(d,"Exp NPG"); pp=n(d,"Progressive Passes"); pc=n(d,"Progressive Carries")
        kp=n(d,"Key passes"); pia=n(d,"Passes into penalty area"); sca=n(d,"Shot creating actions p 90")
        gca=n(d,"Goal creating actions p 90"); ta=n(d,"Tackles attempted"); tw=n(d,"Tackles Won")
        intp=n(d,"Interceptions"); clr=n(d,"Clearances"); sb=n(d,"Shots blocked")
        pb=n(d,"Passes blocked"); pdt=n(d,"% Dribbles tackled"); pad=n(d,"% Aerial Duels won")
        pl=n(d,"Possessions lost"); err=n(d,"Errors made"); third=n(d,"1/3")
        gc=goals+assts; gcp=gc/m90
        d["Exp NPG"]=expnpg; d["1/3"]=third; d["Shot creating actions p 90"]=sca
        d["Goal creating actions p 90"]=gca; d["% Dribbles tackled"]=pdt
        d["% Aerial Duels won"]=pad; d["Goals & Assists"]=gc
        d["goals_per90"]=goals/m90; d["assists_per90"]=assts/m90; d["xg_per90"]=xg/m90
        d["npg_per90"]=npg/m90; d["sca_per90"]=sca/m90; d["gca_per90"]=gca/m90
        d["key_passes_per90"]=kp/m90; d["pen_area_per90"]=pia/m90
        d["prog_carries_per90"]=pc/m90; d["prog_passes_per90"]=pp/m90; d["third_per90"]=third/m90
        d["tackles_att_per90"]=ta/m90; d["tackles_won_per90"]=tw/m90
        d["interceptions_per90"]=intp/m90; d["clearances_per90"]=clr/m90
        d["shots_blocked_per90"]=sb/m90; d["passes_blocked_per90"]=pb/m90
        d["tackle_success_rate"]=tw/(ta+1e-5); d["pct_dribbles_tackled"]=pdt/100
        d["aerial_won_pct"]=pad/100; d["possessions_lost_per90"]=pl/m90; d["errors_per90"]=err/m90
        d["goal_contributions"]=gc; d["gc_per90"]=gcp; d["xg_diff"]=goals-xg
        d["prog_actions"]=pp+pc; d["prog_actions_per90"]=(pp+pc)/m90
        d["box_to_box"]=gcp+tw/m90+intp/m90
        d["top6_x_age_peak"]=d["top6_flag"]*(1/(afp+1)); d["top6_x_gc"]=d["top6_flag"]*gcp
        d["age_x_gc_per90"]=age*gcp; d["age_x_xg_per90"]=age*(xg/m90)
        d["age_x_prog_per90"]=age*(d["prog_actions"]/m90); d["age_x_def"]=age*((tw+intp+clr+sb)/m90)
        d["gc_x_prog"]=gcp*(d["prog_actions"]/m90); d["sca_x_age_peak"]=sca*(1/(afp+1))
        d["gc_x_age_peak"]=gcp*(1/(afp+1)); d["prog_x_age_peak"]=(d["prog_actions"]/m90)*(1/(afp+1))
        d["def_x_age_peak"]=((tw+intp+clr+sb)/m90)*(1/(afp+1))
        d["box_to_box_x_age_peak"]=d["box_to_box"]*(1/(afp+1))
        d["season_x_gc"]=d["season_start_year"]*gcp; d["season_x_prog"]=d["season_start_year"]*(d["prog_actions"]/m90)
        d["prime_x_gc"]=d["prime_age"]*gcp; d["prime_x_box"]=d["prime_age"]*d["box_to_box"]

    elif pos=="defenders":
        peak=27; d["age_from_peak"]=(age-peak).abs(); d["prime_age"]=((age>=24)&(age<=29)).astype(float); afp=d["age_from_peak"]
        ta=n(d,"Tackles attempted"); tw=n(d,"Tackles Won"); pdt=n(d,"% Dribbles tackled")
        pad=n(d,"% Aerial Duels won"); intp=n(d,"Interceptions"); clr=n(d,"Clearances")
        sb=n(d,"Shots blocked"); pb=n(d,"Passes blocked"); pc=n(d,"Progressive Carries")
        pp=n(d,"Progressive Passes"); third=n(d,"1/3"); pl=n(d,"Possessions lost")
        err=n(d,"Errors made"); goals=n(d,"Goals"); assts=n(d,"Assists")
        def_act=tw+intp+clr+sb
        d["Goals & Assists"]=goals+assts; d["% Dribbles tackled"]=pdt; d["% Aerial Duels won"]=pad
        d["tackles_attempted_per90"]=ta/m90; d["tackles_won_per90"]=tw/m90
        d["interceptions_per90"]=intp/m90; d["clearances_per90"]=clr/m90
        d["shots_blocked_per90"]=sb/m90; d["passes_blocked_per90"]=pb/m90
        d["prog_carries_per90"]=pc/m90; d["prog_passes_per90"]=pp/m90; d["third_per90"]=third/m90
        d["possessions_lost_per90"]=pl/m90; d["errors_per90"]=err/m90
        d["goals_per90"]=goals/m90; d["assists_per90"]=assts/m90; d["ga_per90"]=(goals+assts)/m90
        d["pct_dribbles_tackled"]=pdt/100; d["aerial_won_pct"]=pad/100
        d["tackle_success_rate"]=tw/(ta+1e-5); d["def_actions_per90"]=def_act/m90
        d["def_volume"]=def_act; d["prog_actions_per90"]=(pc+pp)/m90
        d["age_x_def_actions"]=age*(def_act/m90); d["age_x_prog"]=age*((pc+pp)/m90)
        d["def_x_age_peak"]=(def_act/m90)*(1/(afp+1)); d["prog_x_age_peak"]=((pc+pp)/m90)*(1/(afp+1))
        d["aerial_x_age_peak"]=(pad/100)*(1/(afp+1)); d["tackle_x_age_peak"]=(tw/m90)*(1/(afp+1))
        d["intercept_x_age_peak"]=(intp/m90)*(1/(afp+1)); d["prime_x_def"]=d["prime_age"]*(def_act/m90)
        d["prime_x_prog"]=d["prime_age"]*((pc+pp)/m90); d["top6_x_age_peak"]=d["top6_flag"]*(1/(afp+1))
        d["top6_x_def"]=d["top6_flag"]*(def_act/m90); d["top6_x_prog"]=d["top6_flag"]*((pc+pp)/m90)
        d["season_x_def"]=d["season_start_year"]*(def_act/m90); d["season_x_prog"]=d["season_start_year"]*((pc+pp)/m90)
        d["def_x_prog"]=(def_act/m90)*((pc+pp)/m90); d["clearance_x_aerial"]=(clr/m90)*(pad/100)
        d["tackle_x_intercept"]=(tw/m90)*(intp/m90)

    elif pos=="goalkeepers":
        peak=28; d["age_from_peak"]=(age-peak).abs(); d["prime_age"]=((age>=25)&(age<=32)).astype(float); afp=d["age_from_peak"]
        ga=n(d,"Goals Against"); gap90=n(d,"Goals against p 90"); sav=n(d,"Saves")
        svpct=n(d,"Saves %"); cs=n(d,"Clean Sheets"); cspct=n(d,"% Clean sheets")
        penpct=n(d,"% Penalty saves"); cross=n(d,"Crosses Stopped")
        d["Saves %"]=svpct; d["% Clean sheets"]=cspct; d["% Penalty saves"]=penpct
        d["saves_per90"]=sav/m90; d["goals_ag_per90"]=gap90; d["clean_sheets_per90"]=cs/m90
        d["crosses_stopped_per90"]=cross/m90; d["saves_pct"]=svpct/100; d["clean_sheet_pct"]=cspct/100
        d["penalty_save_pct"]=penpct/100; d["goals_prevented"]=d["saves_per90"]-gap90
        d["saves_pct_x_volume"]=(svpct/100)*d["saves_per90"]; d["age_x_saves"]=age*d["saves_per90"]
        d["age_x_clean"]=age*(cs/m90); d["saves_x_age_peak"]=d["saves_per90"]*(1/(afp+1))
        d["clean_x_age_peak"]=(cs/m90)*(1/(afp+1)); d["saves_pct_x_age_peak"]=(svpct/100)*(1/(afp+1))
        d["prime_x_saves"]=d["prime_age"]*d["saves_per90"]; d["prime_x_clean"]=d["prime_age"]*(cs/m90)
        d["top6_x_age_peak"]=d["top6_flag"]*(1/(afp+1)); d["top6_x_saves"]=d["top6_flag"]*d["saves_per90"]
        d["season_x_saves"]=d["season_start_year"]*d["saves_per90"]; d["season_x_clean"]=d["season_start_year"]*(cs/m90)
    return d

def predict_df(df_fe,pos,models):
    import sklearn
    from sklearn.impute import SimpleImputer
    m=models[pos]
    imp_cols=m["imputer"].feature_names_in_.tolist()
    X=pd.DataFrame(index=df_fe.index)
    for c in imp_cols:
        X[c]=pd.to_numeric(df_fe[c],errors="coerce").fillna(0) if c in df_fe.columns else 0.0
    X=X.fillna(0)
    try:
        # Refit a fresh imputer with same columns to avoid sklearn version mismatch
        fresh_imp=SimpleImputer(strategy="mean")
        fresh_imp.fit(X)
        X_imp=fresh_imp.transform(X)
        X_sel=m["selector"].transform(X_imp)
        return m["model"].predict(X_sel)
    except Exception as e:
        st.error(f"Predict error ({pos}): {e}"); return np.zeros(len(df_fe))

def run_predictions(full,models,pos_filter="All",season_filter="All"):
    results=[]
    for pos_key,df in full.items():
        pos_cap=pos_key.capitalize()
        if pos_filter!="All" and pos_cap!=pos_filter: continue
        df2=df.copy()
        if season_filter!="All": df2=df2[df2["season_label"]==season_filter]
        if df2.empty: continue
        m=models[pos_key]; df_fe=fe(df2,pos_key,m["squad_map"],m["nation_map"])
        df2=df2.copy(); df2["predicted_value"]=predict_df(df_fe,pos_key,models)
        df2["difference_eur"]=df2["market_value_in_eur"]-df2["predicted_value"]
        df2["pos_cap"]=pos_cap
        keep=[c for c in ["player","squad","age","season_label","market_value_in_eur","predicted_value","difference_eur","pos_cap"] if c in df2.columns]
        results.append(df2[keep])
    return pd.concat(results,ignore_index=True) if results else pd.DataFrame()

# ── SIDEBAR ───────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown("""<div style="padding-bottom:20px;border-bottom:1px solid #1a2e1a;margin-bottom:20px;">
          <div style="font-family:'Bebas Neue',sans-serif;font-size:34px;color:#00ff87;letter-spacing:3px;">ScoutVision</div>
          <div style="color:#3d603d;font-size:9px;text-transform:uppercase;letter-spacing:1.5px;line-height:1.6;">Turning performance data into<br>transfer market intelligence</div>
        </div>""",unsafe_allow_html=True)
        page=st.radio("",["🏠  Home","💎  Undervalued Players","📊  Model Performance",
                           "🔍  Player Lookup","🤖  Predict New Player"],label_visibility="collapsed")
        st.markdown("<br><br><br>",unsafe_allow_html=True)
        st.markdown(f"""<div style="border-top:1px solid #1a2e1a;padding-top:16px;">
          <div style="color:#4d7a4d;font-size:11px;text-transform:uppercase;letter-spacing:1px;">Logged in as</div>
          <div style="color:#00ff87;font-weight:600;margin-top:4px;">{st.session_state.username}</div>
        </div>""",unsafe_allow_html=True)
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("Logout",use_container_width=True):
            st.session_state.logged_in=False
            st.session_state.username=""
            try: cookie_manager.delete("scoutvision_user")
            except: pass
            st.rerun()
    return page

# ══════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════
def page_home(preds,full):
    st.markdown('<script>parent.document.querySelector("section.main").scrollTo(0,0);</script>', unsafe_allow_html=True)
    scroll_top()
    all_pred=pd.concat(preds.values(),ignore_index=True)
    all_full=pd.concat(full.values(),ignore_index=True)

    # Hero
    st.markdown("""<div class="card">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:3.8rem;line-height:1.05;margin-bottom:10px;">
        Transfer Market<br><span style="color:#00ff87;">Intelligence</span>
      </div>
      <div style="color:#4d7a4d;font-size:14px;max-width:600px;">
        An AI-powered framework for detecting undervalued Premier League talent using machine learning and performance analytics.
      </div>
    </div>""",unsafe_allow_html=True)

    # Stats row
    c1,c2,c3,c4,c5=st.columns(5)
    for col,(num,lbl) in zip([c1,c2,c3,c4,c5],[
        (len(all_full),"Total Records"),
        (all_full["player"].nunique(),"Unique Players"),
        (all_full["season_label"].nunique(),"Seasons Covered"),
        (len(all_pred[all_pred["difference_eur"]<-2e6]),"Undervalued Found"),
        (f"{np.mean([v['r2'] for v in META.values()]):.3f}","Avg Model R²"),
    ]):
        with col:
            st.markdown(f"""<div class="stat-card">
              <div class="stat-num">{num}</div><div class="stat-lbl">{lbl}</div>
            </div>""",unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    # Model overview cards
    st.markdown("<div style='font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#4d7a4d;margin-bottom:14px;'>📋 Model Overview</div>",unsafe_allow_html=True)
    cols=st.columns(4)
    for i,(pos,m) in enumerate(META.items()):
        with cols[i]:
            bar_w=int(m["r2"]*100)
            st.markdown(f"""<div class="card" style="border-top:3px solid {m['color']};">
              <div style="font-size:26px;margin-bottom:8px;">{m['icon']}</div>
              <div style="font-family:'Bebas Neue',sans-serif;font-size:20px;letter-spacing:1px;color:#e2efe2;">{pos}</div>
              <div style="color:{m['color']};font-family:'Bebas Neue',sans-serif;font-size:44px;margin:4px 0;line-height:1;">{m['r2']:.4f}</div>
              <div style="color:#4d7a4d;font-size:10px;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px;">Test R²</div>
              <div style="background:#152015;border-radius:4px;height:4px;margin-bottom:12px;">
                <div style="width:{bar_w}%;height:100%;background:{m['color']};border-radius:4px;"></div>
              </div>
              <div style="display:flex;justify-content:space-between;font-size:11px;color:#4d7a4d;">
                <span>RMSE <b style="color:#e2efe2;">€{m['rmse']:.1f}M</b></span>
                <span>MAE <b style="color:#e2efe2;">€{m['mae']:.1f}M</b></span>
                <span>Records <b style="color:#e2efe2;">{m['n']}</b></span>
              </div>
            </div>""",unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    # Top picks — uses same preds CSVs as Undervalued tab (values now match)
    st.markdown("<div style='font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#4d7a4d;margin-bottom:14px;'>🏆 Top Undervalued Picks</div>",unsafe_allow_html=True)
    top=all_pred[all_pred["difference_eur"]<-2e6].nsmallest(8,"difference_eur")
    for _,r in top.iterrows():
        color=POS_COLORS.get(r["position"],"#00ff87")
        gap=abs(r["difference_eur"])/1e6
        pct=gap/(r["market_value_in_eur"]/1e6+1e-5)*100
        sl=r.get("season_label","")
        st.markdown(f"""<div style="background:#0d160d;border:1px solid #1a2e1a;border-left:4px solid {color};
             border-radius:12px;padding:14px 20px;margin-bottom:8px;">
          <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
            <div style="display:flex;align-items:center;gap:10px;">
              <span style="font-weight:700;font-size:15px;color:#e2efe2;">{r["player"]}</span>
              <span style="color:#4d7a4d;font-size:12px;">{r["squad"]} · Age {int(r["age"])}</span>
              <span style="background:{color}22;color:{color};font-size:9px;font-weight:700;padding:2px 8px;border-radius:20px;">{r["position"][:3].upper()}</span>
              <span style="background:#1a2e1a;color:#4d7a4d;font-size:9px;padding:2px 8px;border-radius:20px;">{sl}</span>
            </div>
            <div style="display:flex;align-items:center;gap:12px;">
              <span style="color:#4d7a4d;font-size:12px;">Market <b style="color:#e2efe2;">{fmt(r["market_value_in_eur"]/1e6)}</b></span>
              <span style="color:#2a4a2a;">→</span>
              <span style="color:#4d7a4d;font-size:12px;">Model <b style="color:{color};">{fmt(r["predicted_value"]/1e6)}</b></span>
              <span style="background:rgba(255,80,80,0.12);color:#ff5050;font-weight:700;padding:4px 12px;border-radius:8px;font-size:13px;">
                -{fmt(gap)} <span style="font-size:10px;opacity:0.7;">({pct:.0f}%)</span>
              </span>
            </div>
          </div>
        </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# UNDERVALUED  — FIX: uses pre-saved preds CSVs (same as Home tab)
#                      so values always match. No model re-runs = fast.
# ══════════════════════════════════════════════════════════════
def page_undervalued(preds,full,models):
    st.markdown('<script>parent.document.querySelector("section.main").scrollTo(0,0);</script>', unsafe_allow_html=True)
    scroll_top()
    st.markdown("## 💎 Undervalued Players")
    st.markdown('''<div style="color:#4d7a4d;margin-bottom:20px;font-size:13px;">Players where the model predicts a significantly higher value than the transfer market assigned. The <b style="color:#00ff87;">gap bar</b> shows how undervalued they are as a percentage — a full bar means the model thinks they are worth significantly more than their listed price.</div>''',unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns(4)
    with c1: pos_f=st.selectbox("Position",["All","Attackers","Midfielders","Defenders","Goalkeepers"])
    with c2: sea_f=st.selectbox("Season",SEASONS)
    with c3: thresh=st.selectbox("Min Gap",["€2M+","€5M+","€10M+","€15M+","€20M+"])
    with c4: sort_by=st.selectbox("Sort By",["Biggest Gap","Highest Predicted","Youngest","% Undervalued"])

    tv={"€2M+":2e6,"€5M+":5e6,"€10M+":10e6,"€15M+":15e6,"€20M+":20e6}[thresh]

    # ── Use pre-saved predictions (same source as Home tab) ──
    all_pred=pd.concat(preds.values(),ignore_index=True).copy()
    all_pred["pos_cap"]=all_pred["position"]

    # Apply filters
    res=all_pred.copy()
    if pos_f!="All": res=res[res["position"]==pos_f]
    if sea_f!="All": res=res[res["season_label"].astype(str)==str(sea_f)]
    if res.empty: st.warning("No data for selected filters."); return

    under=res[res["difference_eur"]<-tv].copy()
    under["gap_abs"]=under["difference_eur"].abs()
    under["pct_undervalued"]=under["gap_abs"]/(under["predicted_value"]+1e-5)*100

    if sort_by=="Biggest Gap": under=under.sort_values("gap_abs",ascending=False)
    elif sort_by=="Highest Predicted": under=under.sort_values("predicted_value",ascending=False)
    elif sort_by=="Youngest": under=under.sort_values("age")
    elif sort_by=="% Undervalued": under=under.sort_values("pct_undervalued",ascending=False)

    st.markdown(f"<div style='color:#4d7a4d;margin-bottom:16px;'><b style='color:#00ff87;font-size:18px;'>{len(under)}</b> undervalued players found</div>",unsafe_allow_html=True)

    if under.empty: st.warning("No undervalued players found for selected filters."); return

    max_gap=under["gap_abs"].max() if len(under)>0 else 1
    for _,r in under.iterrows():
        color=POS_COLORS.get(r["pos_cap"],"#00ff87")
        sl=str(r.get("season_label","")) if pd.notna(r.get("season_label","")) else ""
        pct=r["pct_undervalued"]
        bar_fill=min(int((r["gap_abs"]/max_gap)*100),100)
        gap_m=r["gap_abs"]/1e6
        mv=r["market_value_in_eur"]/1e6
        pv=r["predicted_value"]/1e6
        pos_short=r["pos_cap"][:3].upper()
        st.markdown(f"""<div style="background:#0d160d;border:1px solid #1a2e1a;border-left:4px solid {color};border-radius:14px;padding:16px 22px;margin-bottom:10px;">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
      <span style="font-weight:700;font-size:16px;color:#e2efe2;">{r["player"]}</span>
      <span style="color:#4d7a4d;font-size:12px;">{r["squad"]} · Age {int(r["age"])}</span>
      <span style="background:{color}22;color:{color};font-size:9px;font-weight:700;padding:2px 8px;border-radius:20px;">{pos_short}</span>
      <span style="background:#1a2e1a;color:#4d7a4d;font-size:9px;padding:2px 8px;border-radius:20px;">{sl}</span>
    </div>
    <div style="text-align:right;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:26px;color:#ff5050;line-height:1;">-{fmt(gap_m)}</div>
      <div style="color:#4d7a4d;font-size:10px;">{pct:.0f}% undervalued</div>
    </div>
  </div>
  <div style="margin-top:12px;display:flex;gap:30px;align-items:center;flex-wrap:wrap;">
    <div>
      <div style="color:#4d7a4d;font-size:9px;text-transform:uppercase;margin-bottom:2px;">Market Value</div>
      <div style="font-size:15px;font-weight:700;color:#e2efe2;">{fmt(mv)}</div>
    </div>
    <div style="color:#1a2e1a;font-size:18px;">→</div>
    <div>
      <div style="color:#4d7a4d;font-size:9px;text-transform:uppercase;margin-bottom:2px;">Model Predicted</div>
      <div style="font-size:15px;font-weight:700;color:{color};">{fmt(pv)}</div>
    </div>
    <div style="flex:1;min-width:100px;">
      <div style="background:#152015;border-radius:4px;height:5px;">
        <div style="width:{bar_fill}%;height:100%;background:{color};border-radius:4px;"></div>
      </div>
    </div>
  </div>
</div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# MODEL PERFORMANCE
# ══════════════════════════════════════════════════════════════
def page_perf(preds,full):
    st.markdown("## 📊 Model Performance")
    st.markdown("<div style='color:#4d7a4d;margin-bottom:24px;font-size:13px;'>Evaluation metrics for 4 position-specific XGBoost models — Premier League 2019–2024.</div>",unsafe_allow_html=True)

    positions=list(META.keys())
    colors=[META[p]["color"] for p in positions]
    r2v=[META[p]["r2"] for p in positions]
    rmse_v=[META[p]["rmse"] for p in positions]
    mae_v=[META[p]["mae"] for p in positions]
    gap_v=[META[p]["gap"] for p in positions]
    n_v=[META[p]["n"] for p in positions]

    # R² bar
    fig_r2=go.Figure()
    fig_r2.add_trace(go.Bar(x=positions,y=r2v,marker_color=colors,marker_line_width=0,
        text=[f"{v:.4f}" for v in r2v],textposition="outside",
        textfont=dict(size=14,family="Bebas Neue",color="#e2efe2"),
        hovertemplate="<b>%{x}</b><br>R² = %{y:.4f}<extra></extra>"))
    fig_r2.update_layout(**PL,height=340,
        title=dict(text="Test R² Score by Position",font=dict(size=15,color="#e2efe2")),
        xaxis=dict(showgrid=False,tickfont=dict(size=14,color="#e2efe2")),
        yaxis=dict(showgrid=True,gridcolor="#152015",range=[0,1.05],tickfont=dict(color="#e2efe2"),title="R²"))
    st.plotly_chart(fig_r2,use_container_width=True)

    # RMSE + MAE side by side
    c1,c2=st.columns(2)
    with c1:
        fig_rmse=go.Figure()
        fig_rmse.add_trace(go.Bar(x=positions,y=rmse_v,marker_color=colors,marker_line_width=0,
            text=[f"€{v:.1f}M" for v in rmse_v],textposition="outside",textfont=dict(size=13,color="#e2efe2"),
            hovertemplate="<b>%{x}</b><br>RMSE = €%{y:.2f}M<extra></extra>"))
        fig_rmse.update_layout(**PL,height=320,
            title=dict(text="RMSE — Root Mean Squared Error",font=dict(size=13,color="#e2efe2")),
            xaxis=dict(showgrid=False,tickfont=dict(size=13,color="#e2efe2")),
            yaxis=dict(showgrid=True,gridcolor="#152015",range=[0,max(rmse_v)*1.35],tickfont=dict(color="#e2efe2"),title="€M"))
        st.plotly_chart(fig_rmse,use_container_width=True)
    with c2:
        fig_mae=go.Figure()
        fig_mae.add_trace(go.Bar(x=positions,y=mae_v,marker_color=colors,marker_line_width=0,
            text=[f"€{v:.1f}M" for v in mae_v],textposition="outside",textfont=dict(size=13,color="#e2efe2"),
            hovertemplate="<b>%{x}</b><br>MAE = €%{y:.2f}M<extra></extra>"))
        fig_mae.update_layout(**PL,height=320,
            title=dict(text="MAE — Mean Absolute Error",font=dict(size=13,color="#e2efe2")),
            xaxis=dict(showgrid=False,tickfont=dict(size=13,color="#e2efe2")),
            yaxis=dict(showgrid=True,gridcolor="#152015",range=[0,max(mae_v)*1.35],tickfont=dict(color="#e2efe2"),title="€M"))
        st.plotly_chart(fig_mae,use_container_width=True)

    # Grouped RMSE vs MAE
    fig_cmp=go.Figure()
    fig_cmp.add_trace(go.Bar(name="RMSE",x=positions,y=rmse_v,marker_color="#00ff87",
        text=[f"€{v:.1f}M" for v in rmse_v],textposition="outside",textfont=dict(size=12,color="#e2efe2")))
    fig_cmp.add_trace(go.Bar(name="MAE",x=positions,y=mae_v,marker_color="#00d4ff",
        text=[f"€{v:.1f}M" for v in mae_v],textposition="outside",textfont=dict(size=12,color="#e2efe2")))
    fig_cmp.update_layout(**PL,height=340,barmode="group",
        title=dict(text="RMSE vs MAE — Prediction Error Comparison by Position",font=dict(size=13,color="#e2efe2")),
        xaxis=dict(showgrid=False,tickfont=dict(size=13,color="#e2efe2")),
        yaxis=dict(showgrid=True,gridcolor="#152015",title="€M",tickfont=dict(color="#e2efe2"),range=[0,max(rmse_v)*1.35]),
        legend=dict(bgcolor="#0d160d",bordercolor="#1a2e1a",borderwidth=1,font=dict(color="#e2efe2")))
    st.plotly_chart(fig_cmp,use_container_width=True)

    # Overfitting gap + dataset size
    c3,c4=st.columns(2)
    # Dataset distribution pie chart
    st.markdown("<div style='font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#4d7a4d;margin:20px 0 14px;'>📊 Dataset Distribution</div>",unsafe_allow_html=True)
    fig_pie=go.Figure(go.Pie(
        labels=positions, values=n_v,
        marker=dict(colors=colors, line=dict(color="#080c08", width=2)),
        textinfo="percent+value",
        textfont=dict(size=13, color="#e2efe2"),
        hole=0.4,
        hovertemplate="<b>%{label}</b><br>%{value} records<br>%{percent}<extra></extra>"))
    fig_pie.update_layout(**PL, height=400,
        title=dict(text="Training Records by Position", font=dict(size=13, color="#e2efe2")),
        legend=dict(bgcolor="#0d160d", bordercolor="#1a2e1a", borderwidth=1, font=dict(color="#e2efe2")),
        annotations=[dict(text="1,275<br>total", x=0.5, y=0.5, font=dict(size=14, color="#e2efe2"), showarrow=False)])
    st.plotly_chart(fig_pie, use_container_width=True)


    # Scatter actual vs predicted
    st.markdown("<div style='font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#4d7a4d;margin:20px 0 14px;'>🎯 Actual vs Predicted Value</div>",unsafe_allow_html=True)
    pos_sel=st.selectbox("Select Position",list(META.keys()),key="sc_pos")
    df_p=preds[pos_sel.lower()].copy().dropna(subset=["market_value_in_eur","predicted_value"])
    max_v=max(df_p["market_value_in_eur"].max(),df_p["predicted_value"].max())/1e6
    scatter_color=META[pos_sel]["color"]
    df_p["error"]=df_p["predicted_value"]-df_p["market_value_in_eur"]
    df_over=df_p[df_p["error"]>=0]
    df_under=df_p[df_p["error"]<0]
    player_col=df_p["player"].tolist() if "player" in df_p.columns else [""]*len(df_p)
    fig_s=go.Figure()
    # Perfect prediction line
    fig_s.add_trace(go.Scatter(x=[0,max_v],y=[0,max_v],mode="lines",
        line=dict(color="#2a4a2a",dash="dot",width=1.5),
        name="Perfect Prediction",showlegend=True))
    # Undervalued dots (model > market)
    fig_s.add_trace(go.Scatter(
        x=df_under["market_value_in_eur"]/1e6, y=df_under["predicted_value"]/1e6, mode="markers",
        name="Undervalued (Model > Market)",
        marker=dict(color="#00ff87", size=9, opacity=0.85, line=dict(color="#080c08", width=0.5)),
        text=df_under["player"].tolist() if "player" in df_under.columns else [],
        hovertemplate="<b>%{text}</b><br>Market: €%{x:.1f}M<br>Predicted: €%{y:.1f}M<extra></extra>"))
    # Overvalued dots (model < market)
    fig_s.add_trace(go.Scatter(
        x=df_over["market_value_in_eur"]/1e6, y=df_over["predicted_value"]/1e6, mode="markers",
        name="Overvalued (Market > Model)",
        marker=dict(color="#ff5050", size=9, opacity=0.85, line=dict(color="#080c08", width=0.5)),
        text=df_over["player"].tolist() if "player" in df_over.columns else [],
        hovertemplate="<b>%{text}</b><br>Market: €%{x:.1f}M<br>Predicted: €%{y:.1f}M<extra></extra>"))
    fig_s.update_layout(**PL,height=500,
        xaxis=dict(title="Actual Market Value (€M)",showgrid=True,gridcolor="#152015",tickfont=dict(color="#e2efe2")),
        yaxis=dict(title="Model Predicted Value (€M)",showgrid=True,gridcolor="#152015",tickfont=dict(color="#e2efe2")),
        legend=dict(bgcolor="#0d160d",bordercolor="#1a2e1a",borderwidth=1,font=dict(color="#e2efe2",size=11)),
        title=dict(text=f"{pos_sel} — Actual vs Predicted · 🟢 Undervalued · 🔴 Overvalued",font=dict(size=13,color="#e2efe2")))
    st.plotly_chart(fig_s,use_container_width=True)

    # Full metrics table
    st.markdown("<div style='font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:#4d7a4d;margin:20px 0 14px;'>📋 Full Results Summary</div>",unsafe_allow_html=True)
    rows=[{"Position":p,"Test R²":f"{m['r2']:.4f}","RMSE (€M)":f"{m['rmse']:.3f}",
           "MAE (€M)":f"{m['mae']:.3f}","Overfit Gap":f"{m['gap']:.2f}",
           "Seed":m["seed"],"Records":m["n"]} for p,m in META.items()]
    df_results=pd.DataFrame(rows)
    st.markdown(df_results.to_html(index=False,classes="",border=0).replace(
        "<table","<table style='width:100%;color:#c8d8c8;background:#080c08;border-collapse:collapse;font-size:13px;'").replace(
        "<th","<th style='background:#0d160d;color:#4d7a4d;padding:10px;text-align:left;border-bottom:1px solid #1a2e1a;text-transform:uppercase;font-size:11px;letter-spacing:1px;'").replace(
        "<td","<td style='padding:10px;border-bottom:1px solid #0f1f0f;'"),
    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PLAYER LOOKUP
# ══════════════════════════════════════════════════════════════
def page_lookup(full,models):
    st.markdown('<script>parent.document.querySelector("section.main").scrollTo(0,0);</script>', unsafe_allow_html=True)
    scroll_top()
    st.markdown('<script>window.scrollTo(0,0);</script>', unsafe_allow_html=True)
    st.markdown("## 🔍 Player Lookup")
    all_full=pd.concat(full.values(),ignore_index=True)
    all_squads=["All"]+sorted(all_full["squad"].dropna().unique().tolist())
    c1,c2,c3,c4=st.columns([2,1,1,1])
    with c1: search=st.text_input("Search player",placeholder="e.g. Salah, Bruno, De Bruyne...",key="lk_srch")
    with c2: pos_f=st.selectbox("Position",["All","Attackers","Midfielders","Defenders","Goalkeepers"],key="lk_pos")
    with c3: sea_f=st.selectbox("Season",SEASONS,key="lk_sea")
    with c4: squad_f=st.selectbox("Squad",all_squads,key="lk_sq")

    df_show=all_full.copy()
    if search: df_show=df_show[df_show["player"].str.contains(search,case=False,na=False)]
    if pos_f!="All": df_show=df_show[df_show["position"]==pos_f]
    if sea_f!="All": df_show=df_show[df_show["season_label"]==sea_f]
    if squad_f!="All": df_show=df_show[df_show["squad"]==squad_f]
    if df_show.empty: st.warning("No players found."); return

    results=[]
    for pos_key in ["attackers","midfielders","defenders","goalkeepers"]:
        pos_cap=pos_key.capitalize()
        sub=df_show[df_show["position"]==pos_cap].copy()
        if sub.empty: continue
        m=models[pos_key]; df_fe=fe(sub,pos_key,m["squad_map"],m["nation_map"])
        sub=sub.copy(); sub["predicted_value"]=predict_df(df_fe,pos_key,models)
        sub["difference_eur"]=sub["market_value_in_eur"]-sub["predicted_value"]
        results.append(sub)
    if not results: st.warning("No predictions."); return
    res=pd.concat(results,ignore_index=True)

    st.markdown(f"<div style='color:#4d7a4d;margin-bottom:16px;'><b style='color:#00ff87;font-size:18px;'>{len(res)}</b> players found</div>",unsafe_allow_html=True)

    if len(res)==1:
        r=res.iloc[0]; color=POS_COLORS.get(r["position"],"#00ff87")
        act=r["market_value_in_eur"]/1e6; pred=r["predicted_value"]/1e6; diff=r["difference_eur"]/1e6
        dc="#ff5050" if diff<0 else "#00ff87"; lbl="Undervalued ↑" if diff<0 else "Overvalued ↓"
        sl=r.get("season_label",""); pct=abs(diff)/(act+1e-5)*100
        st.markdown(f"""<div class="card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:20px;flex-wrap:wrap;gap:10px;">
            <div>
              <div style="font-family:'Bebas Neue',sans-serif;font-size:32px;letter-spacing:1px;">{r["player"]}</div>
              <div style="color:#4d7a4d;font-size:13px;">{r["squad"]} · Age {int(r["age"])} · {r["position"]} · {sl}</div>
            </div>
            <div style="background:{dc}22;color:{dc};padding:8px 18px;border-radius:10px;font-weight:700;font-size:14px;">{lbl}</div>
          </div>
          <div style="display:flex;gap:40px;flex-wrap:wrap;">
            <div><div style="color:#4d7a4d;font-size:10px;text-transform:uppercase;margin-bottom:4px;">Market Value</div>
                 <div style="font-family:'Bebas Neue',sans-serif;font-size:32px;">{fmt(act)}</div></div>
            <div style="color:#1a2e1a;font-size:28px;align-self:flex-end;padding-bottom:4px;">→</div>
            <div><div style="color:#4d7a4d;font-size:10px;text-transform:uppercase;margin-bottom:4px;">Model Predicted</div>
                 <div style="font-family:'Bebas Neue',sans-serif;font-size:32px;color:{color};">{fmt(pred)}</div></div>
            <div style="margin-left:auto;">
              <div style="color:#4d7a4d;font-size:10px;text-transform:uppercase;margin-bottom:4px;">Valuation Gap</div>
              <div style="font-family:'Bebas Neue',sans-serif;font-size:32px;color:{dc};">{"−" if diff<0 else "+"}€{abs(diff):.1f}M</div>
              <div style="color:#4d7a4d;font-size:11px;">{pct:.1f}% {"undervalued" if diff<0 else "overvalued"}</div>
            </div>
          </div>
        </div>""",unsafe_allow_html=True)
    else:
        disp=res[["player","squad","age","position","season_label","market_value_in_eur","predicted_value","difference_eur"]].copy()
        disp=disp.rename(columns={"player":"Player","squad":"Squad","age":"Age","position":"Position",
            "season_label":"Season","market_value_in_eur":"Actual (€M)","predicted_value":"Predicted (€M)","difference_eur":"Gap (€M)"})
        disp=disp.sort_values("Gap (€M)").reset_index(drop=True)
        disp["Actual (€M)"]=disp["Actual (€M)"].apply(lambda x:round(x/1e6,1))
        disp["Predicted (€M)"]=disp["Predicted (€M)"].apply(lambda x:round(x/1e6,1))
        disp["Gap (€M)"]=disp["Gap (€M)"].apply(lambda x:round(x/1e6,1))
        disp["Age"]=disp["Age"].astype(int)
        html=disp.to_html(index=False,classes="",border=0)
        html=html.replace("<table","<table style='width:100%;border-collapse:collapse;font-size:13px;font-family:DM Sans,sans-serif;'")
        html=html.replace("<th","<th style='background:#0d1f0d;color:#00ff87;padding:12px 16px;text-align:left;border-bottom:2px solid #00ff87;border-right:1px solid #1a2e1a;text-transform:uppercase;font-size:10px;letter-spacing:1.5px;'")
        html=html.replace("<tr>","<tr style='border-bottom:1px solid #1a2e1a;'>")
        html=html.replace("<td","<td style='padding:11px 16px;color:#e2efe2;border-right:1px solid #1a2e1a;background:#080c08;'")
        # Highlight negative gap in red, positive in green
        import re
        def color_gap(m):
            val=m.group(1)
            try:
                num=float(val)
                color="#ff5050" if num<0 else "#00ff87"
                return f"<td style='padding:11px 16px;color:{color};font-weight:700;border-right:1px solid #1a2e1a;background:#080c08;'>{val}</td>"
            except: return m.group(0)
        html=re.sub(r"<td style='padding:11px 16px;color:#e2efe2;border-right:1px solid #1a2e1a;background:#080c08;'>(-?[\d.]+)</td>(?=\s*</tr>)",color_gap,html)
        st.markdown(f"<div style='border:1px solid #1a2e1a;border-radius:12px;overflow:hidden;'>{html}</div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PREDICT NEW PLAYER
# ══════════════════════════════════════════════════════════════
def rng_label(label,mn,avg,mx,unit="",per90=False):
    badge='<span class="p90-badge">PER 90</span>' if per90 else ""
    st.markdown(f'<span class="rng"><b>{label}</b>{badge} &nbsp; Min: {mn}{unit} &nbsp;·&nbsp; Avg: {avg}{unit} &nbsp;·&nbsp; Max: {mx}{unit}</span>',unsafe_allow_html=True)

def page_predict(full,models):
    st.markdown("## 🤖 Predict New Player Market Value")
    st.markdown("""<div style="background:#0d160d;border:1px solid #1a2e1a;border-left:3px solid #00ff87;border-radius:10px;padding:14px 18px;margin-bottom:24px;font-size:13px;color:#4d7a4d;">
        <b style="color:#00ff87;">How this works:</b> Enter a player's season stats. The model uses performance metrics, club prestige, and season year to estimate fair market value.
        Stats marked <span class="p90-badge">PER 90</span> must be entered as per-90-minute rates, not season totals.
    </div>""",unsafe_allow_html=True)

    all_df=pd.concat(full.values(),ignore_index=True)
    squads=sorted(all_df["squad"].dropna().unique().tolist())
    nations=["Albania","Algeria","Argentina","Australia","Austria","Belgium","Bosnia","Brazil",
        "Bulgaria","Cameroon","Canada","Chile","Colombia","Costa Rica","Croatia","Czech Republic",
        "Denmark","Ecuador","Egypt","England","Finland","France","Germany","Ghana","Greece",
        "Guinea","Hungary","Iceland","Ireland","Israel","Italy","Ivory Coast","Jamaica","Japan",
        "Jordan","Mali","Mexico","Montenegro","Morocco","Netherlands","New Zealand","Nigeria",
        "Northern Ireland","Norway","Peru","Poland","Portugal","Romania","Scotland","Senegal",
        "Serbia","Slovakia","Slovenia","South Korea","Spain","Sweden","Switzerland","Tunisia",
        "Turkey","Ukraine","United States","Uruguay","Wales","Zambia","Zimbabwe"]

    c_top1,c_top2,c_top3=st.columns(3)
    with c_top1: pos_sel=st.selectbox("Position",["Attackers","Midfielders","Defenders","Goalkeepers"])
    with c_top2: squad=st.selectbox("Club",squads)
    with c_top3: season=st.selectbox("Season",["2023-24","2022-23","2021-22","2020-21","2019-20"],
        help="Transfer market values have inflated over time — same stats are worth more in 2023-24 than 2019-20.")
    if pos_sel!="Goalkeepers":
        nation=st.selectbox("Nationality",nations)

    pos_key=pos_sel.lower(); m=models[pos_key]
    st.markdown("---")

    if pos_key=="attackers":
        c1,c2,c3=st.columns(3)
        with c1:
            rng_label("Age","17","25","36"); age=st.number_input("Age",16,42,24,label_visibility="collapsed")
            rng_label("Matches Played","13","29","38"); matches=st.number_input("Matches Played",0,38,28,label_visibility="collapsed")
            rng_label("Total Minutes","901","1957","3328"); minutes=st.number_input("Total Minutes",0,4000,2500,label_visibility="collapsed")
            rng_label("Goals","0","7.6","36"); goals=st.number_input("Goals",0,50,8,label_visibility="collapsed")
            rng_label("Assists","0","3.4","14"); assists=st.number_input("Assists",0,30,5,label_visibility="collapsed")
            rng_label("Non-Penalty Goals","0","6.8","29"); npg=st.number_input("Non-Penalty Goals",0,40,7,label_visibility="collapsed")
        with c2:
            rng_label("Expected Goals (xG)","0.4","7.5","29.2"); xg=st.number_input("Expected Goals (xG)",0.0,35.0,7.0,0.5,label_visibility="collapsed")
            rng_label("Exp Non-Penalty Goals","0.4","6.8","23.0"); expnpg=st.number_input("Exp NPG",0.0,30.0,6.0,0.5,label_visibility="collapsed")
            rng_label("Total Shots","4","52.5","133"); shots=st.number_input("Total Shots",0,150,55,label_visibility="collapsed")
            rng_label("Shot on Target %","8","38","64","%"); sot=st.number_input("Shot on Target %",0.0,100.0,38.0,label_visibility="collapsed")
            rng_label("Progressive Passes","6","58.7","197"); pp=st.number_input("Progressive Passes",0,200,55,label_visibility="collapsed")
            rng_label("Progressive Carries","4","62.3","252"); pc=st.number_input("Progressive Carries",0,260,60,label_visibility="collapsed")
        with c3:
            rng_label("Key Passes","3","27.8","91"); kp=st.number_input("Key Passes",0,100,28,label_visibility="collapsed")
            rng_label("Passes into Penalty Area","1","22","73"); pia=st.number_input("Passes into Penalty Area",0,80,22,label_visibility="collapsed")
            rng_label("Shot Creating Actions","1.2","3.0","7.0",per90=True); sca=st.number_input("SCA p90",0.0,10.0,3.0,0.1,label_visibility="collapsed")
            rng_label("Goal Creating Actions","0.0","0.4","1.4",per90=True); gca=st.number_input("GCA p90",0.0,5.0,0.4,0.1,label_visibility="collapsed")
            rng_label("Possessions Lost","4","36","148"); pl=st.number_input("Possessions Lost",0,160,36,label_visibility="collapsed")
            rng_label("Errors Made","0","0.2","3"); err=st.number_input("Errors Made",0,5,0,label_visibility="collapsed")
        row={"age":age,"Matches Played":matches,"Minutes_total":minutes,"Goals":goals,"Assists":assists,
             "Goals & Assists":goals+assists,"Non Penalty Goals":npg,"Penalty Kicks Made":max(goals-npg,0),
             "Expected Goals":xg,"Exp NPG":expnpg,"Total Shots":shots,"% Shots on target":sot,
             "Shots p 90":shots/(minutes/90+1e-5),"Goals p 90":goals/(minutes/90+1e-5),
             "Assists p 90":assists/(minutes/90+1e-5),"Goals per shot":goals/(shots+1e-5),
             "Goals per shot on target":goals/(shots*sot/100+1e-5),"Progressive Carries":pc,
             "Progressive Passes":pp,"Key passes":kp,"1/3":pp*0.5,"Passes into penalty area":pia,
             "Shot creating actions p 90":sca,"Goal creating actions p 90":gca,
             "Possessions lost":pl,"Errors made":err,"squad":squad,"nation":nation,"season":season}

    elif pos_key=="midfielders":
        c1,c2,c3=st.columns(3)
        with c1:
            rng_label("Age","17","25.8","36"); age=st.number_input("Age",16,42,25,label_visibility="collapsed")
            rng_label("Matches Played","11","27.8","38"); matches=st.number_input("Matches Played",0,38,28,label_visibility="collapsed")
            rng_label("Total Minutes","904","1973","3420"); minutes=st.number_input("Total Minutes",0,4000,2500,label_visibility="collapsed")
            rng_label("Goals","0","2.6","23"); goals=st.number_input("Goals",0,25,3,label_visibility="collapsed")
            rng_label("Assists","0","2.3","20"); assists=st.number_input("Assists",0,25,3,label_visibility="collapsed")
            rng_label("Expected Goals (xG)","0","2.5","16.1"); xg=st.number_input("Expected Goals",0.0,20.0,2.5,0.5,label_visibility="collapsed")
        with c2:
            rng_label("Progressive Passes","15","109","376"); pp=st.number_input("Progressive Passes",0,380,100,label_visibility="collapsed")
            rng_label("Progressive Carries","0","38.1","146"); pc=st.number_input("Progressive Carries",0,150,38,label_visibility="collapsed")
            rng_label("Key Passes","1","26.1","136"); kp=st.number_input("Key Passes",0,140,25,label_visibility="collapsed")
            rng_label("Passes into Penalty Area","0","20.7","111"); pia=st.number_input("Passes into Penalty Area",0,115,20,label_visibility="collapsed")
            rng_label("Shot Creating Actions","0.4","2.7","7.5",per90=True); sca=st.number_input("SCA p90",0.0,10.0,2.7,0.1,label_visibility="collapsed")
            rng_label("Goal Creating Actions","0.0","0.3","1.2",per90=True); gca=st.number_input("GCA p90",0.0,5.0,0.3,0.1,label_visibility="collapsed")
        with c3:
            rng_label("Tackles Attempted","6","43.4","152"); ta=st.number_input("Tackles Attempted",0,155,40,label_visibility="collapsed")
            rng_label("Tackles Won","2","24.4","75"); tw=st.number_input("Tackles Won",0,80,24,label_visibility="collapsed")
            rng_label("Interceptions","1","23.7","80"); interc=st.number_input("Interceptions",0,85,23,label_visibility="collapsed")
            rng_label("Clearances","0","25.5","107"); clr=st.number_input("Clearances",0,110,25,label_visibility="collapsed")
            rng_label("% Dribbles Tackled","7.7","37.8","85.7","%"); pdt=st.number_input("% Dribbles Tackled",0.0,100.0,38.0,label_visibility="collapsed")
            rng_label("% Aerial Duels Won","0","43","75","%"); pad=st.number_input("% Aerial Duels Won",0.0,100.0,43.0,label_visibility="collapsed")
        c4,_=st.columns(2)
        with c4:
            rng_label("Possessions Lost","3","22.1","82"); pl=st.number_input("Possessions Lost",0,85,22,label_visibility="collapsed")
            rng_label("Errors Made","0","0.7","4"); err=st.number_input("Errors Made",0,5,1,label_visibility="collapsed")
        row={"age":age,"Matches Played":matches,"Minutes_total":minutes,"Goals":goals,"Assists":assists,
             "Goals & Assists":goals+assists,"Non Penalty Goals":goals,"Expected Goals":xg,"Exp NPG":xg,
             "Progressive Carries":pc,"Progressive Passes":pp,"Key passes":kp,"1/3":pp*0.7,
             "Passes into penalty area":pia,"Shot creating actions p 90":sca,"Goal creating actions p 90":gca,
             "Tackles attempted":ta,"Tackles Won":tw,"% Dribbles tackled":pdt,"Interceptions":interc,
             "Clearances":clr,"Shots blocked":5,"Passes blocked":20,"% Aerial Duels won":pad,
             "Possessions lost":pl,"Errors made":err,"squad":squad,"nation":nation,"season":season}

    elif pos_key=="defenders":
        c1,c2,c3=st.columns(3)
        with c1:
            rng_label("Age","17","26.4","38"); age=st.number_input("Age",16,42,25,label_visibility="collapsed")
            rng_label("Matches Played","10","25","38"); matches=st.number_input("Matches Played",0,38,25,label_visibility="collapsed")
            rng_label("Total Minutes","900","2023","3420"); minutes=st.number_input("Total Minutes",0,4000,2200,label_visibility="collapsed")
            rng_label("Tackles Attempted","2","37.6","129"); ta=st.number_input("Tackles Attempted",0,130,38,label_visibility="collapsed")
            rng_label("Tackles Won","1","22.4","80"); tw=st.number_input("Tackles Won",0,85,22,label_visibility="collapsed")
            rng_label("% Dribbles Tackled","0","55.6","100","%"); pdt=st.number_input("% Dribbles Tackled",0.0,100.0,56.0,label_visibility="collapsed")
        with c2:
            rng_label("Interceptions","5","28","84"); interc=st.number_input("Interceptions",0,90,28,label_visibility="collapsed")
            rng_label("Clearances","14","77.6","204"); clr=st.number_input("Clearances",0,210,78,label_visibility="collapsed")
            rng_label("Shots Blocked","0","13.9","78"); sb=st.number_input("Shots Blocked",0,80,14,label_visibility="collapsed")
            rng_label("Passes Blocked","0","13.4","48"); pb=st.number_input("Passes Blocked",0,50,13,label_visibility="collapsed")
            rng_label("% Aerial Duels Won","14.6","56.2","86.4","%"); pad=st.number_input("% Aerial Duels Won",0.0,100.0,56.0,label_visibility="collapsed")
            rng_label("Progressive Carries","0","28.3","149"); pc=st.number_input("Progressive Carries",0,155,28,label_visibility="collapsed")
        with c3:
            rng_label("Progressive Passes","11","78.8","357"); pp=st.number_input("Progressive Passes",0,360,78,label_visibility="collapsed")
            rng_label("1/3 Passes","8","68.7","309"); third=st.number_input("1/3 Passes",0,315,68,label_visibility="collapsed")
            rng_label("Possessions Lost","0","8.1","56"); pl=st.number_input("Possessions Lost",0,60,8,label_visibility="collapsed")
            rng_label("Errors Made","0","1.0","5"); err=st.number_input("Errors Made",0,5,1,label_visibility="collapsed")
            rng_label("Goals","0","1.0","5"); goals=st.number_input("Goals",0,6,1,label_visibility="collapsed")
            rng_label("Assists","0","1.2","13"); assists=st.number_input("Assists",0,15,1,label_visibility="collapsed")
        row={"age":age,"Matches Played":matches,"Minutes_total":minutes,"Tackles attempted":ta,
             "Tackles Won":tw,"% Dribbles tackled":pdt,"Interceptions":interc,"Clearances":clr,
             "Shots blocked":sb,"Passes blocked":pb,"% Aerial Duels won":pad,"Progressive Carries":pc,
             "Progressive Passes":pp,"1/3":third,"Possessions lost":pl,"Errors made":err,
             "Goals":goals,"Assists":assists,"Goals & Assists":goals+assists,"squad":squad,"nation":nation,"season":season}

    else:  # goalkeepers
        c1,c2,c3=st.columns(3)
        with c1:
            rng_label("Age","20","28.4","38"); age=st.number_input("Age",16,42,27,label_visibility="collapsed")
            rng_label("Matches Played","10","29.7","38"); matches=st.number_input("Matches Played",0,38,28,label_visibility="collapsed")
            rng_label("Total Minutes","900","2664","3420"); minutes=st.number_input("Total Minutes",0,4000,2500,label_visibility="collapsed")
            rng_label("Goals Against","11","41.8","85"); ga=st.number_input("Goals Against",0,90,42,label_visibility="collapsed")
        with c2:
            rng_label("Goals Against p90","0.7","1.4","2.7",per90=True); gap90=st.number_input("Goals Against p90",0.0,4.0,1.4,0.1,label_visibility="collapsed")
            rng_label("Saves","16","88","162"); saves=st.number_input("Saves",0,170,88,label_visibility="collapsed")
            rng_label("Save %","54.2","69.9","80.8","%"); svpct=st.number_input("Save %",0.0,100.0,70.0,label_visibility="collapsed")
            rng_label("Clean Sheets","0","8","20"); cs=st.number_input("Clean Sheets",0,38,8,label_visibility="collapsed")
        with c3:
            rng_label("Clean Sheet %","0","25.8","55.6","%"); cspct=st.number_input("Clean Sheet %",0.0,100.0,26.0,label_visibility="collapsed")
            rng_label("Penalty Save %","0","11.1","66.7","%"); penpct=st.number_input("Penalty Save %",0.0,100.0,11.0,label_visibility="collapsed")
            rng_label("Crosses Stopped","0.6","5.6","12.4"); crosses=st.number_input("Crosses Stopped",0,15,5,label_visibility="collapsed")
        row={"age":age,"Matches Played":matches,"Minutes_total":minutes,"Goals Against":ga,
             "Goals against p 90":gap90,"Saves":saves,"Saves %":svpct,"Clean Sheets":cs,
             "% Clean sheets":cspct,"% Penalty saves":penpct,"Crosses Stopped":crosses,
             "squad":squad,"nation":"ENG","season":season}

    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("⚡  PREDICT MARKET VALUE",use_container_width=False):
        warnings_list=[]
        if pos_key=="attackers":
            if not(17<=age<=36): warnings_list.append(f"Age {age} — typical range: 17–36")
            if not(901<=minutes<=3328): warnings_list.append(f"Minutes {minutes} — typical range: 901–3328")
            if not(0<=goals<=36): warnings_list.append(f"Goals {goals} — typical range: 0–36")
            if not(0<=xg<=29.2): warnings_list.append(f"xG {xg} — typical range: 0–29.2")
        elif pos_key=="midfielders":
            if not(17<=age<=36): warnings_list.append(f"Age {age} — typical range: 17–36")
            if not(904<=minutes<=3420): warnings_list.append(f"Minutes {minutes} — typical range: 904–3420")
        elif pos_key=="defenders":
            if not(17<=age<=38): warnings_list.append(f"Age {age} — typical range: 17–38")
            if not(900<=minutes<=3420): warnings_list.append(f"Minutes {minutes} — typical range: 900–3420")
            if not(0<=clr<=204): warnings_list.append(f"Clearances {clr} — typical range: 0–204")
        elif pos_key=="goalkeepers":
            if not(20<=age<=38): warnings_list.append(f"Age {age} — typical range: 20–38")
            if not(900<=minutes<=3420): warnings_list.append(f"Minutes {minutes} — typical range: 900–3420")
            if not(0<=svpct<=100): warnings_list.append(f"Save % {svpct} — must be 0–100")
        if warnings_list:
            st.warning("⚠ Some stats are outside the training data range — prediction may be less reliable:\n" + "\n".join(f"• {w}" for w in warnings_list))
        df_row=pd.DataFrame([row])
        df_fe=fe(df_row,pos_key,m["squad_map"],m["nation_map"])
        pred_arr=predict_df(df_fe,pos_key,models)
        if len(pred_arr)>0:
            pred_m=max(float(pred_arr[0]),0)/1e6
            color=POS_COLORS.get(pos_sel,"#00ff87")
            top6=squad in TOP6
            st.markdown(f"""<div class="card" style="border-top:3px solid {color};margin-top:20px;text-align:center;padding:40px;">
              <div style="color:#4d7a4d;font-size:10px;text-transform:uppercase;letter-spacing:3px;margin-bottom:8px;">
                Predicted Market Value · {pos_sel} · {season}</div>
              <div style="font-family:'Bebas Neue',sans-serif;font-size:88px;color:{color};letter-spacing:4px;line-height:1;">
                €{pred_m:.1f}M</div>
              <div style="color:#4d7a4d;font-size:13px;margin-top:14px;">
                {squad} {"⭐ Top 6 Club" if top6 else ""} · Age {age} · {pos_sel}
              </div>
            </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
def scroll_top():
    st.markdown("""
    <script>
        window.parent.document.querySelector('section.main').scrollTo(0, 0);
    </script>
    """, unsafe_allow_html=True)

def main():
    # Keep session alive using query params
    if "user" in st.query_params and not st.session_state.logged_in:
        st.session_state.logged_in = True
        st.session_state.username = st.query_params["user"]
    if not st.session_state.logged_in:
        auth_page(); return
    preds,full=load_all_data()
    models=load_models()
    page=sidebar()
    if "current_page" not in st.session_state:
        st.session_state.current_page = page
    if st.session_state.current_page != page:
        st.session_state.current_page = page
        st.markdown('<script>parent.document.querySelector("section.main").scrollTop=0;</script>', unsafe_allow_html=True)
    if st.session_state.current_page != page:
        st.session_state.current_page = page
        st.session_state["_scroll_reset"] = True
        st.rerun()
    if st.session_state.get("_scroll_reset"):
        st.session_state["_scroll_reset"] = False
        st.markdown('<script>parent.document.querySelector("section.main").scrollTo(0,0);</script>', unsafe_allow_html=True)
    if   "Home"        in page: page_home(preds,full)
    elif "Undervalued" in page: page_undervalued(preds,full,models)
    elif "Performance" in page: page_perf(preds,full)
    elif "Lookup"      in page: page_lookup(full,models)
    elif "Predict"     in page: page_predict(full,models)

main()
