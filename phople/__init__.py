import os

from django.conf import settings

"""
AWS Credential Setup
SUPER-IMPORTANT: DO-NOT-EDIT-FOLLOWING-LINE
"""
os.environ['BOTO_CONFIG'] = os.path.join(getattr(settings, 'BASE_DIR'), *['credentials', 'boto.cfg'])
