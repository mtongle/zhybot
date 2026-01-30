from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    api_base_url: str = "https://cf.api.searchgal.top/gal"
    api_tags: dict[str, str] = {
        "NoReq": "无门槛",
        "Login": "需登录",
        "LoginPay": "需付费",
        "LoginRep": "需回复",
        "SuDrive": "自建盘",
        "NoSplDrive": "不限速盘",
        "SplDrive": "限速盘",
        "MixDrive": "混合盘",
        "BTmag": "BT/磁力",
        "magic": "需魔法"
    }
    api_not_recommend: list[str] = ["LoginPay"]
    api_recommend: list[list[str]] = [["NoReq"], ["SuDrive", "NoSplDrive", "MixDrive"]]
    api_warned: list[str] = ["magic", "SplDrive"]
    api_max_show: int = 5