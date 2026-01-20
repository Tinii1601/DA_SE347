import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from google import genai
from google.genai import types
from books.models import Product

# Khởi tạo Client
def get_client():
    try:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            print("Chatbot Error: GEMINI_API_KEY is missing in settings.")
            return None
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Chatbot Init Error: {e}")
        return None

client = None

MODEL_ID = 'gemini-flash-latest' 

@csrf_exempt
def chat_view(request):
    global client
    if client is None:
        client = get_client()

    if request.method == 'POST':
        try:
            if not client:
                return JsonResponse({'response': "Lỗi: Hệ thống chưa cấu hình API Key chính xác."}, status=500)

            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not user_message:
                return JsonResponse({'response': "Chào bạn! Shop có thể giúp gì cho bạn?"})

            # Bước 1: Phân tích ý định (Intent Detection)
            interpretation_prompt = f"""
            Bạn là trợ lý cửa hàng sách. Phân tích tin nhắn: "{user_message}"
            Nếu khách tìm sách hoặc yêu cầu gợi ý, hãy trích xuất 1 từ khóa tìm kiếm ngắn gọn.
            Nếu chỉ chào hỏi, trả về null.
            Trả về định dạng JSON: {{"search_query": "tên sách hoặc null"}}
            """
            
            try:
                response1 = client.models.generate_content(
                    model=MODEL_ID, 
                    contents=interpretation_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type='application/json'
                    )
                )
                interpretation = json.loads(response1.text)
                search_query = interpretation.get('search_query')
            except Exception as e:
                print(f"Lỗi phân tích: {e}")
                search_query = None

            context_info = ""
            if search_query and search_query.lower() != 'null':
                # Tìm kiếm trong Database Django
                products = Product.objects.filter(name__icontains=search_query)[:5]
                if products.exists():
                    product_list = [f"- {p.name} (Giá: {p.price:,.0f}đ)" for p in products]
                    context_info = f"Dưới đây là sách tìm thấy cho từ khóa '{search_query}':\n" + "\n".join(product_list)
                else:
                    context_info = f"Tiếc quá, shop hiện chưa có sách khớp với '{search_query}'."

            # Bước 2: Tạo câu trả lời thân thiện
            system_role = "Bạn là trợ lý AI của 'The Bookstore'. Hãy trả lời thân thiện, ngắn gọn bằng tiếng Việt."
            full_prompt = f"{system_role}\nKhách hỏi: {user_message}\nThông tin hệ thống: {context_info}\nTrả lời khách:"

            response2 = client.models.generate_content(
                model=MODEL_ID,
                contents=full_prompt
            )
            
            return JsonResponse({'response': response2.text})

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Lỗi hệ thống Chatbot:\n{error_details}")
            return JsonResponse({'error': f'Lỗi xử lý: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)