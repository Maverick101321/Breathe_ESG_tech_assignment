import threading


_tenant_context = threading.local()


def set_current_tenant_id(tenant_id):
    _tenant_context.tenant_id = tenant_id


def get_current_tenant_id():
    return getattr(_tenant_context, "tenant_id", None)


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant_id = None
        if request.user.is_authenticated:
            tenant_id = request.user.tenant_id
        set_current_tenant_id(tenant_id)
        try:
            return self.get_response(request)
        finally:
            set_current_tenant_id(None)
