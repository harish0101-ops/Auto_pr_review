from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing import List, Dict, TypedDict, Optional
import os

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv
load_dotenv()


llm = ChatOpenAI(
    model="sonar-pro",
    openai_api_base="https://api.perplexity.ai",
    openai_api_key=os.getenv("PERPLEXITY_API_KEY"),
)

class AgentState(TypedDict):
    pr_files: List[Dict] 
    parsed_files: List[Dict] 
    files: List[Dict]
    summary: Dict 

def run_agent(pr_files: List[Dict]) -> Dict:
    """LangGraph-based agent pipeline for PR analysis."""

    graph = StateGraph(AgentState)
    print(" running agent for review pr")

    # Node 1: Parse Diff
    def parse_diff(state: AgentState): 
        parsed_files = []
        for file in state["pr_files"]:
            parsed_files.append({
                "filename": file["filename"],
                "diff_chunks": [
                    hunk.strip() for hunk in file["diff"].split("@@") if hunk.strip()
                    ]
            })
        return {"parsed_files": parsed_files}

    # Node 2: Review Each File
    def review_code(state: AgentState):
        reviewed = []

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You're a code reviewer AI. Analyze the given code diff and detect issues."),
            ("human", "{diff}")
        ])
        chain = prompt_template | llm | StrOutputParser()

        for file in state["parsed_files"]:
            issues = []
            for chunk in file["diff_chunks"]:
                if chunk.strip() == "":
                    continue
                try:
                    llm_output = chain.invoke({"diff": chunk})
                    issues.append({
                        "type": "ai-suggested",
                        "line": 0,
                        "description": llm_output,
                        "suggestion": "Refer to comment"
                    })
                except Exception as e:
                    issues.append({
                        "type": "error",
                        "line": 0,
                        "description": str(e),
                        "suggestion": "LLM failed"
                    })

            reviewed.append({
                "name": file["filename"],
                "issues": issues
            })

        return {"files": reviewed}


    # Node 3: Summarize
    def summarize(state: AgentState): # Add type hint for clarity
        total_issues = sum(len(f["issues"]) for f in state["files"])
        return {
            "files": state["files"],
            "summary": {
                "total_files": len(state["files"]),
                "total_issues": total_issues,
                "critical_issues": total_issues // 2  # Simplified logic
            }
        }

    # Graph connections (revised for newer LangGraph API)
    graph.add_node("parse_diff", parse_diff)
    graph.add_node("review_code", review_code)
    graph.add_node("summarize", summarize)

    graph.add_edge("parse_diff", "review_code")
    graph.add_edge("review_code", "summarize")

    graph.set_entry_point("parse_diff") # Use set_entry_point instead of set_entry_node

    graph.set_finish_point("summarize") # Use set_finish_point instead of set_finish_node

    app = graph.compile()

    final_result = app.invoke({"pr_files": pr_files})
    return final_result