活动数据看板
一个基于 Python + Streamlit + Pandas 的轻量级活动数据看板，用于展示 4 个二维码的每日转化数据对比、趋势和抽奖记录。
功能
🎯 核心指标卡：落地页浏览、下单页浏览、创建订单、支付成功、成单率
📋 二维码横向对比表：4 个二维码所有指标并排对比，含合计列
📈 每日趋势图：支持切换指标，查看各二维码的历史变化
🎁 抽奖记录：支持日期、活动 key、场次 key、礼品、抽奖结果筛选和用户 ID 搜索，用户 ID 自动脱敏
🔍 顶部筛选：日期范围 + 二维码多选
快速开始
1. 安装依赖
cd activity-dashboard
pip install -r requirements.txt

2. 启动看板
streamlit run app.py

启动后浏览器会自动打开 http://localhost:8501。
3. 数据文件放在哪里
将 Excel 文件（.xlsx / .xls）或 CSV 文件放入项目的 data/ 目录即可。
当前已放入 抽奖数据.xlsx 作为示例数据。
activity-dashboard/
├── app.py
├── requirements.txt
├── README.md
└── data/
    └── 抽奖数据.xlsx   ← 数据文件放这里

每天怎么更新数据
有两种方式，任选其一：
方式一：替换文件（推荐）
将当天最新的数据导出为 Excel 文件
替换 data/ 目录中的旧文件（文件名可以不同，程序会自动读取最新修改的文件）
在浏览器中按 F5 刷新页面，即可看到最新数据
方式二：追加数据
在原 Excel 文件中新增一行当天的数据（保持列名不变），保存后刷新页面。
⚠️ 注意：程序不会修改你的原始 Excel 文件，只做读取。每日数据会保留历史，不会覆盖。
4 个二维码对应字段在哪里修改
打开 app.py，找到顶部的 QR_CODE_CONFIG 配置项：
QR_CODE_CONFIG = {
    "二维码1": "校边店海报1",
    "二维码2": "校边店海报2",
    "二维码3": "校边店海报3",
    "二维码4": "校边店海报4",
}

键（如 "二维码1"）：页面上显示的名称
值（如 "校边店海报1"）：Excel 文件中对应的 Sheet 名称
如果后续二维码对应的 Sheet 名变化，只需修改这里的值即可。
抽奖记录的 Sheet 名也可以在同文件中修改：
LOTTERY_SHEET_NAME = "抽奖记录"

数据格式要求
二维码数据 Sheet
每个二维码对应一个 Sheet，需包含以下列（列名需一致）：
列名
说明
日期
MMDD 格式，如 909 表示 9 月 9 日
落地页浏览
整数
选择年级
整数
下单页浏览
整数
发送验证码
整数
登陆成功
整数
创建订单
整数
支付成功
整数
落地页转化率
小数（如 0.2 表示 20%）
下单页转化率
小数
支付成功率
小数
成单率
小数
完善信息页曝光 UV
整数
地址提交 UV
整数
支付结果页曝光 UV
整数

转化率列中的 - 或空值会被自动视为空值处理，不影响其他数据。
抽奖记录 Sheet
列名
说明
用户 id
整数（页面会自动脱敏显示）
活动 key
文本
场次 key
文本
抽奖时间
日期时间
礼品 id
文本
礼品
文本
礼品类型
文本
抽奖结果
文本（如 "已中奖"）
日期
MMDD 格式

怎么部署成其他人可以访问的网页
方案一：Streamlit Community Cloud（免费，推荐）
将项目推送到 GitHub 仓库
访问 share.streamlit.io
用 GitHub 账号登录，点击 "New app"
选择你的仓库、分支，主文件填 app.py
点击 "Deploy"，几分钟后获得一个 https://xxx.streamlit.app 链接
把链接发给导师即可
注意：Streamlit Cloud 上 data/ 目录中的文件需要随代码一起提交到 GitHub。更新数据时需要重新提交并推送。
方案二：内网部署（团队服务器）
在一台团队可访问的服务器上：
# 安装依赖
pip install -r requirements.txt

# 启动（指定端口和允许外部访问）
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

其他人通过 http://服务器IP:8501 访问。
方案三：内网穿透（临时分享）
使用 ngrok、frp 等工具将本地端口映射到公网，适合临时演示。
常见问题
Q: 刷新页面后数据没更新？
A: 请确认新文件已放入 data/ 目录，且文件名以 .xlsx / .xls / .csv 结尾。程序会自动读取目录中最新修改的文件。
Q: 页面提示 "未找到 sheet"？
A: 检查 Excel 文件中的 Sheet 名称是否与 app.py 中 QR_CODE_CONFIG 配置一致。
Q: 日期显示不对？
A: 程序默认将 MMDD 格式的日期解析为 2026 年。如果年份不同，修改 app.py 中 parse_date 函数里的 year=2026。
Q: 有重复日期怎么办？
A: 页面顶部会弹出数据提示，列出存在重复日期的二维码。请检查原始数据，删除或修正重复行。
技术栈
Python 3.9+
Streamlit（Web 框架）
Pandas（数据处理）
NumPy（数值计算）
OpenPyXL（Excel 读取）