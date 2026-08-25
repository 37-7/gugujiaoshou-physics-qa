# -*- coding: utf-8 -*-
"""
B站评论区多期合集 -> 物理题可视化 HTML 生成器
输入: 9 个唯一期数的 archive JSON (第1,2,3,5,6,7,8,9,10期; 第4期数据缺失; ep5 有重复文件)
图片: 已由 download_images.py 下载压缩到 _imgs/, 用 manifest.json 映射 URL->本地文件
分类: 第10期 = 人工通读映射(最准); 其余期 = 关键词规则自动分类(标注"自动")
"""
import json, re, html, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from formula import formula_html

BASE = r'C:/Users/Jerry/WorkBuddy/2026-08-25-15-05-40'
IMGDIR = os.path.join(BASE, '_imgs')
OUT = os.path.join(BASE, '评论区物理题集_第1-10期合集.html')

# 期数配置(按顺序; ep5 重复文件只取一份)
EPISODES = [
    ('ep1',  '第1期',  r'C:/Users/Jerry/Downloads/ep1_archive.json'),
    ('ep2',  '第2期',  r'C:/Users/Jerry/Downloads/ep2_archive.json'),
    ('ep3',  '第3期',  r'C:/Users/Jerry/Downloads/ep1773472304999_archive.json'),
    ('ep4',  '第4期',  r'C:/Users/Jerry/Downloads/ep1774068069536_archive.json'),
    ('ep5',  '第5期',  r'C:/Users/Jerry/Downloads/ep1774677279463_archive.json'),
    ('ep6',  '第6期',  r'C:/Users/Jerry/Downloads/ep1775294076729_archive.json'),
    ('ep7',  '第7期',  r'C:/Users/Jerry/Downloads/ep1775882842744_archive.json'),
    ('ep8',  '第8期',  r'C:/Users/Jerry/Downloads/ep1776495656356_archive.json'),
    ('ep9',  '第9期',  r'C:/Users/Jerry/Downloads/ep1777092338561_archive.json'),
    ('ep10', '第10期', r'C:/Users/Jerry/Downloads/ep1777796135094_archive.json'),
]
EP10_MANUAL = {  # 第10期人工分类(与上一版一致, [12]已修正为静摩擦题→mech)
    298630419889: 'vibration', 301585026192: 'mech', 298576847553: 'em',
    298428631169: 'energy', 298633666801: 'other', 298533652257: 'vibration',
    298417533793: 'math', 301916122832: 'energy', 298528539057: 'other',
    301558070688: 'circuit', 299694537649: 'mech', 301183698880: 'circuit',
    298326025601: 'energy', 298300876049: 'em', 298275240689: 'em',
    298307064689: 'vibration', 298345632097: 'momentum', 301176377680: 'em',
    298632434161: 'circuit', 301331369424: 'mech', 303511864672: 'thermal',
    301545282304: 'energy', 301390309296: 'thermal', 300344539345: 'mech',
    299696543473: 'circuit', 298534779137: 'ac', 298290398481: 'momentum',
    302563453536: 'thermal', 298417763425: 'thermal', 298615805073: 'esfield',
    301191408352: 'ac', 298725233297: 'mech', 298256267601: 'thermal',
    301178872864: 'thermal',
}

