import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
import google.generativeai as genai
from google.genai import types
from books.models import Product, Category

# Khởi tạo Client
def get_client():
    try:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            print("Chatbot Error: GEMINI_API_KEY is missing in settings.")
            return None
        # Debug: Print masked key to verify which key is being used
        masked_key = api_key[:5] + "..." + api_key[-5:] if len(api_key) > 10 else "***"
        print(f"Chatbot: Using API Key: {masked_key}")
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
            Nhiệm vụ:
            1. Xác định xem khách có đang tìm sách, hỏi về sách, hay muốn gợi ý sách không.
            2. Trích xuất từ khóa chính (Subject/Title/Category). 
               - Loại bỏ các từ chỉ tính chất: 'hay', 'tốt nhất', 'mới nhất', 'hot', 'giúp tôi', 'gợi ý', 'top', 'những', 'các'.
               - Loại bỏ các từ chỉ số lượng hoặc đối tượng chung chung nếu chúng không phải là tên riêng: '5', '10', 'sản phẩm', 'quyển', 'cuốn', 'sách'.
               - Giữ lại tên tác giả, tên tác phẩm, hoặc thể loại cụ thể.
            
            Ví dụ:
            - "Gợi ý 5 sách văn học hay" -> "Văn học"
            - "cho mình xem 5 san pham ve tam ly" -> "Tâm lý"
            - "Tìm sách Nhà giả kim" -> "Nhà giả kim"
            - "Có truyện doremon không" -> "Doremon"
            - "Chào shop" -> null

            Trả về định dạng JSON duy nhất: {{"search_query": "tên sách/danh mục hoặc null"}}
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
                print(f"Chatbot: Search Query = '{search_query}'")
            except Exception as e:
                print(f"Lỗi phân tích: {e}")
                search_query = None

            context_info = ""
            products_data = [] # Dữ liệu sản phẩm gửi về frontend

            if search_query and str(search_query).lower() != 'null':
                # Tìm kiếm trong Database Django (Tên hoặc Danh mục)
                from django.db.models import Q

                # 1. Tìm các Categories khớp với keyword để lấy cả danh mục con
                target_cat_ids = set()
                try:
                    matching_cats = Category.objects.filter(name__icontains=search_query)
                    for cat in matching_cats:
                        target_cat_ids.update(cat.get_descendants_and_self_ids())
                except Exception as e:
                    print(f"Lỗi tìm danh mục: {e}")

                # 2. Tìm sản phẩm: Theo tên HOẶC theo danh mục (bao gồm cả danh mục con)
                products = Product.objects.filter(
                    Q(name__icontains=search_query) | 
                    Q(category__id__in=target_cat_ids) |
                    Q(category__name__icontains=search_query),
                    is_active=True
                ).distinct()[:5]
                
                print(f"Chatbot: Found {products.count()} products for '{search_query}'")

                if products.exists():
                    product_list_text = []
                    for p in products:
                        if p.is_on_sale:
                            price_str = f"{p.get_final_price():,.0f}đ (Gốc: {p.price:,.0f}đ - Giảm {p.discount_percentage}%)".replace(",", ".")
                            final_price = f"{p.get_final_price():,.0f}đ".replace(",", ".")
                        else:
                            price_str = f"{p.price:,.0f}đ".replace(",", ".")
                            final_price = f"{p.price:,.0f}đ".replace(",", ".")

                        product_list_text.append(f"- {p.name} (Giá: {price_str})")
                        
                        # Build info for card
                        try:
                            img_url = p.cover_image.url if p.cover_image else '/static/img/default-book-cover.jpg'
                        except:
                            img_url = '/static/img/default-book-cover.jpg'

                        products_data.append({
                            'name': p.name,
                            'price': final_price,
                            'original_price': f"{p.price:,.0f}đ".replace(",", ".") if p.is_on_sale else "",
                            'is_on_sale': p.is_on_sale,
                            'image': img_url,
                            'url': reverse('books:book_detail', args=[p.slug])
                        })

                    context_info = f"Hệ thống tìm thấy {len(products)} sách phù hợp với '{search_query}':\n" + "\n".join(product_list_text)
                else:
                    context_info = f"Hệ thống tìm kiếm '{search_query}' nhưng không thấy sản phẩm nào khớp."

            # Bước 2: Tạo câu trả lời thân thiện
            system_role = "Bạn là trợ lý AI của 'The Bookstore'. Hãy trả lời thân thiện, ngắn gọn bằng tiếng Việt. Nếu có danh sách sách, hãy mời khách xem thẻ bên dưới."
            full_prompt = f"{system_role}\nKhách hỏi: {user_message}\nThông tin hệ thống: {context_info}\nTrả lời khách:"

            response2 = client.models.generate_content(
                model=MODEL_ID,
                contents=full_prompt
            )
            
            return JsonResponse({
                'response': response2.text,
                'products': products_data
            })

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Lỗi hệ thống Chatbot:\n{error_details}")
            
            # Xử lý lỗi API Key bị lộ hoặc hết hạn
            error_str = str(e)
            if "403" in error_str or "PERMISSION_DENIED" in error_str:
                return JsonResponse({'response': "Xin lỗi, hệ thống AI đang bảo trì (Lỗi API Key). Vui lòng liên hệ Admin."}, status=200)
            
            if "400" in error_str and "API key expired" in error_str:
                 return JsonResponse({'response': "Xin lỗi, key AI đã hết hạn. Vui lòng cập nhật key mới."}, status=200)

            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                 return JsonResponse({'response': "Xin lỗi, chatbot đang bị quá tải giới hạn miễn phí của Google (Rate Limit). Bạn vui lòng đợi khoảng 15-30 giây rồi thử lại nhé!"}, status=200)

            return JsonResponse({'response': "Xin lỗi, hiện tại mình đang gặp chút sự cố. Bạn thử lại sau nhé!"}, status=200)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)