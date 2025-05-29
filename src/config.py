import os

# API Configuration
DEEPSEEK_API_KEY = "sk-26a1f35c1d4246ef95d99e97e65ad095"
DEEPSEEK_API_URL = "https://api.deepseek.com"
MODEL_NAME ="deepseek-chat"

# Threading Configuration
MAX_WORKERS = 4  # Adjust based on your system and API rate limits
BATCH_SIZE = 10  # Process files in batches to manage memory

# API Rate Limiting
API_RATE_LIMIT = 60  # requests per minute
REQUEST_DELAY = 1.0  # seconds between requests

EXTRACTION_PROMPT = """你是一个专业的文档分析师，负责从PDF文档中提取关键信息。请根据以下内容提取关键信息，并以JSON格式返回结果。
内容如下：
案件号
原告居住城市
原告代理律师所属律所
原告委托代理人姓名
虚假陈述实施日
原告主张虚假陈述揭露日
被告主张虚假陈述揭露日
原告主张虚假陈述基准日
被告主张虚假陈述基准日
法院认定虚假陈述揭露日
法院认定虚假陈述基准日
更正日
投资者买入股票的日期
投资者卖出股票的日期
法院立案日期
法院裁判日期
诉讼请求金额
实际支持金额
被告名称
虚假陈述种类
投资者未获赔偿理由
是否采取第三方核定计算书
法院计算投资者损失时使用的方法
重大性
是否连带中介机构
省份


注意事项：
若无法提取某个字段，请返回空字符串。
提到中证中心或者多因子模型或者证券投资者损失测算意见书，说明使用了第三方核定计算书。
虚假陈述种类存在以下几种：财务数据造假，关联交易隐瞒，重大合同隐瞒，股权情况造假，重大风险隐瞒，不当披露预测性信息，误导性陈述，不正当披露，重大债务损失隐瞒，承诺履行情况隐瞒，经营情况造假。该信息一般出现在证监会《行政处罚决定书》内容后，或本院认为内容中。
虚假陈述种类可能会有多种情况同时出现，如果有多个虚假陈述种类，请用逗号分隔。
连带高管或自然人指的是被告除了公司以外，还出现了的自然人的姓名
连带中介机构指的是被告除了公司以外，还出现了的会计事务所、律所等中介机构

返回的JSON格式如下：
{
    "案件号": "",
    "原告居住城市": "",
    "原告代理律师所属律所": "",
    "原告委托代理人姓名": "",
    "原告主张虚假陈述揭露日" : "YYYY-MM-DD",
    "被告主张虚假陈述揭露日" : "YYYY-MM-DD",
    "原告主张虚假陈述基准日" : "YYYY-MM-DD",
    "被告主张虚假陈述基准日" : "YYYY-MM-DD",
    "法院认定虚假陈述揭露日" : "YYYY-MM-DD",
    "法院认定虚假陈述基准日": "YYYY-MM-DD",
    "更正日": "YYYY-MM-DD",
    "投资者买入股票的日期": "YYYY-MM-DD",
    "投资者卖出股票的日期": "YYYY-MM-DD",
    "法院立案日期": "YYYY-MM-DD",
    "法院裁判日期": "YYYY-MM-DD",
    "诉讼请求金额": 0,
    "实际支持金额": 0,
    "被告名称": "",
    "虚假陈述种类": "",
    "投资者未获赔偿理由": "",
    "是否采取第三方核定计算书": true,
    "法院计算投资者损失时使用的方法": "",
    "重大性": true,
    "是否连带中介机构": true,
    "是否连带高管或自然人": true,
    "省份": ""
}
"""

# File paths
DEFAULT_OUTPUT_DIR = "./data/output"