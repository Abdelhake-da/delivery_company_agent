from pydantic_ai import RunContext
from .agent import shipping_agent, ShippingAgentDeps, to_json
from api_client import ShippingAPIError

@shipping_agent.tool
def get_executive_report_data(ctx: RunContext[ShippingAgentDeps]) -> str:
    """. تجمع هذه الأداة البيانات الأساسية اللازمة لبناء تقرير تنفيذي عن وضع الشركة
، تشمل البيانات: الملخص الإداري العام، ملخص المدفوعات، أداء الفروع
. الشحنات المتأخرة، وسجلات المرتجعات
،استخدم هذه الأداة عندما يطلب المستخدم تقريرا تنفيذيا
. أو ملخصا إداريا شاملًا، أو نظرة عامة تساعد الإدارة على اتخاذ قرار"""
    try:
        data = {
            "management_overview": ctx.deps.api.get_management_overview(),
            "payment_summary": ctx.deps.api.get_payments_summary(),
            "branch_performance": ctx.deps.api.get_branches_performance(),
            "delayed_shipments": ctx.deps.api.get_delayed_shipments(),
            "return_records": ctx.deps.api.get_returns()
        }
        return to_json(data)
    except ShippingAPIError as e:
        return f"Error: {e}"
