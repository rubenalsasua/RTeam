from django.shortcuts import redirect

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
            return redirect('index')
        return view_func(request, *args, **kwargs)

    return wrapper


class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'ADMIN':
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)
