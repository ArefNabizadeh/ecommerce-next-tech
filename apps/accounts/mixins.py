# apps/accounts/mixins.py
from .models import UserActivity


class ActivityLogMixin:
    """میکسین برای ثبت خودکار فعالیت‌ها"""

    def log_activity(self, activity_type, message, icon=None, metadata=None):
        if self.request.user.is_authenticated:
            UserActivity.log_activity(
                user=self.request.user,
                activity_type=activity_type,
                message=message,
                icon=icon,
                metadata=metadata,
                request=self.request
            )