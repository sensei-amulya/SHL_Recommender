from fastapi import FastAPI, HTTPException
from models import ChatRequest, ChatResponse, Recommendation
import search_engine
import llm_agent
from dotenv import load_dotenv
import re

load_dotenv()

app = FastAPI(title="SHL Conversational Assessment Recommender")

KEY_TO_TYPE = {
    "Knowledge & Skills": "K",
    "Personality & Behavior": "P",
    "Simulations": "S",
    "Ability & Aptitude": "A",
    "Biodata & Situational Judgment": "B",
    "Competencies": "C",
    "Development & 360": "D",
    "Assessment Exercises": "E"
}

def get_test_type(keys_list: list) -> str:
    types = []
    for key in keys_list:
        if key in KEY_TO_TYPE:
            val = KEY_TO_TYPE[key]
            if val not in types:
                types.append(val)
    if types:
        return ",".join(types)
    return "U"

def extract_shl_urls(text: str) -> list:
    pattern = r"https?://(?:www\.)?shl\.com/products/product-catalog/view/[a-zA-Z0-9_-]+/??"
    urls = re.findall(pattern, text)
    return [u.strip() for u in urls]

@app.on_event("startup")
async def startup_event():
    search_engine.load_and_clean_data()

@app.get("/")
async def root():
    return {"message": "SHL Recommender API is running. Use POST /chat for recommendations, or GET /health for health check."}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty")

    latest_user_message = ""
    for i in range(len(request.messages) - 1, -1, -1):
        msg = request.messages[i]
        if msg.role == "user":
            latest_user_message = msg.content
            break

    if not latest_user_message:
        raise HTTPException(status_code=400, detail="No user message found")

    user_turns = sum(1 for m in request.messages if m.role == "user")

    # Extract previously recommended products from assistant messages in history
    prev_products = []
    seen_prev_ids = set()
    for msg in request.messages:
        if msg.role == "assistant":
            urls = extract_shl_urls(msg.content)
            for u in urls:
                norm_u = search_engine.normalize_url(u)
                if norm_u in search_engine.CATALOG_BY_URL:
                    prod = search_engine.CATALOG_BY_URL[norm_u]
                    eid = str(prod.get("entity_id")).strip()
                    if eid not in seen_prev_ids:
                        seen_prev_ids.add(eid)
                        prev_products.append(prod)

    # Search top 25 products from Chroma DB
    top_25_products = search_engine.search(latest_user_message, top_k=25)

    messages_dicts = [{"role": m.role, "content": m.content} for m in request.messages]

    llm_response = llm_agent.generate_response(
        messages=messages_dicts,
        top_products=top_25_products,
        prev_products=prev_products,
        turn=user_turns
    )

    recommended_ids = llm_response.get("recommended_ids", [])
    if not isinstance(recommended_ids, list):
        recommended_ids = []

    # Valid validation IDs are the union of top 25 matches and previously recommended ones
    valid_validation_ids = set()
    for p in top_25_products:
        valid_validation_ids.add(str(p.get("entity_id")).strip())
    for p in prev_products:
        valid_validation_ids.add(str(p.get("entity_id")).strip())

    seen_recs = set()
    final_recommendations = []
    for eid in recommended_ids:
        str_eid = str(eid).strip()

        if str_eid not in valid_validation_ids:
            continue

        if str_eid in search_engine.CATALOG_DICT:
            if str_eid not in seen_recs:
                seen_recs.add(str_eid)
                product = search_engine.CATALOG_DICT[str_eid]
                name = product.get("name", "")
                url = product.get("link", "")
                test_type = get_test_type(product.get("keys", []))

                final_recommendations.append(Recommendation(
                    name=name,
                    url=url,
                    test_type=test_type
                ))

    final_recommendations = final_recommendations[:10]

    # If the user turn is >= 8, or if LLM marks end of conversation, set end_of_conversation to True
    end_of_conv = bool(llm_response.get("end_of_conversation", False))
    if user_turns >= 8:
        end_of_conv = True

    return ChatResponse(
        reply=llm_response.get("reply", "I'm not sure how to respond to that."),
        recommendations=final_recommendations,
        end_of_conversation=end_of_conv
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

