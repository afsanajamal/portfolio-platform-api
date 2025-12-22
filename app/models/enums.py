from enum import Enum

class OrgRole(str, Enum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"
