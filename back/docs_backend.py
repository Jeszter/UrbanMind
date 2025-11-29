from dotenv import load_dotenv
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from agents import Agent, Runner, function_tool, WebSearchTool
import PyPDF2
from pydantic import BaseModel
from back.system_prompts import docs_system_prompt

load_dotenv()

router = APIRouter()

class RequestValue(BaseModel):
    message: str

def read_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

@function_tool
def about_doc(file_path: str) -> str:
    """
    Passes the content of a PDF document to the main agent.

    :param file_path: path to the PDF file
    :return: text content of the PDF
    """
    return read_pdf(file_path)

document_agent = Agent(
    name="Document Agent",
    instructions=docs_system_prompt,
    model="gpt-4o",
    tools=[WebSearchTool(), about_doc]
)

@router.post("/chat")
async def docs_chat(request_data: RequestValue):
    """
    Request body should be JSON like:
    {
        "message": "user text"
    }
    """
    message = request_data.message.strip()
    if not message:
        return JSONResponse({"status": "error", "message": "Message is empty."}, status_code=400)
    try:
        result = await Runner.run(document_agent, message)
        reply = result.final_output
        return JSONResponse({"status": "success", "reply": reply})
    except Exception as e:
        return JSONResponse({"status": "error", "message": f"Documents chat error: {str(e)}"}, status_code=500)
