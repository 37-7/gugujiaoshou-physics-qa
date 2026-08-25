# -*- coding: utf-8 -*-
"""
纯文本 -> 可渲染 LaTeX 的公式转换模块 v4
策略: 预处理中文运算词/全角括号 -> 保护(URL/提及/表情) -> 中文标点分隔切分 -> 覆盖表 -> 规则引擎 -> 判定数学模式
"""
import re, html

# ---------------- Unicode 数学字符 -> LaTeX ----------------
GREEK = {
    'ρ': r'\rho ', 'θ': r'\theta ', 'Θ': r'\Theta ', 'ω': r'\omega ', 'Ω': r'\Omega ',
    'α': r'\alpha ', 'β': r'\beta ', 'γ': r'\gamma ', 'λ': r'\lambda ', 'μ': r'\mu ',
    'π': r'\pi ', 'φ': r'\varphi ', 'Φ': r'\Phi ', 'σ': r'\sigma ', 'Σ': r'\Sigma ',
    'δ': r'\delta ', 'Δ': r'\Delta ', '∆': r'\Delta ', 'η': r'\eta ', 'κ': r'\kappa ',
    'ϵ': r'\epsilon ', 'ε': r'\varepsilon ', 'τ': r'\tau ', 'χ': r'\chi ', 'ξ': r'\xi ',
    'ψ': r'\psi ',
    # 数学斜体变体(U+1D6FC 起)统一回落到普通希腊命令
    '𝛼': r'\alpha ', '𝛽': r'\beta ', '𝛾': r'\gamma ', '𝛿': r'\delta ', '𝜀': r'\varepsilon ',
    '𝜁': r'\zeta ', '𝜂': r'\eta ', '𝜃': r'\theta ', '𝜄': r'\iota ', '𝜅': r'\kappa ',
    '𝜆': r'\lambda ', '𝜇': r'\mu ', '𝜈': r'\nu ', '𝜉': r'\xi ', '𝜋': r'\pi ',
    '𝜌': r'\rho ', '𝜍': r'\sigma ', '𝜎': r'\sigma ', '𝜏': r'\tau ', '𝜐': r'\upsilon ',
    '𝜙': r'\phi ', '𝜒': r'\chi ', '𝜓': r'\psi ', '𝜔': r'\omega ',
}
OPS = {
    '＝': '=', '＋': '+', '－': '-', '＜': '<', '＞': '>',
    '×': r'\times ', '÷': r'\div ', '➗': r'\div ', '➖': '-', '➕': '+',
    '≡': r'\equiv ', '≈': r'\approx ', '≠': r'\ne ', '≤': r'\le ', '≥': r'\ge ',
    '±': r'\pm ', '∞': r'\infty ', '∝': r'\propto ', '∠': r'\angle ',
    '∥': r'\parallel ', '⊥': r'\perp ',
    '√': r'\sqrt', '∫': r'\int ', '∑': r'\sum ', '∏': r'\prod ', '∂': r'\partial ',
    '∇': r'\nabla ', '∈': r'\in ', '°': r'^\circ ', '△': r'\Delta ',
    '∵': r'\because ', '∴': r'\therefore ', '∓': r'\mp ',
    '²': '^2', '³': '^3', '⁰': '^0', '¹': '^1', '⁴': '^4', '⁵': '^5',
    '½': r'\frac{1}{2}', '¼': r'\frac{1}{4}', '¾': r'\frac{3}{4}',
    '−': '-', '–': '-',
}
# 分数检测字符集(不含{}; 含希腊字母, 在希腊转换前使用)
FRAC_CHARS = 'A-Za-z0-9_\\^()²³⁰¹½ΔθωφρλμπσδγηκτξψΩΦΣαβϵε∆'

