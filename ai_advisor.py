import google.generativeai as genai
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class AIAdvisor:
    """AI Financial Advisor sử dụng Google Gemini"""
    
    def __init__(self):
        print("=" * 60)
        print("🤖 Đang khởi tạo AI Advisor...")
        
        # Kiểm tra API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY chưa được cấu hình trong .env")
            raise ValueError("GEMINI_API_KEY chưa được cấu hình trong .env")
        
        # Mask API key khi hiển thị (chỉ hiện 8 ký tự đầu + cuối)
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
        print(f"✓ API Key tìm thấy: {masked_key}")
        
        try:
            # Cấu hình Gemini
            genai.configure(api_key=api_key)
            print("✓ Đã cấu hình Google Generative AI")
            
            # Khởi tạo model
            self.model = genai.GenerativeModel('gemini-3-flash-preview')  
            print("✓ Đã khởi tạo model: gemini-3-flash-preview")
            
            # Test kết nối đơn giản
            print("⏳ Đang test kết nối API...")
            test_response = self.model.generate_content("Hello")
            
            if test_response and test_response.text:
                print("✅ Kết nối AI thành công!")
                print(f"   Test response: {test_response.text[:50]}...")
            else:
                print("⚠️  Kết nối OK nhưng không nhận được response")
                
        except Exception as e:
            print(f"❌ Lỗi khi khởi tạo AI: {type(e).__name__}")
            print(f"   Chi tiết: {str(e)}")
            if "API_KEY_INVALID" in str(e):
                print("   → API key không hợp lệ. Kiểm tra lại GEMINI_API_KEY trong .env")
            elif "quota" in str(e).lower():
                print("   → Đã hết quota API. Kiểm tra giới hạn tại https://makersuite.google.com")
            elif "network" in str(e).lower() or "connection" in str(e).lower():
                print("   → Lỗi kết nối mạng. Kiểm tra internet và firewall")
            raise
        
        print("=" * 60)
    
    def analyze_financial_health(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phân tích tình hình tài chính tổng thể
        
        Args:
            data: {
                'total_income': float,
                'total_expense': float,
                'savings_goals': List[Dict],
                'current_savings': float,
                'monthly_avg_expense': float,
                'period_months': int
            }
        """
        print("\n" + "=" * 60)
        print("🔍 Đang phân tích tài chính...")
        
        prompt = self._build_analysis_prompt(data)
        print(f"✓ Đã tạo prompt (độ dài: {len(prompt)} ký tự)")
        
        try:
            print("⏳ Đang gọi Gemini API...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                print(f"✅ Nhận được phân tích (độ dài: {len(response.text)} ký tự)")
                print("=" * 60 + "\n")
                return {
                    'success': True,
                    'analysis': response.text,
                    'raw_data': data
                }
            else:
                print("⚠️  Response trống")
                return {
                    'success': False,
                    'error': 'Empty response',
                    'message': 'AI trả về response trống'
                }
                
        except Exception as e:
            print(f"❌ Lỗi khi phân tích: {type(e).__name__}")
            print(f"   Chi tiết: {str(e)}")
            print("=" * 60 + "\n")
            
            error_msg = str(e)
            if "quota" in error_msg.lower():
                user_msg = "Đã hết quota API Gemini. Vui lòng kiểm tra giới hạn."
            elif "invalid" in error_msg.lower() or "key" in error_msg.lower():
                user_msg = "API key không hợp lệ. Kiểm tra GEMINI_API_KEY trong .env"
            elif "network" in error_msg.lower():
                user_msg = "Lỗi kết nối mạng. Kiểm tra internet."
            else:
                user_msg = f"Không thể kết nối AI: {error_msg}"
            
            return {
                'success': False,
                'error': str(e),
                'message': user_msg
            }
    
    def suggest_savings_plan(self, goal: Dict[str, Any], financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gợi ý kế hoạch tiết kiệm cho mục tiêu cụ thể
        
        Args:
            goal: {'name', 'targetAmount', 'currentAmount', 'deadline'}
            financial_data: {'monthly_income', 'monthly_expense', 'other_goals'}
        """
        print("\n" + "=" * 60)
        print(f"📋 Đang tạo kế hoạch cho mục tiêu: {goal.get('name', 'N/A')}")
        
        prompt = self._build_savings_plan_prompt(goal, financial_data)
        print(f"✓ Đã tạo prompt (độ dài: {len(prompt)} ký tự)")
        
        try:
            print("⏳ Đang gọi Gemini API...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                print(f"✅ Nhận được kế hoạch (độ dài: {len(response.text)} ký tự)")
                print("=" * 60 + "\n")
                return {
                    'success': True,
                    'plan': response.text,
                    'goal': goal
                }
            else:
                print("⚠️  Response trống")
                return {
                    'success': False,
                    'error': 'Empty response'
                }
                
        except Exception as e:
            print(f"❌ Lỗi khi tạo kế hoạch: {type(e).__name__}")
            print(f"   Chi tiết: {str(e)}")
            print("=" * 60 + "\n")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Xây dựng prompt phân tích tài chính"""
        total_income = data.get('total_income', 0)
        total_expense = data.get('total_expense', 0)
        current_savings = data.get('current_savings', 0)
        savings_goals = data.get('savings_goals', [])
        monthly_avg = data.get('monthly_avg_expense', 0)
        period = data.get('period_months', 1)
        
        # Tính toán các chỉ số
        savings_rate = ((total_income - total_expense) / total_income * 100) if total_income > 0 else 0
        total_goals = sum(g.get('targetAmount', 0) - g.get('currentAmount', 0) for g in savings_goals)
        
        prompt = f"""
Bạn là chuyên gia tư vấn tài chính cá nhân. Hãy phân tích tình hình tài chính sau và đưa ra lời khuyên cụ thể bằng tiếng Việt:

📊 TÌNH HÌNH TÀI CHÍNH ({period} tháng gần đây):
- Tổng thu nhập: {total_income:,.0f} VNĐ
- Tổng chi tiêu: {total_expense:,.0f} VNĐ
- Chi tiêu trung bình/tháng: {monthly_avg:,.0f} VNĐ
- Tiền tiết kiệm hiện tại: {current_savings:,.0f} VNĐ
- Tỷ lệ tiết kiệm: {savings_rate:.1f}%

🎯 MỤC TIÊU TIẾT KIỆM:
"""
        
        if savings_goals:
            for i, goal in enumerate(savings_goals, 1):
                remaining = goal.get('targetAmount', 0) - goal.get('currentAmount', 0)
                deadline = goal.get('deadline', 'Chưa xác định')
                prompt += f"\n{i}. {goal.get('name', 'Không rõ')}"
                prompt += f"\n   - Mục tiêu: {goal.get('targetAmount', 0):,.0f} VNĐ"
                prompt += f"\n   - Đã có: {goal.get('currentAmount', 0):,.0f} VNĐ"
                prompt += f"\n   - Còn thiếu: {remaining:,.0f} VNĐ"
                prompt += f"\n   - Thời hạn: {deadline}"
        else:
            prompt += "\n(Chưa có mục tiêu nào)"
        
        prompt += f"""

HÃY PHÂN TÍCH VÀ Tư VẤN:
1. Đánh giá tình hình tài chính hiện tại (điểm mạnh/yếu)
2. Tỷ lệ tiết kiệm có hợp lý không? (Chuẩn khuyến nghị: 20-30%)
3. Khả năng đạt được các mục tiêu tiết kiệm
4. Gợi ý số tiền nên tiết kiệm mỗi tháng cho từng mục tiêu
5. Cảnh báo rủi ro (nếu có)
6. 3 hành động cụ thể nên làm ngay

Trả lời ngắn gọn, súc tích, dễ hiểu, sử dụng emoji phù hợp.
"""
        return prompt
    
    def _build_savings_plan_prompt(self, goal: Dict[str, Any], financial_data: Dict[str, Any]) -> str:
        """Xây dựng prompt kế hoạch tiết kiệm cho mục tiêu"""
        target = goal.get('targetAmount', 0)
        current = goal.get('currentAmount', 0)
        remaining = target - current
        deadline = goal.get('deadline', '')
        name = goal.get('name', 'Mục tiêu')
        
        monthly_income = financial_data.get('monthly_income', 0)
        monthly_expense = financial_data.get('monthly_expense', 0)
        monthly_available = monthly_income - monthly_expense
        
        # Tính số tháng còn lại
        months_left = None
        if deadline:
            try:
                deadline_date = datetime.fromisoformat(deadline)
                now = datetime.now()
                delta = deadline_date - now
                months_left = max(1, delta.days // 30)
            except:
                pass
        
        prompt = f"""
Bạn là chuyên gia lập kế hoạch tài chính. Hãy tạo kế hoạch tiết kiệm chi tiết cho mục tiêu sau bằng tiếng Việt:

🎯 MỤC TIÊU: {name}
- Số tiền cần đạt: {target:,.0f} VNĐ
- Đã tiết kiệm: {current:,.0f} VNĐ
- Còn thiếu: {remaining:,.0f} VNĐ
- Thời hạn: {deadline if deadline else 'Chưa xác định'}
{f'- Số tháng còn lại: {months_left}' if months_left else ''}

💰 TÌNH HÌNH TÀI CHÍNH:
- Thu nhập/tháng: {monthly_income:,.0f} VNĐ
- Chi tiêu/tháng: {monthly_expense:,.0f} VNĐ
- Còn dư/tháng: {monthly_available:,.0f} VNĐ

HÃY TẠO KẾ HOẠCH:
1. Số tiền nên tiết kiệm mỗi tháng (realistic và achievable)
2. Timeline cụ thể (từng milestone)
3. Chiến lược tối ưu hóa chi tiêu để đạt mục tiêu
4. Dự phòng rủi ro (nếu thu nhập giảm hoặc chi tiêu tăng)
5. Động viên và tips giữ động lực

Trả lời bằng tiếng Việt, súc tích, dễ hiểu, có emoji.
"""
        return prompt

    def quick_advice(self, question: str, context: Optional[Dict] = None) -> str:
        """Tư vấn nhanh dựa trên câu hỏi người dùng"""
        print("\n" + "=" * 60)
        print(f"💬 Câu hỏi: {question[:50]}...")
        
        prompt = f"Bạn là chuyên gia tài chính cá nhân. Trả lời ngắn gọn bằng tiếng Việt:\n\n{question}"
        
        if context:
            prompt += f"\n\nBối cảnh: {context}"
        
        try:
            print("⏳ Đang gọi Gemini API...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                print(f"✅ Nhận được câu trả lời (độ dài: {len(response.text)} ký tự)")
                print("=" * 60 + "\n")
                return response.text
            else:
                print("⚠️  Response trống")
                return "Xin lỗi, AI không thể trả lời lúc này."
                
        except Exception as e:
            print(f"❌ Lỗi: {type(e).__name__}: {str(e)}")
            print("=" * 60 + "\n")
            return f"Lỗi: {str(e)}"