# ---------------- 人工逐条分类(第1-9期; 第10期用上面的表) ----------------
# 键: "ep{rpid}" 或 "ep{rpid}"，值: 模块key。2026-08-25 逐条通读全部243条后判定。
MANUAL_MAP = {
    # ===== 第1期 =====
    'ep1:291590542145': 'momentum',   # 动量vs动能概念
    'ep1:291570647921': 'nuclear',    # 光电流随电压变化(光电效应)
    'ep1:293887628976': 'mech',       # 微元法/直角褶子压力
    'ep1:291566121777': 'optics',     # 肥皂膜亮环/全反射
    'ep1:291579026817': 'nuclear',    # 量子双缝观测者效应
    'ep1:293896973680': 'mech',       # 两圆交点速度/绳拉船速度分解
    'ep1:291713085537': 'mech',       # 微元法近似
    'ep1:291637084881': 'mech',       # 微元法/近似本质
    'ep1:293873455968': 'esfield',    # 正多边形顶点电荷场强对称性
    'ep1:291680169185': 'other',      # 牵星术/天球定位(天文,与高中物理关联弱)
    'ep1:293896672192': 'mech',       # 微元法/斜边长度悖论
    'ep1:293866385840': 'em',         # 充电器电流声/导线安培力振动
    'ep1:292008613457': 'mech',       # 牵引力/整体外力分析
    'ep1:291878034593': 'mech',       # 微元法题解答
    'ep1:291985277169': 'mech',       # 实验题/矢量理解
    'ep1:291619520353': 'momentum',   # 传送带完全非弹性碰撞能量
    'ep1:293865550960': 'mech',       # 熊掉坑算g(自由落体)
    'ep1:293868635488': 'mech',       # 静摩擦力与绳子拉力先后
    'ep1:293913432752': 'energy',     # 动能公式1/2mv²直觉
    'ep1:293869194464': 'mech',       # 惯性力/物理学习
    'ep1:294260949744': 'energy',     # 链条1/4圆弧/势能
    'ep1:291985457425': 'math',       # 等差数列Sn梯形面积
    'ep1:293881979248': 'mech',       # 连接体加速度比较
    'ep1:292065947057': 'thermal',    # 气体原子碰活塞弹回
    'ep1:292063508849': 'optics',     # 天空越抬头越蓝(散射)
    # ===== 第2期 =====
    'ep2:292958941233': 'energy',     # 斜抛射程极值/矢量三角形
    'ep2:294771591328': 'vibration',  # 单摆/圆锥摆周期公式
    'ep2:294702141088': 'energy',     # 动能定理在非地面系
    'ep2:294849532480': 'em',         # 磁通量有效面积
    'ep2:294763579888': 'em',         # 库仑力vs磁场力(粒子运动)
    'ep2:294761980704': 'math',       # 圆与斜边相切(几何+解题思维)
    'ep2:292469838561': 'energy',     # 万有引力定律推导/公理
    'ep2:292446148017': 'em',         # 单杆+电容器匀加速
    'ep2:295028531264': 'esfield',    # 平行板电容器匀强电场
    'ep2:292471603025': 'energy',     # 天体运动确定性/广义相对论
    'ep2:294773704288': 'energy',     # 地球为何不被太阳拉近
    'ep2:294709825856': 'mech',       # 完全失重问题
    'ep2:292548157745': 'mech',       # 为何同加速度下落
    'ep2:292519932801': 'mech',       # 质量/惯性本质
    'ep2:292959337921': 'vibration',  # 简谐运动叠加/线性系统
    'ep2:292928892417': 'momentum',   # 动量守恒条件(外力远小于内力)
    # ===== 第3期 =====
    'ep3:293552162417': 'em',         # 磁场边界问题
    'ep3:295417096320': 'thermal',    # p-V图圈圈面积/体积功
    'ep3:293165436689': 'energy',     # 卫星逃离引力场
    'ep3:293047102129': 'mech',       # 动滑轮速度/位移关系
    'ep3:295415542112': 'em',         # 双棒电磁感应+摩擦力
    'ep3:292996036593': 'math',       # 圆环体积(微元法/祖暅原理)
    'ep3:293576995825': 'esfield',    # 同球面电荷分布形状
    'ep3:295413993280': 'momentum',   # 水流弯管冲击力/微元法
    'ep3:295415894544': 'vibration',  # 弹簧振子/AB分离
    'ep3:293027198017': 'mech',       # 平均速度/匀变速运动学
    'ep3:293737150305': 'em',         # 柯尼希定理(双棒题)
    'ep3:293440478113': 'math',       # 甲烷构型/向量/正单纯形
    'ep3:295420696800': 'em',         # 通电螺线管小磁针
    'ep3:295421555552': 'thermal',    # 气体压强/活塞
    'ep3:293184568593': 'other',      # 2006老题(内容在图)
    'ep3:292998011521': 'energy',     # 椭圆轨道卫星喷气
    'ep3:292999305025': 'energy',     # 喷泉功率计算
    'ep3:292998826977': 'math',       # 排列组合隔板法
    'ep3:292998544177': 'mech',       # 大海运动/地球自转(相对运动思考)
    'ep3:295911172928': 'em',         # 电磁学轮摆线
    'ep3:295458029408': 'em',         # 双棒题解法
    # ===== 第4期 =====
    'ep4:293716261281': 'vibration',  # 运动叠加/补偿法/简谐运动
    'ep4:293694418449': 'math',       # 圆环体积(微元/祖暅, 上期答案)
    'ep4:296173134192': 'vibration',  # 假设调整法/弹簧振子分离
    'ep4:293692728881': 'esfield',    # 同球面等量电荷分布/正多面体对称
    'ep4:293797120641': 'em',         # 洛伦兹力冲量
    'ep4:293682010705': 'em',         # 法拉第电磁感应/辐向磁场/磁通量
    'ep4:296283691440': 'em',         # 感生/金属框磁通量/等效电源
    'ep4:293687266449': 'math',       # 无穷悖论/数学极限
    'ep4:293696546257': 'other',      # 小龙老师题(内容在图)
    'ep4:296159687008': 'mech',       # 绳子重块受力/情景区分
    'ep4:296180034240': 'energy',     # 能量分析/传送带物块
    'ep4:296250066192': 'esfield',    # 库仑力/漏电球平衡
    'ep4:293743621793': 'other',      # 一模题(内容在图)
    'ep4:293697033457': 'em',         # 电磁场边界条件(E/D/B/H)
    'ep4:296425219456': 'other',      # "hello"(3图,无文字)
    'ep4:296862340144': 'mech',       # 小球斜面绳约束/几何vs受力
    'ep4:294028157329': 'mech',       # 小球斜面/惯性力/摩擦力
    # ===== 第5期 =====
    'ep5:297426642576': 'mech',       # 车内飞虫/相对运动
    'ep5:294961736641': 'thermal',    # 水滴下滑合并加速(表面张力)
    'ep5:294663087473': 'em',         # 单棒切割电荷分布
    'ep5:294697048305': 'momentum',   # 动能动量得出/功与势能
    'ep5:297586583040': 'energy',     # 时间积累量正放倒放
    'ep5:294499829377': 'momentum',   # 能量问题4连(动量积分/动能)
    'ep5:296930335184': 'energy',     # 动能定理微元累加
    'ep5:297027886528': 'mech',       # 运动学"倒放"
    'ep5:294660588257': 'em',         # 电磁感应动量能量解题
    'ep5:296944032416': 'mech',       # 物块圆盘模型/摩擦力
    'ep5:294437374817': 'energy',     # 共面三体圆周运动
    'ep5:297033728208': 'other',      # "如下"(5图,无文字)
    'ep5:294406913441': 'optics',     # 镜子囚禁光
    'ep5:294398743281': 'em',         # 武汉三调磁场题
    'ep5:295061770545': 'other',      # @KAXINMI(2图,无正文)
    'ep5:297624553184': 'mech',       # 换参考系约束t'>0
    'ep5:296935078912': 'mech',       # 小球斜面绳约束
    'ep5:294454549361': 'em',         # 电磁感应产生热量
    'ep5:296928268704': 'thermal',    # 盘子端菜滑动(热空气空腔)
    'ep5:294401544625': 'thermal',    # 气体压强随高度/横截面积
    'ep5:294556321217': 'em',         # 天津压轴线圈发电时间
    'ep5:294760642561': 'mech',       # 自重弹簧等效质量
    'ep5:294455410465': 'energy',     # 平轨进圆轨临界支持力
    'ep5:294665018305': 'energy',     # 斜抛最小速度/斜交分解
    'ep5:296936028432': 'energy',     # 非匀速圆周切向加速度
    'ep5:294500149745': 'energy',     # 卫星追击相遇
    'ep5:295054425569': 'mech',       # 刚体瞬心
    'ep5:295055835665': 'other',      # 综合力学电学(1图,无文字)
    'ep5:294866253041': 'energy',     # 积分能量守恒求位移
    'ep5:297314439824': 'em',         # 配速法
    'ep5:294395871137': 'mech',       # 蚂蚁高空坠落/空气阻力
    'ep5:297418923168': 'em',         # 电感线圈电流变化率
    # ===== 第6期 =====
    'ep6:295548563809': 'em',         # 自感/感应电流机制
    'ep6:295388978833': 'mech',       # 地心说日心说/参考系
    'ep6:295236420721': 'momentum',   # 动量定理一个方向就够
    'ep6:295502433601': 'em',         # 不等距切割e-t图像
    'ep6:295373395649': 'momentum',   # 牛顿摆碰撞+喷气背包能量
    'ep6:295520792961': 'em',         # 单棒稳态时间无穷
    'ep6:295500888417': 'em',         # 涡流路径选取
    'ep6:298012188880': 'em',         # 磁通量与动量/电荷量
    'ep6:298438114768': 'mech',       # 小球轨道斜面谁定死谁
    'ep6:295166227041': 'em',         # 金属棒+线圈简谐运动
    'ep6:298219613344': 'other',      # 基础公式推导所有题(方法论)
    'ep6:298155100608': 'other',      # "送你们的"(2图,无正文)
    'ep6:297751477152': 'mech',       # 无人机在电梯中飞行
    'ep6:297966550736': 'mech',       # 正放倒放1/2at²
    'ep6:295156176337': 'mech',       # 圆盘模型摩擦力指向圆心
    'ep6:297751912992': 'circuit',    # 内接法测电阻(电学实验)
    'ep6:295522159473': 'mech',       # 两道基础力学题思考
    'ep6:295693443697': 'energy',     # 势能如何准确定义
    'ep6:297711773824': 'mech',       # 汽车摩擦力动力vs阻力
    'ep6:297794106720': 'energy',     # 能量守恒求竖直速度
    'ep6:295145541361': 'vibration',  # 物块平衡位置叠加
    'ep6:295128407457': 'energy',     # 势能/位移积累求时间
    'ep6:295200707921': 'vibration',  # 简谐运动题
    'ep6:295291323169': 'em',         # 无电阻单棒能量去向
    'ep6:295137550465': 'energy',     # 势能定义/力随位移
    'ep6:297755500528': 'mech',       # 电梯钢缆受力
    'ep6:297790224560': 'mech',       # 动力学中m被滥用
    'ep6:295581125281': 'optics',     # 路灯影子明暗
    'ep6:295378401233': 'energy',     # 绳子圆周能量守恒
    'ep6:295384752081': 'em',         # 匀强磁场最小面积
    'ep6:295498545265': 'energy',     # 斜抛斜交分解
    'ep6:295286763825': 'math',       # v=k/x积分过程
    'ep6:297801232576': 'math',       # 蜗牛v=k/x求时间
    # ===== 第7期 =====
    'ep7:299227255280': 'other',      # 自创题目(6图,内容在图)
    'ep7:298814584000': 'mech',       # 力在平动与转动分析
    'ep7:296055727841': 'math',       # 角度/弧度制/量纲/角速度
    'ep7:295941556641': 'em',         # 单杆电容器匀加速
    'ep7:298557694608': 'other',      # 基础公式推导所有题(方法论)
    'ep7:298554392512': 'em',         # 求教(磁聚焦,1图)
    'ep7:295940573457': 'em',         # 阿拉果圆盘涡流
    'ep7:295945987377': 'thermal',    # P-T图割线/切线
    'ep7:298504759312': 'optics',     # 衍射缝宽与波长
    'ep7:295845825745': 'em',         # 单棒切割扫过面积
    'ep7:296037228753': 'momentum',   # 机械能/动量守恒区分
    'ep7:295900709713': 'ac',         # 理想变压器自感电动势
    'ep7:295940137697': 'em',         # 磁通量变化感应电动势
    'ep7:298509582784': 'vibration',  # 弹簧模型简谐运动
    'ep7:295901385361': 'ac',         # 正弦交变电路电压表
    'ep7:296247701809': 'vibration',  # 简谐位移最大处等效
    'ep7:296028783697': 'energy',     # 低轨卫星重力加速度机械能
    'ep7:295846182209': 'em',         # 不等距切割(与ep6重复问)
    'ep7:299058972960': 'energy',     # 角动量+能量守恒椭圆轨道
    'ep7:298875809744': 'em',         # 三角形线圈内阻
    'ep7:296229044401': 'circuit',    # 输出功率内外电阻
    # ===== 第8期 =====
    'ep8:299391478880': 'math',       # 抛硬币期望(概率)
    'ep8:296974866769': 'thermal',    # 气泡压强/大气压
    'ep8:296679779889': 'em',         # 感生电动势能量转换
    'ep8:299438081376': 'em',         # 感生电动势/拓扑线圈
    'ep8:299466242048': 'mech',       # 光滑金属块摩擦(分子引力)
    'ep8:299358114800': 'mech',       # 约束条件把握确定性
    'ep8:296769798385': 'em',         # 带电粒子纯磁场
    'ep8:299292209792': 'mech',       # 摩擦力做功/地面动能
    'ep8:299285556768': 'thermal',    # 气态星球压强随半径
    'ep8:296904535985': 'mech',       # 相似三角形力的平衡
    'ep8:296681036961': 'thermal',    # 饱和汽压与液面弯曲
    'ep8:299563906320': 'nuclear',    # 氢原子能级跃迁/光子
    'ep8:297185153969': 'mech',       # 两杆夹圆环与球
    'ep8:299311663632': 'mech',       # 小船极坐标/速度分解
    'ep8:296764575553': 'thermal',    # 通入气体物质的量
    'ep8:296762034081': 'em',         # 洛伦兹力冲量式/配速法
    'ep8:299353604176': 'energy',     # 半圆轨道恰好脱离
    'ep8:296979647553': 'em',         # 正离子磁场最小速度
    # ===== 第9期 =====
    'ep9:300289679552': 'mech',       # 平均速度与x-t凹凸性
    'ep9:300997163840': 'em',         # 曲边磁场面积/感生动生叠加
    'ep9:300277230112': 'optics',     # 镜子怎么知道书后有火
    'ep9:298155296369': 'math',       # 赤道绳子周长6.28m
    'ep9:298105196817': 'mech',       # 动滑轮加速度2倍
    'ep9:297397350913': 'thermal',    # 压强微分/封闭体系
    'ep9:297577489489': 'em',         # 单棒切割绳子外力
    'ep9:300915447616': 'mech',       # 角速度增大摩擦力减小
    'ep9:300352364096': 'em',         # 含容电路感应电动势
    'ep9:297533804977': 'energy',     # 小球斜坡相对速度
    'ep9:300304774688': 'thermal',    # 高温低温熵增
    'ep9:300323223040': 'mech',       # 弹簧物块分离条件
    'ep9:297469665761': 'math',       # 抛硬币条件概率感想
    'ep9:300639073376': 'em',         # 霍尔效应/反馈电阻
    'ep9:300467207008': 'momentum',   # 6球碰撞次数
    'ep9:297363396833': 'ac',         # 高压输电功率损耗
    'ep9:300142203520': 'other',      # 分享一道题(1图)
    'ep9:300343808448': 'energy',     # 斜面两次斜抛同一落点
    'ep9:297435033313': 'thermal',    # 帕斯卡原理/微小位形
    'ep9:300344701824': 'circuit',    # 两电源并联电路
    'ep9:297431904273': 'other',      # 感谢+定量回答(1图)
    'ep9:300143079984': 'circuit',    # 并联等效电动势
    'ep9:297382156417': 'math',       # 抛硬币问题起心动念
    'ep9:297698265569': 'energy',     # 竖直圆周R可消/量纲
    'ep9:297406700241': 'thermal',    # 理想气体状态方程比例
    'ep9:297341198033': 'thermal',    # 饱和汽压与液面弯曲
    'ep9:297481033873': 'energy',     # 机器狗斜抛障碍
    'ep9:300343644544': 'energy',     # 斜面上斜抛结论
    'ep9:301037586736': 'energy',     # 传送带物块电机做功
    'ep9:300198556880': 'ac',         # 变压器等效电阻求电压
    'ep9:297390055281': 'thermal',    # 打气抽气气体
    'ep9:297402318033': 'esfield',    # 电场力圆周运动/等效重力
    'ep9:300692432208': 'mech',       # 两圆纯滚动轨迹
    'ep9:300127103344': 'em',         # 离子发射器磁场边界
    'ep9:300180941072': 'mech',       # 约束/几何与运动学约束
    'ep9:300155270720': 'optics',     # 折射定律n1sinθ1
    'ep9:297515189265': 'em',         # 电容穿导体棒等效质量
    'ep9:297461988545': 'em',         # 电容导体棒+钓鱼+物理图像
}

