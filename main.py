from langchain.prompts import PromptTemplate
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain.chat_models import ChatOpenAI
import os
from langchain.chains import LLMChain
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing import Annotated

from langchain.tools import tool
from langchain.schema import HumanMessage
from langchain.schema.messages import SystemMessage
from langchain.schema.messages import HumanMessage, AIMessage
import re
import json

from samples import samples
from prompts import extract_prompt_template, standardize_prompt_template
import json
from IPython.display import Image, display
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]
    input: str
    extracted: str
    standardized: str

# 初始化通义千问模型
# 这里需要将 DASHSCOPE_API_KEY 替换为你在阿里云控制台开通的 API KEY
os.environ["DASHSCOPE_API_KEY"] = ""

# 可以通过 model 指定模型
llm = ChatTongyi(model='qwen-vl-max')
llmText = ChatTongyi(model='qwen-plus',temperature=0.5)

def extract_json_blocks(text):
    """
    从文本中提取所有 ```json ... ``` 块，并转为 Python dict 列表
    """
    pattern = r'```json\s*(\{.*?\})\s*```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    json_objects = []
    for json_str in matches:
        try:
            obj = json.loads(json_str)
            json_objects.append(obj)
        except json.JSONDecodeError as e:
            print(f"解析失败: {e}")
            continue
    return json_objects


@tool
def recognize_image_from_url(image_url: str):
    """识别图片内容，输入是图片URL，输出是识别结果。"""
    systemPrompt= """
    "你是一个信息抽取专家。请从以下文本中提取所有有用的字段（字段名和字段值），并返回 JSON 格式，如：{{"buyer": "值1", "address": "值2", "OrderItem": "值3", "Amount": "值4"}}"
    """
    messages = [
        SystemMessage(content=systemPrompt),
        HumanMessage(content=[
            {"text": "请描述这张图片的内容："},
            {"image": image_url}
        ])
    ]
    response = llm(messages)
    print(response.text)
    return response.text

# 抽取链
extract_chain = LLMChain(
    llm=llm,
    prompt=extract_prompt_template
)

# 标准化链
standardize_chain = LLMChain(
    llm=llmText,
    prompt=standardize_prompt_template
)

# 自定义状态（可选）
# class ExtractState(dict):
#     pass

# 创建流程图
workflow = StateGraph(State)

# ➤ 多模态节点
def recognize_image(state:State):
    # 调用工具函数
    image_url = state["input"]
    result = recognize_image_from_url(image_url)
    # print("图片识别结果：", result)
    return {"input": result}

# ➤ 抽取节点
def extract_fn(state:State):
    response = extract_chain.invoke({"input": state["input"]})

    # print("抽取结果：", response["text"])
    return {"extracted": response["text"]}

# ➤ 标准化节点
def standardize_fn(state:State):
    response = standardize_chain.invoke({"extracted": state["extracted"]})
    print("标准化结果：", response["text"])
    return {"standardized": response["text"]}

# ➤ 输出节点
def output_fn(state:State):
    try:
        return {"output": json.loads(state["standardized"])}
    except:
        return {"output": {"error": "无法解析为 JSON", "raw": state["standardized"]}}

# 添加节点
workflow.add_node("recognize_image", recognize_image)   # ➡️ 先加识别图片的节点
workflow.add_node("extract", extract_fn)
workflow.add_node("standardize", standardize_fn)
workflow.add_node("output", output_fn)

# 设置流程图的边和入口出口
workflow.set_entry_point("recognize_image")  # ➡️ 入口改成 recognize_image
workflow.add_edge("recognize_image", "extract")  # ➡️ 连边 recognize_image -> extract
workflow.add_edge("extract", "standardize")
workflow.add_edge("standardize", "output")
workflow.add_edge("output", END)


# 编译流程图
graph = workflow.compile()

from utils.oss_uploader import OSSUploader
import os
import json

# 初始化OSS上传器
oss_uploader = OSSUploader()

def upload_to_oss(file_path):
    """上传文件到阿里云OSS"""
    try:
        return oss_uploader.upload_file(file_path)
    except Exception as e:
        error_msg = f"[{datetime.datetime.now()}] 上传文件 {file_path} 失败: {str(e)}\n"
        print(error_msg)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(error_msg)
        return None

import datetime

if __name__ == "__main__":
    # 确保log目录存在
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 获取当前日期作为日志文件名
    log_file = os.path.join(log_dir, f"{datetime.datetime.now().strftime('%Y-%m-%d')}.log")
    
    try:
        print("正在生成图像...")
        # 获取图像对象
        graph_image = graph.get_graph().draw_mermaid_png()
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "langgraph_flow.png")
        with open(image_path, "wb") as f:
            f.write(graph_image)
        print(f"图像已保存到: {image_path}")
        # 如果你只是在 Jupyter 中展示，直接 display(image_obj) 就够了
        # display(graph_image)

    except Exception as e:
        error_msg = f"[{datetime.datetime.now()}] 无法生成图像: {str(e)}\n"
        print(error_msg)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(error_msg)
        # This requires some extra dependencies and is optional
        pass
    
    # 上传data文件夹中的png文件
    urls = []
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
    for file in os.listdir(data_dir):
        
        if file.endswith('.png'):
            file_path = os.path.join(data_dir, file)
            oss_url = upload_to_oss(file_path)
            print(f"正在上传文件: {file_path}")
            print(f"OSS URL: {oss_url}")
            if oss_url:
                urls.append(oss_url)
                print(f"已上传文件: {file_path} -> {oss_url}")
    
    # 添加测试URL
    # urls.append('https://agent-dataset.oss-cn-shenzhen.aliyuncs.com/test/data1.png')
    # 运行测试样本
    # for i, sample in enumerate(samples):
    #     print(f"\n 样本 {i+1}：\n原始文本：\n{sample.strip()}\n")
    #     result = app.invoke({"input": sample})
    #     print("📦 结构化输出：")
    #     print(json.dumps(result["extracted"], indent=2, ensure_ascii=False))
    # for i , url in enumerate(urls):
    #     print(f"\n 样本 {i+1}：\n原始文本：\n{url}\n")
    #     result = graph.invoke({"input": url})
    #     # print("📦 结构化输出：")
    #     json_data = result['standardized']
    #     result_json = extract_json_blocks(json_data)

    #     print("📦 结构化输出END：",result_json[0])
        # json_data = result["output"]
        # json_str = json_data.replace("```json", "").replace("```", "").strip()
        # print(json.dumps(json_data, indent=2, ensure_ascii=False))

    # ... 原有代码 ...

    for i , url in enumerate(urls):
        print(f"\n 样本 {i+1}：\n原始文本：\n{url}\n")
        result = graph.invoke({"input": url})
        json_data = result['standardized']
        result_json = extract_json_blocks(json_data)
        if not result_json:
            print("未找到有效的 JSON 块")
            continue
        print("📦 结构化输出END：",result_json[0])

        # 创建 output 文件夹（如果不存在）
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 生成文件名
        file_name = f"sample_{i + 1}.json"
        file_path = os.path.join(output_dir, file_name)

        # 将结果保存到 JSON 文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result_json[0], f, ensure_ascii=False, indent=2)
            print(f"结果已保存到: {file_path}")
        except Exception as e:
            print(f"保存文件 {file_path} 失败: {str(e)}")