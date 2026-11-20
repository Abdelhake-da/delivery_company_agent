import json
from dataclasses import dataclass

from dotenv import load_dotenv
from pydantic_ai import Agent, NativeOutput
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider

from api_client import ShippingAPIClient
from models import OperationsAnswer

load_dotenv()


@dataclass
class ShippingAgentDeps:
    api: ShippingAPIClient

def to_json(data: dict, max_items: int = 25) -> str:
    """
    Serialize API data to a compact JSON string safe for the LLM context window.
    - Removes null values recursively to save tokens.
    - Truncates long lists to `max_items` and appends a truncation notice.
    - Uses compact separators (no indentation) to save tokens.
    """
    if isinstance(data, dict):
        processed = {}
        for k, v in data.items():
            if isinstance(v, list):
                if len(v) > max_items:
                    processed[k] = v[:max_items]
                    processed[f"{k}_truncated"] = f"{len(v) - max_items} more items omitted"
                else:
                    processed[k] = v
            else:
                processed[k] = v
        data = processed

    def _drop_nulls(obj):
        if isinstance(obj, dict):
            return {k: _drop_nulls(v) for k, v in obj.items() if v is not None}
        if isinstance(obj, list):
            return [_drop_nulls(v) for v in obj]
        return obj

    data = _drop_nulls(data)
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


ollama_model = OpenAIChatModel(
    model_name="gemma4:12b",
    provider=OllamaProvider(base_url="http://localhost:11434/v1"),
    
)

shipping_agent = Agent(
    ollama_model,  
    deps_type=ShippingAgentDeps,
    model_settings={'thinking': False},
    output_type=OperationsAnswer,
    retries={'tools': 3, 'output': 4}, 
    instructions="""
    أنت مساعد عمليات داخلي لشركة توصيل.
    هدفك مساعدة الإدارة على الاستعلام عن الشحنات والمدفوعات والمرتجعات وأداء الفروع عبر أدوات API المتاحة.

    قواعد استخدام الأدوات:
    - إذا طلب المستخدم ملخصاً إدارياً عاماً أو تقريراً تنفيذياً، استخدم get_management_report.
    - إذا طلب المستخدم قائمة الشحنات أو تفاصيلها، استخدم get_shipments أو get_shipment_by_id.
    - إذا طلب المستخدم الشحنات المتأخرة، استخدم get_delayed_shipments.
    - إذا طلب المستخدم الشحنات المرتجعة، استخدم get_returned_shipments.
    - إذا طلب المستخدم سجلات أو أسباب المرتجعات، استخدم get_returns.
    - إذا طلب المستخدم المدفوعات أو الملخص المالي، استخدم get_payments_summary.
    - إذا طلب المستخدم أداء الفروع أو مقارنتها، استخدم get_branches_performance.
    - إذا كانت البيانات ناقصة، اسأل فقط عن البيانات الناقصة ولا تنفذ الأداة.
    - لا تقل إنك لا تستطيع التنفيذ إذا كانت الأداة المناسبة متاحة والبيانات مكتملة.
    - لا تعرض JSON الخام للمستخدم إلا إذا طلب ذلك صراحة.

    قواعد السلامة التشغيلية:
    - لا تخمّن أي رقم أو حالة شحنة.
    - اعتمد على الأدوات وبيانات API فقط.
    - لا تستخدم أداة إذا كان الطلب غامضاً.
    - اجعل الإجابة بالعربية، مختصرة، عملية، ومناسبة لفريق الإدارة.

    شكل الإجابة:
    - اكتب answer كملخص واضح لما حدث أو لما وجدته.
    - املأ used_data_sources بأسماء الأدوات أو مسارات API المستخدمة.
    - أضف key_metrics عند وجود أرقام مهمة.
    - أضف operational_insights عند وجود مشكلة تشغيلية أو ملاحظة مهمة.
    - أضف proposed_actions عند وجود إجراء مقترح أو خطوة متابعة.

    قاعدة تقنية صارمة جداً:
    - لتسليم الإجابة النهائية، يجب عليك دائماً استدعاء الأداة المخصصة للنتيجة النهائية (final_result) وتمرير البيانات إليها.
    - إياك أن تكتب كود JSON كنص عادي في رسالة الرد المباشرة.

    عند استدعاء أداة final_result، التزم حرفيًا بأسماء المفاتيح الإنجليزية التالية ولا تستبدلها بأي أسماء أخرى:
    - داخل key_metrics استخدم فقط: name, value, meaning
    - داخل operational_insights استخدم فقط: title, severity, evidence, possible_cause, recommended_action
    - داخل proposed_actions استخدم فقط: action_type, description, requires_human_approval
    - داخل draft_messages استخدم فقط: target, reason, message, requires_human_approval
    """,
)