# ---------------- 精确片段覆盖表(人工审阅; 键为预处理后形式) ----------------
OVERRIDES = {
    'EP1+W=EP2+△Ek': r'E_{P1}+W=E_{P2}+\Delta E_k',
    'EP1': r'E_{P1}', 'EP2': r'E_{P2}', 'Ek': r'E_k', 'Ep': r'E_p', 'Fn': r'F_n',
    'B2L2C': 'B^2L^2C',
    '1\\2at^2': r'\frac{1}{2}at^2',
    'delta_i/delta_t': r'\frac{\Delta i}{\Delta t}',
    'delta(w)*r/delta(t)': r'\frac{\Delta (w)r}{\Delta (t)}',
    'delta Q=cm * delta T': r'\Delta Q=cm\,\Delta T ',
    'vb=2vasinθ': r'v_b=2v_a\sin\theta',
    'BLv': r'B\,L\,v', 'IBL': r'I\,B\,L', 'BIL': r'B\,I\,L',
    'mgsin': r'mg\sin ', 'gsin': r'g\sin ', 'gcos': r'g\cos ',
    '1/2mv2': r'\frac{1}{2}mv^2', 'mv2': 'mv^2',
    'Ek=1/2mv2': r'E_k=\frac{1}{2}mv^2',
    'Ek=1/2mv2;Ep=mgh;Ep=1/2k2x=1/2fx=1/2max;':
        r'E_k=\frac{1}{2}mv^2;\;E_p=mgh;\;E_p=\frac{1}{2}kx^2=\frac{1}{2}fx=\frac{1}{2}ma\,x;',
    'u2/r': r'\frac{u^2}{r}', 'gm/r2': r'\frac{gm}{r^2}', 'a=GM/r2': r'a=\frac{GM}{r^2}',
    'gm/r²': r'\frac{gm}{r^2}',
    'C42=6': r'\binom{4}{2}=6',
    'pv=constant': r'pV=\text{constant}',
    'I=0.01s x 10N  = 0.1 Ns': r'I=0.01\,\text{s}\times10\,\text{N}=0.1\,\text{N}\!\cdot\!\text{s}',
    'x= V 0 t+1/2 at²': r'x=V_0t+\frac{1}{2}at^2',
    "v'=x(t2)-x(t1)/t2-t1= V0+1/2a": r"v'=\frac{x(t_2)-x(t_1)}{t_2-t_1}=V_0+\frac{1}{2}a",
    'v=t1+t2/2=v0+a×(t1+t2': r'v=\frac{t_1+t_2}{2}=v_0+\frac{a(t_1+t_2)}{2}',
    'v=t1+t2/2=v0+a×(t1+t2）/2': r'v=\frac{t_1+t_2}{2}=v_0+\frac{a(t_1+t_2)}{2}',
    '1/2m \\bar{v^2}': r'\frac{1}{2}m\bar{v}^2',
    'x02': 'x_0^2', 't=kx02': r't=kx_0^2', '21x2': r'\frac{1}{2}x^2', '21x02': r'\frac{1}{2}x_0^2',
    'x-1/v': r'x-\frac{1}{v}',
    'a<<λ': r'a\ll\lambda ', 'a/λ': r'\frac{a}{\lambda}',
    'ω=const': r'\omega=\mathrm{const}',
    '1sinθ': r'1\sin\theta ',
    'sint': r'\sin t', 'cost': r'\cos t', 'tant': r'\tan t',
    'v_y t -1/2g t^2': r'v_y t-\frac{1}{2}g t^2',
    'sinA': r'\sin A', 'sinB': r'\sin B',
    'B30': r'B\ 30', 'x=7.5m': r'x=7.5\,\text{m}', 'x=7.5cm': r'x=7.5\,\text{cm}',
    'Tm=436.25K': r'T_m=436.25\,\text{K}', '7.5cm': r'7.5\,\text{cm}', 'xcm': r'x\,\text{cm}',
    '2R△θ/△t-R△φ/△t=0': r'\frac{2R\Delta\theta}{\Delta t}-\frac{R\Delta\varphi}{\Delta t}=0',
    'U=(I1-I2)R': r'U=(I_1-I_2)R', 'E1-U=I1r': r'E_1-U=I_1r', 'E2+U=I2r': r'E_2+U=I_2r',
    'S/Tm': r'\frac{S}{T_m}', 'an+a1': r'a_n+a_1', 'Sn=(an+a1)n': r'S_n=(a_n+a_1)n',
    'Sn=(an+a1)n/2': r'S_n=\frac{(a_n+a_1)n}{2}',
}
# 规则无法完美处理的整句(正则覆盖)
REGEX_OVERRIDES = [
    (re.compile(r'∫\s*x\s*0\s*x\s*x\s*d\s*x\s*=\s*∫\s*0\s*t\s*k\s*d\s*t'),
     r'\int_{x_0}^{x}x\,dx=\int_0^t k\,dt'),
]
# 双字母下标字面替换(数学上下文中)
LITERAL_SUBS = [
    ('va', r'v_a'), ('vb', r'v_b'), ('vA', r'v_A'), ('vB', r'v_B'), ('vN', r'v_N'),
    ('vx', r'v_x'), ('mA', r'm_A'), ('mB', r'm_B'), ('PA', r'P_A'), ("PA'", r"P_A'"),
    ('Uc', r'U_c'), ('Rf', r'R_f'), ('Tm', r'T_m'), ('Sn', r'S_n'), ('an', r'a_n'),
    ('i_max', r'i_{\max}'), ('v0max', r'v_{0\max}'), ('x0max', r'x_{0\max}'),
    ('Ek', r'E_k'), ('Ep', r'E_p'), ('Fn', r'F_n'), ('EP1', r'E_{P1}'), ('EP2', r'E_{P2}'),
]

