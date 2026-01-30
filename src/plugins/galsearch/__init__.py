from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata


from .config import Config

__plugin_meta__ = PluginMetadata(
    name="galsearch",
    description="galgame搜索",
    usage="/gal <搜索名>",
    config=Config,
)

config = get_plugin_config(Config)

from .search import handle_search_gal