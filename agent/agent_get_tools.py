

from pydantic_ai import RunContext
from .agent import shipping_agent, ShippingAgentDeps, to_json
from api_client import ShippingAPIError, ShippingAPIClient

@shipping_agent.tool
def get_management_report(ctx:RunContext[ShippingAgentDeps]) -> str:
    """
    ،تجلب هذه الأداة ملخصا إداريًا عامًا عن حالة شركة التوصيل
    ،مثل عدد الشحنات، حالات التسليم، التأخير، المرتجعات
    . الشحنات الملغاة، الإيرادات المحصلة، والإيرادات المعلقة
    . استخدم هذه الأداة عندما يسأل المستخدم عن ملخص الشركة أو التقرير التنفيذي
    """
    try:
        return to_json(ctx.deps.api.get_management_overview())
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


@shipping_agent.tool
def get_delayed_shipments(ctx:RunContext[ShippingAgentDeps]) -> str:
    """
    تجلب هذه الأداة قائمة الشحنات المتأخرة
    استخدم هذه الأداة عندما يسأل المستخدم عن الشحنات المتأخرة
    """
    try:
        return to_json(ctx.deps.api.get_delayed_shipments())
    except ShippingAPIError as e:
        return "API Error: " + str(e)


@shipping_agent.tool
def get_returned_shipments(ctx:RunContext[ShippingAgentDeps]) -> str:
    """
    تجلب هاته الأدات قائمة الشحنات المرتجعة
    إسمتخدم هذه الأداة عندما يسأل الامستخدم عن الشحنات التي رجعت أو عن عدد الشحنات المرتجعة او تفاصيلها 
    """
    try:
        return to_json(ctx.deps.api.get_returned_shipments())
    except ShippingAPIError as e:
        return "API Error: " + str(e)

@shipping_agent.tool
def get_returns(ctx:RunContext[ShippingAgentDeps]) -> str:
    """
   تجلب هاته الأدات سجلات المرتجعات مع أسباب الإرجاع و قيم الإسترداد 
   إستخدم هاته الأداة عندما يسال المستخدم عن أسباب المرتجعات او مشكلات الإرجاع أو المبالغ المتردة او تتجليل المرتجعات
    """
    try:
        return to_json(ctx.deps.api.get_returns())
    except ShippingAPIError as e:
        return "API Error: " + str(e)

@shipping_agent.tool
def get_branches_performance(ctx:RunContext[ShippingAgentDeps]) -> str:
    """
   تجلب هذه الأداة مؤشرات أداء الفروع، مثل عدد الشحنات الكلي
   وعدد الشحنات المسلمة، والمتأخرة، والمرتجعة، والملغاة
   والإيرادات المحصلة لكل فرع
   استخدم هذه الأداة عندما يسأل المستخدم عن أفضل الفروع
   أو أضعف الفروع، أو مقارنة الفروع، أو التأخير حسب الفرع
   أو المرتجعات حسب الفرع، أو الإيرادات حسب الفرع
    """
    try:
        return to_json(ctx.deps.api.get_branches_performance())
    except ShippingAPIError as e:
        return "API Error: " + str(e)





def create_agent_deps():
    return ShippingAgentDeps(api=ShippingAPIClient.from_env())
