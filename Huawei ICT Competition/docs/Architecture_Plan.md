华为ICT大赛 - 赛道3：基于Nexent的演进式决策智能体
Huawei ICT Competition - Challenge 3: Evolving Decision-Making Agent


1. 问题背景（基于v5.2原型验证）
1. The Problem (Proven by v5.2 Prototype)

我们在本地基于Ollama的原型（v5.2）中证明了：原生大语言模型（LLM）无法被信任来直接进行底层的连续物理控制。测试中出现了以下问题：
Our local Ollama prototype (v5.2) proved that raw LLMs cannot be trusted with low-level, continuous physics control. The LLM exhibited:

控制抖动 (Control Chatter): LLM每隔0.2秒在加速和减速之间来回震荡，导致移动3米需要耗费40个控制步长。

逻辑倒置 (Logic Inversion): 当机器人已经处于静止状态（0.0 m/s）时，LLM发出指令“减速以达到0.5 m/s的限速”。

延迟盲区 (Latency Blind Spots): 由于LLM API的响应延迟，系统错过了关键的制动窗口。

Control Chatter: Oscillating between accelerate/decelerate every 0.2s, taking 40 steps to cross 3 meters.

Logic Inversion: Commanding the robot to "decelerate to reach 0.5 m/s" when the robot was already stationary at 0.0 m/s.

Latency Blind Spots: Missing the braking window because of LLM API response times.


2. 解决方案（v6.0 层级式原型）
2. The Solution (v6.0 Hierarchical Prototype)

我们设计了一种解耦的层级架构，将“战略推理”交给LLM，将“物理与安全”交给确定性的Python代码：
We designed a decoupled architecture where the LLM handles strategic reasoning, while deterministic Python handles physics and safety:

组件A：战略智能体 (LLM)： 根据所需的制动距离，决定高层的运行模式（NORMAL_MODE 或 SAFE_APPROACH_MODE）。

组件B：本地控制器： 类PID的确定性控制循环，执行平滑的加速/减速，彻底消除控制抖动。

组件C：独立安全监督器： 最终权限者。如果触及数学计算出的制动阈值，它将强制覆盖LLM的危险决策，执行紧急制动。

Component A: Strategic Agent (LLM): Decides high-level modes (NORMAL_MODE or SAFE_APPROACH_MODE) based on the required braking distance.

Component B: Local Controller: A deterministic PID-like loop that executes smooth acceleration/deceleration to prevent chatter.

Component C: Safety Supervisor: The final authority. Overrides unsafe LLM decisions if the mathematical braking threshold is breached.


3. 向华为Nexent平台的迁移计划 (最终架构)
3. Transition to Huawei Nexent (Final Architecture)

当前的v6.0 Python代码是基于Ollama的本地概念验证。为了满足大赛对“先进制造”和“激活沉睡数据资产”的要求，系统将于12月全面迁移至华为 ModelEngine Nexent。
The current v6.0 Python code is a local proof-of-concept running on Ollama. To meet the competition requirements for "Advanced Manufacturing" and "Sleeping Data Assets," the system will migrate to Huawei ModelEngine Nexent in December.

A. 虚拟环境构建与数据资产 (Excel与RAG)

我们将使用结构化的Excel表格构建虚拟工厂环境（例如：映射12米至4米人类工作区的分区表，以及详细说明1.0 m/s²最大减速度的机器人规格表）。

这些Excel文件及PDF安全手册将被上传至Nexent知识库。Nexent将作为RAG（检索增强生成）引擎，将“沉睡的数据”转化为主动的安全规则。
A. Virtual Environment & Data Assets (Excel & RAG)

We will build structured Excel tables to represent the virtual factory environment (e.g., Zoning Tables mapping the Human Work Zone from 12m to 4m, and Robot Specs detailing max deceleration of 1.0 m/s²).

These Excel files, along with PDF Safety Manuals, will be uploaded to the Nexent Knowledge Base. Nexent will act as the RAG engine, turning our "sleeping data" into active safety rules.

B. 将Nexent作为核心大脑

本地的Ollama将被Nexent平台上的盘古大模型（或DeepSeek）取代。

战略智能体将不再依赖硬编码的提示词。它将使用Nexent查询知识库并进行推理（例如：“根据Excel数据，机器人当前负载500kg，因此制动距离必须增加。”）
B. Nexent as the Core Brain

Local Ollama will be replaced by Huawei's Pangu Model (or DeepSeek) hosted on Nexent.

The Strategic Agent will no longer rely on hardcoded prompts. It will use Nexent to query the Knowledge Base, reasoning: "The robot is carrying 500kg (from Excel data), so the braking distance increases."

C. MCP工具 (技能集成)

我们的Python函数 calculate_required_distance 将被部署为MCP工具（模型上下文协议）。

Nexent智能体将通过“检索-推理”双驱动流程调用该工具。LLM负责逻辑，MCP工具负责精确的数学计算。
C. MCP Tools (Skills)

Our Python calculate_required_distance function will be deployed as an MCP Tool (Model Context Protocol).

The Nexent Agent will call this tool via a "Retrieval-Reasoning" flow. The LLM handles the logic; the MCP tool executes the math.

D. 持续演进与记忆

在本地原型中，经验教训保存在JSON文件中。在Nexent中，记忆将由平台的Memory模块统一管理。

当安全监督器覆盖了LLM的错误决策时，Nexent将存储该“失败片段”并动态更新智能体的上下文，确保系统“越用越聪明”。
D. Persistent Evolution

In the local prototype, lessons are saved to a JSON file. In Nexent, memory will be managed by the platform's Memory Module.

When the Safety Supervisor overrides a bad LLM decision, Nexent will store this "Failure Episode" and dynamically update the Agent's context, ensuring the system gets "smarter the more it's used."


4. 竞赛交付物
4. Competition Deliverables

当前已完成： 本地Python仿真（v6.0）、失败分析文档、架构方案。

12月计划： Nexent智能体配置、MCP工具集成、Excel数据资产、开发与设计Word文档。

Current (Done): Local Python simulation (v6.0), Failure Analysis Document, Architecture Plan.

December (Upcoming): Nexent Agent configuration, MCP tool integration, Excel Data Assets, Development & Design Word Document.
