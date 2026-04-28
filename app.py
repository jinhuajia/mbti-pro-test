import streamlit as st
import json
import os

# ==========================================
# 1. 基础配置与商业级 UI 样式
# ==========================================
st.set_page_config(page_title="专业 MBTI 性格测评", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #f0f4f8; }
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
    .result-box { 
        text-align: left; background: #f8fafc; padding: 25px; 
        border-radius: 15px; margin-top: 20px; border-left: 5px solid #0072ff; 
    }
    .result-box h4 { color: #0072ff; margin-bottom: 15px; font-size: 20px; font-weight: bold; }
    .result-box p { font-size: 16px; color: #475569; text-align: left; line-height: 1.7; margin-bottom: 12px; font-weight: normal; }
    .stButton > button {
        width: 100%; border-radius: 12px; padding: 15px; margin-top: 20px;
        background-color: #ffffff; color: #475569; border: 2px solid #e2e8f0; transition: all 0.2s;
    }
    .stButton > button:hover { border-color: #0072ff; color: #0072ff; background-color: #f0f7ff; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 动态激活码加载系统 (读取 codes.txt)
# ==========================================
def load_valid_codes():
    """从本地 codes.txt 文件加载所有有效激活码"""
    codes = []
    if os.path.exists('codes.txt'):
        try:
            with open('codes.txt', 'r', encoding='utf-8') as f:
                # 读取每一行，去掉首尾空格，并过滤掉空行
                codes = [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            st.error(f"读取激活码文件失败: {e}")
    return codes

# ==========================================
# 3. 16 种性格深度解析数据库
# ==========================================
MBTI_PROFILES = {
    "ESTJ": {"name": "总经理", "core": "出色的管理者，在管理事物或人的方面无与伦比。", "adv": "极度敬业、意志坚定、擅长将混乱转化为秩序，是天生的组织者。", "weak": "过于注重传统和既定规则，有时显得缺乏灵活性，难以共情他人的脆弱。", "career": "<b>适合领域：</b>企业高级管理、金融合规、法律、项目管理、军队。<br><b>工作风格：</b>你喜欢清晰的层级结构和明确的KPI。你是团队中极其可靠的执行者和监督者，极度厌恶低效、推诿和不守时。", "relationship": "在人际关系中，你非常看重<b>承诺、忠诚和稳定</b>。你喜欢直来直去，不喜欢伴侣让你“猜心思”。虽然你不擅长花言巧语，但你会通过承担责任、规划未来和提供物质保障来展现深刻的爱。", "growth": "1. <b>倾听异见：</b>尝试倾听那些听起来不太合逻辑的“疯狂点子”。<br>2. <b>放下掌控：</b>偶尔放下控制欲，接受不完美。<br>3. <b>先肯定后批评：</b>学习在指出别人错误前，先肯定对方的付出。"},
    "INTJ": {"name": "建筑师", "core": "富有想象力和战略性的思想家，一切皆在计划之中。", "adv": "极度理性、独立、专注，能一眼看透事物的本质并制定长远战略。", "weak": "可能过于完美主义，对愚蠢零容忍，有时容易忽略他人的情感需求，显得傲慢或冷漠。", "career": "<b>适合领域：</b>科学研究、系统架构、企业战略、投资分析、人工智能。<br><b>工作风格：</b>你喜欢解决极其复杂的系统性问题。你厌恶微观管理和无意义的社交，渴望智力上的绝对挑战。", "relationship": "寻找的是<b>智力上的伴侣</b>，而非纯粹的情感依赖。一旦做出承诺就会极其忠诚。你会用严密的逻辑帮伴侣解决人生难题。", "growth": "1. <b>接受不可控：</b>接受并非所有事情都能被完美预测和控制。<br>2. <b>提供情绪价值：</b>学会在伴侣需要安慰时给个拥抱，而不是只给解决方案。"},
    "INTP": {"name": "逻辑学家", "core": "具有创造力的发明家，对知识有着永不满足的渴望。", "adv": "绝对客观、思想极度开放、擅长分析复杂的抽象理论，极具创新精神。", "weak": "容易陷入无休止的自我沉思，在处理日常琐事时显得心不在焉，常常难以坚持将想法落地。", "career": "<b>适合领域：</b>软件开发、理论物理、数据科学家、哲学、学术研究。<br><b>工作风格：</b>你喜欢在不受约束的环境中探索宇宙的底层逻辑。对于枯燥的落地过程，你往往缺乏耐心。", "relationship": "你直接且诚实，极度需要<b>大量的个人空间</b>。可能会因为过于沉溺在自己的精神世界里，而忽略伴侣的日常感受。", "growth": "1. <b>跨出脑海：</b>尝试将宏大的构想拆解为可执行的小步骤。<br>2. <b>关注现实：</b>偶尔降落回现实生活，记住对伴侣重要的纪念日。"},
    "ENTJ": {"name": "指挥官", "core": "大胆、富有想象力且意志强大的领导者，总能找到解决方法。", "adv": "极具领导天赋、效率奇高、自信果敢，具有出色的宏观战略眼光。", "weak": "显得过于强势和固执，较难容忍低效和情感外露，有时会为了目标碾压他人的感受。", "career": "<b>适合领域：</b>企业创始人、高管、管理顾问、诉讼律师、风险投资。<br><b>工作风格：</b>你是天生的统帅，善于迅速发现系统中的缺陷并果断采取雷霆行动。你乐于带领团队攻克最难的关卡。", "relationship": "期待伴侣能与你<b>并肩作战、共同成长</b>，而非互相依附。你欣赏强强联手的爱情。", "growth": "1. <b>放慢脚步：</b>学会停下来，耐心倾听团队底层成员的反馈。<br>2. <b>拥抱柔软：</b>认识到情感也是人类互动的重要力量。"},
    "ENTP": {"name": "辩论家", "core": "聪明好奇的思考者，无法抗拒智力上的挑战。", "adv": "思维敏捷如电、极具人格魅力、极其善于发现新视角和打破常规。", "weak": "容易三分钟热度，喜欢为了辩论而辩论，有时难以坚持完成枯燥的收尾工作。", "career": "<b>适合领域：</b>公关营销、创意指导、政治评论、风投咨询、连环创业。<br><b>工作风格：</b>你是极佳的头脑风暴者和破局者，喜欢推翻现有框架。但在落地阶段时，你极易感到无聊并想开启下一个项目。", "relationship": "感情生活充满激情和惊喜。喜欢与伴侣进行<b>思想上的深度交锋</b>，极度讨厌一成不变的枯燥生活。", "growth": "1. <b>培养自律：</b>强迫自己培养“完成比完美更重要”的习惯。<br>2. <b>停止杠精：</b>意识到并非所有日常对话都需要变成一场辩论。"},
    "INFJ": {"name": "提倡者", "core": "安静而神秘，同时鼓舞人心且不知疲倦的理想主义者。", "adv": "洞察人心、富有极深的同理心、为了内心的信仰坚定不移，极具个人原则。", "weak": "极度注重个人隐私，容易因为背负太多他人的情绪垃圾或过度追求完美而陷入严重内耗。", "career": "<b>适合领域：</b>心理咨询、深度写作、非政府组织(NGO)、人力资源、艺术疗愈。<br><b>工作风格：</b>希望自己的工作能对人类社会产生深远的积极影响。反感职场政治，偏好独立思考或在和谐的小团队中运作。", "relationship": "极度渴望<b>深刻、真实的灵魂共鸣</b>。很难向他人完全敞开心扉，但一旦认定对方，你将毫无保留地付出。", "growth": "1. <b>建立边界：</b>学会隔离情绪，不要把全人类的痛苦都当成自己的责任。<br>2. <b>降低滤镜：</b>允许你自己和这个世界是不完美的。"},
    "INFP": {"name": "调停者", "core": "富有诗意、善良且利他的理想主义者，总是热情地提供帮助。", "adv": "同理心溢出、思想包容开放、绝对忠于自己的内在价值观，具有独特的艺术灵性。", "weak": "过于理想化，有时会因为沉溺于幻想而忽略现实生存法则，面对批评极其敏感甚至破碎。", "career": "<b>适合领域：</b>文学创作、独立设计、翻译、社会工作、心理辅导。<br><b>工作风格：</b>工作必须与你的灵魂契合。在充满狼性文化、高压或高度竞争的环境中，你会迅速枯萎。", "relationship": "浪漫至死不渝。对伴侣抱有极高的理想化期望，渴望童话般纯粹和谐的关系。", "growth": "1. <b>直面冲突：</b>勇敢面对现实世界中的人际冲突，学会坚定地表达自己的想法。<br>2. <b>接纳现实：</b>培养处理行政琐事等“世俗”生活的能力。"},
    "ENFJ": {"name": "主人公", "core": "充满魅力和鼓舞人心的领导者，有使听众着迷的能力。", "adv": "天生的精神领袖、极度可靠、热衷于帮助他人成长，人际交往能力满分。", "weak": "过度在意他人的看法，容易把别人的问题揽到自己身上，为了顾全大局而严重忽视自身需求。", "career": "<b>适合领域：</b>高等教育、公关发言人、政治家、企业教练、团队主管。<br><b>工作风格：</b>你是最出色的团队凝聚者。擅长敏锐地发现每个成员的潜能，并激励他们为了共同目标努力。", "relationship": "热情似火且全身心投入。会把伴侣的幸福放在首位，但也极易因为没有得到回应而感到失落。", "growth": "1. <b>学会拒绝：</b>你的核心价值不取决于你能为别人解决多少麻烦。<br>2. <b>自我关怀：</b>定期给自己留出完全独处的时间。"},
    "ENFP": {"name": "竞选者", "core": "热情、富有创造力且热爱社交的自由灵魂，总能找到微笑的理由。", "adv": "永远充满好奇心、热情洋溢、极具沟通和感染天赋，能敏锐捕捉并调动他人的情绪。", "weak": "极其容易分心，难以专注处理枯燥的行政事务，情绪起伏大，容易过度承诺。", "career": "<b>适合领域：</b>传媒记者、活动策划、创意总监、演艺界、市场营销。<br><b>工作风格：</b>需要极大的创意空间和灵活度。讨厌死板的打卡制度和高度重复的机械性任务。", "relationship": "充满魅力和惊喜。渴望与伴侣共同探索世界，但在长期稳定的关系中可能偶尔会感到受束缚。", "growth": "1. <b>对抗拖延：</b>练习做详细的日程计划并严格执行。<br>2. <b>冷思考：</b>在做重大的人生或财务决定前，强迫自己停下来用逻辑进行分析。"},
    "ISTJ": {"name": "物流师", "core": "实际且注重事实的个人，其可靠性不容怀疑。", "adv": "诚实直接、责任心坚不可摧、能够在极端混乱中迅速建立秩序，细节记忆力惊人。", "weak": "不善于变通，面对不熟悉或未经证实的创新事物时极为抗拒，有时显得刻板和冷漠。", "career": "<b>适合领域：</b>审计、财务会计、物流管理、军警系统、政府行政。<br><b>工作风格：</b>一丝不苟、绝对遵守规则。喜欢有明确说明书、标准流程的工作，能按时保质完成任务。", "relationship": "稳定、忠诚、有担当。会通过承担沉重的家庭责任和提供坚实的物质保障来表达深沉的爱。", "growth": "1. <b>拥抱变化：</b>尝试对不可预见的改变和新方法保持开放态度。<br>2. <b>软化表达：</b>认识到有时别人的“情绪感受”比客观事实更重要。"},
    "ISFJ": {"name": "守卫者", "core": "非常专注且温暖的保护者，时刻准备着保护他们爱的人。", "adv": "极其可靠、观察力细致入微、擅长默默为他人付出，记忆力极佳且注重每一个生活细节。", "weak": "过度谦虚，习惯性压抑自己的真实需求，容易被自私的人利用而不自知，极度害怕改变。", "career": "<b>适合领域：</b>医疗护理、学前教育、客户服务、行政助理、人力资源。<br><b>工作风格：</b>勤奋、忠诚且无私。在幕后默默维持着整个团队的正常运转，极度负责但往往低调而不愿居功。", "relationship": "体贴和顾家。会用心记住伴侣的所有喜好和每一个纪念日。是家庭中最温柔的基石。", "growth": "1. <b>表达需求：</b>学会大声、明确地说出自己的渴望。<br>2. <b>设立底线：</b>勇敢且坚决地拒绝那些超出你职责范围的无理要求。"},
    "ESFJ": {"name": "执政官", "core": "极有同情心、热爱社交且受欢迎的人，总是热心提供帮助。", "adv": "极具责任感、擅长团队合作、能敏锐察觉群体的需求并迅速提供实际的后勤帮助。", "weak": "对批评高度敏感，过于渴望被主流社会认同，有时会出于好意而把自己的价值观强加给别人。", "career": "<b>适合领域：</b>教育培训、医疗管理、公共关系、活动策划、社区工作。<br><b>工作风格：</b>团队中最完美的“粘合剂”。喜欢和谐的工作氛围，擅长组织人员并建立融洽的人际网络。", "relationship": "传统的家庭拥护者。喜欢按部就班的恋爱。非常需要伴侣经常性的赞美和正向反馈来确认被爱。", "growth": "1. <b>课题分离：</b>接受“并不是每个人都会喜欢你”这个事实。<br>2. <b>尊重差异：</b>不要把伴侣的独立选择视为对你个人的背叛。"},
    "ISTP": {"name": "鉴赏家", "core": "大胆而实际的实验家，擅长使用任何形式的工具。", "adv": "随和灵活、冷静极其理性、擅长在突发危机中迅速找到硬核解决办法，动手能力拉满。", "weak": "极度需要个人空间，容易对长期承诺感到窒息和厌倦，有时会做出冒险举动。", "career": "<b>适合领域：</b>机械工程、飞行员、外科医生、网络安全、急救人员。<br><b>工作风格：</b>偏好通过“拆解和实践”来学习。讨厌冗长的会议和务虚的理论，喜欢直接解决具体问题。", "relationship": "随性、不拘小节。不愿意被关系束缚，需要伴侣给予自由度。不擅长处理复杂的眼泪和情感拉扯。", "growth": "1. <b>尝试承诺：</b>尝试对重要的人做出长期承诺，并体验坚持带来的深度价值。<br>2. <b>情绪表达：</b>学会在适当的时候开口表达自己的情感。"},
    "ISFP": {"name": "探险家", "core": "灵活而有魅力的艺术家，随时准备探索和体验新鲜事物。", "adv": "充满令人放松的魅力、对周遭环境极其敏感、极具艺术天赋，包容性极强。", "weak": "过于活在当下，严重缺乏对未来的长远规划，面对冲突时第一反应往往是退缩或逃避。", "career": "<b>适合领域：</b>艺术设计、摄影、独立音乐、园艺、美容时尚。<br><b>工作风格：</b>追求极致的审美和个人体验。喜欢在没有严格规则的环境中工作，希望工作就是生活美学的一部分。", "relationship": "温柔、随和且充满关爱。喜欢通过实际行动（如做一顿大餐）而非言辞来表达爱意。", "growth": "1. <b>长远目光：</b>强迫自己制定一些中长期的理财规划，不要总是月光。<br>2. <b>直面战场：</b>学会直面人际冲突，要明白逃避往往会让问题发酵。"},
    "ESTP": {"name": "企业家", "core": "聪明、精力充沛且非常敏锐的人，真正喜欢生活在边缘。", "adv": "绝对的行动派、环境观察力极其敏锐、擅长人际谈判，天生的危机处理专家。", "weak": "极易冲动行事，讨厌规则和束缚，难以专注于长期且单调的目标，追求即时满足。", "career": "<b>适合领域：</b>一线销售、连续创业、商业谈判、体育竞技、危机公关。<br><b>工作风格：</b>高风险高回报的追求者。善于在混乱中敏锐地发现商机，行动力爆表，先开火再瞄准。", "relationship": "充满激情和乐趣。和他们在一起永远不会无聊，但他们较难安定下来，需要伴侣能跟上节奏。", "growth": "1. <b>谋定后动：</b>在采取行动前，至少花 5 分钟思考一下长远代价。<br>2. <b>培养耐心：</b>刻意培养对枯燥理论知识和复杂逻辑复盘的耐心。"},
    "ESFP": {"name": "表演者", "core": "随性、充满活力且热情的表演者，生活在他们周围永远不会无聊。", "adv": "极具人群感染力、擅长活跃气氛、实干且极致注重当下体验，天生的乐天派。", "weak": "容易为了眼前的快乐而逃避责任，不擅长复杂的逻辑分析和长远的人生规划。", "career": "<b>适合领域：</b>演艺娱乐、公关媒介、餐饮管理、旅游体验、大客户销售。<br><b>工作风格：</b>需要与人互动的舞台。能够迅速适应新环境并成为团队绝对的开心果，讨厌孤独的工作。", "relationship": "热烈且无拘无束。爱情对你来说必须是充满快乐和激情的。极度讨厌冷战和过度严肃的对话。", "growth": "1. <b>承担责任：</b>意识到生活不仅是聚会，勇敢承担起那些枯燥但必要的成年人责任。<br>2. <b>拒绝逃避：</b>遇到困难时，不要总是试图用转移注意力来逃避核心问题。"}
}

# ==========================================
# 4. 动态逻辑系统
# ==========================================
def main():
    # --- 门禁系统验证 ---
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h1>MBTI 专业深度测评系统</h1>", unsafe_allow_html=True)
        st.markdown("<div class='sub-title'>请输入您的专属激活码以开始测试</div>", unsafe_allow_html=True)
        
        # 实时加载最新的激活码列表
        valid_codes = load_valid_codes()
        
        # 如果文件丢失或为空，给管理员一个紧急提示（仅在本地测试时可见）
        if not valid_codes:
            st.warning("⚠️ 系统尚未配置有效激活码，请联系管理员。")

        code_input = st.text_input("激活码 (Activation Code)", placeholder="请输入您的激活码")
        
        if st.button("验证并进入系统"):
            if code_input in valid_codes:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ 激活码无效或已过期，请核对后重试。")
        return 

    # --- 测评程序 ---
    questions = load_questions()
    if not questions:
        st.error("⚠️ 未检测到题库文件 mbti_questions.json")
        return

    if 'step' not in st.session_state:
        st.session_state.step = 0
        st.session_state.scores = {"E":0,"I":0,"S":0,"N":0,"T":0,"F":0,"J":0,"P":0}
        st.session_state.show_detail = False

    st.markdown("<h1>MBTI 性格类型测试</h1>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>探索真实的自我，找寻潜在的力量</div>", unsafe_allow_html=True)
    
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
        profile = MBTI_PROFILES.get(res_code, MBTI_PROFILES["ESTJ"]) 
        
        if not st.session_state.show_detail:
            st.balloons()
            st.markdown(f"<h2 style='text-align:center; color:#0072ff; font-size: 38px;'>{profile['name']} [ {res_code} ]</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:#64748b; font-size: 16px;'>E({s['E']}) I({s['I']}) | S({s['S']}) N({s['N']}) | T({s['T']}) F({s['F']}) | J({s['J']}) P({s['P']})</p>", unsafe_allow_html=True)
            st.markdown(f"""<div class="result-box" style="text-align: center;">
<p style="font-size: 18px; color: #1e293b; font-weight: bold;">{profile['core']}</p>
<p style="color: #64748b; font-size: 14px; margin-top: 10px;">系统已为您生成专属的深度分析报告。</p>
</div>""", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            if col1.button("查看详细深度解析 ➔"):
                st.session_state.show_detail = True
                st.rerun()
            if col2.button("重新开始测试"):
                st.session_state.step = 0
                st.session_state.scores = {k:0 for k in st.session_state.scores}
                st.session_state.show_detail = False
                st.rerun()
        else:
            st.markdown(f"<h3 style='text-align:left; color:#1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;'>{profile['name']} ({res_code}) 专属深度解析</h3>", unsafe_allow_html=True)
            st.markdown(f"""<div class="result-box">
<h4>🌟 核心优势与潜在挑战</h4>
<p><b>核心优势：</b>{profile['adv']}</p>
<p><b>潜在挑战：</b>{profile['weak']}</p>
<hr style="margin: 20px 0; border-top: 1px dashed #cbd5e1;">
<h4>💼 职业发展规划</h4>
<p>{profile['career']}</p>
<hr style="margin: 20px 0; border-top: 1px dashed #cbd5e1;">
<h4>❤️ 人际交往与情感</h4>
<p>{profile['relationship']}</p>
<hr style="margin: 20px 0; border-top: 1px dashed #cbd5e1;">
<h4>🌱 专属成长指南</h4>
<p>{profile['growth']}</p>
</div>""", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            if col1.button("⬅ 返回简版结果"):
                st.session_state.show_detail = False
                st.rerun()
            if col2.button("重新开始测试"):
                st.session_state.step = 0
                st.session_state.scores = {k:0 for k in st.session_state.scores}
                st.session_state.show_detail = False
                st.rerun()

if __name__ == "__main__":
    main()