LATEX_HINT = re.compile(r'\\[A-Za-z]+|\$|[_^{}]')
# 希腊命令+数字下标(白名单)
GREEK_CMD = (r'\\theta|\\omega|\\rho|\\lambda|\\mu|\\pi|\\varphi|\\sigma|\\delta|\\eta|'
             r'\\kappa|\\epsilon|\\varepsilon|\\tau|\\chi|\\xi|\\psi|\\Delta|\\alpha|\\beta|'
             r'\\gamma|\\Phi|\\Omega|\\Sigma|\\Theta')
GREEK_DIGIT = re.compile(r'(%s)\s*(\d+)(?![\dA-Za-z_{}])' % GREEK_CMD)
DELTA_SUB = re.compile(r'\\Delta\s*([A-Za-z])([a-z])')          # ΔEk -> \Delta E_k
DELTA_SUB2 = re.compile(r'\\Delta\s*([A-Z])([A-Z])')            # ΔVx -> \Delta V_x
GLUED_TRIG = re.compile(r'([A-Za-z0-9)])(sin|cos|tan|log|ln|exp)(?=[A-Za-zθφω(=+\-])')
TRIG = re.compile(r'(?<![A-Za-z])(sin|cos|tan|log|ln|exp)(?![A-Za-z])')

def sub_greek_ops(s):
    for k, v in GREEK.items():
        s = s.replace(k, v)
    for k, v in OPS.items():
        s = s.replace(k, v)
    return s

def sub_delta_word(s):
    s = re.sub(r'(?<![A-Za-z])delta(?![A-Za-z])', r'\\Delta ', s)
    s = re.sub(r'(?<![A-Za-z])theta(?![A-Za-z])', r'\\theta ', s)
    s = re.sub(r'(?<![A-Za-z])fai(?![A-Za-z])', r'\\Phi ', s)
    s = re.sub(r'(?<![A-Za-z])pi(?![A-Za-z])', r'\\pi ', s)
    return s

def sub_glued_trig(s):
    # 粘连三角函数: mgsin= -> mg\,\,sin= (只加间距, 命令由 TRIG 统一补)
    s = GLUED_TRIG.sub(lambda m: m.group(1) + r'\,\,' + m.group(2) + ' ', s)
    s = TRIG.sub(lambda m: '\\' + m.group(1) + ' ', s)
    return s

