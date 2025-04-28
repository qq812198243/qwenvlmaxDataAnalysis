# prompts.py
from langchain.prompts import PromptTemplate

# 提取原始字段的 prompt
extract_prompt_template = PromptTemplate(
    input_variables=["input"],
    template="""
# 角色
你是一个信息抽取专家。请从以下文本中提取所有有用的字段（字段名和字段值），并返回 JSON 格式，如：
{{"buyer": "值1", "address": "值2", "OrderItem": "值3", "Amount": "值4"}}

# 文本如下：

{input}
    """
)

# 标准化字段名的 prompt
standardize_prompt_template = PromptTemplate(
    input_variables=["extracted"],
    template="""
# 你是一个语义理解专家。请将以下 JSON 中的字段名标准化为以下四个之一：

- buyer
- address
- OrderItem
- Amount

# 原始字段：
{extracted}

# 返回json格式要求：
{{"buyer": "值1", "address": "值2", "OrderItem": "值3", "Amount": "值4"}}

    """
)