# 人工判定为噪音、需额外移除的评论
REMOVE_EXTRA = {
    ('ep1', 291563408369): '纯赞美无内容',
    ('ep4', 296163580304): '视频传错公告(无关)',
    ('ep5', 296935295104): 'UP主点赞提醒(公告)',
    ('ep7', 296420148177): '私信请求(无关)',
    ('ep9', 297469821761): '时间感慨(无关)',
    ('ep9', 300601151392): '"收获很多"(无内容)',
}

# ---------------- 模块定义(含新增的 光学/原子物理, 无内容则不显示) ----------------
MODULES = [
    dict(key='mech',     name='力学基础',          desc='运动学 · 力 · 牛顿运动定律（必修一）',              color='#34495e'),
    dict(key='energy',   name='曲线运动与机械能',   desc='圆周运动 · 抛体 · 机械能（必修二）',                color='#2c6e49'),
    dict(key='momentum', name='动量与能量',        desc='动量定理 · 动量守恒（选择性必修一）',                color='#8d6e63'),
    dict(key='vibration',name='机械振动与机械波',   desc='简谐运动 · 叠加 · 波（选择性必修一）',               color='#4a6fa5'),
    dict(key='optics',   name='光学',              desc='折射 · 干涉 · 衍射 · 全反射（选择性必修一）',         color='#5d6d7e'),
    dict(key='esfield',  name='静电场',            desc='电场 · 电势 · 电势差（必修三）',                      color='#1f6f78'),
    dict(key='circuit',  name='电路与电学实验',    desc='恒定电流 · 闭合电路 · 实验（必修三）',                color='#2874a6'),
    dict(key='em',       name='磁场与电磁感应',    desc='磁场 · 洛伦兹力 · 电磁感应 · 自感（选择性必修二）',   color='#283747'),
    dict(key='ac',       name='交变电流与电磁振荡', desc='交变电流 · 有效值 · LC 振荡（选择性必修二）',         color='#6c3483'),
    dict(key='thermal',  name='热学',              desc='分子动理论 · 气体 · 液体 · 热力学（选择性必修三）',   color='#a04000'),
    dict(key='nuclear',  name='原子与核',          desc='原子结构 · 核反应 · 光电效应（选择性必修三）',        color='#7d6608'),
    dict(key='math',     name='思维方法 · 数学题', desc='非物理：数学思维题（三角函数等，供参考）',             color='#707b7c'),
    dict(key='other',    name='其他 · 待定',      desc='内容在题图中或属学习讨论，未归入具体模块',             color='#6c6c6c'),
]
MODULE_BY_KEY = {m['key']: m for m in MODULES}

# ---------------- 关键词规则分类器 ----------------
RULES = {
    'mech':     ['惯性','牛顿','摩擦','受力分析','受力','弹力','静摩擦','滑动摩擦','加速度','参考系','相对运动',
                 '滑轮','轻绳','轻杆','平衡','矢量','匀变速','自由落体','刹','位移','运动学','平均速度','瞬时速度',
                 '追击','相遇','合力','分力','超重','失重','重心','支持力','绳','拉力'],
    'energy':   ['圆周','向心','抛体','平抛','斜抛','机械能','动能定理','动能','势能','能量守恒','万有引力','卫星',
                 '轨道','角速度','线速度','离心','变力','做功','功率','最高点','最低点','连接体'],
    'momentum': ['动量','冲量','碰撞','反冲','流体','冲击','爆炸','弹性碰撞','动量守恒','质心'],
    'vibration':['简谐','振动','单摆','弹簧振子','周期','振幅','相位','叠加','机械波','波长','波速','驻波','受迫',
                 '共振','回复力','简谐运动'],
    'optics':   ['折射','反射','全反射','干涉','衍射','偏振','透镜','双缝','光程','色散','杨氏','凸透镜','凹透镜','光'],
    'esfield':  ['电场','电势','电荷','库仑','静电力','等势面','静电','点电荷','电场线','电势能','静电场','电容器'],
    'circuit':  ['电路','电源','电动势','欧姆','串反并同','电表','内阻','等效电源','滑动变阻器','电压表','电流表',
                 '短路','断路','焦耳','电功率','伏安','电桥','电学实验'],
    'em':       ['磁场','磁感','洛伦兹','安培','电磁感应','感生','动生','磁通','自感','电感','线圈','楞次','法拉第',
                 '导体棒','磁力','安培力','磁感应强度','通电导线','磁场力','感应电动势'],
    'ac':       ['交变','交流','有效值','变压器','振荡','电磁波','正弦','峰值','瞬时值','无线电','LC'],
    'thermal':  ['热学','温度','内能','分子','气体','沸点','沸腾','饱和汽','毛细','表面张力','热力学','熵','布朗',
                 '理想气体','水银','液面','汽化','液化','分子势能','分子动能','扩散','热量','熔化','凝固','物态'],
    'nuclear':  ['原子','核反应','衰变','光子','光电效应','能级','玻尔','辐射','质能','半衰期','中子','质子','裂变',
                 '聚变','放射性','量子'],
    'math':     ['数学','三角函数','sin','cos','tan','不等式','葛军','数列','导数','几何','代数','方程','函数','概率','恒等式'],
}
RULE_SCORE = {k: len(v) for k, v in RULES.items()}


def classify_auto(texts):
    """texts: [str,...] 第一条为楼主正文(权重x3)，其余为回复(权重x1)"""
    root = texts[0].lower() if texts else ''
    replies = ' '.join(texts[1:]).lower()
    best, best_score = 'other', 0
    for mod, kws in RULES.items():
        s = 3 * sum(root.count(k) for k in kws) + sum(replies.count(k) for k in kws)
        if s > best_score:
            best, best_score = mod, s
    return best

# ---------------- 噪音过滤 ----------------
EXACT_NOISE = {'前排', '前排前排', '第一', '第二', '第三', '第四', '第五', '沙发', '板凳',
               '占楼', '打卡', '路过', '顶', '666', '牛', '沙发', '第一！', '第一[doge]'}
SUBSTR_NOISE = ['占楼', '前排', '三连', '硬币', '膜拜', '已三连', '哈哈哈', '哈哈', '收藏了',
                '支持一下', '关注了', '围观', '已阅', '前来', '吃瓜看戏', '蹲一个']
NOISE_PHRASES = ['服务器', '备案', '播放量', '封面', 'up主', 'UP主', '老师辛苦了', '感谢分享',
                 '谢谢老师', '老师讲得', '辛苦了', '催更', '关注up', '一键三连']


def is_noise(msg):
    m = msg.strip()
    if not m:
        return True
    ml = m.lower()
    for p in NOISE_PHRASES:
        if p in ml:
            return True
    if m in EXACT_NOISE:
        return True
    if len(m) <= 14:
        for k in SUBSTR_NOISE:
            if k in m:
                return True
    return False

# ---------------- 文本格式化 ----------------
EMOJI = {
    '[doge]': '🐶', '[doge_金箍]': '🐶', '[脱单doge]': '🐶', '[滑稽]': '😏',
    '[吃瓜]': '🍉', '[笑哭]': '😂', '[喜极而泣]': '😭', '[藏狐]': '🦊',
    '[打call]': '🙌', '[星星眼]': '🤩', '[脸红]': '😳', '[嗑瓜子]': '🥜',
    '[大哭]': '😭', '[蹲蹲]': '🧘', '[思考]': '🤔', '[抠鼻]': '😏',
    '[妙啊]': '🤙', '[tv_点赞]': '👍', '[委屈]': '🥺', '[微笑]': '🙂',
    '[呲牙]': '😁', '[惊讶]': '😲', '[偷笑]': '🤭', '[捂脸]': '🤦', '[OK]': '👌',
    '[脱单]': '💑', '[害羞]': '😊', '[点赞]': '👍', '[喜欢]': '❤️', '[击掌]': '🤝',
}
URL_RE = re.compile(r'https?://[^\s]+')
MENTION_RE = re.compile(r'^\s*回复\s*@([^:：]+?)\s*[:：]')


