import streamlit as st
import json
import os
import base64

# ==========================================
# 1. 基础配置与商业级 UI 样式
# ==========================================
st.set_page_config(page_title="专业 MBTI 性格测评 2.0", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #f4f7fb; }
    header { visibility: hidden; }
    .block-container {
        background-color: #ffffff;
        border-radius: 20px;
        padding: 3rem 4rem 4rem 4rem !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin-top: 3rem;
        max-width: 800px;
    }
    h1 { text-align: center; color: #1e293b; font-weight: 800; font-size: 32px; margin-bottom: 5px; }
    .sub-title { text-align: center; color: #64748b; font-size: 16px; margin-bottom: 30px; }
    
    /* 高级结果页 UI */
    .result-title { text-align: center; color: #1e293b; font-size: 28px; font-weight: bold; margin-bottom: 20px; }
    .info-card { 
        background-color: #f0f7ff; border-radius: 12px; padding: 20px; 
        display: flex; align-items: center; gap: 20px; margin-bottom: 20px; 
        border: 1px solid #dbeafe;
    }
    .info-card img { width: 120px; border-radius: 8px; object-fit: cover; background-color: #fff; padding: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);}
    .info-card p { font-size: 16px; color: #334155; margin: 0; line-height: 1.7; }
    
    .traits-card {
        background-color: #f8fafc; border-radius: 12px; padding: 25px; 
        border: 1px solid #e2e8f0; margin-bottom: 30px;
    }
    .traits-card p { font-size: 16px; color: #475569; line-height: 1.9; margin: 0; }
    
    .stButton > button {
        width: 100%; border-radius: 12px; padding: 15px; margin-top: 20px;
        background-color: #ffffff; color: #475569; border: 2px solid #e2e8f0; font-weight: bold;
    }
    .stButton > button:hover { border-color: #0072ff; color: #0072ff; background-color: #f0f7ff; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 图像转换引擎与门禁系统
# ==========================================
def get_image_base64(image_filename):
    """将本地图片转换为 HTML 可直接读取的 Base64 格式"""
    if os.path.exists(image_filename):
        try:
            with open(image_filename, "rb") as img_file:
                mime_type = "image/png" if image_filename.lower().endswith('.png') else "image/jpeg"
                return f"data:{mime_type};base64,{base64.b64encode(img_file.read()).decode()}"
        except Exception:
            pass
    return "https://placehold.co/150x200/e2e8f0/64748b?text=Image+Missing"

def load_valid_codes():
    codes = []
    if os.path.exists('codes.txt'):
        try:
            with open('codes.txt', 'r', encoding='utf-8') as f:
                codes = [line.strip() for line in f.readlines() if line.strip()]
        except Exception:
            pass
    return codes

# ==========================================
# 3. 16 种性格全量数据库
# ==========================================
MBTI_PROFILES = {
    "ISTJ": {"name": "物流师型人格", "image_file": "ISTJ.jpg", "core": "内向、实感、理智、独立。物流师型人格的人正直务实，恪尽职守，深爱家庭以及拥护规则，他们愿意为自己的行为负责，为努力完成目标所做的一切感到骄傲。", "traits": "1. 严肃、安静、藉由集中意志与全力投入，及可被信赖获致成功。<br>2. 行事务实、有序、实际、逻辑、真实及可信赖。<br>3. 十分留意且乐于任何事（工作、居家、生活均有良好组织及有序）。<br>4. 负责任。<br>5. 照设定成效来作出决策且不畏阻挠与闲言会坚定为之。<br>6. 重视传统与忠诚。<br>7. 传统性的思考者或经理。"},
    "ISFJ": {"name": "守卫者型人格", "image_file": "ISFJ.jpg", "core": "非常专注和热情的保护者，总是随时准备保护他们所爱的人。", "traits": "1. 极其可靠、观察力细致入微。<br>2. 擅长默默为他人付出，记忆力极佳且注重每一个生活细节。<br>3. 勤奋、忠诚且无私，总是在幕后默默维持着运转。"},
    "ESTJ": {"name": "总经理型人格", "image_file": "ESTJ.jpg", "core": "出色的管理者，在管理事物或人的方面无与伦比。", "traits": "1. 极度敬业、意志坚定。<br>2. 擅长将混乱转化为秩序，是天生的组织者。<br>3. 喜欢清晰的层级结构和明确的规则，极其可靠的执行者和监督者。"},
    "ESFJ": {"name": "执政官型人格", "image_file": "ESFJ.jpg", "core": "非常关心他人，善于社交，受人欢迎，总是乐于助人。", "traits": "1. 极具责任感、擅长团队合作。<br>2. 能敏锐察觉群体的需求并迅速提供实际的后勤帮助。<br>3. 团队中最完美的“粘合剂”，喜欢和谐的氛围。"},
    "INTJ": {"name": "建筑师型人格", "image_file": "INTJ.jpg", "core": "富有想象力和战略性的思想家，一切皆在计划之中。", "traits": "1. 极度理性、独立、专注。<br>2. 能一眼看透事物的本质并制定长远战略。<br>3. 喜欢解决极其复杂的系统性问题，渴望智力上的绝对挑战。"},
    "INTP": {"name": "逻辑学家型人格", "image_file": "INTP.jpg", "core": "具有创造力的发明家，对知识有着永不满足的渴望。", "traits": "1. 绝对客观、思想极度开放。<br>2. 擅长分析复杂的抽象理论，极具创新精神。<br>3. 喜欢在不受约束的环境中探索事物的底层逻辑。"},
    "ENTJ": {"name": "指挥官型人格", "image_file": "ENTJ.jpg", "core": "大胆、富有想象力且意志强大的领导者，总能找到或创造解决方法。", "traits": "1. 极具领导天赋、效率奇高、自信果敢。<br>2. 具有出色的宏观战略眼光。<br>3. 天生的统帅，善于迅速发现系统中的缺陷并果断采取雷霆行动。"},
    "ENTP": {"name": "辩论家型人格", "image_file": "ENTP.jpg", "core": "聪明好奇的思考者，不会放弃任何智力上的挑战。", "traits": "1. 思维敏捷如电、极具人格魅力。<br>2. 极其善于发现新视角和打破常规。<br>3. 极佳的头脑风暴者和破局者，喜欢推翻现有框架。"},
    "INFJ": {"name": "提倡者型人格", "image_file": "INFJ.jpg", "core": "安静而神秘，同时鼓舞人心且不知疲倦的理想主义者。", "traits": "1. 洞察人心、富有极深的同理心。<br>2. 为了内心的信仰坚定不移，极具个人原则。<br>3. 渴望深刻、真实的灵魂共鸣，关注对社会产生深远影响。"},
    "INFP": {"name": "调停者型人格", "image_file": "INFP.jpg", "core": "诗意、善良的利他主义者，总是热情地为正当理由提供帮助。", "traits": "1. 同理心溢出、思想包容开放。<br>2. 绝对忠于自己的内在价值观，具有独特的艺术灵性。<br>3. 浪漫至死不渝，是一台“意义驱动”的机器。"},
    "ENFJ": {"name": "主人公型人格", "image_file": "ENFJ.jpg", "core": "富有魅力、鼓舞人心的领导者，有使听众着迷的能力。", "traits": "1. 天生的精神领袖、极度可靠。<br>2. 热衷于帮助他人成长，人际交往能力满分。<br>3. 出色的团队凝聚者，擅长敏锐地发现每个成员的潜能。"},
    "ENFP": {"name": "竞选者型人格", "image_file": "ENFP.jpg", "core": "热情，有创造力爱社交的自由自在的人，总能找到理由微笑。", "traits": "1. 永远充满好奇心、热情洋溢。<br>2. 极具沟通和感染天赋，能敏锐捕捉并调动他人的情绪。<br>3. 需要极大的创意空间和灵活度，充满无可救药的魅力。"},
    "ISTP": {"name": "鉴赏家型人格", "image_file": "ISTP.jpg", "core": "大胆而实际的实验家，擅长使用任何形式的工具。", "traits": "1. 随和灵活、冷静极其理性。<br>2. 擅长在突发危机中迅速找到硬核解决办法，动手能力拉满。<br>3. 偏好通过拆解和实践来学习，喜欢直接上手解决具体问题。"},
    "ISFP": {"name": "探险家型人格", "image_file": "ISFP.jpg", "core": "灵活有魅力的艺术家，时刻准备着探索和体验新鲜事物。", "traits": "1. 充满令人放松的魅力、对周遭环境极其敏感。<br>2. 极具艺术天赋，包容性极强。<br>3. 追求极致的审美和个人体验，温柔、随和且充满感官的关爱。"},
    "ESTP": {"name": "企业家型人格", "image_file": "ESTP.jpg", "core": "聪明，精力充沛善于感知的人们，真心享受生活在边缘。", "traits": "1. 绝对的行动派、环境观察力极其敏锐。<br>2. 擅长人际交往和利益谈判，天生的危机处理专家。<br>3. 善于在极度混乱中敏锐地发现商机或破局点，行动力爆表。"},
    "ESFP": {"name": "表演者型人格", "image_file": "ESFP.jpg", "core": "自发的，精力充沛而热情的表演者——生活在他们周围永不无聊。", "traits": "1. 极具人群感染力、擅长活跃任何僵硬的气氛。<br>2. 实干且极致注重当下体验，天生的乐天派。<br>3. 能够迅速适应任何新环境并成为团队绝对的开心果。"}
}

# ==========================================
# 4. 动态逻辑系统
# ==========================================
def load_questions():
    if os.path.exists('mbti_questions.json'):
        with open('mbti_questions.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def main():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h1>MBTI 专业深度测评系统</h1>", unsafe_allow_html=True)
        st.markdown("<div class='sub-title'>请输入您的专属激活码以开始测试</div>", unsafe_allow_html=True)
        valid_codes = load_valid_codes()
        code_input = st.text_input("激活码 (Activation Code)", placeholder="请输入您的激活码")
        if st.button("验证并进入系统"):
            if code_input in valid_codes:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ 激活码无效或已过期，请核对后重试。")
        return 

    questions = load_questions()
    if not questions:
        st.error("⚠️ 未检测到题库文件 mbti_questions.json")
        return

    if 'step' not in st.session_state:
        st.session_state.step = 0
        st.session_state.scores = {"E":0,"I":0,"S":0,"N":0,"T":0,"F":0,"J":0,"P":0}

    st.markdown("<h1>MBTI 性格类型测试</h1>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>探索真实的自我，寻找潜在的力量</div>", unsafe_allow_html=True)
    
    st.progress(min(st.session_state.step / len(questions), 1.0))
    st.write("---") 

    if st.session_state.step < len(questions):
        item = questions[st.session_state.step]
        st.write(f"**{item['question']}**")
        for i, opt in enumerate(item["options"]):
            if st.button(opt["text"], key=f"q_{st.session_state.step}_{i}"):
                dim = opt.get("dim", "")
                if dim in st.session_state.scores:
                    st.session_state.scores[dim] += 1
                st.session_state.step += 1
                st.rerun()
    else:
        s = st.session_state.scores
        res_code = (("E" if s["E"] >= s["I"] else "I") + ("S" if s["S"] >= s["N"] else "N") + 
                    ("T" if s["T"] >= s["F"] else "F") + ("J" if s["J"] >= s["P"] else "P"))
        profile = MBTI_PROFILES.get(res_code, MBTI_PROFILES["ISTJ"]) 
        
        img_b64 = get_image_base64(profile["image_file"])
        
        st.balloons()
        st.markdown("<div class='sub-title' style='margin-bottom:10px;'>量表测评结果</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='result-title'>{profile['name']}（{res_code}）</div>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-card">
            <img src="{img_b64}" alt="{res_code}">
            <p>{profile['core']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="traits-card">
            <p>{profile['traits']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<p style='text-align:center; color:#94a3b8; font-size: 14px;'>得分详情：E({s['E']}) I({s['I']}) | S({s['S']}) N({s['N']}) | T({s['T']}) F({s['F']}) | J({s['J']}) P({s['P']})</p>", unsafe_allow_html=True)
        
        if st.button("重新开始测试"):
            st.session_state.step = 0
            st.session_state.scores = {k:0 for k in st.session_state.scores}
            st.rerun()

if __name__ == "__main__":
    main()