def sub_star(s):
    s = re.sub(r'(?<=[A-Za-z0-9}])\*\*(?=[A-Za-z0-9])', '^', s)
    s = re.sub(r'(?<=[A-Za-z0-9}])\*(?=[A-Za-z0-9])', r'\\cdot ', s)
    s = re.sub(r'(?<=[A-Za-z0-9}])·(?=[A-Za-z0-9])', r'\\cdot ', s)   # v·dv -> v\cdot dv
    return s

def sub_frac(s):
    # 1) 纯数字分数 1/2 -> \frac{1}{2} (日期已在主流程保护)
    s = re.sub(r'(?<![A-Za-z0-9}])(\d+)/(\d+)(?![\d.])', r'\\frac{\1}{\2}', s)
    # 2) 字母开头 token 分数 mg/L -> \frac{mg}{L} (返回函数中的反斜杠不会被二次处理)
    def rep(m):
        a, b = m.group(1), m.group(2)
        if '/' in a or '/' in b:
            return m.group(0)
        return '\\frac{%s}{%s}' % (a, b)
    pat = (r'(?<![A-Za-z0-9}])'
           r'([A-Za-z][A-Za-z0-9_\\^()²³⁰¹½]*?)/'
           r'([A-Za-z0-9_\\^()²³⁰¹½]+?)'
           r'(?![A-Za-z0-9_\\^{}])')
    s = re.sub(pat, rep, s)
    return s

def sub_superscript(s):
    # 字母+数字下标: v0->v_0 (允许后接字母/前有数字)
    s = re.sub(r'(?<![A-Za-z_])([A-Za-z])(\d+)(?![0-9_{}.])', r'\1_{\2}', s)
    # 希腊命令+数字: \theta 1 -> \theta_1
    s = GREEK_DIGIT.sub(r'\1_{\2}', s)
    return s

def sub_sqrt(s):
    s = re.sub(r'\\sqrt\s*([A-Za-z0-9])', r'\\sqrt{\1}', s)
    return s

def convert_run(run):
    if '\x00' in run or '@' in run:
        return None
    # 颜文字/表情保护: ^O^ 、=・ω・= 、^_^ 等
    if '・' in run or KAOMOJI.match(run) or run in ('qwq', 'QwQ', 'emm', 'hhh'):
        return None
    for pat, repl in REGEX_OVERRIDES:
        if pat.search(run):
            return pat.sub(lambda m, r=repl: r, run)
    if run in OVERRIDES:
        return OVERRIDES[run]
    s = sub_delta_word(run)      # 英文词先(防二次替换)
    s = sub_frac(s)              # 分数(原始字符含Δ/²)
    s = sub_greek_ops(s)         # 希腊/运算符
    s = sub_glued_trig(s)
    s = sub_star(s)
    s = sub_superscript(s)
    s = DELTA_SUB.sub(r'\\Delta \1_{\2}', s)
    s = DELTA_SUB2.sub(r'\\Delta \1_{\2}', s)
    s = sub_sqrt(s)
    # 双字母下标(仅当片段有数学上下文; lambda 返回值不做转义处理)
    if LATEX_HINT.search(s) or any(c in s for c in '=+−-×·÷≤≥≠≈^_'):
        for k, v in LITERAL_SUBS:
            s = re.sub(r'(?<![A-Za-z0-9_\\])' + re.escape(k) + r'(?![A-Za-z0-9_{}\\])',
                       lambda m, vv=v: vv, s)
    s = s.replace('$', '')
    if LATEX_HINT.search(s):
        return s
    return s if s != run else None

TRIGGER_CHARS = set('=+−-×·÷≤≥≠≈±∞∫∑∏∂∇∈∝∠⊥°√^_')
KAOMOJI = re.compile(r'^[\^]+[A-Za-z_^][\^]*$')
def is_math_trigger(run, latex):
    if '@' in run or '\x00' in run:
        return False
    if '・' in run or KAOMOJI.match(run):
        return False
    if latex is not None and latex != run:
        return True
    if any(c in run for c in TRIGGER_CHARS):
        if re.search(r'[A-Za-z0-9]', run):
            return True
    return False

