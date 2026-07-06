from utils import plugins
from utils.install import update_settings
from events import logic as events_logic

PLUGIN_NAME = "Sabar Language Check"
DISPLAY_NAME = "Sabar"
SHORT_NAME = "sabar"
MANAGER_URL = "sabar_index"
VERSION = "0.1"
JANEWAY_VERSION = "1.7.0"
IS_WORKFLOW_PLUGIN = True
JUMP_URL = "sabar_article"
HANDSHAKE_URL = "sabar_articles"
ARTICLE_PK_IN_HANDSHAKE_URL = True
STAGE = "sabar_plugin"
KANBAN_CARD = "sabar/elements/card.html"
DASHBOARD_TEMPLATE = "sabar/elements/dashboard.html"


class SabarPlugin(plugins.Plugin):
    plugin_name = PLUGIN_NAME
    display_name = DISPLAY_NAME
    short_name = SHORT_NAME
    stage = STAGE
    manager_url = MANAGER_URL
    version = VERSION
    janeway_version = JANEWAY_VERSION
    is_workflow_plugin = IS_WORKFLOW_PLUGIN
    handshake_url = HANDSHAKE_URL
    article_pk_in_handshake_url = ARTICLE_PK_IN_HANDSHAKE_URL


def install():
    SabarPlugin.install()
    update_settings(file_path="plugins/sabar/install/settings.json")


def hook_registry():
    return {
        "core_article_tasks": {
            "module": "plugins.sabar.hooks",
            "function": "article_task_hook",
        }
    }


def register_for_events():
    from plugins.sabar import events

    events_logic.Events.register_for_event(
        events_logic.Events.ON_ARTICLE_SUBMITTED, events.on_article_submitted
    )
