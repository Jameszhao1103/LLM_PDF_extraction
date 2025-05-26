import os

# API Configuration
DEEPSEEK_API_KEY = "sk-26a1f35c1d4246ef95d99e97e65ad095"
DEEPSEEK_API_URL = "https://api.deepseek.com"
MODEL_NAME ="deepseek-chat"

# Document extraction prompt
EXTRACTION_PROMPT = """你是一个专业的文档分析师，负责从PDF文档中提取关键信息。请根据以下内容提取关键信息，并以JSON格式返回结果。
内容如下：
虚假陈述实施日
虚假陈述揭露日
更正日
立案日期
裁判日期诉讼请求金额
实际支持金额
被告名称
虚假陈述种类
是否采取第三方核定计算书
重大性
是否连带中介结构
省份

注意事项：
提到中证中心或者多因子模型或者证券投资者损失测算意见书，说明使用了第三方核定计算书。
虚假陈述种类存在以下几种：财务数据造假，关联交易隐瞒，重大合同隐瞒，股权情况造假，重大风险隐瞒，不当披露预测性信息，误导性陈述，不正当披露，重大债务损失隐瞒，承诺履行情况隐瞒，经营情况造假。
虚假陈述种类可能会有多种情况同时出现，如果有多个虚假陈述种类，请用逗号分隔。

返回的JSON格式如下：
{
    "虚假陈述实施日": "YYYY-MM-DD",
    "虚假陈述揭露日": "YYYY-MM-DD",
    "更正日": "YYYY-MM-DD",
    "立案日期": "YYYY-MM-DD",
    "裁判日期": "YYYY-MM-DD",
    "诉讼请求金额": 0,
    "实际支持金额": 0,
    "被告名称": "",
    "虚假陈述种类": "",
    "是否采取第三方核定计算书": true,
    "重大性": true,
    "是否连带中介结构": true,
    "省份": ""
}
"""

# File paths
DEFAULT_OUTPUT_DIR = "../data/output"