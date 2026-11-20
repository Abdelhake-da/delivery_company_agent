
from .agent import shipping_agent, ShippingAgentDeps, to_json
from api_client import ShippingAPIError
from pydantic_ai import RunContext

@shipping_agent.tool
def create_shipment(
    ctx: RunContext[ShippingAgentDeps],
    customer_id: str,
    customer_name: str,
    branch_id: str,
    branch_name: str,
    origin_city: str,
    destination_city: str,
    expected_delivery: str,
    amount: float,
    weight_kg: float,
) -> str:
    """
    تنشئ هذه الأداة شحنة جديدة من خلال Shipping API.

    الحقول المطلوبة:
    customer_id, customer_name, branch_id, branch_name, origin_city,
    destination_city, expected_delivery, amount, weight_kg.

    استخدم هذه الأداة عندما يطلب المستخدم إنشاء شحنة جديدة
    وتكون جميع البيانات المطلوبة متوفرة.
    """
    shipment_data = {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "branch_id": branch_id,
        "branch_name": branch_name,
        "origin_city": origin_city,
        "destination_city": destination_city,
        "expected_delivery": expected_delivery,
        "amount": amount,
        "weight_kg": weight_kg,
    }

    try:
        return to_json(ctx.deps.api.create_shipment(shipment_data))
    except ShippingAPIError as error:
        return f"API_ERROR: {error}"


@shipping_agent.tool
def update_shipment(
    ctx: RunContext[ShippingAgentDeps],
    shipment_id: str,
    customer_name: str | None = None,
    destination_city: str | None = None,
    expected_delivery: str | None = None,
    amount: float | None = None,
    weight_kg: float | None = None,
) -> str:
    """
    تعدل هذه الأداة الحقول القابلة للتعديل في شحنة موجودة.

    الحقول القابلة للتعديل:
    customer_name, destination_city, expected_delivery, amount, weight_kg.

    استخدم هذه الأداة عندما يطلب المستخدم تعديل بيانات شحنة
    ويحدد رقم الشحنة والحقول التي يريد تعديلها.
    """
    updates = {
        "customer_name": customer_name,
        "destination_city": destination_city,
        "expected_delivery": expected_delivery,
        "amount": amount,
        "weight_kg": weight_kg,
    }

    updates = {
        key: value
        for key, value in updates.items()
        if value is not None
    }

    if not updates:
        return "NO_UPDATES_PROVIDED"

    try:
        data = ctx.deps.api.update_shipment(
            shipment_id=shipment_id,
            updates=updates,
        )
        return to_json(data)
    except ShippingAPIError as error:
        return f"API_ERROR: {error}"


@shipping_agent.tool
def change_shipment_status(
    ctx: RunContext[ShippingAgentDeps],
    shipment_id: str,
    status: str,
) -> str:
    """
    تغيّر هذه الأداة حالة شحنة موجودة.

    الحالات المسموحة:
    delivered, in_transit, delayed, returned, cancelled.

    استخدم هذه الأداة عندما يطلب المستخدم تغيير حالة شحنة.

    """
    allowed_statuses = {
        "delivered",
        "in_transit",
        "delayed",
        "returned",
        "cancelled",
    }

    status = status.strip().lower()

    if status not in allowed_statuses:
        return f"INVALID_STATUS. Allowed statuses: {', '.join(sorted(allowed_statuses))}"

    try:
        data = ctx.deps.api.change_shipment_status(
            shipment_id=shipment_id,
            status=status,
        )
        return to_json(data)
    except ShippingAPIError as error:
        return f"API_ERROR: {error}"


@shipping_agent.tool
def reschedule_shipment(
    ctx: RunContext[ShippingAgentDeps],
    shipment_id: str,
    expected_delivery: str,
) -> str:
    """
   تعيد هذه الأداة جدولة موعد التسليم المتوقع لشحنة.

    استخدم هذه الأداة عندما يطلب المستخدم تغيير موعد التسليم،
    أو تأجيله، أو إعادة جدولة تاريخ التسليم المتوقع.

    """
    try:
        data = ctx.deps.api.reschedule_shipment(
            shipment_id=shipment_id,
            expected_delivery=expected_delivery,
        )
        return to_json(data)
    except ShippingAPIError as error:
        return f"API_ERROR: {error}"


@shipping_agent.tool
def cancel_shipment(
    ctx: RunContext[ShippingAgentDeps],
    shipment_id: str,
    reason: str,
) -> str:
    """
    تلغي هذه الأداة شحنة مع تسجيل سبب واضح للإلغاء.
    هذا الإلغاء آمن soft cancellation، وليس حذفًا نهائيًا من النظام.
    استخدم هذه الأداة فقط عندما يطلب المستخدم إلغاء شحنة
    ويذكر سبب الإلغاء.

    """
    reason = reason.strip()

    if not reason:
        return "CANCELLATION_REASON_REQUIRED"

    try:
        data = ctx.deps.api.cancel_shipment(
            shipment_id=shipment_id,
            reason=reason,
        )
        return to_json(data)
    except ShippingAPIError as error:
        return f"API_ERROR: {error}"


# ---------------------------------------------------------------------
# Safe Drafting Tool
# ---------------------------------------------------------------------

@shipping_agent.tool
def draft_follow_up_message(
    ctx: RunContext[ShippingAgentDeps],
    target: str,
    reason: str,
) -> str:
    """
    تجهز هذه الأداة مسودة رسالة متابعة آمنة لفرع أو فريق داخلي.

    هذه الأداة لا ترسل الرسالة فعليًا، بل تجهز مسودة فقط
    حتى يراجعها الإنسان قبل الإرسال.

    استخدم هذه الأداة عندما يطلب المستخدم إشعار فرع،
    أو متابعة فريق داخلي، أو تجهيز رسالة عن التأخير،
    أو المرتجعات، أو الأعمال المعلقة.
    """
    message = {
        "target": target,
        "reason": reason,
        "requires_human_approval": True,
        "draft_message": (
            f"يرجى مراجعة الحالة التالية: {reason}. "
            "نحتاج إلى تحديث واضح قبل نهاية اليوم مع توضيح سبب التأخير أو المشكلة والإجراء المتخذ."
        ),
    }

    return to_json(message)

def create_agent_deps() -> ShippingAgentDeps:
    return ShippingAgentDeps(
        api=ShippingAPIClient.from_env(),
    )