def fmt_message(msg):
    s = html.escape(msg, quote=False)
    mention = None
    m = MENTION_RE.match(msg)
    if m:
        mention = m.group(1).strip()
        rest = re.sub(r'^\s*[:：]+\s*', '', msg[m.end():])
        s = html.escape(rest, quote=False)
    s = re.sub(r'(回复\s*@[^:：]+?[:：])', r'<span class="mention">\1</span>', s)
    s = URL_RE.sub(lambda mm: f'<a href="{mm.group(0)}" target="_blank" rel="noopener">{mm.group(0)}</a>', s)
    for k, v in EMOJI.items():
        s = s.replace(k, v)
    if mention:
        s = f'<span class="mention">回复 @{html.escape(mention)}</span>' + ((' ' + s) if s else '')
    return s


def fmt(msg):
    """公式转 LaTeX + 提及高亮 + emoji 替换"""
    esc, mention = formula_html(msg)
    # 嵌套 "回复 @xxx :" 高亮
    esc = re.sub(r'(回复\s*@[^:：\s]{1,30}?\s*[:：])', r'<span class="mention">\1</span>', esc)
    for k, v in EMOJI.items():
        esc = esc.replace(k, v)
    if mention:
        esc = '<span class="mention">回复 @' + html.escape(mention) + '</span> ' + esc
    return esc


