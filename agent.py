import json
from dataclasses import dataclass

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext, NativeOutput

from api_client import ShippingAPIClient, ShippingAPIError
from models import OperationsAnswer

load_dotenv()

@dataclass
class ShippingAgentDeps:
    api: ShippingAPIClient


def to_json(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)

shipping_agent = Agent(
    model="ollama:gemma4:12b",
    deps_type=ShippingAgentDeps,
    output_type=NativeOutput(OperationsAnswer),
    # model_settings={'thinking': False}, 
    instructions="""
    أنت مساعد عمليات داخلي لشركة توصيل.
    هدفك مساعدة الإدارة على الاستعلام عن الشحنات وتحليل العمليات وتنفيذ مهام إدارة الشحنات عبر API.

    لديك أدوات فعلية تستطيع من خلالها:
    - إنشاء شحنة جديدة.
    - تعديل بيانات شحنة.
    - تغيير حالة شحنة.
    - إعادة جدولة موعد التسليم.
    - إلغاء شحنة مع سبب.
    - الاستعلام عن الشحنات والمدفوعات والمرتجعات وأداء الفروع.
    - إعداد تقرير تنفيذي شامل اعتمادًا على بيانات الشحنات والمدفوعات والفروع والتأخير والمرتجعات.

    قواعد استخدام الأدوات:
    - إذا طلب المستخدم إنشاء شحنة وكانت كل البيانات المطلوبة متوفرة، استخدم أداة create_shipment.
    - إذا طلب المستخدم تعديل بيانات شحنة وكانت البيانات واضحة، استخدم أداة update_shipment.
    - إذا طلب المستخدم تغيير حالة شحنة، استخدم أداة change_shipment_status.
    - إذا طلب المستخدم إعادة جدولة التسليم، استخدم أداة reschedule_shipment.
    - إذا طلب المستخدم إلغاء شحنة وذكر السبب، استخدم أداة cancel_shipment.
    - إذا طلب المستخدم تقريرًا تنفيذيًا، أو ملخصًا إداريًا شاملًا، أو نظرة عامة عن وضع الشركة، استخدم أداة get_executive_report_data.
    - إذا كانت البيانات ناقصة، اسأل فقط عن البيانات الناقصة ولا تنفذ الأداة.
    - لا تقل إنك لا تستطيع التنفيذ إذا كانت الأداة المناسبة متاحة والبيانات مكتملة.
    - لا تعرض JSON الخام للمستخدم إلا إذا طلب ذلك صراحة.
    - بعد أي عملية إنشاء أو تعديل أو إلغاء، لخّص ما تم تنفيذه بوضوح.
    
    - إذا استخدمت أداة draft_follow_up_message، فضع نص الرسالة الناتجة داخل draft_messages.
    - لا تضع نص مسودة الرسالة داخل proposed_actions فقط.
    - يمكن إضافة إجراء من نوع message_draft داخل proposed_actions، لكن نص الرسالة الكامل يجب أن يكون في draft_messages.
    - لا ترسل الرسالة فعليًا، بل جهزها فقط للمراجعة البشرية.

    قواعد السلامة التشغيلية:
    - لا تخمّن أي رقم أو حالة شحنة.
    - اعتمد على الأدوات وبيانات API.
    - لا تستخدم أداة تنفيذية إذا كان الطلب غامضًا.
    - لا تلغي شحنة إلا إذا ذكر المستخدم سبب الإلغاء.
    - إذا حاول المستخدم حذف شحنة نهائيًا، وضّح أن النظام يستخدم إلغاءً آمنًا soft cancellation بدل الحذف النهائي.
    - اجعل الإجابة بالعربية، مختصرة، عملية، ومناسبة لفريق الإدارة.
    

    شكل الإجابة:
    - اكتب answer كملخص واضح لما حدث أو لما وجدته.
    - املأ used_data_sources بأسماء الأدوات أو مسارات API المستخدمة.
    - أضف key_metrics عند وجود أرقام مهمة.
    - أضف operational_insights عند وجود مشكلة تشغيلية أو ملاحظة مهمة.
    - أضف proposed_actions عند وجود إجراء مقترح أو خطوة متابعة.

    """,

)

@shipping_agent.tool
def get_management_report(ctx:RunContext[ShippingAgentDeps]) -> str:
    """
    ،تجلب هذه الأداة ملخصا إداريًا عامًا عن حالة شركة التوصيل
    ،مثل عدد الشحنات، حالات التسليم، التأخير، المرتجعات
    . الشحنات الملغاة، الإيرادات المحصلة، والإيرادات المعلقة
    . استخدم هذه الأداة عندما يسأل المستخدم عن ملخص الشركة أو التقرير التنفيذي
    """
    try:
        return ctx.deps.api.get_management_overview()
    except ShippingAPIError as e:
        return "API Error: " + str(e)

@shipping_agent.tool
def get_shipments(ctx:RunContext[ShippingAgentDeps], status: str | None = None, branch_name: str | None = None) -> str:
    """
    .تجلب هذه الأداة قائمة الشحنات مع إمكانية استخدام فلاتر اختيارية حسب الحالة واسم الفرع
    . cancelled, returned, delayed, transitin , delivered: OVÁszomall ð „
    . استخدم هذه الأداة عندما يسأل المستخدم عن قائمة الشحنات أو عن بيانات شحنات مفلترة
    """
    try:
        return to_json(ctx.deps.api.get_shipments(status, branch_name))
    except ShippingAPIError as e:
        return "API Error: " + str(e)

@shipping_agent.tool
def get_shipment_by_id(ctx:RunContext[ShippingAgentDeps], shipment_id: str) -> str:
    """
    .تجلب هذه الأداة تفاصيل شحنة محددة باستخدام معرفها
    . استخدم هذه الأداة عندما يسأل المستخدم عن تفاصيل شحنة محددة
    """
    try:
        return to_json(ctx.deps.api.get_shipment_by_id(shipment_id))
    except ShippingAPIError as e:
        return "API Error: " + str(e)

@shipping_agent.tool
def get_payments_summary(ctx:RunContext[ShippingAgentDeps]) -> str:
    """
    ، تجلب هذه الأداة ملخص المدفوعات، بما في ذلك المبالغ المدفوعة
    . والمبالغ المعلقة، والمبالغ المستردة
    ، استخدم هذه الأداة عندما يسأل المستخدم عن الإيرادات
    ،أو التحصيل، أو المدفوعات المعلقة، أو المبالغ المستردة . أو الملخص المالي
    """
    try:
        return to_json(ctx.deps.api.get_payments_summary())
    except ShippingAPIError as e:
        return "API Error: " + str(e)

def create_agent_deps():
    return ShippingAgentDeps(api=ShippingAPIClient.from_env())