# ---------------- 主函数 ----------------
URL_RE = re.compile(r'https?://[^\s<>"\']+')
EMOJI_RE = re.compile(r'\[[^\]]{1,20}\]')
MENTION_RE_HEAD = re.compile(r'^\s*回复\s*@([^:：]+?)\s*[:：]')
SPLIT_RE = re.compile(r'[\u4e00-\u9fff、。，；：？！…“”‘’\u2014～①②③④⑤⑥⑦⑧⑨⑩]+|[^\u4e00-\u9fff、。，；：？！…“”‘’\u2014～①②③④⑤⑥⑦⑧⑨⑩]+')

# 单个字母视为物理量、转 LaTeX 斜体（排除选项字母 A/B/C/D、几何点 O、坐标轴 X/Y/Z、少见 J/K）
SINGLE_PHYSICS = set('mvagxtrsfpqnhuiklwy') | set('FTEPRLIUQMNSVHWG')


def formula_html(msg):
    """返回 (escaped_html, 提及用户名或None)"""
    msg = html.unescape(msg)
    msg = msg.replace('\xa0', ' ').replace('ⅴ', 'v').replace('º', '°').replace('℉', 'F').replace('℃', '°C')
    # ---- 预处理(切分前, 整句) ----
    msg = re.sub(r'(?<=[^\u4e00-\u9fff])十(?=[^\u4e00-\u9fff])', '+', msg)
    msg = re.sub(r'(?<=[^\u4e00-\u9fff])等于(?=[^\u4e00-\u9fff])', '=', msg)
    msg = msg.replace('＝', '=').replace('＋', '+').replace('－', '-') \
             .replace('＜', '<').replace('＞', '>')
    msg = re.sub(r'([A-Za-z0-9)\]])方(?!向|法|式|程|便|位|形)', r'\1^2', msg)
    msg = re.sub(r'([A-Za-z0-9)\]}]|\\[A-Za-z]+)的平方', r'\1^2', msg)
    msg = msg.replace('西塔', r'\theta ')
    msg = re.sub(r'根号下([^\u4e00-\u9fff，。；！？、\s]+)', r'\\sqrt{\1}', msg)
    msg = msg.replace('（', '(').replace('）', ')')
    msg = msg.replace('′', "'").replace('’', "'").replace('‘', "'")

    # ---- 保护: 首部提及 ----
    mention = None
    m = MENTION_RE_HEAD.match(msg)
    if m:
        mention = m.group(1).strip()
        msg = re.sub(r'^\s*[:：]+\s*', '', msg[m.end():])

    # ---- 保护: URL 与表情码 ----
    tokens = []
    def keep(s):
        tokens.append(s)
        return '\x00%d\x00' % (len(tokens) - 1)
    msg = URL_RE.sub(lambda mm: keep(mm.group(0)), msg)
    msg = EMOJI_RE.sub(lambda mm: keep(mm.group(0)), msg)
    # 保护日期 2026/5/27 之类(避免被当分数)
    msg = re.sub(r'(?<!\d)(\d{4}/\d{1,2}/\d{1,2})(?!\d)', lambda mm: keep('D' + mm.group(0)), msg)

    # ---- 切分与转换 ----
    out = []
    for m in SPLIT_RE.finditer(msg):
        seg = m.group(0)
        if not seg:
            continue
        if seg[0] >= '\u4e00':
            out.append(html.escape(seg, quote=False))
            continue
        if '\x00' in seg:
            out.append(html.escape(seg, quote=False))
            continue
        # 单字母物理量 -> LaTeX 斜体
        if len(seg) == 1 and seg in SINGLE_PHYSICS:
            out.append('<span class="math">\\(' + seg + '\\)</span>')
            continue
        latex = convert_run(seg)
        if is_math_trigger(seg, latex):
            body = latex if latex is not None else seg
            body = body.replace('&', '&amp;')
            out.append('<span class="math">\\(' + body + '\\)</span>')
        else:
            out.append(html.escape(seg, quote=False))

    result = ''.join(out)
    for i, tok in enumerate(tokens):
        result = result.replace('\x00%d\x00' % i, html.escape(tok, quote=False))
    return result, mention