def load_manifest():
    mp = os.path.join(IMGDIR, 'manifest.json')
    if os.path.exists(mp):
        with open(mp, encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_face_manifest():
    mp = os.path.join(IMGDIR, 'face_manifest.json')
    if os.path.exists(mp):
        with open(mp, encoding='utf-8') as f:
            return json.load(f)
    return {}


def local_src(url, manifest):
    fn = manifest.get(url)
    return ('_imgs/' + fn) if fn else url


def face_src(url, face_manifest):
    fn = face_manifest.get(url)
    return ('_imgs/' + fn) if fn else url

# ---------------- 单期处理 ----------------
def build_episode(ep_key, ep_title, path, manifest, face_manifest, is_ep10=False):
    with open(path, encoding='utf-8') as f:
        raw = json.load(f)
    entries = raw['data']
    excluded = set(raw.get('excludedRpids') or [])

    # 重建评论树
    roots = {}
    for x in entries:
        if x.get('message', '').strip():
            roots[x['rpid']] = x
    replies_map, seen = {}, set()
    ghost_merged = 0
    for x in entries:
        for r in (x.get('replyToOthersDetails') or []):
            key = (r.get('uid'), r['message'])
            if key in seen:
                continue
            seen.add(key)
            rr = r.get('rootRpid')
            if rr is None:
                continue
            replies_map.setdefault(rr, []).append(dict(
                uname=x['uname'], face=face_src(x['face'], face_manifest),
                like=r.get('adjustedLike', 0) or 0,
                message=fmt(r['message']),
            ))
            if not x.get('message', '').strip():
                ghost_merged += 1

    kept, removed, auto_cnt = [], [], 0
    for rpid, entry in roots.items():
        if (ep_key, rpid) in REMOVE_EXTRA:
            removed.append((entry['uname'], entry['message'][:36], '人工判定噪音'))
            continue
        if rpid in excluded:
            removed.append((entry['uname'], entry['message'][:36], '归档时已排除'))
            continue
        if is_noise(entry['message']):
            removed.append((entry['uname'], entry['message'][:36], '占楼/闲聊'))
            continue
        # 分类：优先人工逐条判定，找不到才退回关键词自动(标注auto)
        manual = EP10_MANUAL if is_ep10 else MANUAL_MAP
        mod = manual.get(f'{ep_key}:{rpid}', manual.get(rpid, None))
        if mod is None:
            texts = [entry['message']] + [r['message'] for r in replies_map.get(rpid, [])]
            mod = classify_auto(texts)
            auto_cnt += 1
            auto = True
        else:
            auto = False
        reps = replies_map.get(rpid, [])
        reps.sort(key=lambda r: r['like'], reverse=True)
        cid = f'{ep_key}:{rpid}'
        kept.append(dict(
            id=cid, module=mod, auto=auto,
            uname=entry['uname'], face=face_src(entry['face'], face_manifest),
            like=entry.get('rootLikeCount', 0) or 0,
            message=fmt(entry['message']),
            raw_message=entry['message'],
            images=[local_src(u, manifest) for u in (entry.get('images') or [])],
            replies=[dict(r, id=f'{cid}:r{i}') for i, r in enumerate(reps)],
        ))
    kept.sort(key=lambda c: c['like'], reverse=True)
    order = {m['key']: i for i, m in enumerate(MODULES)}
    kept.sort(key=lambda c: (order[c['module']], -c['like']))
    mod_stats = {}
    for c in kept:
        st = mod_stats.setdefault(c['module'], {'q': 0, 'r': 0, 'img': 0})
        st['q'] += 1; st['r'] += len(c['replies']); st['img'] += len(c['images'])
    return dict(
        key=ep_key, title=ep_title, episodeId=raw.get('episodeId', ''),
        export=raw.get('exportTime', '')[:10], comments=kept,
        mod_stats=mod_stats, removed=removed, ghost_merged=ghost_merged,
        total_q=len(kept), total_r=sum(len(c['replies']) for c in kept),
        total_img=sum(len(c['images']) for c in kept), auto_cnt=auto_cnt,
    )

# ---------------- 主流程 ----------------
manifest = load_manifest()
face_manifest = load_face_manifest()
print(f'manifest 图片映射数: {len(manifest)} | 头像映射数: {len(face_manifest)}')
episodes = [build_episode(k, t, p, manifest, face_manifest, is_ep10=(k == 'ep10')) for k, t, p in EPISODES]

payload = dict(
    modules=MODULES,
    episodes=episodes,
    total_q=sum(e['total_q'] for e in episodes),
    total_r=sum(e['total_r'] for e in episodes),
    total_img=sum(e['total_img'] for e in episodes),
    missing_ep4=True,
)
json_str = json.dumps(payload, ensure_ascii=False).replace('</', '<\\/')

for e in episodes:
    dist = {m['key']: e['mod_stats'].get(m['key'], {}).get('q', 0) for m in MODULES}
    dist = {k: v for k, v in dist.items() if v}
    print(f"{e['title']}: {e['total_q']}问/{e['total_r']}回复/{e['total_img']}图 | 自动分类{e['auto_cnt']} | 分布 {dist}")

# ================= HTML 模板 =================
HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>物理系咕咕叫兽 · 好题分享评论区物理题集（第1-10期）</title>
<style>
:root{--bg:#f5f6f7;--card:#fff;--line:#d8dce1;--txt:#1a1f24;--sub:#6b7480;--accent:#1f4e79;--accent2:#2e6da4;--nav-w:236px}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:"Songti SC","Noto Serif SC","STSong","SimSun",Georgia,"Times New Roman",serif;background:var(--bg);color:var(--txt);font-size:15px;line-height:1.75}
a{color:#1a5276;text-decoration:none}a:hover{text-decoration:underline}

.layout{display:flex;min-height:100vh}
.sidebar{width:var(--nav-w);flex:none;position:sticky;top:0;height:100vh;overflow-y:auto;background:#fff;border-right:1px solid var(--line);padding:18px 14px;z-index:30}
.brand{display:flex;align-items:center;gap:10px;padding:4px 6px 14px}
.brand .logo{width:34px;height:34px;border-radius:4px;background:#1f4e79;display:flex;align-items:center;justify-content:center;color:#fff;font-size:17px;font-weight:700;font-family:Georgia,serif}
.brand .t1{font-size:14.5px;font-weight:700;line-height:1.3}
.brand .t2{font-size:11px;color:var(--sub)}
.nav-label{font-size:11px;color:var(--sub);margin:10px 8px 6px;letter-spacing:1px}
.nav a{display:flex;align-items:center;gap:9px;padding:7px 9px;border-radius:8px;color:var(--txt);font-size:13.5px;transition:.15s;cursor:pointer}
.nav a:hover{background:#f4f5f7}
.nav a.active{background:#e8eef5;color:var(--accent2);font-weight:600}
.nav a .dot{width:9px;height:9px;border-radius:50%;flex:none}
.nav a .cnt{margin-left:auto;font-size:11.5px;color:var(--sub);background:#f1f2f5;border-radius:10px;padding:0 7px}
.nav a.active .cnt{background:#d6e4f0;color:var(--accent2)}
.side-foot{margin-top:18px;padding:12px 8px;border-top:1px solid var(--line);font-size:11px;color:var(--sub)}

.main{flex:1;min-width:0;max-width:1080px;margin:0 auto;padding:0 28px 60px}

/* 期数 Tab 栏 */
.tabs{position:sticky;top:0;z-index:40;background:rgba(255,255,255,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);margin:0 -28px;padding:10px 28px;display:flex;gap:6px;overflow-x:auto;flex-wrap:nowrap}
.tab{flex:none;padding:7px 15px;border-radius:20px;font-size:13px;cursor:pointer;color:var(--txt);border:1px solid var(--line);background:#fff;transition:.15s;white-space:nowrap}
.tab:hover{border-color:var(--accent)}
.tab.active{background:var(--accent);border-color:var(--accent);color:#fff;font-weight:600}
.tab .n{font-size:11px;opacity:.75;margin-left:3px}

.hero{padding:26px 0 4px}
.hero h1{font-size:24px;font-weight:700;letter-spacing:.5px}
.hero h1 .ep{color:var(--accent2)}
.hero .sub{color:var(--sub);margin-top:6px;font-size:13px}
.stats{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}
.stat{background:#fff;border:1px solid var(--line);border-radius:10px;padding:9px 16px;min-width:96px}
.stat b{font-size:19px;display:block}
.stat span{font-size:11.5px;color:var(--sub)}
.searchbox{margin-top:16px;position:relative;max-width:480px}
.searchbox input{width:100%;padding:10px 14px 10px 38px;border:1px solid var(--line);border-radius:10px;background:#fff;font-size:14px;outline:none;transition:.15s}
.searchbox input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(31,78,121,.12)}
.searchbox .ico{position:absolute;left:13px;top:50%;transform:translateY(-50%);color:var(--sub);font-size:15px}
#searchHint{font-size:12px;color:var(--sub);margin-top:6px}

/* 期横幅(全部模式) */
.ep-banner{display:flex;align-items:center;gap:12px;margin:30px 0 2px;padding:12px 18px;background:#fff;border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:4px;scroll-margin-top:70px}
.ep-banner .badge{background:var(--accent);color:#fff;font-weight:700;border-radius:8px;padding:3px 12px;font-size:14px}
.ep-banner .meta{color:var(--sub);font-size:12px}

.section{margin-top:30px;scroll-margin-top:70px}
.sec-head{display:flex;align-items:center;gap:10px;margin-bottom:6px;padding:9px 14px;border-left:4px solid var(--sec-color,#1f4e79);background:#fff;border-radius:0 4px 4px 0;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.sec-head .dot{width:11px;height:11px;border-radius:2px;flex:none}
.sec-head h2{font-size:16px;font-weight:700}
.sec-head .badge{font-size:11.5px;color:var(--sub);background:#f4f6f8;border:1px solid var(--line);border-radius:10px;padding:1px 9px}
.sec-desc{color:var(--sub);font-size:12.5px;margin:0 0 12px 14px}
.ep-subhead{display:flex;align-items:center;gap:8px;margin:14px 0 8px;padding:5px 12px;background:#eef3f8;border-left:3px solid var(--accent2);border-radius:0 3px 3px 0;font-size:13px}
.ep-subhead .epn{font-weight:700;color:var(--accent)}
.ep-subhead .c{font-size:11.5px;color:var(--sub)}

.c-card{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--card-accent,#cbd2d9);border-radius:5px;padding:16px 18px;margin-bottom:14px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.c-top{display:flex;align-items:center;gap:10px}
.avatar{width:38px;height:38px;border-radius:50%;background:#e8eaf0;border:2px solid var(--avatar-accent,#cbd2d9);flex:none;overflow:hidden;display:flex;align-items:center;justify-content:center;color:#6b7076;font-weight:600}
.avatar img{width:100%;height:100%;object-fit:cover;display:block}
.uname{font-weight:600;font-size:13.5px}
.tag{font-size:10.5px;color:var(--accent2);border:1px solid #b8c9dc;background:#eef3f8;border-radius:4px;padding:0 5px;margin-left:6px;flex:none}
.like{margin-left:auto;display:flex;align-items:center;gap:4px;color:var(--sub);font-size:12.5px;flex:none}
.like .h{color:#2e6da4;font-size:13px}
.c-msg{margin:10px 2px 0;font-size:14px;white-space:pre-wrap;word-break:break-word}
.c-msg .mention{color:#61666d}
.c-msg a{word-break:break-all}
.c-msg.long .full{display:none}
.math{background:rgba(46,109,164,.09);padding:1px 4px;border-radius:3px;margin:0 1px}
.morebtn{display:inline-block;margin-top:4px;color:#1a5276;font-size:12.5px;cursor:pointer;white-space:nowrap}
.img-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px;margin-top:12px}
.img-grid img{width:100%;height:150px;object-fit:cover;border-radius:6px;cursor:zoom-in;background:#f4f5f7;border:1px solid var(--line);transition:.15s}
.img-grid img:hover{transform:scale(1.02);box-shadow:0 3px 10px rgba(0,0,0,.12)}
.img-grid.one img{height:auto;max-height:420px;object-fit:contain}
.img-miss{grid-column:1/-1;font-size:12px;color:#b8bcc2;background:#f8f9fb;border:1px dashed var(--line);border-radius:6px;padding:10px;text-align:center}

.replies{margin-top:14px;border-top:1px solid var(--line);border-left:3px solid #e2e6ea;background:#fafbfc;padding:6px 12px 8px;border-radius:0 4px 4px 0}
.replies-head{font-size:12px;color:var(--sub);margin:4px 0 8px;display:flex;align-items:center;gap:6px}
.replies-head .count{font-weight:600;color:#2e6da4}
.r-item{display:flex;gap:9px;padding:9px 8px;border-radius:6px}
.r-item:hover{background:#f1f3f5}
.r-item .avatar{width:30px;height:30px;border:1.5px solid #cbd2d9}
.r-box{flex:1;min-width:0}
.r-top{display:flex;align-items:center;gap:6px}
.r-top .uname{font-size:12.5px}
.r-like{margin-left:auto;font-size:11.5px;color:var(--sub);flex:none}
.r-like .h{color:#2e6da4}
.r-msg{margin-top:3px;font-size:13px;white-space:pre-wrap;word-break:break-word}
.r-msg .mention{color:#61666d}
.r-msg.long .full{display:none}

#empty{display:none;text-align:center;color:var(--sub);padding:70px 0;font-size:15px}
.report{margin-top:44px;background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 20px}
.report summary{cursor:pointer;font-size:14.5px;font-weight:600;outline:none}
.report summary::marker{color:var(--accent)}
.report ul{margin:12px 0 0 20px;font-size:12.8px;color:#5b6066}
.report li{margin-bottom:4px}
.report .why{color:#2e6da4}

.lightbox{position:fixed;inset:0;background:rgba(0,0,0,.9);display:none;align-items:center;justify-content:center;z-index:100;flex-direction:column;padding:30px;overflow:hidden}
.lightbox.open{display:flex}
.lb-stage{position:relative;width:100%;height:100%;display:flex;align-items:center;justify-content:center;overflow:hidden;cursor:grab}
.lb-stage.grabbing{cursor:grabbing}
.lb-stage img{max-width:92vw;max-height:82vh;border-radius:6px;box-shadow:0 8px 40px rgba(0,0,0,.5);transform-origin:center center;user-select:none;-webkit-user-drag:none}
.lb-info{color:#ccc;font-size:13px;margin-top:10px}
.lb-toolbar{position:absolute;bottom:18px;left:50%;transform:translateX(-50%);display:flex;gap:8px;background:rgba(30,30,30,.75);border-radius:22px;padding:8px 14px;backdrop-filter:blur(6px)}
.lb-toolbar button{background:transparent;border:none;color:#fff;font-size:16px;width:34px;height:34px;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center}
.lb-toolbar button:hover{background:rgba(255,255,255,.18)}
.lb-nav{position:absolute;top:50%;transform:translateY(-50%);width:46px;height:60px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:30px;cursor:pointer;background:rgba(255,255,255,.08);border-radius:10px;user-select:none;z-index:2}
.lb-nav:hover{background:rgba(255,255,255,.2)}
.lb-nav.prev{left:22px}.lb-nav.next{right:22px}
.lb-close{position:absolute;top:16px;right:24px;color:#fff;font-size:30px;cursor:pointer;width:44px;height:44px;display:flex;align-items:center;justify-content:center;border-radius:50%;background:rgba(255,255,255,.1);z-index:2}
.lb-close:hover{background:rgba(255,255,255,.25)}
.lb-orig{margin-top:6px;font-size:12px;color:#999}

/* 卡片操作按钮 */
.c-actions{display:flex;gap:6px;flex:none}
.c-btn{font-size:12px;color:var(--sub);background:#f4f5f7;border:1px solid var(--line);border-radius:8px;padding:2px 8px;cursor:pointer;transition:.15s;white-space:nowrap}
.c-btn:hover{border-color:var(--accent);color:var(--accent2)}
.c-btn.faved{color:#a08000;border-color:#a08000;background:#fbf7ec}
.c-btn.seen{color:var(--sub);opacity:.5}

/* 顶栏功能按钮 */
.toolbar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:14px}
.toolbar .tbtn{font-size:13px;color:var(--txt);background:#fff;border:1px solid var(--line);border-radius:10px;padding:7px 14px;cursor:pointer;transition:.15s}
.toolbar .tbtn:hover{border-color:var(--accent);color:var(--accent2)}
.toolbar .tbtn.on{background:#e8eef5;border-color:var(--accent);color:var(--accent2);font-weight:600}

/* 已阅历史 modal */
.modal-mask{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:120;display:none;align-items:center;justify-content:center;padding:24px}
.modal-mask.open{display:flex}
.modal{background:#fff;border-radius:14px;max-width:640px;width:100%;max-height:80vh;display:flex;flex-direction:column;box-shadow:0 12px 50px rgba(0,0,0,.25)}
.modal-head{display:flex;align-items:center;justify-content:space-between;padding:16px 20px;border-bottom:1px solid var(--line)}
.modal-head b{font-size:15px}
.modal-close{cursor:pointer;font-size:22px;color:var(--sub)}
.modal-body{overflow-y:auto;padding:12px 20px;flex:1}
.seen-item{display:flex;align-items:center;gap:10px;padding:10px 6px;border-bottom:1px solid #f2f3f5}
.seen-item .t{flex:1;min-width:0;font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.seen-item .ep{font-size:11px;color:var(--sub);flex:none}
.seen-item button{font-size:12px;color:#1a5276;background:none;border:none;cursor:pointer;flex:none}
.modal-empty{color:var(--sub);text-align:center;padding:40px 0;font-size:13px}
.katex{font-size:1.02em}

@media (max-width:900px){
  .layout{display:block}
  .sidebar{position:static;width:100%;height:auto;border-right:none;border-bottom:1px solid var(--line)}
  .nav{display:flex;flex-wrap:wrap;gap:4px}
  .nav a{font-size:12.5px;padding:5px 8px}
  .nav a .cnt{display:none}
  .main{padding:0 14px 50px}
  .tabs{margin:0 -14px;padding:8px 14px}
  .img-grid{grid-template-columns:repeat(auto-fill,minmax(120px,1fr))}
}
</style>
<link rel="stylesheet" href="assets/katex/katex.min.css">
</head>
<body>
<div class="layout">
  <aside class="sidebar">
    <div class="brand">
      <div class="logo">Φ</div>
      <div><div class="t1">评论区物理题集</div><div class="t2">第1-10期 · 物理系咕咕叫兽</div></div>
    </div>
    <div class="nav-label" id="navLabel">物理模块</div>
    <nav class="nav" id="nav"></nav>
    <div class="side-foot" id="sideFoot"></div>
  </aside>

  <main class="main">
    <div class="tabs" id="tabs"></div>
    <header class="hero">
      <h1><span class="ep" id="epName"></span> 评论区物理题集</h1>
      <div class="sub" id="heroSub"></div>
      <div class="stats" id="statsRow"></div>
      <div class="toolbar">
        <button class="tbtn on" id="viewEp">按【期数】</button>
        <button class="tbtn" id="viewMod">按【知识点】</button>
        <span style="width:1px;height:18px;background:var(--line)"></span>
        <button class="tbtn" id="favToggle">★ 收藏夹 <span id="favCount">0</span></button>
        <button class="tbtn" id="seenToggle">☑ 已阅历史 <span id="seenCount">0</span></button>
        <span style="font-size:12px;color:var(--sub)">卡片左侧色条=知识点，色环=楼主；公式淡蓝底。</span>
      </div>
      <div class="searchbox">
        <span class="ico">⌕</span>
        <input id="search" type="text" placeholder="搜索当前期的问题关键词，如：惯性、电磁感应、有效值…">
      </div>
      <div id="searchHint"></div>
    </header>

    <div id="sections"></div>
    <div id="empty">没有匹配的结果，换个关键词试试～</div>

    <details class="report">
      <summary id="reportSummary">过滤说明</summary>
      <ul id="reportList"></ul>
    </details>
    <div style="height:30px"></div>
  </main>
</div>

<div class="lightbox" id="lightbox">
  <div class="lb-close" id="lbClose">×</div>
  <div class="lb-nav prev" id="lbPrev">‹</div>
  <div class="lb-stage" id="lbStage"><img id="lbImg" src="" alt=""></div>
  <div class="lb-toolbar" id="lbToolbar">
    <button id="lbZoomIn" title="放大">＋</button>
    <button id="lbZoomOut" title="缩小">－</button>
    <button id="lbReset" title="重置">1:1</button>
    <button id="lbRotL" title="逆时针旋转">⟲</button>
    <button id="lbRotR" title="顺时针旋转">⟳</button>
    <button id="lbDl" title="下载原图">⭳</button>
  </div>
  <div class="lb-info" id="lbInfo"></div>
  <a class="lb-orig" id="lbOrig" target="_blank" rel="noopener">在新窗口查看原图 ↗</a>
  <div class="lb-nav next" id="lbNext">›</div>
</div>

<div class="modal-mask" id="modalMask">
  <div class="modal">
    <div class="modal-head"><b id="modalTitle">已阅历史</b><span class="modal-close" id="modalClose">×</span></div>
    <div class="modal-body" id="modalBody"></div>
  </div>
</div>

<script src="assets/katex/katex.min.js"></script>
<script src="assets/katex/contrib/auto-render.min.js"></script>
<script>
const DATA = __DATA__;
let viewMode = 'episode';  // 'episode' 按期数 | 'module' 按知识点
let currentEp = 'all';
let currentMod = 'all';
let lbList = [], lbIdx = 0;
let lbScale = 1, lbRot = 0, lbTx = 0, lbTy = 0;

/* ---------- localStorage: 收藏 / 已阅 ---------- */
const LS_FAV = 'wb_phys_fav', LS_SEEN = 'wb_phys_seen';
function getLS(k){ try { return JSON.parse(localStorage.getItem(k)) || []; } catch(e){ return []; } }
function setLS(k, v){ localStorage.setItem(k, JSON.stringify(v)); }
let favIds = getLS(LS_FAV), seenIds = getLS(LS_SEEN);

/* ---------- Tab（随视图切换：期数 or 知识点） ---------- */
const tabsEl = document.getElementById('tabs');
function buildTabs() {
  tabsEl.innerHTML = '';
  const mk = (key, label, activeKey) => {
    const d = document.createElement('div');
    d.className = 'tab' + (activeKey === key ? ' active' : '');
    d.innerHTML = label;
    d.onclick = () => {
      if (viewMode === 'episode') currentEp = key; else currentMod = key;
      buildTabs(); render();
    };
    tabsEl.appendChild(d);
  };
  if (viewMode === 'episode') {
    const allQ = DATA.total_q;
    mk('all', '全部期数 <span class="n">' + allQ + '问</span>', currentEp);
    DATA.episodes.forEach(e => mk(e.key, e.title + ' <span class="n">' + e.total_q + '问</span>', currentEp));
  } else {
    mk('all', '全部知识点 <span class="n">' + DATA.total_q + '问</span>', currentMod);
    DATA.modules.forEach(m => {
      const cnt = DATA.episodes.reduce((s, e) => s + e.comments.filter(c => c.module === m.key).length, 0);
      if (cnt > 0) mk(m.key, m.name + ' <span class="n">' + cnt + '问</span>', currentMod);
    });
  }
}

/* ---------- 渲染 ---------- */
const sectionsEl = document.getElementById('sections');
const navEl = document.getElementById('nav');
const statsRow = document.getElementById('statsRow');
const navLabel = document.getElementById('navLabel');

function makeMsg(wrap, text, isReply) {
  wrap.className = isReply ? 'r-msg' : 'c-msg';
  const full = document.createElement('span');
  full.className = 'full';
  full.innerHTML = text;
  wrap.appendChild(full);
  if (wrap.textContent.length > 420) {
    wrap.classList.add('long');
    const btn = document.createElement('span');
    btn.className = 'morebtn';
    btn.textContent = '展开全文 ▾';
    btn.onclick = () => {
      wrap.classList.toggle('long');
      btn.textContent = wrap.classList.contains('long') ? '展开全文 ▾' : '收起 ▴';
    };
    wrap.appendChild(btn);
  }
}

function renderCommentCard(c, modColor) {
  const card = document.createElement('div');
  card.className = 'c-card';
  card.style.setProperty('--card-accent', modColor);
  card.style.setProperty('--avatar-accent', modColor);
  card.dataset.key = (c.uname + ' ' + c.raw_message).toLowerCase();
  card.dataset.id = c.id;
  const top = document.createElement('div');
  top.className = 'c-top';
  const av = document.createElement('div');
  av.className = 'avatar';
  if (c.face) {
    const img = document.createElement('img');
    img.src = c.face; img.loading = 'lazy';
    img.onerror = () => { av.textContent = c.uname[0] || '?'; };
    av.appendChild(img);
  } else av.textContent = c.uname[0] || '?';
  top.appendChild(av);
  const un = document.createElement('div');
  un.innerHTML = `<div class="uname">${c.uname}</div>`;
  if (c.auto) { const t = document.createElement('span'); t.className = 'tag'; t.textContent = '自动分类'; un.appendChild(t); }
  top.appendChild(un);
  const like = document.createElement('div');
  like.className = 'like';
  like.innerHTML = `<span class="h">♥</span>${c.like}`;
  top.appendChild(like);
  // 收藏/已阅按钮
  const act = document.createElement('div');
  act.className = 'c-actions';
  const favBtn = document.createElement('span');
  favBtn.className = 'c-btn' + (favIds.includes(c.id) ? ' faved' : '');
  favBtn.textContent = favIds.includes(c.id) ? '★ 已收藏' : '☆ 收藏';
  favBtn.onclick = (e) => { e.stopPropagation(); toggleFav(c.id); };
  const seenBtn = document.createElement('span');
  seenBtn.className = 'c-btn';
  seenBtn.textContent = '☑ 已阅';
  seenBtn.onclick = (e) => { e.stopPropagation(); markSeen(c.id); };
  act.appendChild(favBtn); act.appendChild(seenBtn);
  top.appendChild(act);
  card.appendChild(top);
  const msg = document.createElement('div');
  makeMsg(msg, c.message, false);
  card.appendChild(msg);
  if (c.images.length) {
    const grid = document.createElement('div');
    grid.className = 'img-grid' + (c.images.length === 1 ? ' one' : '');
    c.images.forEach((u, i) => {
      if (/^_imgs\//.test(u)) {
        const im = document.createElement('img');
        im.src = u; im.loading = 'lazy'; im.alt = '题图 ' + (i + 1);
        im.onerror = () => { im.style.display = 'none'; };
        im.onclick = () => openLightbox(c.images, i);
        grid.appendChild(im);
      } else {
        const miss = document.createElement('div');
        miss.className = 'img-miss';
        miss.textContent = '⚠ 题图未能下载到本地（' + (i + 1) + '）';
        grid.appendChild(miss);
      }
    });
    card.appendChild(grid);
  }
  if (c.replies.length) {
    const rw = document.createElement('div');
    rw.className = 'replies';
    const rh = document.createElement('div');
    rh.className = 'replies-head';
    rh.innerHTML = `<span class="count">${c.replies.length}</span> 条回复`;
    rw.appendChild(rh);
    c.replies.forEach(r => {
      const item = document.createElement('div');
      item.className = 'r-item';
      item.dataset.key = (r.uname + ' ' + r.message.replace(/<[^>]+>/g, '')).toLowerCase();
      const rav = document.createElement('div');
      rav.className = 'avatar';
      if (r.face) {
        const img = document.createElement('img');
        img.src = r.face; img.loading = 'lazy'; img.referrerPolicy = 'no-referrer';
        img.onerror = () => { rav.textContent = r.uname[0] || '?'; };
        rav.appendChild(img);
      } else rav.textContent = r.uname[0] || '?';
      item.appendChild(rav);
      const box = document.createElement('div');
      box.className = 'r-box';
      const rtop = document.createElement('div');
      rtop.className = 'r-top';
      rtop.innerHTML = `<div class="uname">${r.uname}</div><div class="r-like"><span class="h">♥</span>${r.like}</div>`;
      box.appendChild(rtop);
      const rmsg = document.createElement('div');
      makeMsg(rmsg, r.message, true);
      box.appendChild(rmsg);
      item.appendChild(box);
      rw.appendChild(item);
    });
    card.appendChild(rw);
  }
  return card;
}

function renderModuleSection(epKey, mod, cs, isAll) {
  const sec = document.createElement('section');
  sec.className = 'section';
  sec.id = (isAll ? epKey + '-' : '') + mod.key;
  sec.style.setProperty('--sec-color', mod.color);
  const nReply = cs.reduce((s, c) => s + c.replies.length, 0);
  const nImg = cs.reduce((s, c) => s + c.images.length, 0);
  const head = document.createElement('div');
  head.className = 'sec-head';
  head.innerHTML = `<span class="dot" style="background:${mod.color}"></span><h2>${mod.name}</h2>
    <span class="badge">${cs.length} 问 · ${nReply} 回复${nImg ? ' · ' + nImg + ' 图' : ''}</span>`;
  sec.appendChild(head);
  const desc = document.createElement('div');
  desc.className = 'sec-desc';
  desc.textContent = mod.desc;
  sec.appendChild(desc);
  cs.forEach(c => sec.appendChild(renderCommentCard(c, mod.color)));
  return sec;
}

let favOnly = false;
function visComments(e) {
  return e.comments.filter(c => !seenIds.includes(c.id) && (!favOnly || favIds.includes(c.id)));
}

function render() {
  sectionsEl.innerHTML = '';
  navEl.innerHTML = '';
  statsRow.innerHTML = '';
  document.getElementById('search').value = '';
  document.getElementById('searchHint').textContent = '';

  let tq = 0, tr = 0, ti = 0;

  if (viewMode === 'episode') {
    const isAll = currentEp === 'all';
    const eps = isAll ? DATA.episodes : DATA.episodes.filter(e => e.key === currentEp);
    if (isAll) {
      navLabel.textContent = '期数导航';
      eps.forEach(e => {
        const vc = visComments(e);
        const a = document.createElement('a');
        a.href = '#ep-' + e.key;
        a.innerHTML = `<span class="dot" style="background:var(--accent)"></span>${e.title}<span class="cnt">${vc.length}</span>`;
        a.dataset.target = 'ep-' + e.key;
        navEl.appendChild(a);
        const banner = document.createElement('div');
        banner.className = 'ep-banner';
        banner.id = 'ep-' + e.key;
        banner.innerHTML = `<span class="badge">${e.title}</span>
          <span class="meta">${e.episodeId} · 导出 ${e.export} · ${vc.length} 问 / ${vc.reduce((s,c)=>s+c.replies.length,0)} 回复 / ${vc.reduce((s,c)=>s+c.images.length,0)} 图</span>`;
        sectionsEl.appendChild(banner);
        DATA.modules.forEach(mod => {
          const cs = vc.filter(c => c.module === mod.key);
          if (!cs.length) return;
          sectionsEl.appendChild(renderModuleSection(e.key, mod, cs, true));
        });
        tq += vc.length; tr += vc.reduce((s,c)=>s+c.replies.length,0); ti += vc.reduce((s,c)=>s+c.images.length,0);
      });
    } else {
      navLabel.textContent = '知识点模块';
      const e = eps[0];
      const vc = visComments(e);
      DATA.modules.forEach(mod => {
        const cs = vc.filter(c => c.module === mod.key);
        if (!cs.length) return;
        const a = document.createElement('a');
        a.href = '#' + mod.key;
        a.innerHTML = `<span class="dot" style="background:${mod.color}"></span>${mod.name}<span class="cnt">${cs.length}</span>`;
        a.dataset.target = mod.key;
        navEl.appendChild(a);
        sectionsEl.appendChild(renderModuleSection(e.key, mod, cs, false));
      });
      tq = vc.length; tr = vc.reduce((s,c)=>s+c.replies.length,0); ti = vc.reduce((s,c)=>s+c.images.length,0);
    }
    document.getElementById('epName').textContent = isAll ? '第1-10期' : eps[0].title;
    document.getElementById('heroSub').textContent = isAll
      ? `全部期数合集 · 支持按【期数】或按【知识点】双维度浏览`
      : `${eps[0].episodeId} · 导出 ${eps[0].export}`;
  } else {
    // 按知识点视图（跨期聚合）
    navLabel.textContent = '知识点导航';
    const mods = DATA.modules.filter(m => {
      if (currentMod !== 'all') return m.key === currentMod;
      return DATA.episodes.some(e => visComments(e).some(c => c.module === m.key));
    });
    mods.forEach(mod => {
      const entries = [];
      DATA.episodes.forEach(e => {
        visComments(e).forEach(c => { if (c.module === mod.key) entries.push({ ep: e, c }); });
      });
      if (!entries.length) return;
      const a = document.createElement('a');
      a.href = '#' + mod.key;
      a.innerHTML = `<span class="dot" style="background:${mod.color}"></span>${mod.name}<span class="cnt">${entries.length}</span>`;
      a.dataset.target = mod.key;
      navEl.appendChild(a);
      const sec = document.createElement('section');
      sec.className = 'section';
      sec.id = mod.key;
      sec.style.setProperty('--sec-color', mod.color);
      const nReply = entries.reduce((s, o) => s + o.c.replies.length, 0);
      const nImg = entries.reduce((s, o) => s + o.c.images.length, 0);
      const head = document.createElement('div');
      head.className = 'sec-head';
      head.innerHTML = `<span class="dot" style="background:${mod.color}"></span><h2>${mod.name}</h2>
        <span class="badge">${entries.length} 问 · ${nReply} 回复${nImg ? ' · ' + nImg + ' 图' : ''}</span>`;
      sec.appendChild(head);
      const desc = document.createElement('div');
      desc.className = 'sec-desc';
      desc.textContent = mod.desc;
      sec.appendChild(desc);
      DATA.episodes.forEach(e => {
        const cs = entries.filter(o => o.ep.key === e.key).map(o => o.c);
        if (!cs.length) return;
        const sub = document.createElement('div');
        sub.className = 'ep-subhead';
        sub.innerHTML = `<span class="epn">${e.title}</span><span class="c">${cs.length} 问</span>`;
        sec.appendChild(sub);
        cs.forEach(c => sec.appendChild(renderCommentCard(c, mod.color)));
      });
      sectionsEl.appendChild(sec);
      tq += entries.length; tr += nReply; ti += nImg;
    });
    const modObj = DATA.modules.find(m => m.key === currentMod);
    document.getElementById('epName').textContent = currentMod === 'all' ? '全部知识点' : (modObj ? modObj.name : '');
    document.getElementById('heroSub').textContent = currentMod === 'all'
      ? `跨期聚合 · 同一知识点下的题目按期数排列`
      : `${modObj ? modObj.desc : ''} · 跨期聚合`;
  }

  const items = [[tq, '个物理问题'], [tr, '条有效回复'], [ti, '张题图']];
  items.forEach(([n, t]) => {
    const d = document.createElement('div');
    d.className = 'stat';
    d.innerHTML = `<b>${n}</b><span>${t}</span>`;
    statsRow.appendChild(d);
  });
  document.getElementById('sideFoot').textContent = `当前：${tq} 问 · ${tr} 回复`;
  document.getElementById('favCount').textContent = favIds.length;
  document.getElementById('seenCount').textContent = seenIds.length;
  document.getElementById('favToggle').classList.toggle('on', favOnly);
  document.getElementById('viewEp').classList.toggle('on', viewMode === 'episode');
  document.getElementById('viewMod').classList.toggle('on', viewMode === 'module');
  setupScrollspy();
  doSearch();
  if (window.renderMathInElement) {
    try {
      renderMathInElement(sectionsEl, { delimiters: [{left:'\\(', right:'\\)', display:false}], throwOnError:false });
    } catch(e) {}
  }
}

/* ---------- 搜索 ---------- */
const search = document.getElementById('search');
function doSearch() {
  const q = search.value.trim().toLowerCase();
  let shown = 0;
  sectionsEl.querySelectorAll('.c-card').forEach(card => {
    const hit = !q || card.dataset.key.includes(q);
    card.style.display = hit ? '' : 'none';
    if (hit) shown++;
  });
  // 隐藏空分区
  sectionsEl.querySelectorAll('.section').forEach(sec => {
    const any = Array.from(sec.querySelectorAll('.c-card')).some(c => c.style.display !== 'none');
    sec.style.display = any ? '' : 'none';
  });
  // 隐藏空的期数小标题（按知识点视图）
  sectionsEl.querySelectorAll('.ep-subhead').forEach(sub => {
    let nxt = sub.nextElementSibling, any = false;
    while (nxt && !nxt.classList.contains('ep-subhead') && !nxt.classList.contains('section')) {
      if (nxt.classList.contains('c-card') && nxt.style.display !== 'none') { any = true; break; }
      nxt = nxt.nextElementSibling;
    }
    sub.style.display = any ? '' : 'none';
  });
  sectionsEl.querySelectorAll('.ep-banner').forEach(b => {
    let nxt = b.nextElementSibling, any = false;
    while (nxt && !nxt.classList.contains('ep-banner')) {
      if (nxt.classList.contains('section')) {
        const vis = Array.from(nxt.querySelectorAll('.c-card')).some(c => c.style.display !== 'none');
        if (vis) { any = true; break; }
      }
      nxt = nxt.nextElementSibling;
    }
    b.style.display = any ? '' : 'none';
  });
  document.getElementById('empty').style.display = shown ? 'none' : 'block';
  document.getElementById('searchHint').textContent = q ? `匹配到 ${shown} 条评论` : '';
}
search.addEventListener('input', doSearch);

/* ---------- 滚动高亮 ---------- */
let navLinks = [];
function setupScrollspy() {
  navLinks = Array.from(navEl.querySelectorAll('a'));
  if (!navLinks.length) return;
  const targets = navLinks.map(a => document.getElementById(a.dataset.target)).filter(Boolean);
  const onScroll = () => {
    const mid = window.scrollY + window.innerHeight * 0.32;
    let cur = navLinks[0].dataset.target;
    targets.forEach((t, i) => { if (t.offsetTop <= mid) cur = navLinks[i].dataset.target; });
    navLinks.forEach(a => a.classList.toggle('active', a.dataset.target === cur));
  };
  window.addEventListener('scroll', onScroll);
  onScroll();
}

/* ---------- 灯箱(缩放/拖动/旋转/下载) ---------- */
function openLightbox(list, i) {
  lbList = list; lbIdx = i; lbScale = 1; lbRot = 0; lbTx = 0; lbTy = 0; updateLightbox();
  document.getElementById('lightbox').classList.add('open');
}
function applyTransform() {
  const img = document.getElementById('lbImg');
  img.style.transform = `translate(${lbTx}px,${lbTy}px) rotate(${lbRot}deg) scale(${lbScale})`;
}
function updateLightbox() {
  const u = lbList[lbIdx];
  const img = document.getElementById('lbImg');
  img.src = u;
  document.getElementById('lbInfo').textContent = (lbIdx + 1) + ' / ' + lbList.length + '　滚轮缩放 · 拖动平移';
  document.getElementById('lbOrig').href = u;
  document.getElementById('lbDl').onclick = () => {
    const a = document.createElement('a');
    a.href = u; a.download = u.split('/').pop(); document.body.appendChild(a); a.click(); a.remove();
  };
  applyTransform();
}
const lbBox = document.getElementById('lightbox');
document.getElementById('lbClose').onclick = () => lbBox.classList.remove('open');
document.getElementById('lbPrev').onclick = e => { e.stopPropagation(); lbIdx = (lbIdx - 1 + lbList.length) % lbList.length; lbScale=1;lbRot=0;lbTx=0;lbTy=0; updateLightbox(); };
document.getElementById('lbNext').onclick = e => { e.stopPropagation(); lbIdx = (lbIdx + 1) % lbList.length; lbScale=1;lbRot=0;lbTx=0;lbTy=0; updateLightbox(); };
document.getElementById('lbZoomIn').onclick = () => { lbScale *= 1.25; applyTransform(); };
document.getElementById('lbZoomOut').onclick = () => { lbScale /= 1.25; applyTransform(); };
document.getElementById('lbReset').onclick = () => { lbScale = 1; lbRot = 0; lbTx = 0; lbTy = 0; applyTransform(); };
document.getElementById('lbRotL').onclick = () => { lbRot -= 90; applyTransform(); };
document.getElementById('lbRotR').onclick = () => { lbRot += 90; applyTransform(); };
// 滚轮缩放
const lbStage = document.getElementById('lbStage');
lbStage.addEventListener('wheel', e => {
  e.preventDefault();
  lbScale *= (e.deltaY < 0 ? 1.15 : 1 / 1.15);
  lbScale = Math.min(8, Math.max(0.1, lbScale));
  applyTransform();
}, { passive: false });
// 拖动平移
let dragging = false, sx = 0, sy = 0;
lbStage.addEventListener('mousedown', e => { if (e.target.tagName === 'IMG') { dragging = true; sx = e.clientX - lbTx; sy = e.clientY - lbTy; lbStage.classList.add('grabbing'); } });
window.addEventListener('mousemove', e => { if (dragging) { lbTx = e.clientX - sx; lbTy = e.clientY - sy; applyTransform(); } });
window.addEventListener('mouseup', () => { dragging = false; lbStage.classList.remove('grabbing'); });
lbBox.addEventListener('click', e => { if (e.target.id === 'lightbox') lbBox.classList.remove('open'); });
document.addEventListener('keydown', e => {
  if (!lbBox.classList.contains('open')) return;
  if (e.key === 'Escape') lbBox.classList.remove('open');
  if (e.key === 'ArrowLeft') { lbIdx = (lbIdx - 1 + lbList.length) % lbList.length; lbScale=1;lbRot=0;lbTx=0;lbTy=0; updateLightbox(); }
  if (e.key === 'ArrowRight') { lbIdx = (lbIdx + 1) % lbList.length; lbScale=1;lbRot=0;lbTx=0;lbTy=0; updateLightbox(); }
  if (e.key === '+' || e.key === '=') { lbScale *= 1.25; applyTransform(); }
  if (e.key === '-') { lbScale /= 1.25; applyTransform(); }
  if (e.key === '0') { lbScale = 1; lbRot = 0; lbTx = 0; lbTy = 0; applyTransform(); }
});

/* ---------- 收藏 / 已阅 交互 ---------- */
function toggleFav(id) {
  const i = favIds.indexOf(id);
  if (i >= 0) favIds.splice(i, 1); else favIds.push(id);
  setLS(LS_FAV, favIds);
  if (favOnly) render(); else updateCardButtons();
}
function markSeen(id) {
  if (!seenIds.includes(id)) seenIds.push(id);
  setLS(LS_SEEN, seenIds);
  render();
}
function updateCardButtons() {
  sectionsEl.querySelectorAll('.c-card').forEach(card => {
    const id = card.dataset.id;
    const favBtn = card.querySelector('.c-btn.faved, .c-btn:first-child');
    if (favBtn) { const on = favIds.includes(id); favBtn.classList.toggle('faved', on); favBtn.textContent = on ? '★ 已收藏' : '☆ 收藏'; }
  });
}
document.getElementById('favToggle').onclick = () => { favOnly = !favOnly; render(); };
document.getElementById('seenToggle').onclick = () => openSeenModal();

function openSeenModal() {
  const body = document.getElementById('modalBody');
  document.getElementById('modalTitle').textContent = '已阅历史（' + seenIds.length + '）';
  body.innerHTML = '';
  if (!seenIds.length) {
    body.innerHTML = '<div class="modal-empty">还没有标记已阅的题目。</div>';
  } else {
    const all = DATA.episodes.flatMap(e => e.comments.map(c => ({ ep: e.title, c })));
    const byId = {}; all.forEach(o => byId[o.c.id] = o);
    seenIds.forEach(id => {
      const o = byId[id];
      const it = document.createElement('div');
      it.className = 'seen-item';
      const t = document.createElement('div');
      t.className = 't';
      t.textContent = o ? o.c.uname + '：' + o.c.raw_message.slice(0, 60) : id;
      it.appendChild(t);
      const ep = document.createElement('span');
      ep.className = 'ep';
      ep.textContent = o ? o.ep : '';
      it.appendChild(ep);
      const btn = document.createElement('button');
      btn.textContent = '恢复显示';
      btn.onclick = () => {
        seenIds = seenIds.filter(x => x !== id);
        setLS(LS_SEEN, seenIds);
        openSeenModal();
        render();
      };
      it.appendChild(btn);
      body.appendChild(it);
    });
  }
  document.getElementById('modalMask').classList.add('open');
}
document.getElementById('modalClose').onclick = () => document.getElementById('modalMask').classList.remove('open');
document.getElementById('modalMask').addEventListener('click', e => {
  if (e.target.id === 'modalMask') document.getElementById('modalMask').classList.remove('open');
});

/* ---------- 过滤说明 ---------- */
(function buildReport() {
  const ul = document.getElementById('reportList');
  const removedTotal = DATA.episodes.reduce((s, e) => s + e.removed.length, 0);
  const ghostTotal = DATA.episodes.reduce((s, e) => s + e.ghost_merged, 0);
  document.getElementById('reportSummary').textContent =
    `过滤说明（共移除 ${removedTotal} 条占楼/闲聊/归档排除项；${ghostTotal} 条"纯回复"条目已并入所属主题）`;
  const li = document.createElement('li');
  li.innerHTML = '<span class="why">移除内容：</span>' + DATA.episodes.map(e => {
    const lines = e.removed.slice(0, 6).map(r => `${r[0]}「${r[1]}」`).join('、');
    const more = e.removed.length > 6 ? ` 等共 ${e.removed.length} 条` : '';
    return `${e.title}：${lines}${more}`;
  }).join('；');
  ul.appendChild(li);
  const li2 = document.createElement('li');
  li2.innerHTML = `<span class="why">分类说明：</span>全部 ${DATA.episodes.length} 期的 ${DATA.total_q} 条问题均已逐条人工通读分类（含回复上下文），仅个别内容完全在题图中的归入"其他·待定"。`;
  ul.appendChild(li2);
  const li3 = document.createElement('li');
  li3.innerHTML = '<span class="why">结构说明：</span>题图与头像已本地化到 _imgs/ 文件夹（B 站防盗链，浏览器直链无法显示），公式由 KaTeX 本地渲染；请保持 HTML 与 _imgs/、assets/ 目录完整。';
  ul.appendChild(li3);
})();

/* ---------- 视图切换 ---------- */
document.getElementById('viewEp').onclick = () => { viewMode = 'episode'; buildTabs(); render(); };
document.getElementById('viewMod').onclick = () => { viewMode = 'module'; buildTabs(); render(); };

buildTabs();
render();
</script>
</body>
</html>
"""

HTML = HTML.replace('__DATA__', json_str)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(HTML)
print('OK 输出:', os.path.basename(OUT))
print(f'合计: {payload["total_q"]}问 / {payload["total_r"]}回复 / {payload["total_img"]}图')
